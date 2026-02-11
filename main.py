import uvicorn
from fastapi import FastAPI

from parkly.adapters.app_factory import create_app
from parkly.adapters.config import AppSettings

settings: AppSettings = AppSettings()
app: FastAPI = create_app(settings)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )
