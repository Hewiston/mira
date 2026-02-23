from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = "local"

    bot_token: str

    database_url: str
    redis_url: str
    internal_api_key: str = ""

    # Admin auth
    admin_username: str = "admin"
    admin_password: str = "admin"
    admin_token_secret: str = "change-me"  # HMAC secret for admin tokens

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    public_base_url: str = "http://localhost:8000"
    
    # Gemini
    gemini_api_key: str = ""
    gemini_image_model: str = "gemini-2.5-flash-image"
    photo_cost_coins: int = 10
    media_dir: str = "media"


settings = Settings()
