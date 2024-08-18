import threading
def thread_it(func, *args):
    # 创建
    t = threading.Thread(target=func, args=args)
    # 守护 !!!
    t.setDaemon(True)
    # 启动
    t.start()
# 自定义错误
class PathTamperingError(Exception):
    """路径篡改错误"""
    # def __init__(self, message):
    #     self.message = message
    #     # super().__init__(self.message)
    def __init__(self, *args, **kwargs): # real signature unknown
        pass