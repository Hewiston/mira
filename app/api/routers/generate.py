import os
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_internal_api_key
from app.common.config import settings
from app.db.repo.users import get_or_create_wallet_by_telegram_id
from app.db.repo.holds import get_held_amount, create_hold, finalize_hold, release_hold
from app.db.models.generation import Generation
from app.api.services.gemini_image import generate_image_png

log = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["generate"])


class GeneratePhotoIn(BaseModel):
    telegram_id: int
    prompt: str = Field(min_length=3, max_length=2000)


class GeneratePhotoOut(BaseModel):
    generation_id: str
    image_url: str
    new_balance: int
    spent: int


@router.post("/generate/photo", response_model=GeneratePhotoOut)
async def generate_photo_route(
    payload: GeneratePhotoIn,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_internal_api_key),
):
    cost = int(settings.photo_cost_coins)

    wallet = await get_or_create_wallet_by_telegram_id(db, telegram_id=payload.telegram_id)
    held = await get_held_amount(db, user_id=wallet.user_id)
    available = int(wallet.balance) - int(held)

    if available < cost:
        raise HTTPException(status_code=402, detail="Not enough coins")

    hold = await create_hold(db, user_id=wallet.user_id, amount=cost, reason="image_generation")

    gen = Generation(
        user_id=wallet.user_id,
        provider="gemini",
        model=settings.gemini_image_model,
        status="processing",
        prompt=payload.prompt,
        cost=cost,
        hold_id=hold.id,
    )
    db.add(gen)
    await db.flush()

    try:
        png_bytes = await generate_image_png(payload.prompt)

        os.makedirs(os.path.join(settings.media_dir, "generated"), exist_ok=True)
        rel_path = f"generated/{gen.id}.png"
        abs_path = os.path.join(settings.media_dir, rel_path)

        with open(abs_path, "wb") as f:
            f.write(png_bytes)

        await finalize_hold(db, hold_id=hold.id)
        

        gen.status = "done"
        gen.result_path = f"media/{rel_path}"
        gen.finished_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(wallet)  # чтобы new_balance был актуальный

        return GeneratePhotoOut(
            generation_id=str(gen.id),
            image_url = f"{settings.public_base_url}/media/{rel_path}",
            new_balance=int(wallet.balance),
            spent=cost,
        )

    except Exception as e:
        # 1) логируем оригинальную причину (с traceback)
        log.exception("Generation failed (telegram_id=%s, gen_id=%s)", payload.telegram_id, gen.id)

        # 2) пытаемся корректно закрыть хвосты, но не даём этому скрыть первичную ошибку
        try:
            await release_hold(db, hold_id=hold.id)
            gen.status = "failed"
            gen.error = f"{type(e).__name__}: {e}"
            gen.finished_at = datetime.now(timezone.utc)
            await db.commit()
        except Exception:
            log.exception("Cleanup after generation failure also failed (gen_id=%s)", gen.id)

        raise HTTPException(status_code=500, detail="Generation failed") from e