import asyncio
import sys

from src.routers.utils import scrape

sys.path.append("../")


async def crawl():
    content = await scrape(
        [
            "https://cafef.vn/lo-dat-19-ti-nay-phai-ban-13-ti-nguoi-trong-cuoc-chi-cach-cho-nha-dau-tu-bat-dong-san-khong-con-bi-mat-tien-trong-nam-2024-188240104100628814.chn"
        ],
        "5",
        "8",
        "213213_2131223",
    )
    print(content)


asyncio.run(crawl())
