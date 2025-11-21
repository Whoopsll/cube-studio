"""
评估历史数据管理
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
import uuid
import os
from docx import Document

router = APIRouter(
    prefix='/access'
)
@router.post("/get")
def get_list(req: AccessSelect):
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    redict = []
    with session.begin():
        info_list = session.query(AccessModel.AccessDataTable).limit(req.num).offset((req.page - 1) * req.num).all()
        total_num = len(session.query(AccessModel.AccessDataTable).all())
        redict = [i.to_dict() for i in info_list]
    return {"code": 1, "msg": "操作成功", "data": {"info": redict, "total_num": total_num}}


@router.post("/delete")
def delete_access(req: AccessID):
    """
    删除评估指标
    :param req:
    :return:
    """
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    with session.begin():
        info = session.query(AccessModel.AccessDataTable).where(AccessModel.AccessDataTable.id == req.id).first()
        if info:
            session.delete(info)
        session.commit()
    return {"code": 1, "msg": "操作成功", "data": {}}


@router.post("/upload")
def upload_docx(req: DocxUid):
    """
    下载文档
    :param req:
    :return:
    """
    doc = Document(os.path.join(global_var.get_value("current_dir"),"WordDir","{}.docx".format(req.uid)))
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)  # 将文件指针移到开始位置
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=template.docx"}
    )