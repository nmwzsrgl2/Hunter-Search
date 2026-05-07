import yaml
from pydantic import BaseModel, Field
from pathlib import Path

# --- 定义数据模型 (对应 settings.yaml 的结构) ---

class UserInfo(BaseModel):
    api_key: str

class SearchConfig(BaseModel):
    fields: str = "url,ip,port,web_title,web_body,web_code"
    size: int = 100
    full: bool = False
    start_page: int = 1
    end_page: int = 2
    start_time: str = "2021-01-01"
    end_time: str = "2021-03-01"
    is_web: int = 1


class FastCheckConfig(BaseModel):
    check_alive: bool = True
    timeout: int = 5


class SystemConfig(BaseModel):
    logger: bool = True
    sheet_merge: bool = True
    concurrency: int = 10
    export_format: str = "xlsx"
    output_dir: str = "results"


class Config(BaseModel):
    userinfo: UserInfo
    search: SearchConfig
    fast_check: FastCheckConfig = Field(default_factory=FastCheckConfig)
    system: SystemConfig = Field(default_factory=SystemConfig)


# --- 加载逻辑 ---

def load_config() -> Config:
    config_path = Path(__file__).parent / "settings.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"配置文件未找到: {config_path}，请参照模板创建。")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            # 现在 Config(**data) 会正确映射 base_url 和 model 了
            return Config(**data)
    except Exception as e:
        print(f"[!] 配置文件解析失败: {e}")
        print("[!] 请检查 config/settings.yaml 的格式是否正确")
        exit(1)


# 初始化全局单例配置
settings = load_config()
