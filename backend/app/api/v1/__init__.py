from fastapi import APIRouter

from app.api.v1 import agents, auth, models, pipelines, prompt_optimizer, runs, stats, tools

router = APIRouter(prefix="/v1")
router.include_router(auth.router)
router.include_router(agents.router)
router.include_router(runs.router)
router.include_router(tools.router)
router.include_router(pipelines.router)
router.include_router(prompt_optimizer.router)
router.include_router(models.router)
router.include_router(stats.router)
