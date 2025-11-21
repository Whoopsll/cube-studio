"""
幂指数法
"""


class PowerSeriesClass():
    @staticmethod
    def ResultCalc(resultWeightList, calc_type=0):
        """
        :param resultWeightList:
        :param calc_type: 计算类型 1 加权和(加权平均)，0 加权积(幂指数)
        :return:
        """
        ifSuccess = False
        finalResult = 0.0
        errorInfo = ""
        weightSum = 0.0
        for data in resultWeightList:
            if data["item_weight"] < 0:
                errorInfo = "权重出现负值！"
                return ifSuccess, finalResult, errorInfo
            weightSum += data["item_weight"]
        if abs(weightSum) < 1e-6:  # 校验权重是否均为0 小数点位数可调整
            errorInfo = "注意！权重均为0！"
            return ifSuccess, finalResult, errorInfo

        if calc_type == 1:
            temp_result = 0.0
            for data in resultWeightList:
                temp_result += data["item_weight"] * data["item_value"]
            finalResult = temp_result
            ifSuccess = True
        else:
            temp_result = 1.0
            for data in resultWeightList:
                temp_result *= data["item_value"] ** data["item_weight"]
            finalResult = temp_result
            ifSuccess = True
        return ifSuccess, finalResult, errorInfo


if __name__ == "__main__":
    testdata = [
        {'item_value': 0, 'item_weight': 0.2},
        {'item_value': 0, 'item_weight': 0.3},
        {'item_value': 100, 'item_weight': 0.5},
    ]
    print(PowerSeriesClass.ResultCalc(testdata))
