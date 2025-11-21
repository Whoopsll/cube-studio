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
    # 从环境变量或配置文件读取配置
    config_file = os.getenv('CONFIG_FILE', 'config.yml')
    
    # 读取配置文件
    if os.path.exists(config_file):
        with open(config_file, encoding='utf-8') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
    else:
        # 使用环境变量配置
        config = {
            "server_port": int(os.getenv('SERVER_PORT', '10086')),
            "server_ip": os.getenv('SERVER_IP', '0.0.0.0'),
            "mysql_ip": os.getenv('MYSQL_IP', 'mysql-service'),
            "mysql_port": int(os.getenv('MYSQL_PORT', '3306')),
            "mysql_user": os.getenv('MYSQL_USER', 'root'),
            "mysql_pwd": os.getenv('MYSQL_PASSWORD', 'rootpassword'),
            "mysql_db": os.getenv('MYSQL_DB', 'AccessDB'),
            "current_dir": os.getenv('CURRENT_DIR', '/app')
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


