"""
因子分析法
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import FactorAnalysis
from sklearn.decomposition import PCA

class FactorAnalysisClass():
    @staticmethod
    def factor_analysis(data, n_factors=None):
        """
        基于因子分析法计算变量权重（兼容旧版本scikit-learn）

        参数:
        data: DataFrame，包含原始数据（行=样本，列=变量）
        n_factors: 因子个数，若为None则自动根据特征值>1确定

        返回:
        weights: 各变量的权重Series
        """
        # 1. 数据标准化
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data)

        # 2. 确定因子个数（若未指定）
        if n_factors is None:
            # 用PCA的特征值判断
            pca = PCA()
            pca.fit(data_scaled)
            eigenvalues = pca.explained_variance_
            n_factors = sum(eigenvalues > 1)  # 特征值大于1的因子个数
            print(f"自动确定因子个数: {n_factors}")

        # 3. 因子分析（移除method参数，兼容旧版本）
        fa = FactorAnalysis(n_components=n_factors, rotation='varimax')
        fa.fit(data_scaled)

        # 4. 获取因子载荷矩阵和方差贡献率
        loadings = pd.DataFrame(
            fa.components_.T,  # 转置后行=变量，列=因子
            index=data.columns,
            columns=[f'因子{i + 1}' for i in range(n_factors)]
        )

        # 计算各因子的方差贡献率（近似）
        factor_var = np.sum(loadings ** 2, axis=0)
        factor_contrib = factor_var / np.sum(factor_var)  # 因子贡献率（归一化）

        # 5. 计算权重：因子载荷绝对值 × 因子贡献率，再归一化
        weighted_loadings = np.abs(loadings) * factor_contrib.values
        weights = weighted_loadings.sum(axis=1)  # 每个变量的总权重
        weights = weights / weights.sum()  # 归一化到总和为1

        return weights, loadings, factor_contrib


# 示例：计算5个变量的权重
if __name__ == "__main__":
    # 生成示例数据（100个样本，5个变量）
    data = pd.DataFrame({
        '变量1': np.random.normal(50, 10, 3),
        '变量2': np.random.normal(60, 12, 3),
        '变量3': np.random.normal(55, 8, 3),
        '变量4': np.random.normal(70, 15, 3),
        '变量5': np.random.normal(65, 11, 3)
    })

    # 计算权重
    weights, loadings, contrib = FactorAnalysisClass.factor_analysis(data)

    # 输出结果
    print("因子载荷矩阵:\n", loadings.round(4))
    print("\n因子贡献率:", contrib.round(4).to_dict())
    print("\n各变量权重:")
    for var, w in weights.items():
        print(f"{var}: {w:.4f} ({w * 100:.2f}%)")
    print(f"\n权重总和: {weights.sum():.4f}")
