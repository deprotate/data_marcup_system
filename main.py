from contextlib import asynccontextmanager

from fastapi import FastAPI

from api_v1.core.DBHelper import db_helper
from api_v1.core.models.Base import MegaBase
from api_v1.users.auth import auth_router, register_router, reset_pw_router, verify_router, users_router
from api_v1.task_templates.views import router as templates_router
from api_v1.tasks.views import router as tasks_router
from api_v1.assignments.views import router as assignments_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(MegaBase.metadata.create_all)
    yield
app = FastAPI(lifespan=lifespan)


app.include_router(auth_router,     prefix="/auth/jwt", tags=["auth"])
app.include_router(register_router, prefix="/auth",     tags=["auth"])
app.include_router(reset_pw_router, prefix="/auth",     tags=["auth"])
app.include_router(verify_router,   prefix="/auth",     tags=["auth"])
app.include_router(users_router,    prefix="/users",    tags=["users"])

app.include_router(templates_router)

app.include_router(tasks_router)


app.include_router(assignments_router)




@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
