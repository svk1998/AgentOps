from httpx import AsyncClient
import pytest


async def _auth_headers(client: AsyncClient) -> dict[str, str]:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "phase1@example.com",
            "password": "secret123",
            "display_name": "Phase 1 Tester",
        },
    )
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "phase1@example.com", "password": "secret123"},
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


@pytest.mark.asyncio
async def test_agent_dataset_eval_run_flow(client: AsyncClient):
    headers = await _auth_headers(client)

    agent_res = await client.post(
        "/api/v1/agents",
        headers=headers,
        json={
            "name": "Wine Label Recognizer",
            "agent_type": "vision",
            "endpoint_url": "https://api.internal/agents/wine",
            "model_provider": "Gemini 1.5 Pro",
            "input_schema": {"type": "object"},
            "output_schema": {"type": "object"},
            "version": "1.0.0",
            "tags": ["vision", "wine"],
            "owner": "QA",
            "status": "active",
        },
    )
    assert agent_res.status_code == 201
    agent = agent_res.json()

    dataset_res = await client.post(
        "/api/v1/datasets",
        headers=headers,
        json={
            "name": "Wine Labels v1",
            "agent_type": "vision",
            "items": [
                {
                    "input": {"image_url": "https://example.com/bottle.jpg"},
                    "expected_output": {"wine_name": "Demo Wine"},
                    "metadata": {"difficulty": "easy"},
                }
            ],
        },
    )
    assert dataset_res.status_code == 201
    dataset = dataset_res.json()
    assert dataset["item_count"] == 1

    run_res = await client.post(
        "/api/v1/eval-runs",
        headers=headers,
        json={"agent_id": agent["id"], "dataset_id": dataset["id"], "config": {"matcher": "exact"}},
    )
    assert run_res.status_code == 201
    run = run_res.json()
    assert run["agent_version"] == "1.0.0"
    assert run["total_items"] == 1

    versions_res = await client.get(f"/api/v1/agents/{agent['id']}/versions", headers=headers)
    assert versions_res.status_code == 200
    assert len(versions_res.json()) == 1
