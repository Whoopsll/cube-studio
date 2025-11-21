# 指标管理
from fastapi import APIRouter, FastAPI, Request, HTTPException, Depends
from Utiles.ParameterClass import *
from Utiles import global_var
from sqlalchemy.orm import sessionmaker
from fastapi import UploadFile, File, Form
from fastapi.responses import StreamingResponse
import io
from Model import AccessModel
import numexpr as ne

router = APIRouter(
    prefix='/metric'
)




@router.post("/get")
def get_list(req: SelectMetric):
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    redict = []
    with session.begin():
        if not req.name:
            info_list = session.query(AccessModel.MetricTable).limit(req.num).offset((req.page - 1) * req.num).all()
            total_num = len(session.query(AccessModel.MetricTable).all())
            redict = [i.to_dict() for i in info_list]
        else:
            info_list = session.query(AccessModel.MetricTable).where(
                AccessModel.MetricTable.name.like("%{}%".format(req.name))).limit(req.num).offset(
                (req.page - 1) * req.num).all()
            total_num = len(session.query(AccessModel.MetricTable).where(
                AccessModel.MetricTable.name.like("%{}%".format(req.name))).all())
            redict = [i.to_dict() for i in info_list]
    return {"code": 1, "msg": "操作成功", "data": {"info": redict, "total_num": total_num}}


@router.post("/delete")
def add_metric(req: MetricID):
    """
    删除评估指标
    :param req:
    :return:
    """
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    with session.begin():
        info = session.query(AccessModel.MetricTable).where(AccessModel.MetricTable.id == req.id).first()
        if info:
            session.delete(info)
        session.commit()
    return {"code": 1, "msg": "操作成功", "data": {}}


@router.post("/update")
def update_metric(req: MetricInfo):
    """
    修改评估指标
    :param req:
    :return:
    """
    # 校验公式以及参数
    variables_dict = {}
    for i in req.params:
        variables_dict[i["alias"]] = 1
    try:
        result = ne.evaluate(req.formula, variables_dict)
    except:
        return {"code": 0, "msg": "公式或参数错误", "data": {}}
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    with session.begin():
        info = session.query(AccessModel.MetricTable).where(AccessModel.MetricTable.id == req.id).first()
        info.name = req.name
        info.formula = req.formula
        info.constraint = req.constraint
        info.description = req.description
        info.creator = req.creator
        info.createTime = req.createTime
        info.params = req.params
        session.commit()
    return {"code": 1, "msg": "操作成功", "data": {}}


@router.post("/add")
def add_metric(req: MetricInfo):
    """
    增加评估指标
    :param req:
    :return:
    """
    # 校验公式以及参数
    variables_dict = {}
    for i in req.params:
        variables_dict[i["alias"]] = 1
    try:
        print(variables_dict)
        print(req.formula)
        result = ne.evaluate(req.formula, variables_dict)
    except Exception as e:
        print(e)
        return {"code": 0, "msg": "公式或参数错误", "data": {}}
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    with session.begin():
        info = AccessModel.MetricTable()
        info.name = req.name
        info.formula = req.formula
        info.constraint = req.constraint
        info.description = req.description
        info.creator = req.creator
        info.createTime = req.createTime
        info.params = req.params
        session.add(info)
        session.commit()
    return {"code": 1, "msg": "操作成功", "data": {}}

