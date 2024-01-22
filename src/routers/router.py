import asyncio
import datetime
import json
import os

import src.routers.utils as ut
from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    Path,
    Query,
    UploadFile,
)
from fastapi.responses import JSONResponse
from src.utilities import (
    RuntimeStorageChat,
    TokenBucketChat,
    generate_session_id,
    verify_session_id,
)
from token_throttler import TokenThrottler

from .history import get_detail_session_id, get_history_user_id
from .schemas import User


async def delete_key_message_id_after_delay(
    user: dict, user_id: str, message_id: str, delay: int
):
    if user[user_id][message_id]["is_done"]:
        # Đợi (sleep) trong thời gian xác định bằng giây
        await asyncio.sleep(delay)
        # Xóa thông tin sau khi thời gian chờ kết thúc
        user[user_id].pop(message_id, None)


# router
router = APIRouter(prefix="/genk")


@router.on_event("startup")
async def startup_event():
    global user, ban_hammer, manager

    # user
    user = dict()

    # ratelimiter
    ban_hammer = TokenThrottler(cost=1, storage=RuntimeStorageChat())


@router.get(
    "/get_docs",
    responses={
        200: {
            "description": "sucessful",
            "content": {
                "application/json": {
                    "example": {
                        "data": {
                            "latest": "1.0",
                            "changelogs": [
                                {
                                    "version": "1.0",
                                    "log": "",
                                },
                            ],
                        }
                    }
                }
            },
        },
        505: {
            "description": "error",
            "content": {"application/json": {"example": {"data": {}}}},
        },
    },
    tags=["docs"],
)
def get_docs():
    try:
        folders = os.listdir(os.path.join("docs"))
        folders.sort(key=lambda f: float(f), reverse=True)
        docs = []
        for folder in folders:
            with open(
                os.path.join(f"docs/{folder}/README.md"), encoding="utf-8"
            ) as file:
                markdown_content = file.read()
            data = {"version": str(folder), "log": markdown_content}
            docs.append(data)

        return JSONResponse(
            status_code=200,
            content={"data": {"latest": str(folders[0]), "changelogs": docs}},
        )
    except Exception as err:
        print(f"get docs error: {str(err)}")
        return JSONResponse(
            status_code=505,
            content={"data": {}},
        )


@router.get(
    "/get_state/{user_id}/{message_id}",
    responses={
        200: {
            "description": "sucessful",
            "content": {
                "application/json": {
                    "example": {
                        "data": {
                            "user_id": "141",
                            "message_id": "cb0a65c286f6098091c2ef3ea5877e6a",
                            "role_id": 11,
                            "session_id": "",
                            "session": {"name": "", "date": "2024-01-09"},
                            "is_use_role": False,
                            "is_processing": True,
                            "is_done": False,
                            "content": "",
                            "content_html": "",
                        }
                    }
                }
            },
        },
        404: {
            "description": "user_id error",
            "content": {
                "application/json": {"example": {"data": "user id 1 not in database"}}
            },
        },
        505: {
            "description": "error",
            "content": {"application/json": {"example": {"data": {}}}},
        },
    },
    tags=["get_state"],
)
def get_state(
    user_id: str = Path(title="id của user"),
    message_id: str = Path(title="id message của user"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
) -> None:
    try:
        if user_id not in user:
            return JSONResponse(
                status_code=404, content={"data": f"user id {user_id} not in database"}
            )
        else:
            background_tasks.add_task(
                delete_key_message_id_after_delay,
                user=user,
                user_id=user_id,
                message_id=message_id,
                delay=30,
            )

            return {"data": user[user_id][message_id]}

    except Exception as err:
        print(f"get_state error: {str(err)}")
        return JSONResponse(status_code=505, content={"data": {}})


@router.get(
    "/history_v2",
    responses={
        200: {
            "description": "sucessful",
            "content": {
                "application/json": {
                    "example": {
                        "data": [
                            {
                                "session_id": "",
                                "name": "nay thời tiết như nào",
                                "date": "2024-01-08",
                            },
                        ]
                    }
                }
            },
        },
        505: {
            "description": "error",
            "content": {"application/json": {"example": {"data": []}}},
        },
    },
    tags=["get_history"],
)
async def get_history_v2(
    role_id: int,
    user_id: str,
    date: str | None = Query(
        default=None, description="ngày cụ thể để lấy history, format='%Y-%m-%d'"
    ),
    limit: int = Query(default=10, description="số lượng session id muốn lấy"),
) -> None:
    try:
        data = get_history_user_id(
            role_id=str(role_id), user_id=user_id, date=date, limit=limit
        )
        return {"data": data}
    except Exception as err:
        print(f"get history error: {str(err)}")
        return JSONResponse(status_code=505, content={"data": []})


@router.get(
    "/history_session",
    responses={
        200: {
            "description": "sucessful",
            "content": {
                "application/json": {
                    "example": {
                        "data": [
                            {
                                "content": "alo bạn ơi",
                                "additional_kwargs": {
                                    "user_id": "8",
                                    "message_id": "5becdd1ac93e00c14a484261c47b112f",
                                    "role_id": 5,
                                    "session_id": "",
                                    "session": {
                                        "name": "alo bạn ơi",
                                        "date": "2024-01-06",
                                    },
                                    "is_use_role": False,
                                    "is_processing": False,
                                    "is_done": True,
                                    "content": "",
                                    "content_html": "",
                                    "chat_time": "2024-01-06 10:34:37",
                                    "response_time": "2024-01-06 10:34:41",
                                },
                                "type": "human",
                                "example": False,
                            },
                        ]
                    }
                }
            },
        },
        505: {
            "description": "error",
            "content": {"application/json": {"example": {"data": []}}},
        },
    },
    tags=["get_detail_history"],
)
async def get_detail_history_session(
    role_id: int,
    user_id: str,
    session_id: str,
) -> None:
    try:
        data = get_detail_session_id(
            role_id=str(role_id), user_id=user_id, session_id=session_id
        )
        return {"data": data}
    except Exception as err:
        print(f"get detail history error: {str(err)}")
        return JSONResponse(status_code=505, content={"data": []})


@router.post(
    "/upload_file",
    responses={
        200: {
            "description": "chat sucessful",
            "content": {"application/json": {"example": {"data": "sucessful"}}},
        },
        505: {
            "description": "error",
            "content": {
                "application/json": {"example": {"data": "chat message error"}}
            },
        },
    },
    tags=["upload file"],
)
async def upload_file(
    role_id: str,
    user_id: str,
    session_id: str,
    message_id: str,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
) -> None:
    try:
        user[user_id] = {}
        user[user_id][message_id] = {
            "is_upload_done": False,
            "file_path": "",
            "file_extension": "",
        }
        background_tasks.add_task(
            ut.save_file,
            db=user,
            role_id=str(role_id),
            user_id=user_id,
            session_id=session_id,
            message_id=message_id,
            file=file,
        )
        return {"data": "successful"}
    except Exception as err:
        return JSONResponse(
            status_code=505, content={"data": f"upload file: {str(err)}"}
        )


@router.post(
    "/chat_v2",
    responses={
        200: {
            "description": "chat sucessful",
            "content": {"application/json": {"example": {"data": "sucessful"}}},
        },
        505: {
            "description": "error",
            "content": {
                "application/json": {"example": {"data": "chat message error"}}
            },
        },
        429: {
            "description": "rate-limit",
            "content": {
                "application/json": {
                    "example": {
                        "data": {
                            "name": "rate-limit",
                            "time_remain": "2024-01-10 11:00:00",
                        }
                    }
                }
            },
        },
    },
    tags=["chat"],
)
async def chat_v2(
    item: User,
    background_tasks: BackgroundTasks = BackgroundTasks(),
) -> None:
    try:
        if (
            ban_hammer.get_bucket(identifier=item.user_id, bucket_key=str(10800))
            is None
        ):
            ban_hammer.add_bucket(
                str(item.user_id),
                TokenBucketChat(replenish_time=10800, max_tokens=25),
            )

        if ban_hammer.consume(identifier=str(item.user_id)):
            if item.user_id not in user:
                user[item.user_id] = {}
                user[item.user_id][item.message_id] = {}
            else:
                if item.message_id not in user[item.user_id]:
                    user[item.user_id][item.message_id] = {}

            session_id = ""
            session = {}
            if item.session_id is None:
                session_id = generate_session_id(
                    role_id=str(item.role_id), user_id=item.user_id
                )
                session = {
                    "name": item.message,
                    "date": datetime.datetime.strptime(
                        item.chat_time, "%Y-%m-%d %H:%M:%S"
                    ).strftime("%Y-%m-%d"),
                }
            else:
                session_id = item.session_id
                timestamp = float(session_id.split("_")[1])
                date = datetime.datetime.utcfromtimestamp(timestamp).strftime(
                    "%Y-%m-%d"
                )
                file_path = (
                    f"history/{item.role_id}/{item.user_id}/{date}/{session_id}.json"
                )
                absolute_file_path = os.path.abspath(file_path)
                if os.path.exists(absolute_file_path):
                    with open(file_path, "r") as file:
                        data = json.load(file)
                    session = {
                        "name": data[0]["data"]["content"],
                        "date": datetime.datetime.strptime(
                            data[0]["data"]["additional_kwargs"]["chat_time"],
                            "%Y-%m-%d %H:%M:%S",
                        ).strftime("%Y-%m-%d"),
                    }

            if verify_session_id(
                session_id, role_id=str(item.role_id), user_id=item.user_id
            ):
                user[item.user_id][item.message_id].update(
                    {
                        "user_id": item.user_id,
                        "message_id": item.message_id,
                        "role_id": item.role_id,
                        "session_id": session_id,
                        "session": session,
                        "is_use_role": item.is_use_role,
                        "use_tools": item.use_tools,
                        "is_processing": False,
                        "is_done": False,
                        "content": "",
                        "content_html": "",
                    }
                )
                background_tasks.add_task(
                    ut.generate_v2,
                    db=user,
                    role_id=str(item.role_id),
                    user_id=item.user_id,
                    session_id=session_id,
                    message_id=item.message_id,
                    message=item.message,
                    links=item.links,
                    use_upload_file=item.use_upload_file,
                    use_tools=item.use_tools,
                    max_tokens=4096,
                    model_name="gpt-4-1106-preview",
                    temperature=0.8,
                    chat_time=item.chat_time,
                )
                return {"data": "sucessful"}
            else:
                return {"data": f"{session_id} is not valid"}
        else:
            remain_time = ban_hammer.get_bucket(
                identifier=item.user_id, bucket_key=str(10800)
            ).remain_time
            last_replenished = ban_hammer.get_bucket(
                identifier=item.user_id, bucket_key=str(10800)
            ).last_replenished

            time_to_wait = datetime.datetime.fromtimestamp(
                remain_time + last_replenished
            ).strftime("%Y-%m-%d %H:%M:%S")
            return JSONResponse(
                status_code=429,
                content={"data": {"name": "rate-limit", "time_remain": time_to_wait}},
            )
    except Exception as err:
        return JSONResponse(
            status_code=505, content={"data": f"chat error: {str(err)}"}
        )
