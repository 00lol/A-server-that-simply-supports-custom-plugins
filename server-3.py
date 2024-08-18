
import importlib

from flask import Flask, send_file

from depend import Plugin_validation
from depend.Alternative import *
from init import *

logging = logger
# 参数传递
arg = sys.argv
app = Flask(__name__)
# waf = flask_waf.Waf(app)
# 已读取的插件列表
loaded_plugins = []
# 已运行的插件列表
run_plugins = []
# 已注入的url
url_list = []
pl = ''
# 加载线程列表
loaded_thread = {}
# 调用插件线程列表
invoke_thread = {}
# 运行线程列表
run_thread = []
# 配置文件
config = {"old": {}, "new": {}}


def du():
    # logging.info("读取配置文件")
    with open("config.json", "r", encoding="utf-8") as c:
        config["old"] = json.load(c)


# 插件管理
def cin():
    time.sleep(0.6)
    global cmd, pl
    # pl = PluginManager()
    while True:
        time.sleep(0.5)
        cmd = input("%^&>>>")
        # 切开
        cd = cmd.split(' ')
        if cmd == "cmd++":
            if 'plugins.cmd' not in loaded_plugins:
                print("无法切换成cmd++，因为该插件已被卸载")
            else:
                print("已切换成cmd++")
                break
        elif cmd == "list":
            url()
        elif cmd == "stop":
            sever.stop()
            break
        elif cmd == "load plugin":
            pl = PluginManager()
        elif cmd == "":
            pass
        else:
            for i in range(len(cd)):
                if cd[i] == "reload":
                    try:
                        plugin_name = cd[i + 1]
                        pl.reload_pl(pl_name=plugin_name)
                        break
                    except IndexError:
                        print("语法错误")
                        break
                # 卸载
                elif cd[i] == "unload":
                    try:
                        plugin_name = cd[i + 1]
                        pl.unload_pl(pl_name=f"plugins.{plugin_name}")
                        break
                    except IndexError:
                        print("语法错误")
                        break
                # 加载
                elif cd[i] == "load":
                    if cd[i + 1] == "all":
                        pl = PluginManager()
                        pl.load_plugins()
                    try:
                        plugin_name = cd[i + 1]
                        pl.load_plugin(f"plugins.{plugin_name}")
                        break
                    except IndexError:
                        print("语法错误")
                        break
                else:
                    print(f"命令 {cmd} 无效！")


# 插件添加
class PluginManager:
    def __init__(self):
        self.argument = None
        self.leng = 0
        # 本地加载
        # self.load_plugins()
        # 获取 URL 到函数的映射
        self.url_map = app.url_map
        self.pv = Plugin_validation.Validation(app=app)

    # 加载
    def load_plugins(self):
        logging.info("加载插件...")
        # 扫描所有插件
        files = [f for f in os.listdir("plugins") if os.path.isfile(os.path.join("plugins", f))]

        for filename in files:
            if filename.endswith(".pyw"):
                # 使用多线程加载插件
                th = thread_it(lambda: self.load_plugin(f'plugins.{filename[:-4]}'))
                loaded_thread[filename[:-4]] = th
                self.leng += 1

    # 主加载插件
    def load_plugin(self, plugin_name):
        # 加载插件
        def load():
            plugin_module.main(self.argument)
            # 验证路径篡改
            das = self.pv.dynamic_and_static(app=app)
            if not das[0]:
                logger.error(f"[{plugin_name}]:{das[-1]}")
                # raise PathTamperingError(f"[{plugin_name}]:{das[-1]}")
                # 去除
                self.leng -= 1
                # loaded_plugins.remove(plugin_name)
                self.unload_pl(pl_name=plugin_name)
                try:
                    run_plugins.remove(plugin_name)
                except ValueError as e:
                    logging.debug(f"[{plugin_name}]无法在运行列表中找到此插件:{e}")
                try:
                    loaded_plugins.remove(plugin_name)
                except ValueError as e:
                    logging.debug(f"[{plugin_name}]无法在加载列表中找到此插件:{e}")
                return
            run_plugins.append(plugin_name)
            logger.info(f"[{plugin_name}]:加载完成")



        dicklist = {"app": app,
                    "config": config["new"],
                    "PluginManager": pl,
                    "loaded_plugins": loaded_plugins,
                    "cin": cin,
                    "run_plugins": run_plugins,
                    "longging": logging}
        # 传入参数
        self.argument = [app, config["old"], pl, loaded_plugins, cin, run_plugins, logging, dicklist]
        if plugin_name not in loaded_plugins:
            logging.info(f"[{plugin_name}]:正在加载")
            try:
                plugin_module = importlib.import_module(plugin_name)
                # 验证插件合法性质
                verify = self.pv.validation(plugin_module)
                if verify[0]:
                    # 调用插件,通过多线程调用，不让卡死
                    invoke_thread[plugin_name] = thread_it(load)
                    # 将插件列入加载名单
                    loaded_plugins.append(plugin_name)
                else:
                    logging.warning(f"[{plugin_name}]:{verify[-1]}")
                    # 去除
                    self.leng -= 1
            except ModuleNotFoundError:
                logging.error(f"未找到插件模块: {plugin_name}")

            except PathTamperingError as e:
                logging.error(e)

            except Exception as e:
                logging.error(f"加载插件时出错,插件 [{plugin_name}]:{e}")
                # 去除
                self.leng -= 1
                try:
                    run_plugins.remove(plugin_name)
                except ValueError as e:
                    logging.error(f"[{plugin_name}]无法在运行列表中找到此插件:{e}")
                try:
                    loaded_plugins.remove(plugin_name)
                except ValueError as e:
                    logging.error(f"[{plugin_name}]无法在加载列表中找到此插件:{e}")
        else:
            logging.info(f"[{plugin_name}]:已加载")

    # 重载 Reason: "451 No mapping for the Unicode character exists in the target multi-byte code page. ".
    def reload_pl(self, pl_name):
        if self.unload_pl(pl_name):
            if self.load_plugin(pl_name):
                logging.info(f"插件 {pl_name} 已重新加载")
                return True
            else:
                logging.warning(f"插件 {pl_name} 重新加载失败")
                return False
        else:
            logging.error(f"插件 {pl_name} 卸载失败，无法重新加载")
            return False


    # 卸载插件
    def unload_pl(self, pl_name):
        # 获取 URL 到函数的映射
        url_map = app.url_map
        # 获取对应的路由
        url_table = self.pv.GetUrlPath()
        if pl_name in sys.modules:
            # 释放资源
            try:
                try:
                    run_plugins.remove(pl_name)
                    loaded_plugins.remove(pl_name)
                except:
                    pass
                # 从内存中卸载
                del sys.modules[pl_name]
                # 获取路由
                to_remove = []
                if type(url_table[pl_name])==str:
                    to_remove = url_table[pl_name]
                else:
                    for i in url_table[pl_name]:
                        to_remove.append(i)

                for route in to_remove:
                    # 删除路由
                    if route in url_map._rules_by_endpoint:
                        del url_map._rules_by_endpoint[route]
                    # 删除在迭代结束后删除端点函数
                    for endpoint, view_func in app.view_functions.items():
                        if endpoint == route:
                            del app.view_functions[endpoint]
                            app.view_functions.pop(endpoint)
                logging.info(f"[{pl_name}] 已卸载")
                return True
            except ValueError:
                logging.warning(f"没有名为 {pl_name} 的插件")
                return False
        else:
            logging.warning(f"内存中未找到名为 [{pl_name}] 的插件")
            return False



    # 获取插件数量
    def getpluginleng(self):
        return self.leng


def url():
    # 获取 URL 到函数的映射
    url_map = app.url_map
    print(url_map)


class Sever:
    def __init__(self):
        global pl
        self.start_time = time.time()
        self.plugins = True
        # 调用初始化函数，检查设备，以及json文件
        config["new"] = ast.literal_eval(str(Init()))
        logging.info("初始化参数...")
        if "NoPlugin" in arg:
            self.plugins = False
            logging.warning("以不加载插件的情况下开启服务器...")
        logging.info("初始化函数")
        # 初始化插件类
        if self.plugins:
            self.pl = PluginManager()
            pl = self.pl

    # 开启服务器
    def start(self):
        # 读取配置文件
        du()
        if self.plugins:
            # 开始加载插件
            self.pl.load_plugins()
            # 等待所有插件反应
            logger.info("等待所有插件加载完成")
            while True:
                if len(loaded_plugins) == self.pl.getpluginleng():
                    break
            logger.info("已通过数量验证(1/2)")
            while True:
                if len(loaded_plugins) == len(run_plugins):
                    break
            logger.info("已通过加载验证(2/2)")

            logging.info(f"共 {len(run_plugins)} 个插件成功加载，准备开启服务器")
        # cmd插件的特权(* m *)
        if 'plugins.cmd' not in loaded_plugins:
            # 开启插件管理
            thread_it(cin)
        end_time = time.time()
        logging.info(f'服务器将在 {config["new"]["Sever"]["port"]} 端口上开启')
        logging.info(f'ip为: {config["new"]["Sever"]["ip"]}')
        logging.info(f"总共用时：{end_time - self.start_time} 秒")

    def unregister_all_routes(self, app):
        # 获取所有已注册的路由
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(rule.endpoint)

        # 移除所有路由
        for route in routes:
            app.view_functions.pop(route)

    # 关闭服务器
    def stop(self):
        logging.info("接收到命令，关闭服务器")
        # 卸载所有路由
        logging.info("正在卸载所有路由...")
        self.unregister_all_routes(app)
        # 卸载插件
        if self.plugins:
            logging.info("正在卸载插件...")
            logging.info(f"共 {len(run_plugins)} 个")
            while len(run_plugins) != 0:
                for plugin_name in run_plugins:
                    if not pl.unload_pl(pl_name=plugin_name): run_plugins.remove(plugin_name)

        # logging.info("退出所有线程")
        # # 获取当前所有线程
        # thread_list = threading.enumerate()
        # # 遍历并结束所有线程
        # for thread in thread_list:
        #     if thread != threading.current_thread():  # 排除当前主线程
        #         thread.join()
        self.end_time = time.time()
        # 关闭flask
        # func = request.environ.get('werkzeug.server.shutdown')
        # if func is None:
        #     raise RuntimeError('Not running with the Werkzeug Server')
        # func()
        logging.info(f"服务器运行时间: {self.end_time - self.start_time} 秒")
        exit()


# 主体_版本查询
@app.route('/version', methods=['GET'])
def freeze_vaersion():
    du()
    return config["old"]["app"]["version"]


# 主体_获取最新文件
@app.route('/new/app', methods=['GET'])
def freeze_new_app():
    # 新版本文件路径
    du()
    return send_file(config["old"]["app"]["path"])


# 更新部分_版本查询
@app.route('/update/version', methods=['GET'])
def update_section_the_latest_files():
    du()
    return config["old"]["update"]["version"]


# 更新部分_获取最新文件
@app.route('/update/new', methods=['GET'])
def update_latest_files():
    du()
    return config["old"]["update"]["new_app"]


@app.route('/test', methods=['GET'])
def test():
    return "1.1.1.1.1"


if __name__ == '__main__':
    sever = Sever()
    sever.start()
    # 开启服务器
    app.run(host=config["new"]["Sever"]["ip"], port=config["new"]["Sever"]["port"], debug=False)
    sever.stop()
