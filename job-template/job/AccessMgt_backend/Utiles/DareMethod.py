import numpy as np


class DareMethodClass():
    @staticmethod
    def dare_method(comparison_matrix):
        """
        使用环比评分法(DARE法)计算各指标的权重

        参数:
        comparison_matrix: 列表，包含相邻指标的比较结果
                           例如，comparison_matrix[i]表示指标i+1与指标i的重要性比值

        返回:
        weights: 各指标的权重列表
        """
        # 检查输入有效性
        if not isinstance(comparison_matrix, list):
            raise ValueError("比较矩阵必须是一个列表")

        n = len(comparison_matrix) + 1  # 指标数量
        if n < 2:
            raise ValueError("至少需要2个指标才能进行比较")

        # 计算修正后的值
        corrected = [1.0]  # 第一个指标的修正值为1
        for i in range(n - 1):
            corrected.append(corrected[-1] * comparison_matrix[i])

        # 计算总修正值
        total_corrected = sum(corrected)

        # 计算权重
        weights = [c / total_corrected for c in corrected]

        return weights


def main():
    # 示例：计算5个指标的权重
    # 这里的比较矩阵表示：
    # 指标2/指标1 = 1.2，指标3/指标2 = 0.8，指标4/指标3 = 1.5，指标5/指标4 = 1.0
    comparison_matrix = [1.2, 0.8, 1.5, 1.0]

    try:
        weights = DareMethodClass.dare_method(comparison_matrix)
        print(weights)
        print("各指标的权重计算结果：")
        for i, weight in enumerate(weights, 1):
            print(f"指标{i}: {weight:.4f} ({weight * 100:.2f}%)")

        print(f"\n权重总和: {sum(weights):.4f}")
    except ValueError as e:
        print(f"计算出错: {e}")


if __name__ == "__main__":
    main()
