# -*- coding:utf-8 -*-
# python3
# Pycharm 2023.3
# 2024/4/19
"""初始化服务器，保证后续正常工作"""
import ast
import configparser
import json
import os
import platform
import secrets
import string
import subprocess
import sys
import time
import urllib.request as re
import zipfile

import requests
import yaml
from func_timeout import func_timeout, FunctionTimedOut

from loguru import logger
from tqdm import tqdm

import depend.EAD as EAD
import ml


def text(file):
    if file == "Sever":
        return {"Sever": {
            "port": 33780,
            "ip": "0.0.0.0"
        },
            "mysql": {
                "initiate": False,
                "External_libraries": True,
                "port": 3306,
                "ip": "127.0.0.1",
                "Users": "root",
                "password": "",
                "sever": "mysql5743_2"
            },
            "encrypt": True,
            "version": "0.1.2"
        }
    if file == "Users":
        return {}


class Init:
    def __init__(self):
        self.LOG_FORMAT = "[ {time}  {level} ] [{file}] - {message}"
        # 设置 CMD 输出为 UTF-8 编码
        subprocess.run('chcp 65001', shell=True)
        logger.add(r'logs/{time}.log',
                   rotation='00:00',
                   retention='30 days',
                   compression='zip',
                   format=self.LOG_FORMAT)
        logger.info("配置日志系统...")
        self.config = None
        self.version = "0.55.1"
        # 获取路径
        self.PATH = os.getcwd()
        logger.info("将日志输出编码设置为 chcp 65001")
        logger.info(f"服务器版本:{self.version}")
        logger.info(f"服务器路径:{self.PATH}\*")
        # 检测系统
        logger.info(f"兼容性检测...")
        self.test_system()
        self.loadfile()
        logger.info("检查文件...")
        self.files()
        self.mysql()

    # 检测系统
    def test_system(self):
        # 获取操作系统可执行程序的结构
        structure = platform.architecture()
        logger.info(f"系统结构: {structure[1]}x{structure[0]}")
        jiago=["Windows","Liunx"]
        for i in jiago:
            if structure[1].find(i)==-1:
                break
        else:
            raise ValueError("系统不兼容！请使用Windows或者Linux系统")
        if structure[0] != "64bit":
            logger.warning("使用x32架构可能会出现兼容性问题，建议使用x64架构")
        # 系统版本
        logger.info(f"系统操作版本: {platform.platform()}")
        # 计算机的网络名称
        logger.info(f"网络名称: {platform.node()}")
        # 计算机处理器信息
        logger.info(f"CPU: {platform.processor()}")
        # 检测python版本
        ver = sys.version
        logger.info(f"python 版本: {ver}")
        if int(ver[0]) < 3:
            raise ValueError("无法使用旧版Python，请Python版本升级到3.7.4!")
        elif "3.7.4" != ver.split(" ")[0]:
            logger.warning("尽量使用Python 3.7.4 ，防止出现兼容问题")

    # 文件检测
    def files(self):
        # 必要的文件-本地
        FILES = {
            "plugins": [""],  # 插件
            "depend": [""],  # 依赖
            "cache": [""],  # 缓存
            "logs": [""],  # 日志
            "data": [""],  # 用户数据
            "files": ["Sever.yaml", "Users.yaml", "config.yaml"]  # 服务器必要文件
        }
        # 检查文件
        # 普通
        for i in FILES:
            # 确保都有文件夹-第一层
            if not os.path.exists(i):
                os.makedirs(i)
            if i == "files":
                continue
            for i2 in FILES[i]:
                if os.path.exists(f"{i}/{i2}"):
                    continue
                # 检测文件,并创建
                if i2.find(".") != -1:
                    with open(f"{i}/{i2}", "w+", encoding='utf-8') as f:
                        f.write("")
                else:
                    os.makedirs(f"{i}/{i2}")
        # 对于特殊文件
        for file in FILES["files"]:
            if os.path.exists(f"files/{file}"):
                continue
            try:
                with open(f"files/{file}", "w+", encoding="utf-8") as f:
                    yaml.dump(data=text(file.split(".")[0]),
                              stream=f,
                              allow_unicode=True)
            except Exception as f:
                logger.error(f"无法写入文件！files/{file} 原因:{f}")
                return False
        # 如果文件没有创建，那么就读取内置配置
        if self.config is None:
            self.config = text("Sever")
        # 检测数据库
        if not os.path.exists("Mysql") and self.config["mysql"]["initiate"]:
            os.makedirs("Mysql")

            def do():
                url = "https://downloads.mysql.com/archives/get/p/23/file/mysql-5.7.43-winx64.zip"
                logger.info(f"下载数据库，版本:5.7.43,url:{url}")

                # 打开URL并创建一个文件来写入下载的内容
                with re.urlopen(url) as response, open("cache/Mysql.zip", 'wb') as out_file:
                    # 获取文件的总大小以跟踪下载进度
                    file_size = int(response.headers['Content-Length'])
                    pbar = tqdm(total=file_size, unit='B', unit_scale=True)
                    # 设置从响应中读取数据的缓冲区大小
                    buffer_size = 1024

                    # 初始化变量以跟踪读取的字节数
                    bytes_read = 0

                    # 记录开始下载的时间
                    start_time = time.time()
                    time.sleep(0.3)
                    # 开始以块为单位读写数据
                    while True:
                        # 从响应中读取数据块
                        buffer = response.read(buffer_size)

                        # 检查缓冲区是否为空(文件结束)
                        if not buffer:
                            break

                        # 更新读取的总字节数
                        bytes_read += len(buffer)

                        # 将缓冲区数据写入输出文件
                        out_file.write(buffer)

                        # 用当前缓冲区的大小更新进度条
                        pbar.update(len(buffer))

            do()
            # 配置mysql数据库
            logger.info("第一次使用数据库，配置中...")
            with zipfile.ZipFile("cache/Mysql.zip", 'r') as zip_ref:
                zip_ref.extractall("Mysql")
            config = configparser.ConfigParser()
            # 添加一个节
            config['mysqld'] = {
                'port': '3306',
                'basedir': f'{self.PATH}\\\\Mysql\\\\mysql-5.7.43-winx64',
                'datadir': f'{self.PATH}\\\\Mysql\\\\mysql-5.7.43-winx64\\\\data',
                'bind-address': '0.0.0.0',
                'log_syslog': '0'
            }
            # 写入配置文件
            with open('Mysql/mysql-5.7.43-winx64/my.ini', 'w') as configfile:
                config.write(configfile)
            logger.info("初始化mysql...")
            # 数据库初始化
            subprocess.run(
                f'{self.PATH}/Mysql/mysql-5.7.43-winx64/bin/mysqld.exe --initialize-insecure --defaults-file="{self.PATH}/Mysql/mysql-5.7.43-winx64/my.ini"')
            # 设置mysql服务
            logger.info("设置mysql服务,将服务模块设置成：mysql5743")
            subprocess.run(
                f'{self.PATH}/Mysql/mysql-5.7.43-winx64/bin/mysqld.exe --install mysql5743 --defaults-file="{self.PATH}/Mysql/mysql-5.7.43-winx64/my.ini"')
            logger.info("重定向...")
            subprocess.run("net start mysql5743")
            logger.info("初始化数据库列表")
            self.mysql(first=True)
            # 配置密码和账户
            logger.info("数据库配置完成")
        return True

    # 检测网络
    def testurl(self):
        def go(url):
            logger.debug(f"检测url: {url}")
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    with open("cache/url.txt", 'w+', encoding='utf-8') as f:
                        f.write(url)
                    return url  # 网站开启
            except requests.RequestException:
                pass

        try:
            # 读取缓存
            with open("cache/url.txt", 'r', encoding='utf-8') as f:
                url = f.read()
                if go(url) is None:
                    # 删除列表里的url防止再次检测
                    self.url_list.remove(url)
                    for url in self.url_list:
                        go(url)
                    else:
                        return None
        except:
            for url in self.url_list:
                go(url)
            else:
                return None

    # 读取文件
    def loadfile(self):
        if os.path.exists("files/Sever.yaml"):
            with open("files/Sever.yaml", 'r', encoding="utf-8") as f:
                self.config = yaml.load(f.read(), Loader=yaml.FullLoader)
        else:
            self.files()
            self.config = text("Sever")

    # 数据库检测
    def mysql(self, first=False):
        # 尝试连接数据库
        if not self.config["mysql"]["initiate"]:
            logger.warning("mysql数据库已在内置配置文件中关闭，如需要，请在Sever.yaml文件中把mysql下的initiate设置为true")
            return
        if not first:
            # 读取
            with open("depend/config.json", "r", encoding="utf-8") as f:
                po = json.load(f)
            key = ast.literal_eval(po["YEK"])
            iv = ast.literal_eval(po["VI"])
            # 连接
            mu = ml.Mysql(ip=self.config["mysql"]["ip"],
                          port=self.config["mysql"]["port"],
                          user=self.config["mysql"]["Users"],
                          pwd=EAD.decrypt_data(self.config["mysql"]["password"], iv=iv, key=key)  # 存储
                          )
            # 检测连接
            if mu.init_data():
                logger.info("Mysql服务器初始化完成")
            else:
                logger.error("连接出现异常,无法启动服务器")
                sys.exit(0)
            # 启动后台连接
        else:
            logger.info("数据库必须设定一个密码，请输入密码（将在10秒后自动生成强密码）")
            # 超时模块
            time.sleep(1)
            try:
                password = func_timeout(10, lambda: input(">>>"))
            except FunctionTimedOut:
                # 随机生成强密码
                # 密码字符集合，包括大小写字母和数字以及特殊字符
                characters = string.ascii_letters + string.digits  # + string.punctuation
                password = ''.join(secrets.choice(characters) for i in range(32))
            logger.info(f"密码已设置成: {password}")
            # 修改密码
            mu = ml.Mysql(ip="127.0.0.1",
                          port=3306,
                          user='root',
                          pwd="")
            mu.cursor.execute(f'set password = password("{password}")')
            # 检测
            mu.init_data()
            # 加密存储
            data, key, iv = EAD.encrypt_data(password)
            # 二进制转字符串
            self.config["mysql"]["password"] = data
            with open("depend/config.json", "w+", encoding="utf-8") as f:
                json.dump({"YEK": str(key), "VI": str(iv)}, f)
            with open("files/Sever.yaml", "w+", encoding="utf-8") as f:
                yaml.dump(data=self.config,
                          stream=f,
                          allow_unicode=True)
            logger.info("完成加密")

    # 返回值
    def __str__(self):
        return str(self.config)


if __name__ == "__main__":
    p=str(Init())
    print(p)
    print(type(p))
    print(ast.literal_eval(p))
