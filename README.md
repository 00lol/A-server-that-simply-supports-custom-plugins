# Customize the plugin server
* **简介**  
    这是一个基于python Flask 框架的极其简易的服务器。正如标题，这玩意
    是支持自定义插件的
* **食用方法**
    1.在windows下直接右键run.bat以管理员生身份运行即可  
    2.在linux下在运行终端直接运行以下代码  
    `$ gh repo clone 00lol/A-server-that-simply-supports-custom-plugins `  
    `$ cd A-server-that-simply-supports-custom-plugins/`  
    `$ bash run.sh`  
    前提是得安装python
* **命令行**  
一个好的服务端怎么能少得了命令行呢？  
    以下是一些命令，当然，你也可以在`plugins/cmd.pyw`文件里自定义添加或者删除命令
    |所属插件| 命令 | 作用 |  
    | --- | ---- | ---- |  
    |cmd.pyw|plugin list|显示加载的插件|  
    |^|plugin load [PluginName] |加载新的插件|  
    |^|plugin unload [PluginName] |卸载已加载的插件|  
    |^|plugin reload [PluginName] |重载已加载的插件|  
    |^|help |显示列表|  
    |^|list |显示已加载的路由|  
    |内置命令行|load [PluginName]|加载新的插件|
    |^|unload [PluginName] |卸载已加载的插件|  
    |^|reload [PluginName] |重载已加载的插件|  
    |^|cmd++ |切换至cmd++插件|  
    |^|stop |尝试关闭服务器  （当然可以用 <kbd>ctrl</kbd>+<kbd>c</kbd>）|  

    ***注意！*** 如果插件里有路由的话，必须要重启服务器才能生效


* ***关于自定义插件***  
    一般情况下所有的插件都在plugins文件夹下  
    插件的后缀名是`XXX.pyw`为结尾    
    以下是自定义插件的格式（PS：可以直接复制到`test.pyw`文件里）
    ```python
    # 验证模块，是载入服务器的唯一凭证
    def vso():
        text = b"This is a plugin"# 插件简介
        url = ()# 插件绑定的URL,格式为:/test
        return text, url

    # 服务端统一调用的函数，可以理解为c++中的int main()函数
    def main(apu):
        """旧版"""
        apu[5].info("旧版:114514 1919810")
        # apu是从服务端传入的参数，包括但不限于日志函数，多线程函数等，一下是全部的说明
        # 旧版以列表方式传入

        # apu[0]:Flask的app主进程
        # apu[1]:服务器的配置文件(旧版)
        # apu[2]:服务器插件管理函数
        # apu[3]:加载的插件列表
        # apu[4]:内部的终端命令行
        # apu[5]:运行的插件列表
        # apu[5]:日志函数，可以使用.info等其他等级记录。

        # apu[-1] 新版传入参数的方式是以字典的方式,以名称作为寻找函数的开头
        # 比如：apu[-1]["longging"] 这个所对应的就是日志函数，下面是键值对应的值
        # app:Flask的app主进程
        # config:服务器配置文件(新版)
        # PluginManager:服务器插件管理函数
        # loaded_plugins:加载的插件列表
        # cin:内部的终端命令行
        # run_plugins:运行的插件列表
        # longging:日志函数，可以使用.info等其他等级记录。

        # 注意！使用新版方法无法兼容旧版服务端！
        # 旧版插件 无论新旧都可兼容！
        """新版"""
        apu[-1]["longging"].info("新版:114514 1919810")
        ```
* 最后
    >本人第一次上传项目，如果有什么做的不好的地方还请多多指教  
    如果发现BUG的话，请联系我！谢谢  
    Email：sky_diskserver@qq.com
