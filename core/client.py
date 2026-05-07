import httpx
import base64
import json
import asyncio
from config import settings
from utils.logger import logger

class HunterClient:
    def __init__(self):
        # 鹰图官方地址
        self.base_url = "https://hunter.qianxin.com"
        self.api_key = settings.userinfo.api_key
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0"
        }
        self.client_args = {"http2": True, "verify": False, "timeout": 60}

    async def search(self, query_str: str, page: int = 1, fields: str = None):
        """ 执行鹰图搜索 """
        api_url = f"{self.base_url}/openApi/search"
        # 使用URL安全的base64编码，并转换为字符串
        search = base64.urlsafe_b64encode(query_str.encode("utf-8")).decode()
        # 确定初始字段
        current_fields = fields if fields else settings.search.fields

        params = {
            "api-key": self.api_key,
            "search": search,
            "page": page,
            "page_size": settings.search.size,
            "is_web": settings.search.is_web
        }

        async with httpx.AsyncClient(**self.client_args) as client:
            for attempt in range(3):
                try:
                    resp = await client.get(api_url, params=params, headers=self.headers)

                    if resp.status_code == 429:
                        logger.warning(f"触发速率限制 (429)，休眠 3 秒后重试 ({attempt + 1}/3)...")
                        await asyncio.sleep(3)
                        continue

                    try:
                        result = resp.json()
                    except:
                        await asyncio.sleep(1)
                        continue

                    if result.get("code") != 200:
                        errmsg = str(result.get("message", ""))
                        logger.error(f"查询出错: {errmsg}")
                        return [], current_fields

                    # 转换鹰图结果格式为兼容列表格式
                    data = result.get("data", {})
                    arr = data.get("arr", [])
                    results = []
                    for item in arr:
                        row = []
                        for f in current_fields.split(","):
                            f = f.strip()
                            row.append(item.get(f, "-"))
                        results.append(row)

                    return results, current_fields

                except Exception as e:
                    logger.error(f"查询请求异常: {e}")
                    await asyncio.sleep(1)

            return [], current_fields