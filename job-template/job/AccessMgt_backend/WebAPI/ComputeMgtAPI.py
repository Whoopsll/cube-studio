# 用于校验和计算相关函数

from fastapi import APIRouter, FastAPI, Request, HTTPException, Depends
from Utiles.ParameterClass import *
from Utiles import global_var
from sqlalchemy.orm import sessionmaker
from fastapi import UploadFile, File, Form
from sqlalchemy import delete
from fastapi.responses import StreamingResponse
import io
from Utiles.AHP import AHPFuncClass
from Utiles.EntropyWeight import EntropyWeightClass
from Utiles.CoefficientMethod import CoefficientMethodClass
from Utiles.GreyRelationalAnalysis import GreyRelationalAnalysisClass
from Utiles.DareMethod import DareMethodClass
from Utiles.FactorAnalysis import FactorAnalysisClass
from Utiles.PcaWeights import PcaWeightClass
from Utiles.SystemCalcClass import SystemCalcClass
from Utiles.MakeDocx import MakeDocxClass


from datetime import datetime


from Model import AccessModel
import numexpr as ne
import uuid
import csv
import json
import pandas as pd
import numpy as np

router = APIRouter(
    prefix='/compute'
)


@router.post("/ahp")
def compute_ahp(req: ComputeAHPInfo):
    """
    基于ahp算法计算权重
    :param req:
    :return:
    """
    # 将二维矩阵转换为一维
    one_d_list = [item for sublist in req.data_list for item in sublist]
    criteria_matrix2 = np.array(
        one_d_list)
    ifSuccessTest, real_weightTest, errorInfoTest = AHPFuncClass.ahp_analysis(criteria_matrix2)
    if ifSuccessTest:
        return {"code": 1, "msg": "操作成功", "data": list(real_weightTest)}
    else:
        return {"code": 0, "msg": errorInfoTest, "data": []}


@router.post("/entropy_weight")
def compute_entropy_weight(req: ComputeEntropyWeight):
    """
    基于熵权法计算权重
    :param req:
    :return:
    """
    # info = [{"code": 1, "row_list": [1, 2, 3, 4, 5]}, {"code": 2, "row_list": [1, 2, 3, 4, 5]},
    #         {"code": 3, "row_list": [1, 2, 3, 4, 5]}]
    info_dict = {}
    for i in req.data_list:
        info_dict[i["code"]] = [float(i) for i in i["row_list"]]
    data = pd.DataFrame(info_dict)
    weights = EntropyWeightClass.entropy_weight(data)
    re_list = []
    for i, col in enumerate(data.columns):
        field = {}
        field["code"] = col
        field["weight"] = weights[i]
        re_list.append(field)
    return {"code": 1, "msg": "操作成功", "data": re_list}


@router.post("/coefficient_method")
def compute_coefficient_method(req: ComputeCoefficientMethod):
    """
    变异系数法
    :param req:
    :return:
    """
    # info = [{"code": 1, "row_list": [1, 2, 3, 4, 5]}, {"code": 2, "row_list": [1, 2, 3, 4, 5]},
    #         {"code": 3, "row_list": [1, 2, 3, 4, 5]}]
    info_dict = {}
    for i in req.data_list:
        info_dict[i["code"]] = [float(i) for i in i["row_list"]]
    data = pd.DataFrame(info_dict)
    weights = CoefficientMethodClass.coefficient_of_variation_method(data)
    re_list = []
    for i, col in enumerate(data.columns):
        field = {}
        field["code"] = col
        field["weight"] = weights[i]
        re_list.append(field)
    return {"code": 1, "msg": "操作成功", "data": re_list}


@router.post("/grey_relational_analysis")
def compute_grey_relational_analysis(req: ComputeGreyRelationalAnalysis):
    """
    灰色关联分析法
    :return:
    """
    # data = np.array([
    #     [85, 90, 78, 92, 88],  # 样本1的5个指标值
    #     [82, 88, 80, 95, 85],  # 样本2的5个指标值
    #     [90, 85, 82, 90, 92],  # 样本3的5个指标值
    #     [88, 92, 76, 88, 90],  # 样本4的5个指标值
    #     [86, 89, 85, 94, 87],  # 样本5的5个指标值
    #     [89, 87, 81, 91, 89]  # 样本6的5个指标值
    # ])
    data = np.array(req.data_list)
    # 指标类型：5个指标分别为正向、正向、正向、正向、正向
    # 可根据实际情况修改为'negative'
    # index_types = ["positive", "positive", "positive", "positive", "positive"]
    index_types = req.index_types
    # 计算权重
    gra = GreyRelationalAnalysisClass(rho=req.rho)
    weights = gra.calculate_weights(data, index_types)
    return {"code": 1, "msg": "操作成功", "data": list(weights)}


@router.post("/dare_method")
def compute_dare_method(req: ComputeDaraMethod):
    """
    环比系数法
    :param req:
    :return:
    """
    try:
        info = DareMethodClass.dare_method(req.data_list)
    except Exception as e:
        print(e)
    return {"code": 1, "msg": "操作成功", "data": info}


@router.post("/factor_analysis")
def compute_factor_analysis(req: ComputeFactorAnalysis):
    """
    因子子分析法
    :param req:
    :return:
    """
    # req.data_list = [[1,2,3,4,5],[2,3,4,5,6]]
    try:
        print(req.data_list)
        data_dict = {}
        for i in range(len(req.data_list)):
            data_dict[str(i + 1)] = [float(j) for j in req.data_list[i]]
        print(data_dict)
        data = pd.DataFrame(data_dict)

        # 计算权重
        weights, loadings, contrib = FactorAnalysisClass.factor_analysis(data)
        print(weights)
        re_list = []
        for var, w in weights.items():
            if np.isnan(w):
                return {"code": 0, "msg": "自动确定因子个数为0，无法计算出权重", "data": {}}
            re_list.append(w)
        return {"code": 1, "msg": "操作成功", "data": re_list}
    except:
        return {"code": 0, "msg": "无法计算出权重", "data": {}}


@router.post("/pca_weight")
def compute_pca_weight(req: ComputePcaWeight):
    """
    主成分分析法
    :param req:
    :return:
    """
    # req.data_list = [[1, 2, 3, 4, 5], [2, 3, 4, 5, 6]]
    try:
        data_dict = {}
        for i in range(len(req.data_list)):
            data_dict[str(i + 1)] = [float(j) for j in req.data_list[i]]
        data = pd.DataFrame(data_dict)
        weights, loadings, variance_ratio = PcaWeightClass.pca_weights(data)
        re_list = []
        for var, w in weights.items():
            if np.isnan(w):
                return {"code": 0, "msg": "无法计算出权重", "data": {}}
            re_list.append(w)
        return {"code": 1, "msg": "操作成功", "data": re_list}
    except:
        return {"code": 0, "msg": "无法计算出权重", "data": {}}


@router.post("/start")
def compute_system(req: SysytemID):
    """
    执行评估指标
    :return:
    """
    # info = {"treeData": {"baseMetrics": [{"id": "base-metrics", "label": "基础指标", "children": [{"id": 5, "label": "测试", "description": "测试修改"}, {"id": 6, "label": "测试序号", "description": "测试"}]}], "customMetrics": [{"id": "custom-metrics", "label": "自定义指标", "children": [{"id": "custom-1-1", "label": "客户满意度", "description": "客户满意度评分指标"}, {"id": "custom-1-2", "label": "市场占有率", "description": "产品市场占有率指标"}, {"id": "custom-2", "label": "自定义指标组", "children": [{"id": "custom-2-1", "label": "综合评分", "description": "多维度综合评分指标"}], "description": "计算类自定义指标"}, {"id": "custom-1754473221198", "label": "测试", "description": "test"}]}]}, "graphData": {"edges": [{"id": "edge-node-1754640700959-node-1754640702823", "type": "dataflow", "label": "", "source": "node-1754640700959", "target": "node-1754640702823", "createTime": 1754640712819, "updateTime": 1754640712819, "description": ""}, {"id": "edge-node-1754640700959-node-1754640704585", "type": "dataflow", "label": "", "source": "node-1754640700959", "target": "node-1754640704585", "createTime": 1754640714014, "updateTime": 1754640714014, "description": ""}, {"id": "edge-node-1754640700959-node-1754640706771", "type": "dataflow", "label": "", "source": "node-1754640700959", "target": "node-1754640706771", "createTime": 1754640715107, "updateTime": 1754640715107, "description": ""}], "nodes": [{"x": 60, "y": 144.703125, "id": "node-1754640700959", "code": 5, "label": "测试", "params": [{"name": "测试参数一", "alias": "p1"}, {"name": "测试参数二", "alias": "p2"}, {"name": "测试参数三", "alias": "p3"}], "weight": 0, "formula": "p1 + (p2 * p3)", "category": "", "createTime": 1754640700959, "metricType": "base", "updateTime": 1754641536421, "description": "测试修改"}, {"x": 230, "y": 54.703125, "id": "node-1754640702823", "code": "custom-1-1", "label": "客户满意度", "params": [], "weight": 0, "formula": "", "category": "", "createTime": 1754640702823, "metricType": "custom", "updateTime": 1754640784426, "description": "客户满意度评分指标"}, {"x": 230, "y": 144.703125, "id": "node-1754640704585", "code": "custom-1-2", "label": "市场占有率", "params": [], "weight": 0, "formula": "", "category": "", "createTime": 1754640704585, "metricType": "custom", "updateTime": 1754640806582, "description": "产品市场占有率指标"}, {"x": 230, "y": 237.703125, "id": "node-1754640706771", "code": 6, "label": "测试序号", "params": [{"name": "参数一", "alias": "p1"}, {"name": "参数二", "alias": "p2"}], "weight": 0, "formula": "p1-p2", "category": "", "createTime": 1754640706771, "metricType": "base", "updateTime": 1754725426176, "description": "测试"}]}, "nodeDetails": {"node-1754640700959": {"code": 5, "label": "测试", "weight": 0, "formula": "p1 + (p2 * p3)", "category": "", "ahpMatrix": [[1, 3, 2], [0.3333333333333333, 1, 1], [0.5, 1, 1]], "ahpWeights": [{"nodeId": "node-1754640702823", "weight": 0.5499456072975837, "nodeLabel": "客户满意度"}, {"nodeId": "node-1754640704585", "weight": 0.20984352310106175, "nodeLabel": "市场占有率"}, {"nodeId": "node-1754640706771", "weight": 0.24021086960135463, "nodeLabel": "测试序号"}], "updateTime": 1754641536421, "description": "测试修改", "expertScore": 100, "businessRule": "", "childWeights": {"node-1754640702823": 0, "node-1754640704585": 0, "node-1754640706771": 0}, "customWeight": 0, "parameterList": [{"id": "param-1754640718303-0", "name": "测试参数一", "alias": "p1"}, {"id": "param-1754640718303-1", "name": "测试参数二", "alias": "p2"}, {"id": "param-1754640718303-2", "name": "测试参数三", "alias": "p3"}], "scoreSegments": [20, 40, 60], "scoringMethod": [], "fuzzyMatrixData": [{"nodeId": "node-1754640702823", "values": ["12", "23", "33"], "nodeName": "客户满意度"}, {"nodeId": "node-1754640704585", "values": ["11", "22", "54"], "nodeName": "市场占有率"}, {"nodeId": "node-1754640706771", "values": ["5", "56", "77"], "nodeName": "测试序号"}], "selectedAlgorithm": "expert", "normalizationParams": {"d": 0, "k": 1, "mu": 0.5, "std": 1, "mean": 0, "x_max": 0, "x_min": 0, "upDown": 0, "x_list": ["2", "21"], "y_list": ["2", "2"], "decimal": 2}, "normalizationAlgorithm": "gaussian_mapping", "selectedAnalysisMethod": "ahp"}, "node-1754640702823": {"code": "custom-1-1", "label": "客户满意度", "weight": 0, "formula": "", "category": "", "updateTime": 1754640784426, "description": "客户满意度评分指标", "expertScore": 90, "businessRule": "", "childWeights": {}, "customWeight": 0, "parameterList": [], "scoringMethod": "expert", "selectedAlgorithm": "weighted", "normalizationParams": {"d": 0, "k": 1, "mu": 0.5, "std": 1, "mean": 0, "x_max": 0, "x_min": 0, "upDown": 0, "x_list": ["2", "21"], "y_list": ["2", "2"], "decimal": 2}, "normalizationAlgorithm": "gaussian_mapping", "selectedAnalysisMethod": "ahp"}, "node-1754640704585": {"code": "custom-1-2", "label": "市场占有率", "weight": 0, "formula": "", "category": "", "updateTime": 1754640806582, "description": "产品市场占有率指标", "expertScore": 100, "businessRule": "", "childWeights": {}, "customWeight": 0, "parameterList": [], "scoringMethod": "expert", "selectedAlgorithm": "weighted", "normalizationParams": {"d": 0, "k": 1, "mu": 0.5, "std": 1, "mean": 0, "x_max": 0, "x_min": 0, "upDown": 0, "x_list": ["2", "21"], "y_list": ["2", "2"], "decimal": 2}, "normalizationAlgorithm": "segmentation_liner_mapping", "selectedAnalysisMethod": "ahp"}, "node-1754640706771": {"code": 6, "label": "测试序号", "weight": 0, "formula": "p1-p2", "category": "", "updateTime": 1754725426177, "dataSources": {"param-1754640807343-0": {"dataSource": 2, "resultType": "get_median", "updateTime": 1754640817168, "filterConditions": [{"field": 3, "value": "1", "operator": "greater_than"}], "percentageCondition": ""}, "param-1754640807343-1": {"dataSource": 3, "resultType": "get_sum", "updateTime": 1754725423384, "filterConditions": [{"field": 3, "value": "1", "operator": "equals"}], "percentageCondition": ""}}, "description": "测试", "expertScore": 100, "businessRule": "", "childWeights": {}, "customWeight": 0, "parameterList": [{"id": "param-1754640807343-0", "name": "参数一", "alias": "p1"}, {"id": "param-1754640807343-1", "name": "参数二", "alias": "p2"}], "scoringMethod": "formula", "selectedAlgorithm": "weighted", "normalizationParams": {"d": 0, "k": 1, "mu": 0.5, "std": 1, "mean": 0, "x_max": 0, "x_min": 0, "upDown": 0, "x_list": ["2", "21"], "y_list": ["2", "2"], "decimal": 2}, "normalizationAlgorithm": "gaussian_mapping", "selectedAnalysisMethod": "ahp"}}, "workflowType": 1}
    # sql_engine = global_var.get_value("")
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    # 根据体系ID查询
    with session.begin():
        info = session.query(AccessModel.SystemDetailTable).where(
            AccessModel.SystemDetailTable.system_id == req.id).first()
        if info:
            tree_info = info.system_detail
        else:
            return {"code": 0, "msg": "未获得指标体系", "data": {}}
        system_info = session.query(AccessModel.SystemTable).where(AccessModel.SystemTable.id == req.id).first()
        system_name = ""
        system_description = ""
        if system_info:
            system_name = system_info.name
            system_description = system_info.description
        # 数据源id

    results,tree_data,node_details,data_name,data_createTime = SystemCalcClass.calc(tree_info, mysql_engine)
    return {"code": 1, "msg": "操作成功", "data": {"results":results,"tree_data":tree_data[0],"node_details": node_details,"system_name": system_name, "system_description": system_description,"data_name":data_name,"data_description": ""}}


@router.post("/make_docx")
def make_docx(req: SysytemID):
    """
    生成word
    :param req:
    :return:
    """
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    # 根据体系ID查询
    with session.begin():
        info = session.query(AccessModel.SystemDetailTable).where(
            AccessModel.SystemDetailTable.system_id == req.id).first()
        if info:
            tree_info = info.system_detail
        else:
            return {"code": 0, "msg": "未获得指标体系", "data": {}}
        system_info = session.query(AccessModel.SystemTable).where(AccessModel.SystemTable.id == req.id).first()
        system_name = ""
        system_description = ""
        if system_info:
            system_name = system_info.name
            system_description = system_info.description
        if system_info:
            system_info = system_info.to_dict()
    results, tree_data, node_details, data_name,data_createTime = SystemCalcClass.calc(tree_info, mysql_engine)
    basic_info = {"name": data_name,"description": "","createTime": data_createTime}
    uid,doc = MakeDocxClass.make_docx(system_info, basic_info,tree_data[0],node_details,results)

    data_result = {"results": results, "tree_data": tree_data[0], "node_details": node_details,
                   "system_name": system_name, "system_description": system_description, "data_name": data_name,
                   "data_description": ""}
    # 进行数据存储，返回至前端
    mysql_engine = global_var.get_value("mysql_engine")
    session = sessionmaker(bind=mysql_engine)()
    with session.begin():
        model = AccessModel.AccessDataTable()
        current_datetime = datetime.now()
        model.createTime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        model.system_detail = tree_info
        model.system_name = system_name
        model.system_description = system_description
        model.basic_name = basic_info["name"]
        model.basic_description = basic_info["description"]
        model.system_result = data_result
        model.word_uid = uid
        session.add(model)
        session.commit()


    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)  # 将文件指针移到开始位置
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=template.docx"}
    )