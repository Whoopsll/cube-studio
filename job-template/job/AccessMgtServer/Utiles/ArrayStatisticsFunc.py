"""
用于取一个值的算法说明
"""

import numpy as np
from scipy import stats



# get_sum  求和
# get_mean  算术平均数
# get_median  中位数
# get_max  最大值
# get_min  最小值
# get_variance  方差
# get_std   标准差
# get_mode  众数
# get_product  乘积
# get_sum_abs  绝对值就和
# get_mean_abs  绝对值平均
# get_mse  均方差
# get_count  统计个数
# get_percentage   统计特定值占比

class ArrayStatisticsClass:

    @staticmethod
    def get_sum(arr):
        """求和"""
        return np.sum(arr)

    @staticmethod
    def get_mean(arr):
        """算术平均数"""
        return np.mean(arr)

    @staticmethod
    def get_median(arr):
        """中位数"""
        return np.median(arr)

    @staticmethod
    def get_max(arr):
        """最大值"""
        return np.max(arr)

    @staticmethod
    def get_min(arr):
        """最小值"""
        return np.min(arr)

    @staticmethod
    def get_variance(arr):
        """方差"""
        return np.var(arr)

    @staticmethod
    def get_std(arr):
        """标准差"""
        return np.std(arr)

    @staticmethod
    def get_mode(arr):
        """众数（返回第一个出现的众数）"""
        return stats.mode(arr, keepdims=True).mode[0]

    @staticmethod
    def get_product(arr):
        """乘积"""
        return np.prod(arr)

    @staticmethod
    def get_sum_abs(arr):
        """绝对值求和"""
        return np.sum(np.abs(arr))

    @staticmethod
    def get_mean_abs(arr):
        """绝对值平均"""
        return np.mean(np.abs(arr))

    @staticmethod
    def get_mse(arr):
        """均方差（元素平方的均值）"""
        return np.mean(arr ** 2)

    @staticmethod
    def get_count(arr):
        """统计个数"""
        return len(arr)

    @staticmethod
    def get_percentage(arr, target_value):
        """统计特定值的占比"""
        return np.sum(arr == target_value) / len(arr)
