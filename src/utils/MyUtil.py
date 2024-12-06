import datetime
import os
import re
import shutil
import tarfile
import threading
from urllib.parse import quote_plus

import requests

from config import MyConfig


# 复制文件夹，并跳过指定文件或文件夹
def copyFolder(src_folder, dest_folder, skip_list):

    if not os.path.exists(src_folder) or not os.path.isdir(src_folder):
        print(f"源文件夹 {src_folder} 不存在或不是一个文件夹")
        exit()

    # 创建目标文件夹
    os.makedirs(dest_folder, exist_ok=True)

    # 遍历源文件夹中的所有子文件夹和文件
    for root, dirs, files in os.walk(src_folder):
        # 构建目标文件夹中的对应子文件夹路径
        dest_root = os.path.join(dest_folder, os.path.relpath(root, src_folder))

        # 复制子文件夹到目标文件夹中，但跳过在skip_list中的
        dirs[:] = [d for d in dirs if d not in skip_list]
        os.makedirs(dest_root, exist_ok=True)

        # 复制文件到目标文件夹中，但跳过在skip_list中的
        for file in files:
            if file not in skip_list:
                src_file = os.path.join(root, file)
                dest_file = os.path.join(dest_root, file)
                shutil.copy2(src_file, dest_file)  # 使用copy2保留元数据

# 为文件夹下的markdown文件添加样式
# 输入参数 markdownFolder：markdown文件所在的文件夹
# 输入参数 styleText：样式文本
def batchAddMarkdownStyle(markdownFolder,styleText):
    if styleText == "" or styleText == None:
        styleText = MyConfig.PublicConfig.markdownStyle
    for root, dirs, files in os.walk(markdownFolder):
        for file in files:
            if file.endswith(".md"):
                filePath = os.path.join(root, file)
                with open(filePath, 'r', encoding='utf-8') as f:
                    content = f.read()
                with open(filePath, 'w', encoding='utf-8') as f:
                    f.write(content+'\n'+styleText)

# 压缩文件列表或文件夹为tar.gz文件
def compress_to_tar_gz(Folder_or_fileList, output_path,fileName, packName):
    # 确保输出路径存在
    os.makedirs(output_path, exist_ok=True)

    # 构建完整的输出文件路径
    output_file = os.path.join(output_path, f"{fileName}.tar.gz")

    # 检查输入是否为单个目录
    if isinstance(Folder_or_fileList, str) and os.path.isdir(Folder_or_fileList):
        files_to_compress = [os.path.join(Folder_or_fileList, file) for file in os.listdir(Folder_or_fileList)]
    else:
        files_to_compress = Folder_or_fileList

    # 创建一个新的tar.gz文件
    with tarfile.open(output_file, "w:gz") as tar:
        # 添加文件到tar.gz中
        for file in files_to_compress:
            arcname = os.path.relpath(file, start=os.path.dirname(file))
            tar.add(file, arcname=os.path.join(packName, arcname))



# 合并所有md文档
# source_dir = 'F:\\网易\\文档\\打包\\1018临时3.3\\docs'
    # output_dir = 'F:\\网易\\文档\\打包\\1018临时3.3\\输出结果_' + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # link = 'https://static-vusion.nos-eastchina1.126.net/markdown_image'
    # replace_image_paths(mergeDoc(source_dir,output_dir),link)

def mergeDoc(docs_folder, output_folder=None,isDebug=None):
    # 屏蔽的文件夹和文件列表
    skip_items = [".vuepress", "999.others",  "README.md"]
    # 最后导出的文件名 后缀是创建时间
    markdownName = "Codewave智能开发平台使用手册_"+datetime.datetime.now().strftime("%Y-%m%d-%H%M")+".md"
    # 拼接输出文件的绝对路径
    output_markdown = os.path.join(output_folder,markdownName)
    os.makedirs(os.path.dirname(output_markdown), exist_ok=True)
    # 打开输出文件（文件不存在所以是创建），设置编码为utf-8
    with open(output_markdown, 'w', encoding='utf-8') as output:
        # 遍历当前文件夹下的所有文件
        for filename in os.listdir(docs_folder):
            # 判断文件是否以.md结尾
            if filename.endswith('.md'):
                # 构建文件的完整路径
                filepath = os.path.join(docs_folder, filename)
                # 打开当前markdown文件，编码为utf-8
                with open(filepath, 'r', encoding='utf-8') as file:
                    # 读取文件内容，并写入输出文件
                    output.write(file.read())
                # 每个markdown文件之间添加一个换行符
                output.write('\n\n')
        # 遍历根文件夹及其子文件夹
        for foldername, subfolders, filenames in os.walk(docs_folder):
            # 判断当前文件夹或文件是否在屏蔽列表中
            if any(blocked_item in foldername or blocked_item in filenames for blocked_item in skip_items):
                continue
            # 遍历当前文件夹下的所有文件
            for filename in filenames:
                # 判断文件是否以.md结尾
                if filename.endswith('.md'):
                    # 构建文件的完整路径
                    filepath = os.path.join(foldername, filename)
                    # 打开当前markdown文件，编码为utf-8
                    with open(filepath, 'r', encoding='utf-8') as file:
                        # 读取文件内容，并写入输出文件
                        output.write(file.read())
                    # 每个markdown文件之间添加一个换行符
                    output.write('\n\n')
    return output_markdown

#获取文件夹下所有markdown文件列表
def getAllMarkdownFileByFolder(markdown_folderdocs_folder):
    markdow_file_list = []
    for root, _, files in os.walk(markdown_folderdocs_folder):
        for file in files:
            if file.endswith('.md'):
                markdow_file_list.append(os.path.join(root, file))
    return markdow_file_list
def getAllDocContent(docs_folder):
    # 屏蔽的文件夹和文件列表
    skip_items = [".vuepress", "999.others", "README.md"]
    content = ""
    # 遍历当前文件夹下的所有文件
    for filename in os.listdir(docs_folder):
        # 判断文件是否以.md结尾
        if filename.endswith('.md'):
            # 构建文件的完整路径
            filepath = os.path.join(docs_folder, filename)
            # 打开当前markdown文件，编码为utf-8
            with open(filepath, 'r', encoding='utf-8') as file:
                # 读取文件内容
                content += file.read()
    # 遍历根文件夹及其子文件夹
    for foldername, subfolders, filenames in os.walk(docs_folder):
        # 判断当前文件夹或文件是否在屏蔽列表中
        if any(blocked_item in foldername or blocked_item in filenames for blocked_item in skip_items):
            continue
        # 遍历当前文件夹下的所有文件
        for filename in filenames:
            # 判断文件是否以.md结尾
            if filename.endswith('.md'):
                # 构建文件的完整路径
                filepath = os.path.join(foldername, filename)
                # 打开当前markdown文件，编码为utf-8
                with open(filepath, 'r', encoding='utf-8') as file:
                    # 读取文件内容
                    content += file.read()
    return content

def replace_image_paths(markdown_file, link):
    # 读取markdown文件内容
    with open(markdown_file, 'r', encoding='utf-8') as file:
        content = file.read()
    # 替换图片地址
    content = re.sub(r'!\[.*?\]\((\.\./)*assets/([^)]+)\)', r'![\g<1>](%s/\g<2>)' % link, content)
    content = re.sub(r'<img src="(\.\./)*assets/([^"]+)"', r'<img src="%s/\g<2>"' % link, content)
    # 写回markdown文件
    with open(markdown_file, 'w', encoding='utf-8') as file:
        file.write(content)


# 根据txt里的图片链接下载图片
def downloadImgByTxt():


    # 设置cookie
    cookie = "hb_MA-8D32-CBB074308F88_source=docs.popo.netease.com; hb_MA-89F6-A71EC58B127E_source=login.netease.com; hb_MA-809E-C9B7A6CD76FA_source=km.netease.com; COSPREAD_SESSIONID=eb725228-aa99-4b45-858a-38ed03b33df4; SESSION=ZWI3MjUyMjgtYWE5OS00YjQ1LTg1OGEtMzhlZDAzYjMzZGY0; hb_MA-93E2-9647F5DD033F_source=login.netease.com; hb_MA-8391-8FFD554DBEE5_source=aigc-api-demo.hz.netease.com"
    # 设置图片保存路径
    save_path = "F:\\MyPython\\低代码文档脚本\\files\\ImgDownload"
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    # 设置图片命名规则
    name_rule = "liuchenggaishu_"  # "link_name" 或 "order"

    # 读取链接列表并过滤空值
    with open("F:\\MyPython\\低代码文档脚本\\files\\imgLink.txt", "r") as f:
        links = [link.strip() for link in f if link.strip()]

    # 统计下载的文件数量
    download_count = 0


    # 下载图片的函数
    def download_image(link, i):
        try:
            # 检测cookie是否有效
            response = requests.get(link, stream=True, headers={"Cookie": cookie}, allow_redirects=False)
            if response.status_code == 302:
                print(f"Cookie失效了！")
                return
            # 获取图片名称
            if name_rule == "link_name":
                file_name = link.split('path=')[1]
                file_name = quote_plus(file_name)
            else:
                file_name = f"{name_rule}{i + 1}.png"

            # 下载图片
            response = requests.get(link, headers={"Cookie": cookie})
            with open(os.path.join(save_path, file_name), "wb") as f:
                f.write(response.content)
                print(f"已下载图片：{file_name}")
                global download_count
                download_count += 1
        except Exception as e:
            print("出现问题")
            print("链接：" + link)
            print("file_name -> " + file_name)
            print(e)


    # 创建多线程并下载图片
    threads = []
    for i, link in enumerate(links):
        thread = threading.Thread(target=download_image, args=(link, i))
        thread.start()
        threads.append(thread)

    # 等待所有线程执行完毕
    for thread in threads:
        thread.join()

    print("图片下载完成！")
    print(f"下载的文件数量：{download_count}")
    print(f"链接数量：{len(links)}")


def removeInvalidImg(folder_path):

    imgPattern = r"!\[.*?\]\((.*?)\)|<img.*?src=[\"\'](.*?)[\"\'].*?>"
    skip_items = [".vuepress", "999.others", "README.md", "99.参考"]
    for root, dirs, files in os.walk(os.path.join(folder_path, "docs")):
        # 跳过该文件/夹
        if any(blocked_item in root or blocked_item in files for blocked_item in skip_items):
            continue

    #如果输入docs则工作目录为上一级，否则不变

    #

if __name__ == '__main__':
    print(getAllDocContent())
