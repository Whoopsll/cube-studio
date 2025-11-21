# 权重平均法
class WeightedMeanClass():
    @staticmethod
    def ResultCalc(resultWeightList):
        ifSuccess = False
        finalResult = 0.0
        errorInfo = ""
        weightSum = 0.0
        resultSum = 0.0
        for data in resultWeightList:
            if data["item_weight"] < 0:
                errorInfo = "权重出现负值！"
                return ifSuccess, finalResult, errorInfo
            weightSum += data["item_weight"]
            resultSum += (data["item_value"] * data["item_weight"])
        if abs(weightSum) < 1e-6:  # 校验权重是否均为0 小数点位数可调整
            errorInfo = "注意！权重均为0！"
            return ifSuccess, finalResult, errorInfo
        finalResult = resultSum / weightSum
        ifSuccess = True
        return ifSuccess, finalResult, errorInfo


if __name__ == "__main__":
    testdata = [
        {'item_value': 100, 'item_weight': 0.5},
        {'item_value': 0, 'item_weight': 0.3},
        {'item_value': 0, 'item_weight': 0.2},
    ]
    ifSuccess, finalResult, errorInfo = WeightedMeanClass.ResultCalc(testdata)
    print(ifSuccess)
    print(finalResult)
    print(errorInfo)