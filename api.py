import os
import secrets

import openai
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from src.routers import router

# security docs
security = HTTPBasic()


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "chatbot")
    correct_password = secrets.compare_digest(credentials.password, "12345")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


tags_metadata = [
    {
        "name": "chat",
        "description": """\tAPI chat with rate-limit 25msg/1h\n- **HTTP_STATUS_CODE=200** -> {"data": "sucessful"}}\n- **HTTP_STATUS_CODE=429** -> {"data": "rate-limit"}\n - **HTTP_STATUS_CODE=505** -> {"data": message error}""",
    },
    {
        "name": "get_state",
        "description": "\tAPI lấy trạng thái message của user dựa vào user_id và message_id",
    },
    {
        "name": "get_history",
        "description": """\tAPI lấy history của user_id\n - **HTTP_STATUS_CODE=200** -> {"data" : list dict history}\n- **HTTP_STATUS_CODE=505** -> {"data": []}""",
    },
    {
        "name": "get_detail_history",
        "description": """\tAPI lấy nội dung chi tiết của 1 history dựa theo session_id, user_id, role_id\n - **HTTP_STATUS_CODE=200** -> {"data": list của dict từng history trong 1 session_id}\n - **HTTP_STATUS_CODE=505** -> {"data": []}""",
    },
    {
        "name": "docs",
        "description": "\tAPI lấy nội README.md của các phiên bản ChatGPT",
    },
    {
        "name": "upload file",
        "description": "\tAPI upload file của user lên chat",
    },
]

# App writing assistant
app = FastAPI(
    title="Chatbot Writing Assistant",
    root_path="/generative_ai/writing_assistant/chatbot/",
    version="2.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    openapi_tags=tags_metadata,
)
app.include_router(router.router)


@app.middleware("http")
async def cors_handler(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


@app.get("/docs", include_in_schema=False)
async def get_swagger_documentation(
    req: Request, username: str = Depends(get_current_username)
):
    root_path = req.scope.get("root_path", "").rstrip("/")
    openapi_url = root_path + "/openapi.json"
    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title="docs",
    )


@app.get("/redoc", include_in_schema=False)
async def get_redoc_documentation(
    req: Request, username: str = Depends(get_current_username)
):
    root_path = req.scope.get("root_path", "").rstrip("/")
    openapi_url = root_path + "/openapi.json"
    return get_redoc_html(
        openapi_url=openapi_url,
        title="docs",
    )


@app.get("/openapi.json", include_in_schema=False)
async def openapi(username: str = Depends(get_current_username)):
    return get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
        servers=[{"url": app.root_path}],
        tags=app.openapi_tags,
    )


if __name__ == "__main__":
    openai.api_key = os.environ["OPENAI_API_KEY"]

    uvicorn.run(app, host="10.5.0.47", port=2011)
