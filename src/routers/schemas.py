from typing import List, Optional

from pydantic import BaseModel, Field


class User(BaseModel):
    role_id: int = Field(description="id của nhóm của user")
    user_id: str = Field(description="id của user")
    session_id: Optional[str] = Field(
        default=None, description="id của conversation chat của user"
    )
    message_id: str = Field(description="id message của user")
    message: str = Field(description="message của user")
    is_use_role: Optional[bool] = Field(
        default=False, description="trạng thái có sử dụng dữ liệu của nhóm không?"
    )
    links: Optional[List[str]] = Field(
        default=[], description="list links được add vào để lấy dữ liệu của user"
    )
    use_upload_file: Optional[bool] = Field(
        default=False, description="trạng thái có sử dụng data được upload lên không?"
    )
    use_tools: Optional[str] = Field(
        default=None,
        description="người dùng sử dụng tool nào [data analysis,...]",
    )
    chat_time: str = Field(description="thời gian mà user submit message")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "role_id": 0,
                    "user_id": "1",
                    "session_id": "7b52009b64fd0a2a49e6d8a939753077792b0554_1704511813.987679",
                    "message_id": "2",
                    "message": "alo",
                    "is_use_role": False,
                    "links": [],
                    "use_upload_file": False,
                    "chat_time": "2024-01-06 10:34:54",
                }
            ]
        }
