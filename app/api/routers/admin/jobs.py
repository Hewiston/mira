from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin
from app.db.models.generation import Generation

router = APIRouter(prefix="/v1/admin/jobs", tags=["admin-jobs"])


class JobRow(BaseModel):
    id: str
    user_id: str
    status: str
    provider: str
    model: str
    cost: int
    created_at: str
    finished_at: str | None


class JobsOut(BaseModel):
    items: list[JobRow]


@router.get("", response_model=JobsOut)
async def list_jobs(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_admin),
):
    q = select(Generation)
    if status:
        q = q.where(Generation.status == status)
    res = await db.execute(q.order_by(Generation.created_at.desc()).limit(200))
    items = []
    for g in res.scalars().all():
        items.append(JobRow(
            id=str(g.id),
            user_id=str(g.user_id),
            status=g.status,
            provider=g.provider,
            model=g.model,
            cost=int(g.cost),
            created_at=g.created_at.isoformat(),
            finished_at=g.finished_at.isoformat() if g.finished_at else None,
        ))
    return JobsOut(items=items)


class JobDetailOut(BaseModel):
    id: str
    user_id: str
    status: str
    provider: str
    model: str
    prompt: str
    cost: int
    result_path: str | None
    error: str | None
    created_at: str
    finished_at: str | None


@router.get("/{job_id}", response_model=JobDetailOut)
async def get_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_admin),
):
    gid = UUID(job_id)
    g = (await db.execute(select(Generation).where(Generation.id == gid))).scalar_one_or_none()
    if not g:
        raise HTTPException(status_code=404, detail="Not found")
    return JobDetailOut(
        id=str(g.id),
        user_id=str(g.user_id),
        status=g.status,
        provider=g.provider,
        model=g.model,
        prompt=g.prompt,
        cost=int(g.cost),
        result_path=g.result_path,
        error=g.error,
        created_at=g.created_at.isoformat(),
        finished_at=g.finished_at.isoformat() if g.finished_at else None,
    )
