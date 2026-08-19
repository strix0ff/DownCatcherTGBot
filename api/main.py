import asyncio
import uvicorn

from fastapi import (
    FastAPI,
    BackgroundTasks
)

from api.routers.services import ( 
    router
)

from api.core.checker import (
    checker
)

from contextlib import (
    asynccontextmanager
)

from api.config import (
    PORT
)

from api.core.database import (
    init_database
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_database()
    asyncio.create_task(checker())
    yield

app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=PORT)