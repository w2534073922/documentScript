
import os
import requests

from myConfig import MyConfig
from myConfig.MyConfig import PublicConfig


def get7zPath():
    z7FilePath = os.path.join(PublicConfig.project_root,"files/工具软件/7z.exe")
    # 如果files/工具软件目录下没有7z.exe，就先下载文件
    if not os.path.exists(z7FilePath):
        download_url = "https://www.7-zip.org/a/7zr.exe"
        # 创建目录如果不存在
        os.makedirs(os.path.dirname(z7FilePath), exist_ok=True)

        # 下载文件
        response = requests.get(download_url, stream=True)
        if response.status_code == 200:
            with open(z7FilePath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
            print("7z.exe 下载完成")
        else:
            print("7z下载失败，状态码:", response.status_code)
            exit()
    return z7FilePath

import subprocess
import os

def split_compression(source_folder, output_folder, file_size_limit=50 * 1024 * 1024):
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 构建7z命令
    base_name = os.path.join(output_folder, "assets")
    command = [
        get7zPath(), 'a',  # 添加到归档
        f'{base_name}.tar.gz',  # 输出文件名
        source_folder,  # 源文件夹
        f'-v{file_size_limit}b',  # 分卷大小
        #'-tgz'  # 使用tar格式
    ]

    # 执行命令
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("压缩成功")
    except subprocess.CalledProcessError as e:
        print(f"压缩失败: {e.stderr.decode()}")


if __name__ == '__main__':
    split_compression(r"D:\工作\dev\documentScript\files\测试打包", r"D:\工作\dev\documentScript\files\AAAAA")