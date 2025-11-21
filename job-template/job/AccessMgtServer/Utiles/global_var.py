# 全局变量，用于app与router之间通信

def _init():  # 初始化
    global _global_dict
    _global_dict = {}


def set_value(key, value):
    # 定义一个全局变量
    _global_dict[key] = value


def get_value(key):
    # print(_global_dict)
    # 获得一个全局变量，不存在则提示读取对应变量失败
    try:
        if key in _global_dict:
            return _global_dict[key]
        else:
            print(key + "不存在字典中")
    except:
        print('读取' + key + '失败\r\n')


redisObj = None

