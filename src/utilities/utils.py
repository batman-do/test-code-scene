import hashlib
import os
import random
import re
import secrets
import unicodedata
from datetime import datetime, timedelta
from functools import lru_cache, wraps
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List

import httpx
import mdtex2html
import nltk

# import requests
from bs4 import BeautifulSoup
from src.fetchers import LinkContentFetcher
from tenacity import retry, retry_if_result, stop_after_attempt, wait_random

PROXY_POOL = ["http://10.5.3.24:6210"]
USER_AGENT_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/604.3.5 (KHTML, like Gecko) Version/11.0.1 Safari/604.3.5",
]


def timed_lru_cache(seconds: int, maxsize: int = 128):
    """
    The `timed_lru_cache` function is a decorator that adds a time-based expiration to the LRU cache functionality.
    """

    def wrapper_cache(func):
        func = lru_cache(maxsize=maxsize)(func)
        func.lifetime = timedelta(seconds=seconds)
        func.expiration = datetime.now() + func.lifetime

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if datetime.now() >= func.expiration:
                func.cache_clear()
                func.expiration = datetime.now() + func.lifetime

            return func(*args, **kwargs)

        return wrapped_func

    return wrapper_cache


def download_files(
    sources: List[str], role_id: str, user_id: str, session_id: str
) -> List[str]:
    """
    Downloads a list of files from the web and returns a list of their paths where they are stored locally.
    :param sources: A list of URLs to download.
    :type sources: List[str]
    :return: A list of paths to the downloaded files.
    """
    folder_path = f"data/{role_id}/{user_id}/{session_id}/"
    if not os.path.exists(folder_path):
        # Nếu thư mục không tồn tại, tạo mới thư mục
        os.makedirs(folder_path)

    fetcher = LinkContentFetcher()
    streams = fetcher.run(urls=sources)

    all_files = []
    for stream in streams["streams"]:
        file_suffix = (
            ".html" if stream.meta.get("content_type") == "text/html" else ".pdf"
        )
        f = NamedTemporaryFile(delete=False, dir=folder_path, suffix=file_suffix)
        stream.to_file(Path(f.name))
        all_files.append(f.name)

    return all_files


def _parse_text(text: str):
    lines = text.split("\n")
    lines = [line for line in lines if line != ""]
    count = 0
    for i, line in enumerate(lines):
        if "```" in line:
            count += 1
            items = line.split("`")
            if count % 2 == 1:
                lines[i] = f'<pre><code class="language-{items[-1]}">'
            else:
                lines[i] = "<br></code></pre>"
        else:
            if i > 0:
                if count % 2 == 1:
                    line = line.replace("`", r"\`")
                    line = line.replace("<", "&lt;")
                    line = line.replace(">", "&gt;")
                    line = line.replace(" ", "&nbsp;")
                    line = line.replace("*", "&ast;")
                    line = line.replace("_", "&lowbar;")
                    line = line.replace("-", "&#45;")
                    line = line.replace(".", "&#46;")
                    line = line.replace("!", "&#33;")
                    line = line.replace("(", "&#40;")
                    line = line.replace(")", "&#41;")
                    line = line.replace("$", "&#36;")
                lines[i] = "<br>" + line
    text = "".join(lines)
    return text


def convert_content_to_html(content: str):
    """Convert text from chatgpt to html content"""
    html_content = mdtex2html.convert(_parse_text(content))
    return html_content


def clean_pdf_text(text: str):
    # Split the data into lines and remove redundant spaces
    lines: list = [line.strip() for line in text.split("\n") if line.strip() != ""]

    enhanced_text = []

    for idx, line in enumerate(lines):
        # Financial year data followed by metrics, e.g. "5% on FY22$10,164m"
        if re.match(r"^\d+% on FY\d+\$\d+m", line):
            split_line = re.split(r"(\$)", line, 1)
            enhanced_text.append(split_line[0] + split_line[1] + split_line[2])
            enhanced_text.append("\n")  # Add an extra line for clarity

        # Financial metrics followed by details
        elif re.match(r"\$\d+\.?\d*m", line) or re.match(r"\d+\.?\d*%", line):
            enhanced_text.append(line)
            if idx + 1 < len(lines):
                enhanced_text.append(lines[idx + 1])
            enhanced_text.append("\n")  # Add an extra line for clarity

        # Titles and sub-titles
        elif line in [
            "Balance Sheet",
            "Statement of Comprehensive Income",
            "RACV Annual Report",
            "Investments Accounted for Using the Equity Method",
            "Balance Sheet",
            "COMMONWEAL TH BANK",
        ]:
            enhanced_text.append("\n\n" + line + "\n" + "-" * len(line) + "\n")

        # Bullet points (e.g., • Arevo Pty Ltd)
        elif re.match(r"•\s", line):
            enhanced_text.append("  - " + line.split("•")[1])

        # Special notes
        elif line.startswith("1  Refer to note"):
            enhanced_text.append("\nNote: " + line + "\n")

        # Categories followed by descriptions (e.g., "Strategic", "Financial")
        elif line in [
            "Strategic",
            "Financial",
            "Non ‑financial",
            "EmergingRisk",
            "Financial risk",
        ]:
            enhanced_text.append(line + ":")
            if idx + 1 < len(lines):
                enhanced_text.append("  " + lines[idx + 1])
            enhanced_text.append("\n")

        # Page numbers
        elif re.match(r"^\d{1,3} \d{1,3}$", line):
            continue

        else:
            enhanced_text.append(line)

    # Concatenate all the enhanced text into a single string
    cleaned_file = "\n".join(enhanced_text)

    return cleaned_file


def get_links(message: str) -> list[str]:
    # Sử dụng re.findall để lấy tất cả các liên kết từ văn bản
    message = message.replace("\\n", "\n")
    links = re.findall(r"https?://[^\s\n]+", message)
    return links


def process(text: str) -> str:
    """The function help to process raw text is crawled"""
    punch = """#@*^~"""
    text = re.sub(r"http\S+", "", text)
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\n", " . ")
    text = text.replace("&#038", " ")
    text = text.replace("\xa0", " ")
    text = re.sub("[?|!]", ".", text)
    text = re.compile(f"[{re.escape(punch)}]").sub(" ", text)
    text = re.sub(" +", " ", text)
    text = [nltk.word_tokenize(t) for t in nltk.sent_tokenize(text)]
    for list_word in text:
        if list_word[len(list_word) - 1] != ".":
            list_word.insert(len(list_word), ".")
        for i, word in enumerate(list_word):
            if (word == ".") and (i != (len(list_word) - 1)):
                list_word.pop(i)
    text = " ".join(" ".join(doc) for doc in text if doc != ["."])
    text = re.sub("[.]{2,}", " ", text)
    text = re.sub(" +", " ", text)
    return text


# Define the conditions for retrying based on HTTP status codes
def is_retryable_status_code(response):
    return response.status_code in [403, 404]


# callback to modify scrape after each retry
def update_scrape_call(retry_state):
    # change to random proxy on each retry
    new_proxy = random.choice(PROXY_POOL)
    new_user_agent = random.choice(USER_AGENT_POOL)
    print(
        "retry {attempt_number}: {url} @ {proxy} with a new proxy {new_proxy}".format(
            attempt_number=retry_state.attempt_number,
            new_proxy=new_proxy,
            **retry_state.kwargs,
        )
    )
    retry_state.kwargs["proxy"] = new_proxy
    retry_state.kwargs["client_kwargs"]["headers"]["User-Agent"] = new_user_agent


@retry(
    # retry on bad status code
    retry=retry_if_result(is_retryable_status_code),
    # max 5 retries
    stop=stop_after_attempt(5),
    # wait randomly 1-5 seconds between retries
    wait=wait_random(min=1, max=5),
    # update scrape call on each retry
    before_sleep=update_scrape_call,
)
async def scrape(url):
    async with httpx.AsyncClient(
        proxies={"http://": random.choice(PROXY_POOL)},
        headers={"User-Agent": random.choice(USER_AGENT_POOL)},
    ) as client:
        response = await client.get(url)
        return response


def get_content_html(html_content: str):
    soup = BeautifulSoup(html_content, "html.parser")
    try:
        first_h1 = soup.find("h1")
        first_h2 = soup.find("h2")
        # get content
        if (first_h1 is not None) and (first_h2 is not None):
            text = max(
                [
                    (
                        process(first_h1.get_text())
                        + " "
                        + process(first_h2.parent.get_text())
                    ),
                    (process(first_h1.parent.get_text())),
                ],
                key=len,
            )
        else:
            text = process(soup.get_text())

    except Exception as err:
        print(f"scrape error: {str(err)}")
        # get content
        text = process(soup.get_text())
    return text


async def crawl(url: str):
    try:
        results = await scrape(url)
        text = get_content_html(results.content)
        return text

    except Exception as err:
        print(f"error link {url}: {str(err)}")
        return ""


def count_json_elements_recursive(obj):
    if isinstance(obj, list):
        # Nếu đối tượng là một list, đếm số lượng phần tử trong list
        return sum(count_json_elements_recursive(item) for item in obj)
    else:
        # Trường hợp khác, đối tượng là một giá trị đơn
        return 1


def generate_session_id(role_id: str, user_id: str) -> str:
    # Get the current timestamp
    current_timestamp = datetime.now().timestamp()

    # data hash
    data_hash = f"{role_id}{user_id}"

    # Use a hash function (e.g., SHA-1) to create the session_id
    hashed_data = hashlib.sha1(data_hash.encode()).hexdigest()
    hashed_data = f"{hashed_data}_{current_timestamp}"

    return hashed_data


def verify_session_id(session_id: str, role_id: str, user_id: str) -> bool:
    # Extract timestamp from the session_id
    parts = session_id.split("_")
    if len(parts) != 2:
        return False

    hashed_data, timestamp_str = parts

    # Recreate the hash using the provided role_id and user_id
    data_hash = f"{role_id}{user_id}"
    expected_hash = hashlib.sha1(data_hash.encode()).hexdigest()

    # Compare the recreated hash with the one in the session_id
    return secrets.compare_digest(expected_hash, hashed_data)


def clean_answer_da(text: str):
    pattern = r"(Analysis:|Code:|Phân tích:)[ \t]*\n*"
    # Thay thế các cụm phù hợp bằng chuỗi trống
    text = re.sub(pattern, "", text)
    return text
