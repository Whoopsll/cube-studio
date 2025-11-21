"""
变异系数法
"""
import numpy as np
import pandas as pd


class CoefficientMethodClass():
    @staticmethod
    def coefficient_of_variation_method(data):
        """
        变异系数法计算各指标权重

        参数:
        data: DataFrame或numpy数组, 每行代表一个样本, 每列代表一个指标

        返回:
        weights: 各指标的权重
        cv: 各指标的变异系数
        """
        # 确保输入是numpy数组
        if isinstance(data, pd.DataFrame):
            data = data.values

        # 计算各指标的平均值
        mean = np.mean(data, axis=0)

        # 计算各指标的标准差
        std = np.std(data, axis=0, ddof=1)  # 使用样本标准差

        # 计算变异系数 (标准差/平均值)
        cv = std / mean

        # 计算权重 (变异系数归一化)
        weights = cv / np.sum(cv)

        return weights


# 示例用法
if __name__ == "__main__":
    # 生成示例数据 (5个样本, 3个指标)
    data = pd.DataFrame({
        '指标1': [1,2,3,4,5],
        '指标2': [1,2,3,4,5],
        '指标3': [1,2,3,4,5]
    })

    print("原始数据:")
    print(data)
    print("\n")

    # 计算权重和变异系数
    weights = CoefficientMethodClass.coefficient_of_variation_method(data)

    # 输出结果
    result = pd.DataFrame({
        '指标': data.columns,
        '权重': weights
    })

    print("变异系数及权重计算结果:")
    print(result)
