"""
灰色聚类法
"""


class GreyClusteringClass():
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
    def ResultCalc(score_list, score_level_list, level_list, weight_list):
        """
        :param score_list: 指标值列表
        :param score_level_list: 分数分级列表
        :param level_list: 分数段列表
        :param weight_list: 权重列表
        :return:
        """
        ifSuccess = False
        finalResult = 0.0
        errorInfo = ""
        score_level_num = len(score_level_list)
        weight_num = len(weight_list)
        score_num1 = len(level_list)
        score_num2 = len(score_list)

        if score_num1 != weight_num:
            errorInfo = "指标与权重数量不一致！"
            return ifSuccess, finalResult, errorInfo
        if score_num1 != score_num2:
            errorInfo = "指标缺少分级参数！"
            return ifSuccess, finalResult, errorInfo
        if (not GreyClusteringClass.is_monotonic(score_level_list)) or score_level_list[0] > score_level_list[1]:
            errorInfo = "分数段不递增！"
            return ifSuccess, finalResult, errorInfo
        for level_i in level_list:
            if not GreyClusteringClass.is_monotonic(level_i):
                errorInfo = "分数分段不单调！"
                return ifSuccess, finalResult, errorInfo
            if score_level_num != (len(level_i) - 1):
                errorInfo = "分数分段数量错误！"
                return ifSuccess, finalResult, errorInfo

        k_list = []
        for k in range(score_level_num):
            temp_k_result = 0.0
            # 判断每个指标
            for i in range(weight_num):
                score_type = 0
                k_result = 0.0
                score = score_list[i]
                weight = weight_list[i]
                level = level_list[i]
                level_mid = []
                # 逆向指标
                if level[0] > level[1]:
                    score_type = -1
                # 正向指标
                else:
                    score_type = 1
                # 求区间中点
                for j in range(len(level) - 1):
                    level_mid.append((level[j] + level[j + 1]) / 2.0)
                # k1
                if k == 0:
                    end_point = level_mid[1]
                    max_point = level[1]
                    if score_type == 1:
                        if score <= max_point:
                            k_result = 1.0 * weight
                        elif max_point < score < end_point:
                            k_result = (abs(score - end_point) / abs(max_point - end_point)) * weight
                        else:
                            k_result = 0.0
                    else:
                        if score >= max_point:
                            k_result = 1.0 * weight
                        elif max_point > score > end_point:
                            k_result = (abs(score - end_point) / abs(max_point - end_point)) * weight
                        else:
                            k_result = 0.0
                elif k == score_level_num - 1:
                    max_point = level[k]
                    end_point = level_mid[k-1]
                    if score_type == 1:
                        if score >= max_point:
                            k_result = 1.0 * weight
                        elif max_point > score > end_point:
                            k_result = (abs(score - end_point) / abs(max_point - end_point)) * weight
                        else:
                            k_result = 0.0
                    else:
                        if score <= max_point:
                            k_result = 1.0 * weight
                        elif max_point < score < end_point:
                            k_result = (abs(score - end_point) / abs(max_point - end_point)) * weight
                        else:
                            k_result = 0.0
                else:
                    if score_type == 1:
                        left_point = level[k]
                        max_point = level[k + 1]
                        right_point = level_mid[k+1]
                    else:
                        left_point = level_mid[k+1]
                        max_point = level[k+1]
                        right_point = level[k]
                    if left_point < score <= max_point:
                        k_result = abs(score - left_point) / abs(max_point - left_point) * weight
                    elif max_point < score <= right_point:
                        k_result = abs(score - right_point) / abs(max_point - right_point) * weight
                    else:
                        k_result = 0.0
                temp_k_result += k_result
            k_list.append(temp_k_result)
        ifSuccess = True
        pos = k_list.index(max(k_list))
        finalResult = score_level_list[pos]
        return ifSuccess, finalResult, errorInfo


if __name__ == "__main__":
    s_l = [35, 28, 35]  # 算出来的值
    s_l_l = [0, 20, 50, 80]  # 分数段
    l_l = [[40, 30, 20, 10, 00],  # 每一个指标的评分标准
           [00, 10, 20, 30, 40],
           [00, 10, 20, 30, 40]]
    w_l = [0.4, 0.3, 0.3]  # 每个指标的权重
    print('最终结果',GreyClusteringClass.ResultCalc(s_l, s_l_l, l_l, w_l))
