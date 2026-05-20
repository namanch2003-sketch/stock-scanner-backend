import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = "stock-scanner"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    allowed_origins: list[str] = field(default_factory=lambda: ["http://localhost:3000"])
    scan_interval_seconds: int = 5
    timeframes: tuple[str, ...] = ("5m", "15m", "1h")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./stock_scanner.db")


settings = Settings()
