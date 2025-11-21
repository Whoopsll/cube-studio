import numpy as np


class AHPFuncClass():
    @staticmethod
    def get_ri(n):
        """获取平均随机一致性指标RI（n=1~15）"""
        ri_table = {
            1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32,
            8: 1.41, 9: 1.45, 10: 1.49, 11: 1.51, 12: 1.54, 13: 1.56, 14: 1.58, 15: 1.59
        }
        if n not in ri_table:
            raise ValueError(f"RI值仅支持1~15阶矩阵，当前阶数：{n}")
        return ri_table[n]

    @staticmethod
    # 检验输入一维数组是否为 n x n
    def convert_to_nxn_matrix(arr):
        # 初始化
        matrix = []
        errorInfo = ""
        bIfCanTransToMatrix = False

        # 计算数组长度
        length = len(arr)
        # 计算n值（必须是整数，否则无法转换为n×n矩阵）
        n = int(np.sqrt(length))

        # 检查是否能转换为n×n矩阵
        if n * n != length:
            errorInfo = "输入数据错误!"
            return bIfCanTransToMatrix, matrix, errorInfo

        # 转换为n×n矩阵
        matrix = np.array(arr).reshape(n, n)
        bIfCanTransToMatrix = True
        return bIfCanTransToMatrix, matrix, errorInfo

    @staticmethod
    def calculate_weight(matrix):
        """
        计算判断矩阵的权重（特征向量法）并进行一致性检验
        :param matrix: 判断矩阵（n×n numpy数组）
        :return: 归一化权重向量、一致性比率CR
        """
        n = matrix.shape[0]  # 矩阵阶数

        # 1. 计算最大特征值和对应的特征向量
        eigenvalues, eigenvectors = np.linalg.eig(matrix)
        max_idx = np.argmax(eigenvalues)
        lambda_max = np.real(eigenvalues[max_idx])  # 最大特征值（取实部，避免复数）
        eigenvector = np.real(eigenvectors[:, max_idx])  # 对应特征向量（取实部）

        # 2. 特征向量归一化得到权重
        weight = eigenvector / np.sum(eigenvector)

        # 3. 一致性检验
        if n == 1:
            # 1阶矩阵无需检验
            return weight, 0.0
        ci = (lambda_max - n) / (n - 1)  # 一致性指标
        ri = AHPFuncClass.get_ri(n)  # 平均随机一致性指标
        cr = ci / ri  # 一致性比率

        return weight, cr

    @staticmethod
    def ahp_analysis(matrix_data):
        errorInfo = ""
        ifSuccess = False
        matrixResult, realMatrix, errorInfo = AHPFuncClass.convert_to_nxn_matrix(matrix_data)
        if not matrixResult:
            return ifSuccess, realMatrix, errorInfo
        realWeight, real_cr = AHPFuncClass.calculate_weight(realMatrix)
        if real_cr >= 0.1:
            errorInfo = "检查矩阵失败！请重置矩阵！"
            realWeight = []
        else:
            ifSuccess = True
        return ifSuccess, realWeight, errorInfo


if __name__ == "__main__":
    criteria_matrix2 = np.array(
        [1, 3, 5,
         0.33333, 1, 3,
         0.2, 0.3333, 1])
    ifSuccessTest, real_weightTest, errorInfoTest = AHPFuncClass.ahp_analysis(criteria_matrix2)
    print(ifSuccessTest, real_weightTest, errorInfoTest)
