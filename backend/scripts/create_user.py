"""
Create an initial user (admin or regular).

Usage:
    python scripts/create_user.py --email admin@example.com --password secret --superuser
"""
import argparse
import asyncio
from pathlib import Path
import sys
import uuid

# Ensure project root is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models.user import User, UserRole  # noqa: E402


async def create_user(email: str, password: str, full_name: str, superuser: bool) -> None:
    async with AsyncSessionLocal() as db:
        user = User(
            id=uuid.uuid4(),
            email=email,
            hashed_password=hash_password(password),
            display_name=full_name or email.split("@")[0],
            role=UserRole.ADMIN if superuser else UserRole.VIEWER,
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        print(f"Created user: {user.email} (id={user.id}, superuser={user.is_superuser})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an AgentOps user")
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--name", default="", help="Full name (optional)")
    parser.add_argument("--superuser", action="store_true", default=False)
    args = parser.parse_args()

    asyncio.run(create_user(args.email, args.password, args.name, args.superuser))


if __name__ == "__main__":
    main()
