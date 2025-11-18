# 程序主入口
# 导入所需模块
from Utiles import global_var  # 全局变量工具

global_var._init()
import yaml  # YAML配置文件解析

from fastapi import FastAPI  # FastAPI框架
from fastapi.middleware.cors import CORSMiddleware  # 跨域中间件
from WebAPI import MetricMgtAPI
from WebAPI import BasicMgtAPI
from WebAPI import BasicDictMgtAPI
from WebAPI import BasicRowDataMgtAPI
from WebAPI import SystemMgtAPI
from WebAPI import ComputeMgtAPI
from WebAPI import AccessMgtAPI
from urllib.parse import quote_plus as urlquote  # URL编码
from sqlalchemy import create_engine  # 数据库引擎
from threading import Thread
import uvicorn  # ASGI服务器
import os

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

if __name__ == "__main__":
    # 主程序入口
    # 初始化全局变量对象

    # 读取配置文件
    with open("config.yml", encoding='utf-8') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

        # 优先从环境变量读取 MySQL 配置，未设置时回退到 config.yml
        mysql_ip = os.getenv("MYSQL_HOST", config.get("mysql_ip", "127.0.0.1"))
        mysql_port = int(os.getenv("MYSQL_PORT", config.get("mysql_port", 3306)))
        mysql_user = os.getenv("MYSQL_USER", config.get("mysql_user", "root"))
        mysql_pwd = os.getenv("MYSQL_PASSWORD", config.get("mysql_pwd", "admin"))
        mysql_db = os.getenv("MYSQL_DB", config.get("mysql_db", "AccessDB"))

        # 构建数据库连接字符串
        system_connect = (
            f"mysql+pymysql://{mysql_user}:{urlquote(mysql_pwd)}@"
            f"{mysql_ip}:{mysql_port}/{mysql_db}"
        )

        # 创建数据库引擎
        mysql_engine = create_engine(system_connect)
        # 将数据库引擎存入全局变量
        global_var.set_value("mysql_engine", mysql_engine)

        # 获取当前的绝对路径，存储到全局变量中
        current_dir = config["current_dir"]
        global_var.set_value("current_dir", current_dir)

        # 启动 FastAPI 服务器，host/port 也支持环境变量覆盖
        server_ip = os.getenv("SERVER_HOST", config.get("server_ip", "127.0.0.1"))
        server_port = int(os.getenv("SERVER_PORT", config.get("server_port", 10086)))
        uvicorn.run(app, host=server_ip, port=server_port)


