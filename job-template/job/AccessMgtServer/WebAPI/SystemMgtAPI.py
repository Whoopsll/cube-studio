"""
体系管理
"""
from fastapi import APIRouter, FastAPI, Request, HTTPException, Depends
from Utiles.ParameterClass import *
from Utiles import global_var
from sqlalchemy.orm import sessionmaker
from fastapi import UploadFile, File, Form
from fastapi.responses import StreamingResponse
import io
from Model import AccessModel
import numexpr as ne
from datetime import datetime

router = APIRouter(
    prefix='/system'
)


@router.post("/get")
def get_list(req: SelectSystem):
    """
    获取体系管理列表
    :param req:
    :return:
    """
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    redict = []
    with session.begin():
        if not req.name:
            info_list = session.query(AccessModel.SystemTable).limit(req.num).offset((req.page - 1) * req.num).all()
            total_num = len(session.query(AccessModel.SystemTable).all())
            redict = [i.to_dict() for i in info_list]
        else:
            info_list = session.query(AccessModel.SystemTable).where(
                AccessModel.SystemTable.name.like("%{}%".format(req.name))).limit(req.num).offset(
                (req.page - 1) * req.num).all()
            total_num = len(session.query(AccessModel.SystemTable).where(
                AccessModel.SystemTable.name.like("%{}%".format(req.name))).all())
            redict = [i.to_dict() for i in info_list]
    return {"code": 1, "msg": "操作成功", "data": {"info": redict, "total_num": total_num}}


@router.post("/delete")
def delete_system(req: SysytemID):
    """
    删除评估体系
    :param req:
    :return:
    """
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    with session.begin():
        info = session.query(AccessModel.SystemTable).where(AccessModel.SystemTable.id == req.id).first()
        if info:
            session.delete(info)
        session.commit()
    return {"code": 1, "msg": "操作成功", "data": {}}


@router.post("/update")
def update_system(req: SystemInfo):
    """
    修改评估体系
    :param req:
    :return:
    """
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    with session.begin():
        info = session.query(AccessModel.SystemTable).where(AccessModel.SystemTable.id == req.id).first()
        info.name = req.name
        info.createTime = req.createTime
        info.description = req.description
        session.commit()
    return {"code": 1, "msg": "操作成功", "data": {}}


@router.post("/add")
def add_system(req: SystemInfo):
    """
    增加推演基础信息
    :param req:
    :return:
    """
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    with session.begin():
        info = AccessModel.SystemTable()
        info.name = req.name
        info.createTime = req.createTime
        info.description = req.description
        session.add(info)
        session.commit()
    return {"code": 1, "msg": "操作成功", "data": {}}


@router.post("/save")
def save_system_detail(req: SystemDetail):
    """
    保存体系指标详情
    :param req:
    :return:
    """
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    with session.begin():
        info = session.query(AccessModel.SystemDetailTable).where(
            AccessModel.SystemDetailTable.system_id == req.id).first()
        if info:
            info.system_detail = req.detail
        else:
            info = AccessModel.SystemDetailTable()
            info.system_detail = req.detail
            info.system_id = req.id
            session.add(info)
        session.commit()
    return {"code": 1, "msg": "操作成功", "data": {}}


@router.post("/detail")
def get_system_detail(req: SysytemID):
    """
    获取指标树
    :param req:
    :return:
    """
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    re_dict = {}
    with session.begin():
        info = session.query(AccessModel.SystemDetailTable).where(
            AccessModel.SystemDetailTable.system_id == req.id).first()
        if info:
            re_dict = info.system_detail
    return {"code": 1, "msg": "操作成功", "data": re_dict}

@router.post("/copy")
def copy_system(req: SysytemID):
    """
    复制
    :param req:
    :return:
    """
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    re_dict = {}
    with session.begin():
        # 获取体系详情
        info = session.query(AccessModel.SystemDetailTable).where(
            AccessModel.SystemDetailTable.system_id == req.id).first()
        if info:
            re_dict = info.system_detail
        # 获取体系信息
        system_info = session.query(AccessModel.SystemTable).where(AccessModel.SystemTable.id == req.id).first()
        if system_info:
            model = AccessModel.SystemTable()
            model.name = "{}_副本".format(system_info.name)
            model.description = system_info.description
            now = datetime.now()
            model.createTime = now.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return {"code": 0, "msg": "未查询到当前数据", "data": {}}
        session.add(model)
        session.flush()
        # 插入详情数据
        detail_model = AccessModel.SystemDetailTable()
        detail_model.system_id = model.id
        detail_model.system_detail = re_dict
        session.add(detail_model)
        session.commit()
    return {"code": 1, "msg": "操作成功", "data": {}}
