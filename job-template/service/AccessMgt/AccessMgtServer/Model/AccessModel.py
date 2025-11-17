# 数据库映射文件，主要用于系统建模工具数据
from ast import Dict
from math import e
from re import S
from typing import Type
from sqlalchemy.engine import Engine, default
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Date, DateTime, Float, String, Table, Text, text, Integer, JSON
from datetime import datetime, date, timedelta
from sqlalchemy import inspect
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.ext.automap import automap_base

import yaml
import os
import uuid
from urllib.parse import quote_plus as urlquote
from sqlalchemy import create_engine, MetaData

Base = declarative_base()
metadata = Base.metadata


class MetricTable(Base):
    """
    指标管理
    """
    __tablename__ = "MetricTable"
    id = Column(Integer, name="id", nullable=False, primary_key=True, comment="id,唯一标识，自增")
    name = Column(String(256), name="name", nullable=False, comment="指标名称")
    formula = Column(String(512), name="formula", nullable=False, comment="公式")
    constraint = Column(String(512), name="constraint", comment="约束条件")
    description = Column(Text, name="description", comment="备注")
    creator = Column(String(256), name="creator", comment="创建人名称")
    createTime = Column(String(256), name="createTime", comment="创建时间")
    params = Column(JSON, name="params", comment="参数列表")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def update(self, data_dict):
        for key, value in data_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)


class AccessDataTable(Base):
    """
    评估数据管理
    """
    __tablename__ = "AccessDataTable"
    id = Column(Integer, name="id", nullable=False, primary_key=True, comment="id,唯一标识，自增")
    system_name = Column(String(256), name="system_name", nullable=False, comment="体系名称")
    system_description = Column(Text, name="system_description", comment="备注")
    createTime = Column(String(256), name="createTime", comment="t创建时间")
    basic_name = Column(String(256), name="basic_name", nullable=False, comment="推演数据名称")
    basic_description = Column(Text, name="basic_description", comment="备注")
    word_uid = Column(String(256), name="word_uid", nullable=False, comment="文档名称")
    system_detail = Column(JSON,name="system_detail", comment="体系详情")
    system_result = Column(JSON, name="system_result",comment="评估结果")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def update(self, data_dict):
        for key, value in data_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)

class BasicCollectTable(Base):
    """
    原始数据汇总表
    """
    __tablename__ = "BasicCollectTable"
    id = Column(Integer, name="id", nullable=False, primary_key=True, comment="id,唯一标识，自增")
    name = Column(String(256), name="name", nullable=False, comment="推演数据汇总名称")
    createTime = Column(String(256), name="createTime", nullable=False, comment="创建时间")
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def update(self, data_dict):
        for key, value in data_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)

class BasicTable(Base):
    """
    原始数据索引表
    """
    __tablename__ = "BasicTable"
    id = Column(Integer, name="id", nullable=False, primary_key=True, comment="id,唯一标识，自增")
    name = Column(String(256), name="name", nullable=False, comment="推演数据名称")
    createTime = Column(String(256), name="createTime", nullable=False, comment="创建时间")
    description = Column(Text, name="description", comment="备注")
    row_data_uuid = Column(String(256), name="row_data_uuid", comment="原始数据uuid")
    collect_id = Column(Integer, name="collect_id", comment="推演数据汇总ID")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def update(self, data_dict):
        for key, value in data_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)


class BasicDictTable(Base):
    """
    原始数据字典集合
    """
    __tablename__ = "BasicDictTable"
    id = Column(Integer, name="id", nullable=False, primary_key=True, comment="id,唯一标识，自增")
    basic_id = Column(Integer, name="basic_id", nullable=False, comment="原始数据数据索引表id")
    col_type = Column(String(256), name="col_type", nullable=False, comment="数据类型")
    col_name = Column(String(256), name="col_name", nullable=False, comment="数据名称")
    col_field_name = Column(String(256), name="col_field_name", nullable=False, comment="数据字段名称")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def update(self, data_dict):
        for key, value in data_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)


class BasicRowDataTable(Base):
    """
    原始数据基础表
    """
    __tablename__ = "BasicRowDataTable"
    id = Column(Integer, name="id", nullable=False, primary_key=True, comment="id,唯一标识，自增")
    row_data = Column(JSON, name="row_data", nullable=False, comment="原始数据集合")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def update(self, data_dict):
        for key, value in data_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)


class SystemTable(Base):
    """
    体系基础表
    """
    __tablename__ = "SystemTable"
    id = Column(Integer, name="id", nullable=False, primary_key=True, comment="id,唯一标识，自增")
    name = Column(String(256), name="name", nullable=False, comment="体系名称")
    description = Column(Text, name="description", comment="备注")
    createTime = Column(String(256), name="createTime", comment="创建时间")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def update(self, data_dict):
        for key, value in data_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)


class SystemDetailTable(Base):
    """
    体系详情
    """
    __tablename__ = "SystemDetailTable"
    id = Column(Integer, name="id", nullable=False, primary_key=True, comment="id,唯一标识，自增")
    system_id = Column(Integer, name="system_id", nullable=False, comment="体系id")
    system_detail = Column(JSON, name="system_detail", nullable=False, comment="详情")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def update(self, data_dict):
        for key, value in data_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)


def get_table_model(engine, table_name, uid_str=None):
    # 将table_name转换为全小写
    table_name = table_name.lower()
    autobase = automap_base()
    autobase.prepare(engine, reflect=True)

    base_model = None
    try:
        base_model = getattr(autobase.classes, table_name)

    except Exception as e:
        return base_model
    if uid_str == None:  # 不分表的情况
        return base_model
    else:  # 分表的情况
        # 获取基础类
        base_table = autobase.metadata.tables[table_name]
        mdata = MetaData()
        new_table = base_table.tometadata(metadata=mdata, name=f'{table_name}_{uid_str}')
        # new_table = base_model.tometadata(metadata=mdata, name=f'{table_name}_{date}')
        try:
            # 创建表
            new_table.create(bind=engine)
        except BaseException as e:
            # 忽略建表异常，存在多进程同时建表情况，忽略后刷新autobase再试
            pass
            # print(f"创建表{table_name}_{uid_str}失败")
        '''Automap的映射虽然是自动的，但是只有在启动的时候生效，也就是说如果新建一个数据表，
        而没有告诉Automap，那这个表是找不到的。在实际使用中，可以捕获AttributeError异常，
        并再次调用AutoBase.prepare(engine, reflect=True) 刷新映射关系。'''
        autobase = automap_base()
        autobase.prepare(engine, reflect=True)
        base_model = getattr(autobase.classes, f'{table_name}_{uid_str}')
        return base_model

# ---------------------------自动生成表结构----------------------------------
# with open(os.path.join(os.getcwd(),"config.yml"), encoding='utf-8') as f:
#     config = yaml.load(f, Loader=yaml.FullLoader)
# #     print("配置文件内容：",config)
# mysql_connect = f'mysql+pymysql://{config["mysql_user"]}:{urlquote(config["mysql_pwd"])}@{config["mysql_ip"]}:{config["mysql_port"]}/{config["mysql_db"]}'  # mysql连接数据库字符串拼接
# #     # 创建数据库引擎
# mysql_engine = create_engine(mysql_connect)
# Base.metadata.create_all(mysql_engine)
