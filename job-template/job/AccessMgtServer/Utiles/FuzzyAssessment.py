"""
模糊综合评判法
"""
import numpy as np


class FuzzyAssessmentClass():

    @staticmethod
    def is_monotonic(arr):
        # 初始化两个标志，分别表示是否可能递增或递减
        is_increasing = True
        is_decreasing = True

        # 遍历数组检查元素变化
        for i in range(len(arr) - 1):
            if arr[i] > arr[i + 1]:
                is_increasing = False  # 出现递减，排除递增可能
            if arr[i] < arr[i + 1]:
                is_decreasing = False  # 出现递增，排除递减可能

        # 只要有一个标志为True，就是单调数组
        return is_increasing or is_decreasing

    @staticmethod
    def ResultCalc(result_list, weight_list, score_list, membership_matrix):
        """
        :param weight_list: 权重列表
        :param result_list: 计算得出的指标值列表
        :param score_list: 用户设定的分数列表
        :param membership_matrix: 隶属度矩阵
        :return:
        """
        ifSuccess = False
        finalResult = 0.0
        errorInfo = ""
        result_num = len(result_list)
        weight_num = len(weight_list)
        score_num = len(score_list)
        matrix_score_num = len(membership_matrix)  # 行数
        sum_weight = sum(weight_list)
        real_weight_list = []

        # 分数最大值为1
        # real_score_list = [ii / max(score_list) for ii in score_list]
        real_score_list = [ii for ii in score_list]

        # 校验权重并重新归一化
        for weight in weight_list:
            if weight < 0:
                errorInfo = "存在权重值小于零！"
                return ifSuccess, finalResult, errorInfo
            real_weight_list.append(weight / sum_weight)

        if result_num != weight_num:
            errorInfo = "指标结果数量与指标权重数量不一致！"
            return ifSuccess, finalResult, errorInfo

        if result_num != matrix_score_num:
            errorInfo = "指标结果数量与隶属度矩阵维度不符！"
            return ifSuccess, finalResult, errorInfo

        for i in range(matrix_score_num - 1):
            if (len(membership_matrix[i])) != score_num:
                errorInfo = "隶属度矩阵维度与分数维度不一致！"
                return ifSuccess, finalResult, errorInfo
            if not (FuzzyAssessmentClass.is_monotonic(membership_matrix[i])):
                errorInfo = "隶属度矩阵不单调！"
                return ifSuccess, finalResult, errorInfo

        # 计算各指标隶属度
        real_membership_matrix = []
        for i in range(result_num):
            temp_matrix = [0 for ii in range(score_num)]
            matrix_i = membership_matrix[i]
            result_i = result_list[i]
            if result_i < matrix_i[0] < matrix_i[1]:
                temp_matrix[0] = 1
            elif result_i > matrix_i[0] > matrix_i[1]:
                temp_matrix[0] = 1
            elif matrix_i[-2] > matrix_i[-1] > result_i:
                temp_matrix[-1] = 1
            elif matrix_i[-2] < matrix_i[-1] < result_i:
                temp_matrix[-1] = 1
            else:
                for j in range(len(matrix_i) - 1):
                    if matrix_i[j] < result_i < matrix_i[j + 1] or matrix_i[j] > result_i > matrix_i[j + 1]:
                        temp_matrix[j] = 1 - (abs(result_i - matrix_i[j]) / abs(matrix_i[j + 1] - matrix_i[j]))
                        temp_matrix[j+1] = (abs(result_i - matrix_i[j]) / abs(matrix_i[j + 1] - matrix_i[j]))
                        break
                    if matrix_i[j] == result_i:
                        temp_matrix[j] = 1
                        break
                    if matrix_i[j+1] == result_i:
                        temp_matrix[j+1] = 1
            real_membership_matrix.append(temp_matrix)
        np_membership_matrix = np.array(real_membership_matrix)

        # 分数列表
        np_score_list = np.array(real_score_list)
        np_score_list = np_score_list.reshape(1, len(np_score_list))
        # 权重列表
        np_weight_list = np.array(real_weight_list)
        np_weight_list = np_weight_list.reshape(1, len(real_weight_list))

        score_membership = np_membership_matrix @ np_score_list.T
        finalResult = float(np_weight_list @ score_membership)
        ifSuccess = True
        return ifSuccess, finalResult, errorInfo


if __name__ == "__main__":
    r_l = [1, 3, 5, 0, 2.5]  # 指标值得分列表
    s_l = [0, 10, 30, 50, 80, 85, 90, 95, 100]  # 表头分数段
    w_l = [0.2, 0.3, 0.4, 0.1, 0.7]  # 指标对应权重
    m_m = [[0, 2, 4, 6, 8, 10, 13, 15, 20], [10, 8, 6, 4, 1, 0, -1, -4, -5], [7, 6, 5, 4, 3, 2, 1, 0, -1], [9, 6, 4, 3, 2, 1, 0, -1, -5], [10, 8, 6, 4, 2, 1, 0, -3, -10]]  # 隶属度矩阵
    print(FuzzyAssessmentClass.ResultCalc(r_l, w_l, s_l, m_m))
