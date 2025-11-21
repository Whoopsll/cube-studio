# -*- coding: utf-8 -*-
"""
用于体系计算
"""
from Utiles.WeightedMean import WeightedMeanClass
from Utiles.NormalizeFunc import NormalizeFuncClass
from Utiles.PowerSeries import PowerSeriesClass
from Utiles.GreyClustering import GreyClusteringClass
from Utiles.FuzzyAssessment import FuzzyAssessmentClass

from Utiles.ArrayStatisticsFunc import ArrayStatisticsClass
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import sessionmaker
from Model import AccessModel
import numexpr as ne
import json

# a = {"treeData": {"baseMetrics": [{"id": "base-metrics", "label": "基础指标", "children": [{"id": 5, "label": "测试", "description": "测试修改"}, {"id": 6, "label": "测试序号", "description": "测试"}]}], "customMetrics": [{"id": "custom-metrics", "label": "自定义指标", "children": [{"id": "custom-1-1", "label": "客户满意度", "description": "客户满意度评分指标"}, {"id": "custom-1-2", "label": "市场占有率", "description": "产品市场占有率指标"}, {"id": "custom-2", "label": "自定义指标组", "children": [{"id": "custom-2-1", "label": "综合评分", "description": "多维度综合评分指标"}], "description": "计算类自定义指标"}, {"id": "custom-1754473221198", "label": "测试", "description": "test"}]}]}, "graphData": {"edges": [{"id": "edge-node-1754640700959-node-1754640702823", "type": "dataflow", "label": "", "source": "node-1754640700959", "target": "node-1754640702823", "createTime": 1754640712819, "updateTime": 1754640712819, "description": ""}, {"id": "edge-node-1754640700959-node-1754640704585", "type": "dataflow", "label": "", "source": "node-1754640700959", "target": "node-1754640704585", "createTime": 1754640714014, "updateTime": 1754640714014, "description": ""}, {"id": "edge-node-1754640700959-node-1754640706771", "type": "dataflow", "label": "", "source": "node-1754640700959", "target": "node-1754640706771", "createTime": 1754640715107, "updateTime": 1754640715107, "description": ""}], "nodes": [{"x": 60, "y": 144.703125, "id": "node-1754640700959", "code": 5, "label": "测试", "params": [{"name": "测试参数一", "alias": "p1"}, {"name": "测试参数二", "alias": "p2"}, {"name": "测试参数三", "alias": "p3"}], "weight": 0, "formula": "p1 + (p2 * p3)", "category": "", "createTime": 1754640700959, "metricType": "base", "updateTime": 1754641536421, "description": "测试修改"}, {"x": 230, "y": 54.703125, "id": "node-1754640702823", "code": "custom-1-1", "label": "客户满意度", "params": [], "weight": 0, "formula": "", "category": "", "createTime": 1754640702823, "metricType": "custom", "updateTime": 1754640784426, "description": "客户满意度评分指标"}, {"x": 230, "y": 144.703125, "id": "node-1754640704585", "code": "custom-1-2", "label": "市场占有率", "params": [], "weight": 0, "formula": "", "category": "", "createTime": 1754640704585, "metricType": "custom", "updateTime": 1754640806582, "description": "产品市场占有率指标"}, {"x": 230, "y": 237.703125, "id": "node-1754640706771", "code": 6, "label": "测试序号", "params": [{"name": "参数一", "alias": "p1"}, {"name": "参数二", "alias": "p2"}], "weight": 0, "formula": "p1-p2", "category": "", "createTime": 1754640706771, "metricType": "base", "updateTime": 1754725426176, "description": "测试"}]}, "nodeDetails": {"node-1754640700959": {"code": 5, "label": "测试", "weight": 0, "formula": "p1 + (p2 * p3)", "category": "", "ahpMatrix": [[1, 3, 2], [0.3333333333333333, 1, 1], [0.5, 1, 1]], "ahpWeights": [{"nodeId": "node-1754640702823", "weight": 0.5499456072975837, "nodeLabel": "客户满意度"}, {"nodeId": "node-1754640704585", "weight": 0.20984352310106175, "nodeLabel": "市场占有率"}, {"nodeId": "node-1754640706771", "weight": 0.24021086960135463, "nodeLabel": "测试序号"}], "updateTime": 1754641536421, "description": "测试修改", "expertScore": 100, "businessRule": "", "childWeights": {"node-1754640702823": 0, "node-1754640704585": 0, "node-1754640706771": 0}, "customWeight": 0, "parameterList": [{"id": "param-1754640718303-0", "name": "测试参数一", "alias": "p1"}, {"id": "param-1754640718303-1", "name": "测试参数二", "alias": "p2"}, {"id": "param-1754640718303-2", "name": "测试参数三", "alias": "p3"}], "scoreSegments": [20, 40, 60], "scoringMethod": [], "fuzzyMatrixData": [{"nodeId": "node-1754640702823", "values": ["12", "23", "33"], "nodeName": "客户满意度"}, {"nodeId": "node-1754640704585", "values": ["11", "22", "54"], "nodeName": "市场占有率"}, {"nodeId": "node-1754640706771", "values": ["5", "56", "77"], "nodeName": "测试序号"}], "selectedAlgorithm": "expert", "normalizationParams": {"d": 0, "k": 1, "mu": 0.5, "std": 1, "mean": 0, "x_max": 0, "x_min": 0, "upDown": 0, "x_list": ["2", "21"], "y_list": ["2", "2"], "decimal": 2}, "normalizationAlgorithm": "gaussian_mapping", "selectedAnalysisMethod": "ahp"}, "node-1754640702823": {"code": "custom-1-1", "label": "客户满意度", "weight": 0, "formula": "", "category": "", "updateTime": 1754640784426, "description": "客户满意度评分指标", "expertScore": 90, "businessRule": "", "childWeights": {}, "customWeight": 0, "parameterList": [], "scoringMethod": "expert", "selectedAlgorithm": "weighted", "normalizationParams": {"d": 0, "k": 1, "mu": 0.5, "std": 1, "mean": 0, "x_max": 0, "x_min": 0, "upDown": 0, "x_list": ["2", "21"], "y_list": ["2", "2"], "decimal": 2}, "normalizationAlgorithm": "gaussian_mapping", "selectedAnalysisMethod": "ahp"}, "node-1754640704585": {"code": "custom-1-2", "label": "市场占有率", "weight": 0, "formula": "", "category": "", "updateTime": 1754640806582, "description": "产品市场占有率指标", "expertScore": 100, "businessRule": "", "childWeights": {}, "customWeight": 0, "parameterList": [], "scoringMethod": "expert", "selectedAlgorithm": "weighted", "normalizationParams": {"d": 0, "k": 1, "mu": 0.5, "std": 1, "mean": 0, "x_max": 0, "x_min": 0, "upDown": 0, "x_list": ["2", "21"], "y_list": ["2", "2"], "decimal": 2}, "normalizationAlgorithm": "segmentation_liner_mapping", "selectedAnalysisMethod": "ahp"}, "node-1754640706771": {"code": 6, "label": "测试序号", "weight": 0, "formula": "p1-p2", "category": "", "updateTime": 1754725426177, "dataSources": {"param-1754640807343-0": {"dataSource": 2, "resultType": "get_median", "updateTime": 1754640817168, "filterConditions": [{"field": 3, "value": "1", "operator": "greater_than"}], "percentageCondition": ""}, "param-1754640807343-1": {"dataSource": 3, "resultType": "get_sum", "updateTime": 1754725423384, "filterConditions": [{"field": 3, "value": "1", "operator": "equals"}], "percentageCondition": ""}}, "description": "测试", "expertScore": 100, "businessRule": "", "childWeights": {}, "customWeight": 0, "parameterList": [{"id": "param-1754640807343-0", "name": "参数一", "alias": "p1"}, {"id": "param-1754640807343-1", "name": "参数二", "alias": "p2"}], "scoringMethod": "formula", "selectedAlgorithm": "weighted", "normalizationParams": {"d": 0, "k": 1, "mu": 0.5, "std": 1, "mean": 0, "x_max": 0, "x_min": 0, "upDown": 0, "x_list": ["2", "21"], "y_list": ["2", "2"], "decimal": 2}, "normalizationAlgorithm": "gaussian_mapping", "selectedAnalysisMethod": "ahp"}}, "workflowType": 1}


class SystemCalcClass():
    """
    用于指标计算类
    """

    @staticmethod
    def calc(tree_data, db_engine):
        data_id = tree_data['workflowType']
        data_type_dict, row_data_list,data_name,data_createTime = SystemCalcClass.get_db_data(db_engine,data_id)
        # 获取去node节点的详情数据
        node_details = tree_data["nodeDetails"]
        # 获取交联关系
        node_edges = tree_data["graphData"]["edges"]
        # 根据连线关系组织树结构
        tree_data = SystemCalcClass.build_tree(node_edges)
        # 获取树结构
        results = SystemCalcClass.calculate_tree_v2(tree_data[0], node_details,data_type_dict, row_data_list)
        return results,tree_data,node_details,data_name,data_createTime

    @staticmethod
    def build_tree(data, source_key="source", target_key="target"):
        """
        将父子关系数组转换为树结构

        Args:
            data: 包含父子关系的字典列表
            source_key: 父节点字段名
            target_key: 子节点字段名

        Returns:
            树结构的列表（支持多棵树）
        """
        # 创建节点映射表
        nodes = {}
        # 第一次遍历：创建所有节点
        for item in data:
            parent = item[source_key]
            child = item[target_key]
            if parent not in nodes:
                nodes[parent] = {"id": parent, "children": []}
            if child not in nodes:
                nodes[child] = {"id": child, "children": []}
        # 第二次遍历：构建父子关系
        children_ids = set()
        for item in data:
            parent = item[source_key]
            child = item[target_key]
            nodes[parent]["children"].append(nodes[child])
            children_ids.add(child)
        # 找出根节点（所有节点中不是任何子节点的）
        root_ids = set(nodes.keys()) - children_ids
        # 构建最终的树结构
        trees = [nodes[root_id] for root_id in root_ids]
        return trees

    @staticmethod
    def calculate_tree_v2(node, node_detail_dict,data_type_dict, row_data_list):
        """
        递归计算树结构中每个节点的值，并返回包含所有节点结果的字典

        :param node: 当前节点（字典格式，包含calculation_func字段）
        :return: 字典，key为节点ID，value为计算结果
        """
        result_dict = {}

        if not node['children']:
            # 叶子节点 表示没有子节点，因此有两种方式，一种是专家打分法，另外一种是绑定数据源进行取值
            node_id = node['id']
            node_detail = node_detail_dict[node_id]
            if node_detail['scoringMethod'] == "expert":  # 表示专家打分
                value = float(node_detail["expertScore"])
                result_dict[node['id']] = value
                return result_dict
            else:  # 表示数据源
                # print(node_detail_dict[node_id])
                formula = node_detail["formula"]  # 获取公式

                # 获取公式变量列表
                parameterList = node_detail["parameterList"]
                # 提取公式变量字典
                alias_dict = {}
                for parameter in parameterList:
                    paramter_id = parameter["id"]  # 变量id
                    alias = parameter["alias"]  # 公式变量
                    # 获取该变量的数据源
                    print("----",node_detail["dataSources"])
                    parameter_dict = node_detail["dataSources"][paramter_id]
                    # dataSource 数据源id   filterConditions  筛选条件   percentageCondition  统计占比的值
                    # 取值调用函数得出值
                    print("指标信息",node_detail)
                    result_data = SystemCalcClass.sum_value(row_data_list[parameter_dict["InferentialListValue"]], data_type_dict[parameter_dict["InferentialListValue"]],parameter_dict["resultType"], parameter_dict["filterConditions"], parameter_dict["dataSource"], parameter_dict["percentageCondition"])
                    alias_dict[alias] = result_data
                # 进行公式计算
                try:

                    result = ne.evaluate(formula, alias_dict)
                except:
                    result = 0
                # 进行归一化处理
                print("计算出的结果",result,alias_dict)
                normalize_result = SystemCalcClass.calc_normalize_func(node_detail,result)
                print("归一化结果", normalize_result)
                # 对结果进行赋值
                result_dict[node['id']] = normalize_result
                return result_dict

        # 递归计算所有子节点的值并收集结果
        child_results = {}
        child_values = []
        for child in node['children']:
            child_dict = SystemCalcClass.calculate_tree_v2(child, node_detail_dict,data_type_dict, row_data_list)
            child_results.update(child_dict)
            child_values.append(child_dict[child['id']])  # 直接从子节点的结果中获取值
        # 进行指标计算值
        ifSuccess, finalResult, errorInfo = SystemCalcClass.item_calc_func(node_detail_dict[node['id']], child_results)
        if ifSuccess:
            result_dict[node['id']] = finalResult
        else:
            result_dict[node['id']] = 0
        # 合并子节点结果
        result_dict.update(child_results)

        return result_dict

    @staticmethod
    def sum_value(data_list, data_type_dict,result_type, filterConditions, item, percentageCondition):
        """
        :param data_list: 原始数据
        :param data_type_dict: 原始数据对应字典集合
        :param result_type: 求值方式
        :param filterConditions: 筛选条件
        :param item: 取的列
        :param percentageCondition: 统计占比的值
        :return:
        """
        # 定义符号字典
        comparison_dict = {
            "equals": "=",
            "not_equals": "!=",
            "greater_than": ">",
            "less_than": "<",
            "greater_equal": ">=",
            "less_equal": "<=",
            "is_null": "IS NULL",
            "is_not_null": "IS NOT NULL",
            "contains": "LIKE",
            "not_contains": "NOT LIKE",
        }
        # 根据原始数据，以及筛选条件，去除新的集合
        conditions = {}
        for info in filterConditions:
            if data_type_dict[int(info["field"])]["col_field_name"] not in conditions.keys():
                conditions[data_type_dict[int(info["field"])]["col_field_name"]] = []
            # 取出来对应的value值
            data_value = info["value"]
            # 判断字段的数据类型，如果是float或者int以及int类型的数据，将数据转换为float
            if data_type_dict[int(info["field"])]["col_type"] == "int" or data_type_dict[int(info["field"])]["col_type"] == "float" or data_type_dict[int(info["field"])]["col_type"] == "date":
                data_value = float(data_value)
            conditions[data_type_dict[int(info["field"])]["col_field_name"]].append([comparison_dict[info["operator"]],data_value])
        new_data_list = SystemCalcClass.data_query(data_list,conditions)
        # 根据字段将筛选后的结果进行去字段的数组
        print(data_type_dict)
        item_value = data_type_dict[item]["col_field_name"]
        results_data_list = [i[item_value] for i in new_data_list]
        result = 0
        if not results_data_list:
            result = 0
        else:
            # 进行数据取值
            try:
                if result_type == "get_sum":
                    result = ArrayStatisticsClass.get_sum(results_data_list)
                elif result_type == "get_mean":
                    result = ArrayStatisticsClass.get_mean(results_data_list)
                elif result_type == "get_median":
                    result = ArrayStatisticsClass.get_median(results_data_list)
                elif result_type == "get_max":
                    result = ArrayStatisticsClass.get_max(results_data_list)
                elif result_type == "get_min":
                    result = ArrayStatisticsClass.get_min(results_data_list)
                elif result_type == "get_variance":
                    result = ArrayStatisticsClass.get_variance(results_data_list)
                elif result_type == "get_std":
                    result = ArrayStatisticsClass.get_std(results_data_list)
                elif result_type == "get_mode":
                    result = ArrayStatisticsClass.get_mode(results_data_list)
                elif result_type == "get_product":
                    result = ArrayStatisticsClass.get_product(results_data_list)
                elif result_type == "get_sum_abs":
                    result = ArrayStatisticsClass.get_sum_abs(results_data_list)
                elif result_type == "get_mean_abs":
                    result = ArrayStatisticsClass.get_mean_abs(results_data_list)
                elif result_type == "get_mse":
                    result = ArrayStatisticsClass.get_mse(results_data_list)
                elif result_type == "get_count":
                    result = ArrayStatisticsClass.get_count(results_data_list)
                elif result_type == "get_percentage":
                    if data_type_dict[item]["col_type"] == "int" or data_type_dict[item]["col_type"] == "float" or data_type_dict[item]["col_type"] == "date":
                        percentageCondition = float(percentageCondition)
                    result = ArrayStatisticsClass.get_percentage(results_data_list,percentageCondition)
            except:
                pass
        return result

    @staticmethod
    def data_query(records, conditions):
        """
        增强版查询函数，支持类似MySQL的LIKE/NOT LIKE操作

        参数:
            records: 字典列表，表示要查询的数据
            conditions: 字典，键是字段名，值是(操作符, 比较值)的元组或列表

        支持的操作符:
            '=': 等于
            '!=': 不等于
            '>': 大于
            '<': 小于
            '>=': 大于等于
            '<=': 小于等于
            'IS NULL': 为空
            'IS NOT NULL': 不为空
            'LIKE': 包含（类似MySQL的LIKE）
            'NOT LIKE': 不包含
            'IN': 包含在列表中
            'NOT IN': 不包含在列表中
        """
        results = []
        for rec in records:
            match = True
            for field, field_conditions in conditions.items():
                # 统一处理条件，无论单个条件还是多个条件
                if isinstance(field_conditions, tuple):
                    field_conditions = [field_conditions]
                # 检查字段是否存在
                if field not in rec:
                    match = False
                    break
                field_value = rec[field]
                # 处理该字段的所有条件
                for op, value in field_conditions:
                    try:
                        if op == '=':
                            if field_value != value:
                                match = False
                        elif op == '!=':
                            if field_value == value:
                                match = False
                        elif op == '>':
                            if field_value is None or value is None or field_value <= value:
                                match = False
                        elif op == '<':
                            if field_value is None or value is None or field_value >= value:
                                match = False
                        elif op == '>=':
                            if field_value is None or value is None or field_value < value:
                                match = False
                        elif op == '<=':
                            if field_value is None or value is None or field_value > value:
                                match = False
                        elif op == 'IS NULL':
                            if field_value is not None:
                                match = False
                        elif op == 'IS NOT NULL':
                            if field_value is None:
                                match = False
                        elif op == 'LIKE':
                            if not isinstance(field_value, str) or not isinstance(value,str) or value not in field_value:
                                match = False
                        elif op == 'NOT LIKE':
                            if isinstance(field_value, str) and isinstance(value, str) and value in field_value:
                                match = False
                        elif op == 'IN':
                            if field_value not in value:
                                match = False
                        elif op == 'NOT IN':
                            if field_value in value:
                                match = False
                        else:
                            raise ValueError(f"不支持的运算符: {op}")
                    except TypeError:
                        # 处理类型不匹配的情况
                        match = False
                    if not match:
                        break
                if not match:
                    break

            if match:
                results.append(rec)
        return results

    @staticmethod
    def item_calc_func(node_detail, child_results):
        """
        指标函数调用
        :return:
        """
        weight_dict = SystemCalcClass.get_item_weight(node_detail)
        if node_detail["selectedAlgorithm"] == "weighted":  # 表示加权平均法
            # 取出来ahp的参数的数值  组织成{'item_value': 5, 'item_weight': 0.5},
            test_data = []
            for node_id, weight in weight_dict.items():
                try:
                    test_data.append(
                        {"item_value": child_results[node_id], "item_weight": weight})
                except:
                    pass
            ifSuccess, finalResult, errorInfo = WeightedMeanClass.ResultCalc(test_data)
            return ifSuccess, finalResult, errorInfo
        elif node_detail["selectedAlgorithm"] == "grey":  # 灰色白化权聚类法
            greyClusteringSegments = node_detail["greyClusteringSegments"]
            greyClusteringData = node_detail["greyClusteringData"]
            # 整理灰色白化权聚类法数据
            s_l_l = greyClusteringSegments
            s_l = []  # 计算结果的值
            l_l = []  # 每一个指标的评分标准
            w_l = []
            for info in greyClusteringData:
                l_l.append(info["ranges"])
                s_l.append(child_results[info["nodeId"]])
                w_l.append(weight_dict[info["nodeId"]])
            ifSuccess, finalResult, errorInfo = GreyClusteringClass.ResultCalc(s_l, s_l_l, l_l, w_l)
            return ifSuccess, finalResult, errorInfo
        elif node_detail["selectedAlgorithm"] == "fuzzy":  # 模糊综合评判法
            scoreSegments = node_detail["scoreSegments"]
            fuzzyMatrixData = node_detail["fuzzyMatrixData"]
            s_l = scoreSegments  # 分数段
            r_l = []  # 指标分数
            w_l = []  # 指标对应权重
            m_m = []  # 隶属度矩阵
            for info in fuzzyMatrixData:
                r_l.append(child_results[info["nodeId"]])
                w_l.append(weight_dict[info["nodeId"]])
                m_m.append([float(i) for i in info["values"]])
            ifSuccess, finalResult, errorInfo = FuzzyAssessmentClass.ResultCalc(r_l, w_l, s_l, m_m)
            return ifSuccess, finalResult, errorInfo
        elif node_detail["selectedAlgorithm"] == "index":  # 幂指数
            test_data = []
            for node_id, weight in weight_dict.items():
                test_data.append(
                    {"item_value": child_results[node_id], "item_weight": weight})
            ifSuccess, finalResult, errorInfo = PowerSeriesClass.ResultCalc(test_data)
            return ifSuccess, finalResult, errorInfo
        elif node_detail["selectedAlgorithm"] == "expert":  # 专家打分法
            return True, node_detail["expertScore"], ''

    @staticmethod
    def get_item_weight(node_detail):
        """
        获取指标的权重
        :param node_detail:
        :return:
        """
        weight_dict = {}
        if node_detail["selectedAnalysisMethod"] == "ahp":  # 层次分析法
            for widget_info in node_detail["ahpWeights"]:
                weight_dict[widget_info["nodeId"]] = widget_info["weight"]
        elif node_detail["selectedAnalysisMethod"] == "CoefficientMethod":  # 变异系数法
            for widget_info in node_detail["CoefficientMethodWeights"]:
                weight_dict[widget_info["nodeId"]] = widget_info["weight"]
        elif node_detail["selectedAnalysisMethod"] == "PcaWeight":  # 主成分分析法
            for widget_info in node_detail["pcaWeights"]:
                weight_dict[widget_info["nodeId"]] = widget_info["weight"]
        elif node_detail["selectedAnalysisMethod"] == "FactorAnalysis":  # 因子分析法
            for widget_info in node_detail["factorWeights"]:
                weight_dict[widget_info["nodeId"]] = widget_info["weight"]
        elif node_detail["selectedAnalysisMethod"] == "EntropyWeight":  # 熵权法
            for widget_info in node_detail["EntropyWeightWeights"]:
                weight_dict[widget_info["nodeId"]] = widget_info["weight"]
        elif node_detail["selectedAnalysisMethod"] == "GreyRelationalAnalysis":  # 灰色关联分析法
            for widget_info in node_detail["greyRelationalWeights"]:
                weight_dict[widget_info["nodeId"]] = widget_info["weight"]
        elif node_detail["selectedAnalysisMethod"] == "DareMethod":  # 环比系数法
            for widget_info in node_detail["dareWeights"]:
                weight_dict[widget_info["nodeId"]] = widget_info["weight"]
        else:  # 直接赋权法  directEmpowerment
            weight_dict = node_detail["childWeights"]
        return weight_dict

    @staticmethod
    def calc_normalize_func(node_detail, finalResult):
        """
        归一化函数调用  分数调整至100分
        :return:
        """
        if node_detail["normalizationAlgorithm"] == "gaussian_mapping":  # 表示高斯函数映射
            mu = node_detail["normalizationParams"]["mu"]
            k = node_detail["normalizationParams"]["k"]
            ifSuccess, result, errorInfo = NormalizeFuncClass.gaussian_mapping(finalResult, mu, k)
            return result * 100
        elif node_detail["normalizationAlgorithm"] == "cauchy_mapping":  # 表示柯西分布
            mu = node_detail["normalizationParams"]["mu"]
            k = node_detail["normalizationParams"]["k"]
            ifSuccess, result, errorInfo = NormalizeFuncClass.cauchy_mapping(finalResult, mu, k)
            return result * 100
        elif node_detail["normalizationAlgorithm"] == "exponential_decay":  # 指数衰减函数
            mu = node_detail["normalizationParams"]["mu"]
            k = node_detail["normalizationParams"]["k"]
            ifSuccess, result, errorInfo = NormalizeFuncClass.exponential_decay(finalResult, mu, k)
            return result * 100
        elif node_detail["normalizationAlgorithm"] == "logistic_variant":  # 辑斯蒂函数变体
            mu = node_detail["normalizationParams"]["mu"]
            k = node_detail["normalizationParams"]["k"]
            ifSuccess, result, errorInfo = NormalizeFuncClass.logistic_variant(finalResult, mu, k)
            return result * 100
        elif node_detail["normalizationAlgorithm"] == "linear_segment":  # 对称线性函数
            mu = node_detail["normalizationParams"]["mu"]
            d = node_detail["normalizationParams"]["d"]
            ifSuccess, result, errorInfo = NormalizeFuncClass.linear_segment(finalResult, mu, d)
            return result * 100
        elif node_detail["normalizationAlgorithm"] == "linear_mapping":  # 单段线性函数
            x_min = node_detail["normalizationParams"]["x_min"]
            x_max = node_detail["normalizationParams"]["x_max"]
            upDown = node_detail["normalizationParams"]["upDown"]
            ifSuccess, result, errorInfo = NormalizeFuncClass.linear_mapping(finalResult, x_min, x_max, int(upDown))
            return result * 100
        elif node_detail["normalizationAlgorithm"] == "zero_one_mapping":  # 开关函数
            mu = node_detail["normalizationParams"]["mu"]
            upDown = node_detail["normalizationParams"]["upDown"]
            ifSuccess, result, errorInfo = NormalizeFuncClass.zero_one_mapping(finalResult, mu, int(upDown))
            return result * 100
        elif node_detail["normalizationAlgorithm"] == "segmentation_liner_mapping":  # 线性分段函数
            x_list = node_detail["normalizationParams"]["x_list"]
            y_list = node_detail["normalizationParams"]["y_list"]
            ifSuccess, result, errorInfo = NormalizeFuncClass.segmentation_liner_mapping(finalResult, x_list, y_list)
            return result
        elif node_detail["normalizationAlgorithm"] == "segmentation_mapping":  # 台阶分段函数
            x_list = node_detail["normalizationParams"]["x_list"]
            y_list = node_detail["normalizationParams"]["y_list"]
            ifSuccess, result, errorInfo = NormalizeFuncClass.segmentation_mapping(finalResult, x_list, y_list)
            return result
        else:
            return finalResult

    @staticmethod
    def get_db_data(db_engine,data_id):
        """
        读取数据库数据
        :return:
        """
        data_type_dict = {}
        row_data_list = {}
        session = sessionmaker(bind=db_engine)()
        print("数据源集合ID",data_id)
        with session.begin():
            collect_info = session.query(AccessModel.BasicCollectTable).where(AccessModel.BasicCollectTable.id == data_id).first()
            collect_name = collect_info.name
            collect_time = collect_info.createTime
            system_info_list = session.query(AccessModel.BasicTable).where(AccessModel.BasicTable.collect_id == data_id).all()
            for system_info in system_info_list:
                if system_info.id not in data_type_dict.keys():
                    data_type_dict[system_info.id] = {}
                if system_info.id not in row_data_list.keys():
                    row_data_list[system_info.id] = []
                # 获取数据的字典
                data_type_info = session.query(AccessModel.BasicDictTable).where(AccessModel.BasicDictTable.basic_id == system_info.id).all()
                # 新建一个字典，将数据格式统一化
                data_type_field = {}
                for data_type in data_type_info:
                    data_type_dict[system_info.id][data_type.id] = {"col_field_name": data_type.col_field_name, "col_type": data_type.col_type}
                    data_type_field[data_type.col_field_name] = data_type.col_type
                # 获取原始数据  -- 首先获取表对象
                model = AccessModel.get_table_model(db_engine,"BasicRowDataTable",system_info.row_data_uuid)
                row_info_list = session.query(model).all()
                for row_info in row_info_list:
                    row_data = row_info.row_data
                    for k, v in row_data.items():
                        if data_type_field[k] == "int" or data_type_field[k] == "float" or data_type_field[k] == "date":
                            row_data[k] = float(v)
                    row_data_list[system_info.id].append(row_data)
        print("查询出来的数据",data_type_dict)
        return data_type_dict, row_data_list,collect_name,collect_time



if __name__ == "__main__":
    # results = SystemCalcClass.calc(a,db_engine)
    # print(results)
    pass
