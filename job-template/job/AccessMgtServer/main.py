# 程序主入口
# 导入所需模块
from Utiles import global_var  # 全局变量工具

global_var._init()
import yaml  # YAML配置文件解析

from fastapi import FastAPI  # FastAPI框架
from fastapi.middleware.cors import CORSMiddleware  # 跨域中间件
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from WebAPI import MetricMgtAPI
from WebAPI import BasicMgtAPI
from WebAPI import BasicDictMgtAPI
from WebAPI import BasicRowDataMgtAPI
from WebAPI import SystemMgtAPI
from WebAPI import ComputeMgtAPI
from WebAPI import AccessMgtAPI
from urllib.parse import quote_plus as urlquote  # URL编码
from sqlalchemy import create_engine, inspect  # 数据库引擎
from sqlalchemy import text as sa_text
import uvicorn  # ASGI服务器
import re
import os
from pathlib import Path

# 创建FastAPI应用实例
app = FastAPI()

# --------------------------------------------跨域请求配置-----------------------------------------------
# 允许所有来源的跨域请求
origins = ["*"]
# 添加跨域中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许所有来源
    allow_credentials=True,  # 允许携带凭证
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有HTTP头
)

# --------------------------------------------路由注册--------------------------------------
# 将所有API路由注册到FastAPI应用中
app.include_router(MetricMgtAPI.router)
app.include_router(BasicMgtAPI.router)
app.include_router(BasicDictMgtAPI.router)
app.include_router(BasicRowDataMgtAPI.router)
app.include_router(SystemMgtAPI.router)
app.include_router(ComputeMgtAPI.router)
app.include_router(AccessMgtAPI.router)

# --------------------------------------------静态资源服务--------------------------------------
frontend_dir = Path(__file__).parent / "frontend_dist"
if frontend_dir.exists():
    assets_dir = frontend_dir / "assets"
    if assets_dir.exists():
        # 挂载静态资源目录（如 JS/CSS 等）
        app.mount(
            "/assets",
            StaticFiles(directory=assets_dir),
            name="frontend-assets",
        )

    # 根路径返回打包后的 index.html
    @app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(frontend_dir / "index.html")

    # 兼容前端 history 路由，同时允许直接访问其他静态文件
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):
        target = frontend_dir / full_path
        if target.is_file():
            return FileResponse(target)
        return FileResponse(frontend_dir / "index.html")

def _split_sql_statements(sql_text: str):
    """根据分号拆分SQL语句，忽略换行/空白。"""
    normalized = sql_text.replace("\r\n", "\n")
    parts = re.split(r";\s*(?:\n|$)", normalized)
    return [part.strip() for part in parts if part.strip()]


def _seed_database(engine, sql_file: Path):
    if not sql_file.exists():
        raise FileNotFoundError(f"SQL脚本不存在: {sql_file}")

    sql_text = sql_file.read_text(encoding="utf-8")
    statements = _split_sql_statements(sql_text)
    if not statements:
        return

    with engine.begin() as conn:
        for statement in statements:
            conn.exec_driver_sql(statement)


def _ensure_database(config):
    db_name = config["mysql_db"]
    base_connect = f'mysql+pymysql://{config["mysql_user"]}:{urlquote(config["mysql_pwd"])}@{config["mysql_ip"]}:{config["mysql_port"]}/mysql'
    system_connect = f'mysql+pymysql://{config["mysql_user"]}:{urlquote(config["mysql_pwd"])}@{config["mysql_ip"]}:{config["mysql_port"]}/{db_name}'

    base_engine = create_engine(base_connect)
    with base_engine.connect() as conn:
        conn.execute(sa_text(f"CREATE DATABASE IF NOT EXISTS `{db_name}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci"))
    base_engine.dispose()

    mysql_engine = create_engine(system_connect)
    inspector = inspect(mysql_engine)
    tables = inspector.get_table_names()
    if not tables:
        sql_config_value = config.get("accessdb_sql")
        if sql_config_value:
            sql_file = Path(sql_config_value)
        else:
            sql_file = Path(__file__).with_name("accessdb.sql")
        _seed_database(mysql_engine, sql_file)
    return mysql_engine


if __name__ == "__main__":
    # 主程序入口
    # 初始化全局变量对象

    # 优先从环境变量读取配置（与 mysql_demo 一致），如果没有则从 config.yml 读取
    # 读取配置文件（作为默认值）
    config = {}
    config_file = Path(__file__).parent / "config.yml"
    if config_file.exists():
        with open(config_file, encoding='utf-8') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
    
    # MySQL 配置（优先使用环境变量，与 mysql_demo 保持一致）
    mysql_config = {
        "mysql_ip": os.getenv('MYSQL_HOST', config.get("mysql_ip", "mysql-service.infra")),
        "mysql_port": os.getenv('MYSQL_PORT', str(config.get("mysql_port", 3306))),
        "mysql_user": os.getenv('MYSQL_USER', config.get("mysql_user", "root")),
        "mysql_pwd": os.getenv('MYSQL_PASSWORD', config.get("mysql_pwd", "admin")),
        "mysql_db": os.getenv('MYSQL_DATABASE', config.get("mysql_db", "AccessDB")),
    }
    
    # 服务器配置（支持环境变量）
    server_ip = os.getenv('SERVER_IP', config.get("server_ip", "0.0.0.0"))
    server_port = int(os.getenv('SERVER_PORT', config.get("server_port", 10086)))
    
    # 当前目录配置（容器中默认为 /app）
    current_dir = os.getenv('CURRENT_DIR', config.get("current_dir", "/app"))
    
    # 确保数据库与初始数据存在
    mysql_engine = _ensure_database(mysql_config)
    # 将数据库引擎存入全局变量
    global_var.set_value("mysql_engine", mysql_engine)
    # 获取当前的绝对路径，存储到全局变量中
    global_var.set_value("current_dir", current_dir)  # 存储路径到全局变量中，键名为'current_path'，值为路径字符串
    # 启动FastAPI服务器
    uvicorn.run(app, host=server_ip, port=server_port)


