"""
主成分分析法
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

class PcaWeightClass():
    @staticmethod
    def pca_weights(data, n_components=None):
        """
        基于主成分分析法计算变量权重

        参数:
        data: DataFrame，包含原始数据（行=样本，列=变量）
        n_components: 主成分个数，若为None则保留所有主成分

        返回:
        weights: 各变量的权重Series
        components: 主成分矩阵
        explained_variance_ratio: 各主成分的方差贡献率
        """
        # 1. 数据标准化
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data)

        # 2. 主成分分析
        pca = PCA(n_components=n_components)
        pca.fit(data_scaled)

        # 3. 获取主成分载荷（特征向量）和方差贡献率
        loadings = pd.DataFrame(
            pca.components_.T,  # 转置后行=变量，列=主成分
            index=data.columns,
            columns=[f'主成分{i + 1}' for i in range(pca.n_components_)]
        )

        # 主成分的方差贡献率
        explained_variance_ratio = pca.explained_variance_ratio_

        # 4. 计算权重：以主成分载荷的绝对值为基础，结合方差贡献率加权
        weighted_loadings = np.abs(loadings) * explained_variance_ratio
        weights = weighted_loadings.sum(axis=1)  # 每个变量的总权重
        weights = weights / weights.sum()  # 归一化到总和为1

        return weights, loadings, explained_variance_ratio


# 示例：计算5个变量的权重
if __name__ == "__main__":
    # 生成示例数据（100个样本，5个变量）
    np.random.seed(42)
    data = pd.DataFrame({
        '变量1': np.random.normal(50, 10, 100),
        '变量2': np.random.normal(60, 12, 100) + 0.7 * np.random.normal(50, 10, 100),
        '变量3': np.random.normal(55, 8, 100) + 0.6 * np.random.normal(60, 12, 100),
        '变量4': np.random.normal(70, 15, 100),
        '变量5': np.random.normal(65, 11, 100) + 0.8 * np.random.normal(70, 15, 100)
    })

    # 计算权重，保留特征值大于1的主成分
    weights, loadings, variance_ratio = PcaWeightClass.pca_weights(data)

    # 输出结果
    print("主成分载荷矩阵:\n", loadings.round(4))
    print("\n各主成分方差贡献率:", [f"{ratio:.4f}" for ratio in variance_ratio])
    print(f"累计方差贡献率: {sum(variance_ratio):.4f}")
    print("\n各变量权重:")
    for var, w in weights.items():
        print(f"{var}: {w:.4f} ({w * 100:.2f}%)")
    print(f"\n权重总和: {weights.sum():.4f}")
