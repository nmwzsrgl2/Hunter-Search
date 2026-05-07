import sys
import os
import builtins
import logging
import datetime
from pathlib import Path

# ==============================================================================
# 🛡️ MCP 协议防污染补丁（必须最早执行）
# ==============================================================================

_original_print = builtins.print


def mcp_safe_print(*args, **kwargs):
    kwargs['file'] = sys.stderr
    _original_print(*args, **kwargs)


builtins.print = mcp_safe_print


def setup_global_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='[MCP-LOG] %(message)s',
        stream=sys.stderr,
        force=True
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


setup_global_logging()

# ==============================================================================
# 环境初始化 & 依赖注入
# ==============================================================================

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from mcp.server.fastmcp import FastMCP
    from core.client import HunterClient
    from config import settings
    from utils.logger import logger as app_logger
except ImportError as e:
    sys.stderr.write(f"❌ 依赖导入失败: {e}\n")
    sys.exit(1)


# ==============================================================================
# 🛡️ 二次保险：覆盖业务 Logger 输出到 stderr
# ==============================================================================

def mcp_safe_log(msg):
    sys.stderr.write(f"[MCP-LOG] {str(msg)}\n")
    sys.stderr.flush()


app_logger.info = mcp_safe_log
app_logger.error = mcp_safe_log
app_logger.warning = mcp_safe_log
app_logger.ai = mcp_safe_log

# ==============================================================================
# MCP 实例
# ==============================================================================

mcp = FastMCP("HunterMap-Platinum-Full-Expert",host="0.0.0.0",port=8000)


# ==============================================================================
# Markdown 表格工具
# ==============================================================================

def format_table(headers: list, rows: list, max_rows: int = 25) -> str:
    if not rows:
        return "> ⚠️ 无数据。"

    def clean(cell):
        s = str(cell).replace("|", "\\|").replace("\n", " ").strip()
        return (s[:47] + "...") if len(s) > 50 else s

    md = "| " + " | ".join(headers) + " |\n"
    md += "| " + " | ".join(["---"] * len(headers)) + " |\n"

    for i, row in enumerate(rows):
        if i >= max_rows:
            break
        current_row = list(row) + ["-"] * (len(headers) - len(row))
        md += "| " + " | ".join([clean(c) for c in current_row]) + " |\n"

    if len(rows) > max_rows:
        md += f"\n\n> *ℹ️ 共 {len(rows)} 条，仅显示前 {max_rows} 条*"

    return md


# ==============================================================================
# MCP 工具 1：HunterMap 搜索语法提示词
# ==============================================================================

@mcp.tool(
    name="hunter_syntax_guide",
    description="鹰图的语法查询指南,你应该首先阅读它"
)
def hunter_syntax_guide():
    with open(os.path.join(project_root, "docx/语法指南.md"), "r", encoding="utf-8") as f:
        content = f.read()
    return content


# ==============================================================================
# MCP 工具 1：HunterMap 搜索
# ==============================================================================
@mcp.tool()
async def search_assets(query: str, fields: str = None,
                        pages: int = 1, full: bool = False, display_rows: int = 25):
    """
    执行 Hunter 查询。
    你应该调用 hunter_syntax_guide 工具来确定查询语法的具体格式

    Args:
        query: Hunter 查询语句 (例如: `ip="8.8.8.8"`)
        fields: [可选] 逗号分隔的返回字段。默认为基础资产字段。
        pages: 查询页数 (默认 1)
        full: 是否搜索历史数据 (默认 False)
        display_rows: [可选] 决定在返回的 Markdown 表格中最多展示多少行。默认25。如果用户明确要求看更多数据，你可以将其调高(例如 100、200或者其他数值)，但不要过高以免超出对话输出限制。
        size: 每页查询数量，默认为100条，如果用户需要设置，请提醒用户手动去settings.yaml文件中去修改size大小，mcp服务不支持自动修改该参数。
    """

    client = HunterClient()
    
    # 鹰图默认字段
    allowed_defaults = ["url", "ip", "port", "web_title", "web_body", "web_code"]
    
    if not fields:
        target_fields = ",".join(allowed_defaults)
    else:
        target_fields = fields

    try:
        results, effective_fields = await client.search(query, page=pages, fields=target_fields)
    except Exception as e:
        return f"❌ Hunter 请求异常: {str(e)}"

    if not results:
        return f"🔍 未发现资产，实际查询字段: `{effective_fields}`"

    formatted_results = [r if isinstance(r, list) else [r] for r in results]
    header_list = [f.strip().capitalize() for f in target_fields.split(",")]
    clean_headers = [h[:10] for h in header_list]

    return f"### 🔍 Hunter 检索结果: `{query}`\n" + format_table(clean_headers, formatted_results, max_rows=display_rows)



# ==============================================================================
# 入口
# ==============================================================================

if __name__ == "__main__":
    mcp.run(
        transport='streamable-http',
        mount_path='/mcp'
    )
