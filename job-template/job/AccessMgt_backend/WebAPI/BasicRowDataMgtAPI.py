# 原始列表管理
from fastapi import APIRouter, FastAPI, Request, HTTPException, Depends
from Utiles.ParameterClass import *
from Utiles import global_var
from sqlalchemy.orm import sessionmaker
from fastapi import UploadFile, File, Form
from sqlalchemy import delete
from fastapi.responses import StreamingResponse
import io
from Model import AccessModel
import numexpr as ne
import uuid
import csv
import json

router = APIRouter(
    prefix='/basic_row_data'
)


@router.post("/get")
def get_list(req: SelectBasicRowData):
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    model = AccessModel.get_table_model(mysql_engine,"BasicRowDataTable",req.basic_uuid)
    with session.begin():
        info_list = session.query(model).limit(req.num).offset((req.page - 1) * req.num).all()
        total = len(session.query(model).all())
        redict = [{c.name: getattr(info, c.name) for c in info.__table__.columns} for info in info_list]

    return {"code": 1, "msg": "操作成功", "data": {"info": redict,"total":total}}


@router.post("/delete")
def add_basic_row_data(req: BasicRowDataID):
    """
    删除原始数据
    :param req:
    :return:
    """
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    model = AccessModel.get_table_model(mysql_engine, "BasicRowDataTable", req.basic_uuid)
    with session.begin():
        info = session.query(model).where(model.id == req.id).first()
        if info:
            session.delete(info)
        session.commit()
    return {"code": 1, "msg": "操作成功", "data": {}}


@router.post("/update")
def update_basic_row_data(req: BasicRowDataInfo):
    """
    修改推演基础信息
    :param req:
    :return:
    """
    print(req.id)
    print(req.basic_uuid)
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    model = AccessModel.get_table_model(mysql_engine, "BasicRowDataTable", req.basic_uuid)
    with session.begin():
        info = session.query(model).where(model.id == req.id).first()
        info.row_data = req.row_data
        session.commit()
    return {"code": 1, "msg": "操作成功", "data": {}}


@router.post("/add")
def add_basic_row_data(req: BasicRowDataInfo):
    """
    增加字典信息
    :param req:
    :return:
    """
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    model = AccessModel.get_table_model(mysql_engine, "BasicRowDataTable", req.basic_uuid)
    with session.begin():
        info = model()
        info.row_data = req.row_data
        session.add(info)
        session.commit()
    return {"code": 1, "msg": "操作成功", "data": {}}


@router.post("/import")
def import_basic_row_data(file: UploadFile = File(...), basic_uuid: str = Form(...),is_cover: bool = Form(...),basic_id: int = Form(...)):
    contents = file.file.read()
    sql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=sql_engine)()
    with session.begin():
        # 1. 解析文件内容
        records = []
        # 将字节数据解码为字符串并使用StringIO包装
        csv_data = io.StringIO(contents.decode("utf-8", errors='replace'))
        reader = csv.reader(csv_data)
        for line in reader:
            records.append(line)
        records_head = records.pop(0)
        print(records_head)
        col_list = session.query(AccessModel.BasicDictTable).where(AccessModel.BasicDictTable.basic_id == basic_id).all()
        col_field_list = []
        for col_info in col_list:
            if col_info.col_field_name not in records_head:
                return {"code": 0, "message": "文件中中字段与设置字段不匹配", "data": {}}
            col_field_list.append(col_info.col_field_name)
        model = AccessModel.get_table_model(sql_engine, "BasicRowDataTable", basic_uuid)
        if is_cover:
            session.execute(delete(model))
        model_instances = []
        for record in records:
            new_model = model()
            # 组织数据
            info_dict = {}
            for i in col_field_list:
                info_dict[i] = record[records_head.index(i)]
            new_model.row_data = info_dict
            model_instances.append(new_model)
        session.bulk_save_objects(model_instances)  # 批量插入数据  必须是同一类型的
        session.commit()
    return {"code": 1, "message": "操作成功", "data": {}}


@router.post("/export")
def export_basic_row_data(req: BasicRowDataUid):
    """
    导出数据
    :return:
    """
    sql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=sql_engine)()
    with session.begin():
        # 查询该数据包含的表
        info_list = session.query(AccessModel.BasicDictTable).where(AccessModel.BasicDictTable.basic_id == req.basic_id).all()
        data = []
        field_list = []
        for i in info_list:
            field_list.append(i.col_field_name)
        data.append(field_list)
        # 查询原始数据据
        model = AccessModel.get_table_model(sql_engine, "BasicRowDataTable", req.basic_uuid)
        info_list = session.query(model).all()
        for i in info_list:
            row_data = []
            for field in field_list:
                row_data.append((i.row_data)[field])
            data.append(row_data)
        csv_file = io.StringIO()
        csv_writer = csv.writer(csv_file)
        csv_writer.writerows(data)

        # 重置文件指针
        csv_file.seek(0)

        return StreamingResponse(
            csv_file,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=data.csv"}
        )


