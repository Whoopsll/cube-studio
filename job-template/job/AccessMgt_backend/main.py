#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AccessMgt 后端服务启动器
用于在cube-studio平台上运行AccessMgt后端服务
"""

import os
import sys
import yaml
from urllib.parse import quote_plus as urlquote
from sqlalchemy import create_engine
from Utiles import global_var
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from WebAPI import MetricMgtAPI
from WebAPI import BasicMgtAPI
from WebAPI import BasicDictMgtAPI
from WebAPI import BasicRowDataMgtAPI
from WebAPI import SystemMgtAPI
from WebAPI import ComputeMgtAPI
from WebAPI import AccessMgtAPI
import uvicorn

# 初始化全局变量
global_var._init()

# 创建FastAPI应用实例
app = FastAPI()

# 跨域请求配置
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由注册
app.include_router(MetricMgtAPI.router)
app.include_router(BasicMgtAPI.router)
app.include_router(BasicDictMgtAPI.router)
app.include_router(BasicRowDataMgtAPI.router)
app.include_router(SystemMgtAPI.router)
app.include_router(ComputeMgtAPI.router)
app.include_router(AccessMgtAPI.router)

def main():
    # 优先从环境变量读取配置，配置文件仅作为默认值
    config_file = os.getenv('CONFIG_FILE', 'config.yml')
    
    # 读取配置文件作为默认值
    config = {}
    if os.path.exists(config_file):
        with open(config_file, encoding='utf-8') as f:
            config = yaml.load(f, Loader=yaml.FullLoader) or {}
    
    # 环境变量优先级高于配置文件，如果环境变量存在则覆盖配置文件的值
    # 支持 MYSQL_IP 和 MYSQL_HOST 两种环境变量（MYSQL_HOST 优先级更高，与 mysql_demo 保持一致）

    config = {
        "server_port": int(os.getenv('SERVER_PORT', str(config.get('server_port', 10086)))),
        "server_ip": os.getenv('SERVER_IP', config.get('server_ip', '0.0.0.0')),
        "mysql_ip": os.getenv('MYSQL_HOST') or os.getenv('MYSQL_IP') or config.get('mysql_ip', 'mysql-service.infra'),
        "mysql_port": int(os.getenv('MYSQL_PORT', str(config.get('mysql_port', 3306)))),
        "mysql_user": os.getenv('MYSQL_USER', config.get('mysql_user', 'root')),
        "mysql_pwd": os.getenv('MYSQL_PASSWORD', config.get('mysql_pwd', 'admin')),
        "mysql_db": os.getenv('MYSQL_DB', config.get('mysql_db', 'AccessDB')),
        "current_dir": os.getenv('CURRENT_DIR', config.get('current_dir', '/app'))
    }
    
    # 构建数据库连接字符串
    system_connect = f'mysql+pymysql://{config["mysql_user"]}:{urlquote(config["mysql_pwd"])}@{config["mysql_ip"]}:{config["mysql_port"]}/{config["mysql_db"]}'
    
    # 创建数据库引擎
    mysql_engine = create_engine(system_connect)
    
    # 将数据库引擎存入全局变量
    global_var.set_value("mysql_engine", mysql_engine)
    
    # 存储当前目录
    current_dir = config["current_dir"]
    global_var.set_value("current_dir", current_dir)
    
    # 启动FastAPI服务器
    print(f"Starting AccessMgt Server on {config['server_ip']}:{config['server_port']}")
    print(f"Database: {config['mysql_ip']}:{config['mysql_port']}/{config['mysql_db']}")
    
    uvicorn.run(app, host=config["server_ip"], port=config["server_port"])

if __name__ == "__main__":
    main()


