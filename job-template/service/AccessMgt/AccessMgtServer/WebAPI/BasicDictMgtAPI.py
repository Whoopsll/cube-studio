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
    prefix='/basic_dict'
)


@router.post("/get")
def get_list(req: BasicID):
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    redict = []
    with session.begin():
        info_list = session.query(AccessModel.BasicDictTable).where(AccessModel.BasicDictTable.basic_id == req.id).all()
        redict = [i.to_dict() for i in info_list]

    return {"code": 1, "msg": "操作成功", "data": {"info": redict}}


@router.post("/delete")
def add_basic_dict(req: BasicDictID):
    """
    删除评估指标
    :param req:
    :return:
    """
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    with session.begin():
        info = session.query(AccessModel.BasicDictTable).where(AccessModel.BasicDictTable.id == req.id).first()
        if info:
            session.delete(info)
        session.commit()
    return {"code": 1, "msg": "操作成功", "data": {}}


@router.post("/update")
def update_basic_dict(req: BasicDictInfo):
    """
    修改推演基础信息
    :param req:
    :return:
    """
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    with session.begin():
        info = session.query(AccessModel.BasicDictTable).where(AccessModel.BasicDictTable.id == req.id).first()
        info.basic_id = req.basic_id
        info.col_type = req.col_type
        info.col_name = req.col_name
        info.col_field_name = req.col_field_name
        session.commit()
    return {"code": 1, "msg": "操作成功", "data": {}}


@router.post("/add")
def add_basic(req: BasicDictInfo):
    """
    增加字典信息
    :param req:
    :return:
    """
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    with session.begin():
        info = AccessModel.BasicDictTable()
        info.basic_id = req.basic_id
        info.col_type = req.col_type
        info.col_name = req.col_name
        info.col_field_name = req.col_field_name
        session.add(info)
        session.commit()
    return {"code": 1, "msg": "操作成功", "data": {}}
