"""
灰色关联分析法
"""
import numpy as np


class GreyRelationalAnalysisClass:
    def __init__(self, rho=0.5):
        """
        灰色关联分析模型初始化
        参数:
            rho: 分辨系数，默认0.5
        """
        self.rho = rho
        self.weights = None
        self.standardized_data = None
        self.reference_sequence = None

    def _standardize(self, data, index_types):
        """
        对每个指标进行标准化处理
        参数:
            data: 输入数据，形状为(n_samples, n_indicators)
            index_types: 指标类型列表，'positive'或'negative'
        返回:
            标准化后的数据
        """
        n_samples, n_indicators = data.shape
        standardized = np.zeros_like(data, dtype=np.float64)

        for i in range(n_indicators):
            # 提取第i个指标的所有样本值
            indicator_values = data[:, i]
            max_val = np.max(indicator_values)
            min_val = np.min(indicator_values)
            diff = max_val - min_val

            # 处理极端情况（所有值相同）
            if diff == 0:
                standardized[:, i] = 0.5  # 赋予中间值
                continue

            # 根据指标类型标准化
            if index_types[i] == 'positive':
                # 正向指标：值越大越好
                standardized[:, i] = (indicator_values - min_val) / diff
            else:
                # 负向指标：值越小越好
                standardized[:, i] = (max_val - indicator_values) / diff

        return standardized

    def calculate_weights(self, data, index_types):
        """
        计算各指标权重
        参数:
            data: 数据矩阵，shape=(n_samples, n_indicators)
                  每行是一个样本，每列是一个指标的多个观测值
            index_types: 长度为n_indicators的列表，指定每个指标类型
        返回:
            各指标的权重数组
        """
        # 数据标准化
        self.standardized_data = self._standardize(data, index_types)
        n_samples, n_indicators = self.standardized_data.shape

        # 确定参考序列（每个指标的理想最优值）
        self.reference_sequence = np.ones(n_indicators)

        # 计算每个样本与参考序列的绝对差
        abs_differences = np.abs(self.standardized_data - self.reference_sequence)

        # 计算全局最小差和最大差
        min_diff = np.min(abs_differences)
        max_diff = np.max(abs_differences)

        # 计算关联系数
        correlation_coefficients = (min_diff + self.rho * max_diff) / \
                                   (abs_differences + self.rho * max_diff)

        # 计算每个指标的平均关联度
        indicator_correlation = np.mean(correlation_coefficients, axis=0)

        # 归一化得到权重
        self.weights = indicator_correlation / np.sum(indicator_correlation)

        return self.weights


# 示例用法
if __name__ == "__main__":
    # 示例数据：6个样本，5个指标
    # 数据格式：每行是一个样本的观测值，每列是一个指标的多个值
    data = np.array([
        [85, 90, 78, 92, 88],  # 样本1的5个指标值
        [82, 88, 80, 95, 85],  # 样本2的5个指标值
        [90, 85, 82, 90, 92],  # 样本3的5个指标值
        [88, 92, 76, 88, 90],  # 样本4的5个指标值
        [86, 89, 85, 94, 87],  # 样本5的5个指标值
        [89, 87, 81, 91, 89]  # 样本6的5个指标值
    ])

    # 指标类型：5个指标分别为正向、正向、正向、正向、正向
    # 可根据实际情况修改为'negative'
    index_types = ['positive', 'positive', 'positive', 'positive', 'positive']

    # 计算权重
    gra = GreyRelationalAnalysisClass(rho=0.5)
    weights = gra.calculate_weights(data, index_types)
    print(weights)