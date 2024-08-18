# from cryptography.hazmat.primitives import hashes
# from cryptography.hazmat.primitives.asymmetric import rsa, padding
# from cryptography.hazmat.backends import default_backend
# from cryptography.hazmat.primitives import serialization
import re


class Validation:
    def __init__(self,port=None,app=None):
        self.urlList=[]
        self.urlDict={}
        self.static_folder=app.static_folder
        self.template_folder=app.template_folder

    # 解密部分
    def decrypt(self,key):
        return True
    # return False,"第三方插件！无法验证有效，请谨慎加载！"

    # 验证url
    def verify_url(self,name=None):
        match = re.search(r"<module '([^']+)'", str(name))
        plugin_name = match.group(1)
        if type(self.vso[1]) == str:
            kty = (self.vso[1],)
        else:
            kty = self.vso[1]
        for path in kty:
            for i in self.urlDict:
                if path in self.urlDict[i]:
                    return False,f"url:[{path}] 和 插件[{i}]的url发生冲突"
        self.urlDict[plugin_name]=self.vso[1]
        return True,"验证通过"

    # 验证动态文件和静态文件是否被篡改
    def dynamic_and_static(self,app):
        # 获取静态文件夹路径是否一样
        if self.static_folder!=app.static_folder:
            app.static_folder = self.static_folder
            app.template_folder = self.template_folder
            return False,"此插件试图篡改静态文件夹！已停止加载"
        if self.template_folder != app.template_folder:
            app.static_folder = self.static_folder
            app.template_folder = self.template_folder
            return False, "此插件试图篡改动态文件夹！已停止加载"

        return True,""


    def validation(self,plugin_name):
        try:
            self.vso = plugin_name.vso()
            if self.decrypt(114514):
                return self.verify_url(name=plugin_name)
        except Exception as e:
            return False,"没有验证模块，无法验证插件是否篡改"

    # 获取url路径
    def GetUrlPath(self):
        return self.urlDict