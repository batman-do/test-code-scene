import datetime
import json
import os

from langchain.memory.chat_message_histories import FileChatMessageHistory
from langchain_core.messages import BaseMessage


def add_history_v2(
    db: dict,
    role_id: str,
    user_id: str,
    session_id: str,
    message_id: str,
    message: str,
    chat_time: str,
    response_time: str,
) -> None:
    timestamp = float(session_id.split("_")[1])
    date = datetime.datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")
    folder_path = f"history/{role_id}/{user_id}/{date}"
    if not os.path.exists(folder_path):
        # Nếu thư mục không tồn tại, tạo mới thư mục
        os.makedirs(folder_path)

    if not os.path.exists(f"{folder_path}/{session_id}.json"):
        with open(f"{folder_path}/{session_id}.json", "w") as json_file:
            # Write the JSON data to the file
            json.dump({}, json_file, indent=4)

    history = FileChatMessageHistory(f"{folder_path}/{session_id}.json")
    additional_kwargs = db[user_id][message_id]
    additional_kwargs["chat_time"] = chat_time
    additional_kwargs["response_time"] = response_time

    history_message = BaseMessage(
        content=message, type="human", additional_kwargs=additional_kwargs
    )
    history.add_message(history_message)


def get_detail_session_id(role_id: str, user_id: str, session_id: str) -> None:
    timestamp = float(session_id.split("_")[1])
    date = datetime.datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")
    file_path = f"history/{role_id}/{user_id}/{date}/{session_id}.json"
    absolute_file_path = os.path.abspath(file_path)
    if os.path.exists(absolute_file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
        return [res["data"] for res in data]
    else:
        return []


def get_history_user_id(role_id: str, user_id: str, date: str, limit: int = 10):
    if date is None:
        directory = f"history/{role_id}/{user_id}"
        all_folders = [
            f
            for f in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, f))
        ]
        all_folders.sort(
            key=lambda f: datetime.datetime.strptime(f, "%Y-%m-%d"), reverse=True
        )
        all_folders = [
            f"history/{role_id}/{user_id}/{folder}" for folder in all_folders
        ]
    else:
        all_folders = [f"history/{role_id}/{user_id}/{date}"]

    response = []
    total_count = 0
    for folder in all_folders:
        json_files = [f for f in os.listdir(folder) if f.endswith(".json")]
        name_files = [f.split(".json")[0] for f in json_files]
        name_files = sorted(
            name_files, key=lambda x: float(x.split("_")[1]), reverse=True
        )

        if total_count <= limit:
            total_count += len(json_files)
            for name_file in name_files:
                with open(f"{folder}/{name_file}.json", "r") as file:
                    data = json.load(file)
                content = {
                    "session_id": name_file,
                    "name": data[0]["data"]["content"],
                    "date": datetime.datetime.strptime(
                        data[0]["data"]["additional_kwargs"]["chat_time"],
                        "%Y-%m-%d %H:%M:%S",
                    ).strftime("%Y-%m-%d"),
                }
                response.append(content)
    response = response[:limit]
    return response
