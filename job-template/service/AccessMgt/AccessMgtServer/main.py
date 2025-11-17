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
        # 构建数据库连接字符串
        system_connect = f'mysql+pymysql://{config["mysql_user"]}:{urlquote(config["mysql_pwd"])}@{config["mysql_ip"]}:{config["mysql_port"]}/{config["mysql_db"]}'
        # 创建数据库引擎
        mysql_engine = create_engine(system_connect)
        # 将数据库引擎存入全局变量
        global_var.set_value("mysql_engine", mysql_engine)
        # 获取当前的绝对路径，存储到全局变量中
        current_dir = config["current_dir"]
        global_var.set_value("current_dir", current_dir)  # 存储路径到全局变量中，键名为'current_path'，值为路径字符串
        # 启动FastAPI服务器
        uvicorn.run(app, host=config["server_ip"], port=config["server_port"])


