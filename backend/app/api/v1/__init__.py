from fastapi import APIRouter

from app.api.v1 import (
    agents,
    analytics,
    auth,
    datasets,
    eval_runs,
    manual_eval,
    rag_datasets,
    users,
)

router = APIRouter(prefix="/v1")
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(agents.router)
router.include_router(datasets.router)
router.include_router(rag_datasets.router)
router.include_router(eval_runs.router)
router.include_router(manual_eval.router)
router.include_router(analytics.router)
