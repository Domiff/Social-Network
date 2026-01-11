import uvicorn
from fastapi import FastAPI

from src.auth.dependencies import UserInDBDep
from src.auth.middleware import access_middleware
from src.auth.router import router as auth_router
from src.auth.schemas import UserInDB

app = FastAPI()
app.middleware("http")(access_middleware)
app.include_router(auth_router)


@app.get(
    "/users/me",
    response_model=UserInDB,
    response_model_exclude_none=True,
    response_model_exclude={"password"},
)
async def profile(user: UserInDBDep):
    return user


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
