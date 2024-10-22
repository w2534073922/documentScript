from datetime import datetime
import os
import shutil
import sys
from urllib import parse
import requests
from pypinyin import lazy_pinyin
import re
from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QMessageBox,QLabel
from config import MyConfig

global myName
global num
num = 1
def download_images(path="../files/下载popo图片/新.md",cookie=MyConfig.PrivateConfig.popoDocumentImageCookie,imgName=""):

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

        #设置图片名称

        if not imgName:
            match = re.search(r'^#\s+(.*)', content, re.MULTILINE)
            if match:
                imgName = match.group(1)
            imgName = imgFileNameConvertPinyin(imgName)
        imgName = imgName+"_"+datetime.now().strftime("%Y%m%d%H%M")+"_"
        imgName = openForm(imgName)
        print("当前的图片名称为:",imgName,"\n")

        matches = re.findall(r"!\[.*?\]\((.+?)\)", content)
        for url in matches:

            if url.startswith("http") or url.startswith("https"):
                url = url.split(" ")[0]
                # url = parse.quote_plus(url)
                if "code=" in  url:
                    #tt = parse.quote_plus(tt)
                    asset_path = os.path.join(os.path.dirname(path), 'assets', tt)
                else:
                    tt = os.path.basename(url)
                    tt = tt.split("path=")[1]
                    tt = parse.quote_plus(tt)
                    asset_path = os.path.join(os.path.dirname(path), 'assets', tt)

                if not os.path.exists(os.path.dirname(asset_path)):
                    os.makedirs(os.path.dirname(asset_path))
                if not os.path.exists(asset_path):
                    asset_path = asset_path.replace( ' "image"','')
                    content = content.replace(url+' "image"',url)

                    fileType=asset_path.split(".")[-1]

                    global num
                    asset_path = os.path.join('../files/下载popo图片','assets',imgName) + str(num)+'.'+fileType
                    num=num+1
                    response = getImg(url)
                    if response.status_code == 302 or response.status_code == 401:
                        print(f"Cookie失效了！")
                        print("获取popo文档图片cookie的操作步骤：\n\t在浏览器打开一个窗口，打开浏览器控制台→网络\n\t复制一个popo文档图片链接，粘贴后访问\n\t浏览器询问是否下载图片的同时，控制台的网络中有一个关于图片的网络请求，点开\n\t在这个请求的请求头信息中找到cookie，复制并粘贴到配置文件里即可")
                        sys.exit()
                    if response.status_code  != 200:
                        print('状态码非200，重试中')
                        response = getImg(url)
                        if response.status_code != 200:
                            print("状态码非200，再次重试')")
                            response = getImg(url)
                            if response.status_code != 200:
                                print("第三次状态码非200，终止')")
                                sys.exit()
                    content_type = response.headers['content-type']
                    if 'image' in content_type:
                        with open(asset_path, 'wb') as f:
                            #shutil.copyfileobj(r.raw, f)
                            f.write(response.content)
                            print(f"已下载图片：{asset_path}")
                    else:
                        print("下载图片异常，可能是cookie已经失效")
                        sys.exit()
                content = content.replace(url, f"./assets/{os.path.basename(asset_path)}")
                #pattern1 = r'\!\[[^\]]*\]\(([^)]+?)\)'#r'\!\[[^\]]*\]\(([^)]+?)\s+"[^"]+"\)'
                #pattern1 = r'\!\[[^\]]*\]\(([^)]+?)\s+"[^"]+"\)'
                pattern1 = r'\!\[[^\]]*\]\(([^)]+?)(\s+"[^"]+")?\)'
                # 执行替换
                #content = re.sub(pattern1, r'![0](\1)', content)
                content = re.sub(pattern1, r'<img src="\1" class="imgStyle" style="" />', content)


        content = content.replace('*   ', '- ')
        content = content.replace('    * ', '  - ')
        content = content.replace(' ', '')
        global myName
        content = content + f'''
<div style="text-align: right;font-size: 14px;">
    <span style="color: rgb(78, 110, 142);">创建人：</span>
    <span style="color: rgb(118, 118, 118);">{myName}</span>
    <span style="color: rgb(78, 110, 142);margin: 0 0 0 40px;">更新时间：</span>
    <span style="color: rgb(118, 118, 118);">{datetime.now().year}年{datetime.now().month:02d}月{datetime.now().day:02d}日</span>
</div>
'''
#         content = content + '''
# <style>
#     .imgStyle{
#         border-radius: 13px;
#         background: #e0e0e0;
#         box-shadow:  7px 7px 15px #d9d9d985,-7px -7px 15px #e7e7e76e;
#     }
# </style>
#         '''

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

# 将文件的名称转换成拼音表示（markdown的一级标题）
def imgFileNameConvertPinyin(fileName):
    # 将中文转换为拼音，pypinyin默认输出列表，这里用''.join将其合并为字符串
    pinyin_list = lazy_pinyin(fileName)
    pinyin_str = ''.join(pinyin_list)
    # 处理特殊符号，这里简单地去除所有非字母数字的字符，根据需要可以定制化处理
    processed_str = ''.join(filter(lambda x: x.isalnum() or x == '_', pinyin_str))
    return processed_str
def getImg(imgurl):
    response = requests.get(imgurl, stream=True, headers={"Cookie": cookie, "Pragma": "no-cache"},allow_redirects=True)
    return response

# 原本是针对文件夹下的md文件批量下载图片
# def batch_download_images(rootpath,cookie):
#     for subdir, _, files in os.walk(rootpath):
#         for file in files:
#             if file.endswith('.md'):
#                 path = os.path.join(subdir, file)
#                 download_images(path,cookie)
#                 print(f"{path}中的图像已下载。")


class ImagePrefixNameForm(QDialog):
    def __init__(self, fileName):
        super().__init__()
        self.result = None
        self.setWindowTitle("定义图片名前缀")
        self.setFixedSize(400, 150)  # 设置表单的固定大小

        main_layout = QVBoxLayout()

        input_layout = QHBoxLayout()
        input_label = QLabel("图片名前缀:")
        self.input_lineedit = QLineEdit(fileName)
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_lineedit)

        main_layout.addLayout(input_layout)

        self.submit_button = QPushButton("提交")
        main_layout.addWidget(self.submit_button)

        self.setLayout(main_layout)

        self.submit_button.clicked.connect(self.submit)

    def submit(self):
        text = self.input_lineedit.text()
        if text.strip() == "":
            QMessageBox.warning(self, "警告", "输入不能为空")
            # return
        else:
            self.result = text
            self.accept()
        # self.close()
        # self.accept()
        # print("输入的结果:", text)

def openForm(name_prefix) -> str:
    app = QApplication([])
    form_widget = ImagePrefixNameForm(name_prefix)
    form_widget.show()
    result =  form_widget.exec()
    if result:
        return form_widget.result
    else:
        sys.exit(1)


def start():

    # 设置cookie，cookie从浏览器里访问图片地址然后拿
    cookie = MyConfig.PrivateConfig.popoDocumentImageCookie
    myName = MyConfig.PrivateConfig.nickname
    global imgName
    # 为空时根据标题生成拼音，否则使用自定义名称
    #imgName = "ruhezidingyilianjieqi_0807_"
    # 定义旧文件夹和新文件夹
    old_md = '../files/下载popo图片/旧.md'
    new_md = '../files/下载popo图片/新.md'

    # 检查old_md文件是否存在，如果不存在则创建。
    if not os.path.exists(old_md):
        print("旧.md文件不存在，已创建。将markdown内容放到该文件中后再重新运行")
        with open(old_md, 'w', encoding='utf-8') as f:
            f.write("")
        exit()
    #创建修改后的md文件
    shutil.copy(old_md, new_md)

    if not os.path.exists('../files/下载popo图片/assets'):
        os.mkdir('../files/下载popo图片/assets')
    # 如果assets文件夹下有文件，则提示是否需要先清空文件夹
    if len(os.listdir('../files/下载popo图片/assets')) > 0:
        if input("assets文件夹下有文件，是否清空？（y/n）：").lower() == 'y':
            shutil.rmtree('../files/下载popo图片/assets')
            os.mkdir('../files/下载popo图片/assets')
    download_images()

    #弹出文件夹
    os.startfile(os.path.join(os.path.dirname(__file__),'../files/下载popo图片'))
