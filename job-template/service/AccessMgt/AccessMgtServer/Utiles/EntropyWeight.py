import numpy as np
import pandas as pd

"""
    熵权法
"""


class EntropyWeightClass():
    @staticmethod
    def entropy_weight(data):
        """
        计算熵权

        参数:
        data: DataFrame或numpy数组，每行代表一个样本，每列代表一个指标

        返回:
        weights: 各指标的权重
        scores: 各样本的综合得分
        """
        # 将数据转换为numpy数组
        if isinstance(data, pd.DataFrame):
            data = data.values

        # 数据归一化（正向指标）
        # 如果存在负向指标，需要先进行正向化处理
        min_val = np.min(data, axis=0)
        max_val = np.max(data, axis=0)
        normalized_data = (data - min_val) / (max_val - min_val + 1e-10)  # 避免除零

        # 计算第j个指标下第i个样本的比重p_ij
        p = normalized_data / (np.sum(normalized_data, axis=0) + 1e-10)  # 避免除零

        # 计算熵值e_j
        m, n = data.shape  # m为样本数，n为指标数
        e = -np.sum(p * np.log(p + 1e-10) / np.log(m), axis=0)  # 避免log(0)

        # 计算信息熵冗余度d_j
        d = 1 - e

        # 计算权重w_j
        weights = d / np.sum(d)

        return weights


# 示例用法
if __name__ == "__main__":
    # 创建示例数据（4个样本，3个指标）
    data = pd.DataFrame({
        '指标1': [80, 90, 70, 60],
        '指标2': [0.8, 0.9, 0.2, 0.6],
        '指标3': [800, 900, 700, 600]
    })

    print("原始数据:")
    print(data)

    # 计算熵权和得分
    weights = EntropyWeightClass.entropy_weight(data)

    print("\n各指标权重:")
    for i, col in enumerate(data.columns):
        print(f"{col}: {weights[i]:.4f}")
