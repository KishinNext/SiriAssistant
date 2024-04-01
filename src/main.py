import asyncio
import logging

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from src.auth.service import api_key_auth
from src.auth.utils import get_config, get_secrets, setup_logging
from src.data.utils import check_connection
from src.routers import assistant_selector

app = FastAPI(
    title="FastAPI Siri Assistant Backend",
    description="FastAPI Siri Assistant Backend",
    version="0.1.0",
)

config = get_config()
setup_logging(config)
secrets = get_secrets()

app.include_router(assistant_selector.router)

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/token")
async def login():
    access_token_jwt = secrets['api_tokens']['token']
    if access_token_jwt is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    logging.info('authenticated')
    return {"access_token": access_token_jwt, "token_type": "bearer"}


@app.get("/health-check", status_code=200, dependencies=[Depends(api_key_auth)])
async def root():
    logging.info('authenticated')
    return {"message": "Everything is fine."}


async def initialize_app():
    logging.info('Initializing application...')

    from src.auth.spotify import get_spotify_client

    logging.info('Check the necessary config...')
    await get_spotify_client()
    await check_connection()
    logging.info('Application initialized')


if __name__ == "__main__":
    import uvicorn

    asyncio.run(initialize_app())
    uvicorn.run("main:app", reload=False, host="0.0.0.0", port=8080)
