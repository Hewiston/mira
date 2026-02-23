import httpx


class ApiClient:
    def __init__(self, base_url: str, internal_api_key: str = ""):
        self.base_url = base_url.rstrip("/")
        self.internal_api_key = internal_api_key

    @property
    def _headers(self) -> dict[str, str] | None:
        if not self.internal_api_key:
            return None
        return {"X-Internal-Key": self.internal_api_key}

    async def ensure_user(self, telegram_id: int, username: str | None, first_name: str | None):
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(
                f"{self.base_url}/v1/users/ensure",
                json={"telegram_id": telegram_id, "username": username, "first_name": first_name},
                headers=self._headers,
            )
            r.raise_for_status()
            return r.json()

    async def get_wallet(self, telegram_id: int):
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(f"{self.base_url}/v1/wallet/{telegram_id}", headers=self._headers)
            r.raise_for_status()
            return r.json()
        
    async def topup_wallet(self, telegram_id: int, coins: int, reason: str | None = None, payment_id: str | None = None):
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                f"{self.base_url}/v1/wallet/topup",
                json={"telegram_id": telegram_id, "coins": coins, "reason": reason, "payment_id": payment_id},
                headers=self._headers,
            )
            r.raise_for_status()
            return r.json()
    

    async def confirm_payment(self, telegram_id: int, invoice_payload: str, telegram_payment_charge_id: str):
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(
                f"{self.base_url}/v1/payments/confirm",
                json={
                    "telegram_id": telegram_id,
                    "invoice_payload": invoice_payload,
                    "telegram_payment_charge_id": telegram_payment_charge_id,
                },
                headers=self._headers,
            )
            r.raise_for_status()
            return r.json()


    async def generate_photo(self, telegram_id: int, prompt: str):
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(
                f"{self.base_url}/v1/generate/photo",
                json={"telegram_id": telegram_id, "prompt": prompt},
                headers=self._headers,
            )
            try:
                r.raise_for_status()
            except httpx.HTTPStatusError as e:
                # пробрасываем дальше, но добавляем текст ответа (FastAPI detail)
                detail = r.text[:500]
                raise httpx.HTTPStatusError(
                    message=f"{e} | body={detail}",
                    request=e.request,
                    response=e.response,
                ) from e

            return r.json()
        