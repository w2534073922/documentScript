import os

import requests
from dataclasses import dataclass
from typing import List
from dataclasses_json import dataclass_json

from src.utils.MyUtil import getAllMarkdownFileByFolder, getAllMarkdownFileList
import re
import logging

# 设置日志级别
# logging.basicConfig(level=logging.DEBUG)

@dataclass_json
@dataclass
class ImgInfo:
    name: str
    url: str

@dataclass_json
@dataclass
class ImgList:
    """Request"""
    list: List[ImgInfo]
    total: int

def getOnlineImgList() -> ImgList:
    url = "https://documentgroup-community1.app.codewave.163.com//rest/getDocImages?getUrl=true"
    response = requests.request("POST", url)
    return ImgList.from_json(response.text)

def replaceLocalImageWithOnline(content: str, imgList: List[ImgInfo]) -> str:
    # 创建一个字典来快速查找图片信息
    img_dict = {img.name: img.url for img in imgList}
    imgPattern = r"!\[.*?\]\(([^)]*\.\.[^)]*)\)|<img.*?src=[\"\'](.*?)[\"\'].*?>"

    def replace_path(match):
        if match.group(1) is not None:
            path = match.group(1)
        if match.group(2) is not None:
            path = match.group(2)
        # print("path = "+path)
        if path.startswith('http://') or path.startswith('https://'):
            # 如果路径是在线地址，则不进行替换。
            return match.group(0)
        imgName = os.path.basename(path)
        if imgName in img_dict:
            newPath = match.group(0).replace(path, img_dict[imgName])
            return newPath
        else:
            print('字典中找不到')
            return match.group(0)

    return re.sub(imgPattern, replace_path, content)
def start():
    docPath = input("请输入文档文件夹地址，将会直接修改原文件（如果是文档项目文件夹，则应该输入docs路径）：\n")
    docList = getAllMarkdownFileList(docPath)
    print(f"搜索到{len(docList)}个文档")
    # 使用replaceLocalImageWithOnline修改所有docList
    imgList = getOnlineImgList()
    for doc in docList:
        #输出进度数量
        print("处理中请稍后："+str(docList.index(doc)+1)+"/"+str(len(docList)))
        # 以读模式打开文件读取内容
        with open(doc, "r", encoding="utf-8") as file:
            content = file.read()

        # 以写模式打开文件写入修改后的内容
        newContent = replaceLocalImageWithOnline(content, imgList.list)
        if newContent != content:
            with open(doc, "w", encoding="utf-8") as file:
                file.write(newContent)
    print("替换图片为在线链接完成")


if __name__ == '__main__':
    start()

