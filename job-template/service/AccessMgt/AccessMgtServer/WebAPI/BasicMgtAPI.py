# 原始列表管理
from fastapi import APIRouter, FastAPI, Request, HTTPException, Depends
from Utiles.ParameterClass import *
from Utiles import global_var
from sqlalchemy.orm import sessionmaker
from fastapi import UploadFile, File, Form
from fastapi.responses import StreamingResponse
import io
from Model import AccessModel
import numexpr as ne
import uuid

router = APIRouter(
    prefix='/basic'
)

@router.post("/get/collect")
def get_collect(req: SelectMetric):
    """
    获取原始数据汇总
    :return:
    """
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    with session.begin():
        if not req.name:
            info_list = session.query(AccessModel.BasicCollectTable).limit(req.num).offset((req.page - 1) * req.num).all()
            total_num = len(session.query(AccessModel.BasicCollectTable).all())
            redict = [i.to_dict() for i in info_list]
        else:
            info_list = session.query(AccessModel.BasicCollectTable).where(
                AccessModel.BasicCollectTable.name.like("%{}%".format(req.name))).limit(req.num).offset(
                (req.page - 1) * req.num).all()
            total_num = len(session.query(AccessModel.BasicCollectTable).where(
                AccessModel.BasicCollectTable.name.like("%{}%".format(req.name))).all())
            redict = [i.to_dict() for i in info_list]
    return {"code": 1, "msg": "操作成功", "data": {"info": redict, "total_num": total_num}}

@router.post("/update/collect")
def update_collect(req: SelectCollectInfo):
    """
    获取原始数据汇总
    :return:
    """
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    with session.begin():
        info = session.query(AccessModel.BasicCollectTable).where(AccessModel.BasicCollectTable.id == req.id).first()
        info.name = req.name
        info.createTime = req.createTime
        session.commit()
    return {"code": 1, "msg": "操作成功", "data": {}}

@router.post("/add/collect")
def add_collect(req: SelectCollectInfo):
    """
    获取原始数据汇总
    :return:
    """
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    with session.begin():
        info = AccessModel.BasicCollectTable()
        info.name = req.name
        info.createTime = req.createTime
        session.add(info)
        session.commit()
    return {"code": 1, "msg": "操作成功", "data": {}}

@router.post("/delete/collect")
def delete_collect(req: MetricID):
    """
    获取原始数据汇总
    :return:
    """
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    with session.begin():
        info = session.query(AccessModel.BasicCollectTable).where(AccessModel.BasicCollectTable.id == req.id).first()
        session.delete(info)
        session.commit()
    return {"code": 1, "msg": "操作成功", "data": {}}

@router.post("/get")
def get_list(req: SelectBasic):
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    redict = []
    with session.begin():
        if not req.name:
            info_list = session.query(AccessModel.BasicTable).where(AccessModel.BasicTable.collect_id == req.collect_id).limit(req.num).offset((req.page - 1) * req.num).all()
            total_num = len(session.query(AccessModel.BasicTable).where(AccessModel.BasicTable.collect_id == req.collect_id).all())
            redict = [i.to_dict() for i in info_list]
        else:
            info_list = session.query(AccessModel.BasicTable).where(
                AccessModel.BasicTable.collect_id == req.collect_id,AccessModel.BasicTable.name.like("%{}%".format(req.name))).limit(req.num).offset(
                (req.page - 1) * req.num).all()
            total_num = len(session.query(AccessModel.BasicTable).where(
                AccessModel.BasicTable.collect_id == req.collect_id,AccessModel.BasicTable.name.like("%{}%".format(req.name))).all())
            redict = [i.to_dict() for i in info_list]
    return {"code": 1, "msg": "操作成功", "data": {"info": redict, "total_num": total_num}}


@router.post("/delete")
def add_basic(req: MetricID):
    """
    删除评估指标
    :param req:
    :return:
    """
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    with session.begin():
        info = session.query(AccessModel.BasicTable).where(AccessModel.BasicTable.id == req.id).first()
        if info:
            session.delete(info)
        session.commit()
    return {"code": 1, "msg": "操作成功", "data": {}}

@router.post("/update")
def update_basic(req: BasicInfo):
    """
    修改推演基础信息
    :param req:
    :return:
    """
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    with session.begin():
        info = session.query(AccessModel.BasicTable).where(AccessModel.BasicTable.id == req.id).first()
        info.name = req.name
        info.createTime = req.createTime
        info.description = req.description
        info.collect_id = req.collect_id
        session.commit()
    return {"code": 1, "msg": "操作成功", "data": {}}


@router.post("/add")
def add_basic(req: BasicInfo):
    """
    增加推演基础信息
    :param req:
    :return:
    """
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    uuid_str = str(uuid.uuid1())
    with session.begin():
        info = AccessModel.BasicTable()
        info.name = req.name
        info.createTime = req.createTime
        info.description = req.description
        info.row_data_uuid = uuid_str
        info.collect_id = req.collect_id
        session.add(info)
        session.commit()
    AccessModel.get_table_model(mysql_engine,"BasicRowDataTable",uuid_str)
    return {"code": 1, "msg": "操作成功", "data": {}}
