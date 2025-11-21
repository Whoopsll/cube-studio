"""
接口传参
"""
from struct import calcsize
from pydantic import BaseModel


class SelectBasic(BaseModel):
    """
    原始数据查询列
    """
    page: int
    num: int
    name: str
    collect_id: int

class SelectCollectInfo(BaseModel):
    """
    原始数据集合
    """
    id: int
    name : str
    createTime : str


class SelectMetric(BaseModel):
    """
    用于查询指标列表
    """
    page: int
    num: int
    name: str


class SelectSystem(BaseModel):
    """
    用于查询指标列表
    """
    page: int
    num: int
    name: str


class BasicID(BaseModel):
    """
    原始数据ID
    """
    id: int


class SelectBasicRowData(BaseModel):
    """
    查询原始数据信息
    """
    page: int
    num: int
    basic_uuid: str


class BasicDictID(BaseModel):
    """
    原始数据字典ID
    """
    id: int


class BasicRowDataID(BaseModel):
    """
    原始数据ID
    """
    id: int
    basic_uuid: str


class BasicRowDataUid(BaseModel):
    basic_uuid: str
    basic_id: int


class BasicRowDataInfo(BasicRowDataID):
    """
    原始数据信息
    """
    row_data: dict


class MetricID(BaseModel):
    """
    指标ID
    """
    id: int

class AccessID(BaseModel):
    """
    历史数据ID
    """
    id: int

class DocxUid(BaseModel):
    """
    下载文档
    """
    uid:str


class SysytemID(BaseModel):
    """
    体系ID
    """
    id: int


class SystemDetail(BaseModel):
    """
    体系详情
    """
    id: int
    detail: dict


class MetricInfo(BaseModel):
    """
    指标信息
    """
    id: int
    name: str
    formula: str
    constraint: str
    description: str
    creator: str
    createTime: str
    params: list


class BasicInfo(BaseModel):
    """
    推演数据信息
    """
    id: int
    name: str
    description: str
    createTime: str
    collect_id: int


class SystemInfo(BaseModel):
    """
    体系数据信息
    """
    id: int
    name: str
    description: str
    createTime: str


class BasicDictInfo(BaseModel):
    """
    推演数据信息
    """
    id: int
    basic_id: int
    col_type: str
    col_name: str
    col_field_name: str


class ComputeAHPInfo(BaseModel):
    """
    计算ahp
    """
    data_list: list


class ComputeEntropyWeight(BaseModel):
    """
    熵权法
    """
    data_list: list


class ComputeCoefficientMethod(BaseModel):
    """
    变异系数法
    """
    data_list: list


class ComputeGreyRelationalAnalysis(BaseModel):
    """
    灰色关联分析法
    """
    rho: float  # 分辨系数  默认0.5
    index_types: list  # 每个指标的指标类型  positive 越大越好   negative 越小越好
    data_list: list


class ComputeDaraMethod(BaseModel):
    """
    环比系数法
    """
    data_list: list


class ComputeFactorAnalysis(BaseModel):
    """
    因子分析法
    """
    data_list: list

class ComputePcaWeight(BaseModel):
    """
    主成分分析法
    """
    data_list: list


class AccessSelect(BaseModel):
    """
    用于查询指标列表
    """
    page: int
    num: int