import asyncio
import datetime
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import AsyncIterable, Awaitable

from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.schema import HumanMessage
from src.prompts import (
    code_1,
    code_2,
    code_3,
    system_prompt,
    system_prompt_da,
    user_prompt_with_context,
    user_prompt_with_context_da,
    user_prompt_with_no_context,
)
from src.tools import DACodeInterpreter, ImageLinker
from src.utilities import (
    clean_answer_da,
    clean_pdf_text,
    convert_content_to_html,
    crawl,
    download_files,
    get_content_html,
    get_links,
)

from .history import add_history_v2

UPLOAD_DIR = "data"
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
HISTORY_DIR = "history"
Path(HISTORY_DIR).mkdir(parents=True, exist_ok=True)
code_interpreter = DACodeInterpreter()


def save_file(
    db: dict, role_id: str, user_id: str, session_id: str, message_id: str, file
) -> None:
    db[user_id][message_id]["is_upload_done"] = False

    # Add the random string to the filename
    base, ext = os.path.splitext(file.filename)
    randomized_filename = f"{base}{ext}"
    folder = f"{UPLOAD_DIR}/{role_id}/{user_id}/{session_id}/"
    file_path = os.path.join(folder, randomized_filename)
    if os.access(os.path.dirname(file_path), os.W_OK):
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    _, file_extension = os.path.splitext(file_path)
    db[user_id][message_id]["file_path"] = file_path
    db[user_id][message_id]["file_extension"] = file_extension
    db[user_id][message_id]["is_upload_done"] = True


async def scrape(urls: list[str], role_id: str, user_id: str, session_id: str):
    try:
        contents = [await crawl(url) for url in urls]
        contents = [value for value in contents if value != ""]
        urls_content_none = [
            urls[index] for index, value in enumerate(contents) if value == ""
        ]
        if len(urls_content_none) != 0:
            html_content_path_files = download_files(
                sources=urls_content_none,
                role_id=role_id,
                user_id=user_id,
                session_id=session_id,
            )
            contents_html = []
            for file_path in html_content_path_files:
                with open(file_path, "r") as file:
                    html_content = file.read()
                contents_html.append(get_content_html(html_content))

            contents += contents_html
        contents = " ".join(
            [f"[{i+1}] " + content + "\n\n" for i, content in enumerate(contents)]
        )
    except Exception as err:
        print(f"error crawl data {urls}: {str(err)}")
        contents = ""
    return contents


async def chat_v2(
    llm,
    db: dict,
    user_id: str,
    message_id: str,
    message: str,
    role_id: str,
    session_id: str,
    **kwargs,
) -> None:
    db[user_id][message_id]["is_done"] = False
    db[user_id][message_id]["is_processing"] = True
    content = ""
    history = ""
    system = system_prompt
    user_prompt = ""
    timestamp = float(session_id.split("_")[1])
    date = datetime.datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")

    # find all links
    all_links = get_links(message)
    all_links_pdf = [link for link in all_links if os.path.splitext(link)[1] == ".pdf"]
    all_links_others = [
        link for link in all_links if os.path.splitext(link)[1] != ".pdf"
    ]

    content = await scrape(
        all_links_others, role_id=role_id, user_id=user_id, session_id=session_id
    )
    if all_links_pdf != []:
        download_files(
            sources=all_links_pdf,
            user_id=user_id,
            role_id=role_id,
            session_id=session_id,
        )
        loader = DirectoryLoader(
            "data/",
            glob=f"{role_id}/{user_id}/{session_id}/*.pdf",
            loader_cls=PyPDFLoader,
            use_multithreading=True,
            show_progress=True,
        )
        content_pdf = loader.load_and_split()
        content += "\n" + " ".join(
            [
                f"[{i+1+len(all_links_others)}] " + content_pdf[i].page_content + "\n\n"
                for i in range(len(content_pdf))
            ]
        )
        content = clean_pdf_text(content)

    if kwargs.get("use_upload_file"):
        if db[user_id][message_id]["file_extension"] == ".pdf":
            loader = PyPDFLoader(db[user_id][message_id]["file_path"])
            content_upload = loader.load_and_split()
            content += "\n" + " ".join(
                [
                    f"[{i+1}] " + content_upload[i].page_content + "\n\n"
                    for i in range(len(content_upload))
                ]
            )
            content = clean_pdf_text(content)

    # 5 conversation previous
    if not os.path.exists(f"history/{role_id}/{user_id}/{date}/{session_id}.json"):
        history = ""
    else:
        with open(
            f"history/{role_id}/{user_id}/{date}/{session_id}.json", "r"
        ) as json_file:
            # Load the JSON data from the file
            history = json.load(json_file)[-5:]
            if history == []:
                history = ""
            else:
                history = " ".join(
                    [
                        f"### Human: {his['data']['content']}\n### Assistant: {his['data']['additional_kwargs']['content']}\n\n"
                        for his in history
                    ]
                )
    if content != "":
        if kwargs.get("use_tools") == "data analysis":
            user_prompt = user_prompt_with_context_da.format(
                context=content,
                question=message,
                code_1=code_1,
                code_2=code_2,
                code_3=code_3,
                history=history,
            )
            system = system_prompt_da
        else:
            user_prompt = user_prompt_with_context.format(
                context=content,
                question=message,
                history=history,
                current_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
        print(user_prompt)
    else:
        if kwargs.get("use_tools") == "data analysis":
            user_prompt = user_prompt_with_context_da.format(
                context="",
                question=message,
                code_1=code_1,
                code_2=code_2,
                code_3=code_3,
                history=history,
            )
            system = system_prompt_da
        else:
            user_prompt = user_prompt_with_no_context.format(
                question=message,
                history=history,
                current_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
        print(user_prompt)
    response = await llm.agenerate(
        messages=[
            [
                system,
                HumanMessage(content=user_prompt),
            ]
        ]
    )

    return response


async def generate_v2(db: dict, user_id, message_id, **kwargs) -> AsyncIterable[str]:
    """Function get token from streaming type async"""
    callback = AsyncIteratorCallbackHandler()

    # create agent llm
    llm = ChatOpenAI(
        model_name=kwargs.get("model_name"),
        temperature=kwargs.get("temperature"),
        streaming=True,
        callbacks=[callback],
        max_tokens=kwargs.get("max_tokens"),
    )

    content = ""
    db[user_id][message_id]["content"] = ""
    db[user_id][message_id]["content_html"] = ""

    async def wrap_done(fn: Awaitable, event: asyncio.Event):
        """Wrap an awaitable with a event to signal when it's done or an exception is raised."""
        try:
            await fn
        except Exception as e:
            # TODO: handle exception
            print(f"Caught exception: {e}")
        finally:
            # Signal the aiter to stop.
            event.set()

    task = asyncio.create_task(
        wrap_done(
            chat_v2(
                llm=llm,
                db=db,
                user_id=user_id,
                role_id=kwargs.get("role_id"),
                session_id=kwargs.get("session_id"),
                message_id=message_id,
                message=kwargs.get("message"),
                links=kwargs.get("links"),
                use_upload_file=kwargs.get("use_upload_file"),
                use_tools=kwargs.get("use_tools"),
            ),
            callback.done,
        ),
    )
    code_base = ""
    async for token in callback.aiter():
        # Use server-sent-events to stream the response
        content += token
        db[user_id][message_id]["content"] = content
        if kwargs.get("use_tools") == "data analysis":
            db[user_id][message_id]["content"] = clean_answer_da(content)
            code, is_code = code_interpreter.extract_code(content)
            # Thay thế plt.show() bằng plt.savefig()
            if is_code:
                if code != code_base:
                    code_base = code
                    code_save = code
                    if re.search("import seaborn as sns", code) is None:
                        code_save = "import seaborn as sns" + "\n" + code_save

                    if re.search("import numpy as np", code) is None:
                        code_save = "import numpy as np" + "\n" + code_save

                    date = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                    file_name = f"code/{user_id}/{message_id}_{date}.py"
                    code_save = re.sub(
                        r"plt\.show\(\)",
                        f'plt.savefig("code/{user_id}/{message_id}_{date}.png")',
                        code_save,
                    )
                    code_interpreter.save_code(filename=file_name, code=code_save)
                    _, stderr_output = code_interpreter.execute_code(
                        code=file_name, language="python"
                    )
                    if stderr_output == "":
                        file_image = file_name.replace(".py", ".png")
                        public_link = ImageLinker().create_link(
                            os.path.abspath(file_image)
                        )
                        pattern = r"```python.*?" + re.escape(code) + r".*?```"
                        content = re.sub(
                            pattern,
                            f"![Image]({public_link})",
                            content,
                            flags=re.DOTALL,
                        )
                        db[user_id][message_id]["content"] = content
                        # delete all images and file
                        subprocess.run(
                            ["rm", "-rf", os.path.abspath(f"code/{user_id}/"), "*"]
                        )

        db[user_id][message_id]["content_html"] = convert_content_to_html(
            db[user_id][message_id]["content"]
        )

    response_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    add_history_v2(
        db,
        role_id=kwargs.get("role_id"),
        user_id=user_id,
        message_id=message_id,
        session_id=kwargs.get("session_id"),
        message=kwargs.get("message"),
        chat_time=kwargs.get(
            "chat_time",
        ),
        response_time=response_time,
    )
    db[user_id][message_id]["is_processing"] = False
    db[user_id][message_id]["is_done"] = True
    await task
