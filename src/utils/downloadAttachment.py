import os
import shutil
import urllib
from urllib.parse import unquote

import mistune
import requests
from bs4 import BeautifulSoup
from openpyxl.workbook import Workbook

from myConfig import MyConfig
from myConfig.MyConfig import PrivateConfig, PublicConfig
from src.utils import MyUtil

def start():
    markdown_text = MyUtil.getAllDocContent(os.path.join(PrivateConfig.repoPath, "docs"))

    # markdown转HTML
    html = BeautifulSoup(mistune.html(markdown_text), 'html.parser')
    # 获取html文本中的所有a标签，提取出满足特定后缀的链接
    a_tags = html.find_all('a')

    extensions = PublicConfig.download_supported_types
    links = [a['href'] for a in a_tags if any(a['href'].endswith(ext) for ext in extensions)]
    print(f"搜索到{len(links)}个附件")
    video_tags = html.find_all('source')
    video_links = []
    for video_tag in video_tags:
        video_links.append(video_tag['src'])
    if input("是否包含视频？(y)：") == "y":
        # 合并列表
        links.extend(video_links)
        print(f"搜索到{len(video_links)}个视频")

    # 创建一个目录用于保存下载的文件
    download_dir = os.path.join(PublicConfig.project_root, 'files/下载文档中心附件')
    os.makedirs(download_dir, exist_ok=True)

    # 如果目录下有文件则提示是否需要先清空
    if len(os.listdir(download_dir)) > 0:
        if input("下载目录下有文件，是否清空？（y/n）：").lower() == 'y':
            shutil.rmtree(download_dir)
            os.mkdir(download_dir)

    if input("下载文件(y)  生成excel(n)：").lower() == 'y':
        isOnlyDownload = True
    else:
        isOnlyDownload = False

    for link in links:
        # URL解码
        decoded_link = urllib.parse.unquote(link)
        # 获取文件名
        file_name = os.path.basename(decoded_link)
        if isOnlyDownload:
            # 定义文件保存路径
            file_path = os.path.join(download_dir, file_name)
            print(decoded_link)
            # 下载文件
            response = requests.get(decoded_link)
            if response.status_code == 200:
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                print(f"下载完成: {file_name}")
            else:
                print(f"下载失败: {file_name}, 状态码: {response.status_code}")
    if not isOnlyDownload:
        # 写表
        # 创建一个新的工作簿
        wb = Workbook()
        # 默认情况下，新工作簿会有一个名为'Sheet'的工作表
        ws = wb.active
        # 可以更改工作表的名字
        ws.title = "Data"

        new_list = list(
            map(lambda x: [os.path.basename(urllib.parse.unquote(x)),x,urllib.parse.unquote(x),''], links))
        # print(new_list)
        # print(type([['文件名', '原链接', '新链接']]))
        # print(type(new_list))
        # 写入一些数据
        data = [['文件名', '原链接','转义链接', '新链接']]+new_list
        for row in data:
            ws.append(row)
        # 保存工作簿
        outputPath = input("输入表格输出路径：")
        wb.save( os.path.join(outputPath,"文件链接清单.xlsx"))

    # 弹出文件夹
    os.startfile(download_dir)
