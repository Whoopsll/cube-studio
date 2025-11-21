# 表示归一化函数
import numpy as np
import math


class NormalizeFuncClass():

    @staticmethod
    def gaussian_mapping(x, mu, k=1.0):
        errorInfo = ""
        result = 0
        ifSuccess = True
        """高斯函数映射"""
        result = np.exp(-k * (x - mu) ** 2)
        return ifSuccess, result, errorInfo

    @staticmethod
    def cauchy_mapping(x, mu, k=1.0):
        errorInfo = ""
        result = 0
        ifSuccess = True
        """柯西分布映射"""
        result = 1 / (1 + k * (x - mu) ** 2)
        return ifSuccess, result, errorInfo

    @staticmethod
    def exponential_decay(x, mu, k=1.0):
        errorInfo = ""
        result = 0
        ifSuccess = True
        """指数衰减函数"""
        result = np.exp(-k * np.abs(x - mu))
        return ifSuccess, result, errorInfo

    @staticmethod
    def logistic_variant(x, mu, k=5.0):
        errorInfo = ""
        result = 0
        ifSuccess = True
        """逻辑斯蒂函数变体"""
        result = 1 / (1 + np.exp(-k * (1 - np.abs(x - mu))))
        return ifSuccess, result, errorInfo

    @staticmethod
    def linear_segment(x, mu, d=1.0):
        """分段线性函数"""
        errorInfo = ""
        result = 0
        ifSuccess = True

        distance = np.abs(x - mu)
        result = np.where(distance > d, 0.0, 1 - (distance / d))
        return ifSuccess, result, errorInfo

    @staticmethod
    def linear_mapping(x, x_min, x_max, upDown):
        """
        单段线性函数
        :param x:
        :param x_min:  最大值
        :param x_max:  最小值
        :param upDown:  增减
        :return:
        """
        errorInfo = ""
        result = 0
        ifSuccess = True
        if upDown >= 0:
            if x >= x_max:
                result = 1
            elif x <= x_min:
                result = 0
            else:
                result = (x - x_min) / (x_max - x_min)
        else:
            if x >= x_max:
                result = 0
            elif x <= x_min:
                result = 1
            else:
                result = (x_max - x) / (x_max - x_min)
        return ifSuccess, result, errorInfo

    @staticmethod
    def zero_one_mapping(x, mu, upDown):
        """
        开关函数
        :param x:
        :param mu: 值
        :param upDown: 增减
        :return:
        """
        errorInfo = ""
        result = 0
        ifSuccess = True
        if upDown >= 0:
            if x >= mu:
                result = 1
            else:
                result = 0
        else:
            if x <= mu:
                result = 1
            else:
                result = 0
        return ifSuccess, result, errorInfo

    @staticmethod
    def segmentation_liner_mapping(x, x_list, y_list):
        """
        线性分段函数
        :param x:输入x值
        :param x_list:x值列表
        :param y_list:y值列表
        :return:是否成功，y值，错误信息
        """
        errorInfo = ""
        result = 0
        ifSuccess = False
        if len(x_list) != len(y_list):
            errorInfo = "x与y值列表长度不一致！"
            return ifSuccess, result, errorInfo
        if not all(x_list[i] <= x_list[i + 1] for i in range(len(x_list) - 1)):
            errorInfo = "x_list必须按升序排列！"
            return ifSuccess, result, errorInfo
        if min(y_list) < 0:
            errorInfo = "存在小于0的y值！"
            return ifSuccess, result, errorInfo

        # 处理x小于最小分段点的情况
        if x <= x_list[0]:
            result = y_list[0]
            ifSuccess = True
        # 处理x大于最大分段点的情况
        elif x >= x_list[-1]:
            result = y_list[-1]
            ifSuccess = True
        else:
            for i in range(len(x_list) - 1):
                if x_list[i] <= x <= x_list[i + 1]:
                    # 计算线性插值
                    slope = (y_list[i + 1] - y_list[i]) / (x_list[i + 1] - x_list[i])
                    result = y_list[i] + slope * (x - x_list[i])
                    ifSuccess = True
        result = result
        return ifSuccess, result, errorInfo

    @staticmethod
    def segmentation_mapping(x, x_list, y_list):
        """
        台阶分段函数
        x[i]<x<x[i+1] -> y = y[i]
        :param x:输入x值
        :param x_list:x值列表
        :param y_list:y值列表
        :return:是否成功，y值，错误信息
        """
        errorInfo = ""
        result = 0
        ifSuccess = False
        if len(x_list) != len(y_list):
            errorInfo = "x与y值列表长度不一致！"
            return ifSuccess, result, errorInfo
        if not all(x_list[i] <= x_list[i + 1] for i in range(len(x_list) - 1)):
            errorInfo = "x_list必须按升序排列！"
            return ifSuccess, result, errorInfo
        if min(y_list) < 0:
            errorInfo = "存在小于0的y值！"
            return ifSuccess, result, errorInfo

        # 处理x小于最小分段点的情况
        if x <= x_list[0]:
            result = y_list[0]
            ifSuccess = True
        # 处理x大于最大分段点的情况
        elif x >= x_list[-1]:
            result = y_list[-1]
            ifSuccess = True
        else:
            for i in range(len(x_list) - 1):
                if x_list[i] <= x <= x_list[i + 1]:
                    # 计算线性插值
                    result = y_list[i]
                    ifSuccess = True
        result = result
        return ifSuccess, result, errorInfo


if __name__ == "__main__":
    print(NormalizeFuncClass.gaussian_mapping(100,100,1))
    import matplotlib.pyplot as plt
    x1 = np.linspace(start=-10, stop=10, num=1000)
    xx = [0, 1, 4, 5, 6, 9]
    yy = [0, 5, 2, 3, 2, 5]
    y1 = []
    y2 = []
    for ii in x1:
        r, yyy, ss = NormalizeFuncClass.segmentation_mapping(ii, xx, yy)
        y1.append(yyy)
    for ii in x1:
        r, yyy, ss = NormalizeFuncClass.segmentation_liner_mapping(ii, xx, yy)
        y2.append(yyy)
    plt.plot(x1, y1)
    plt.plot(x1, y2)
    plt.plot(xx, yy)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Function Curve')
    plt.show()
    # print(NormalizeFuncClass.segmentation_mapping(7, xx, yy))
