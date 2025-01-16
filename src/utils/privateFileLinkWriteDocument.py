import os.path
import re

import pandas as pd

from myConfig import MyConfig
from src.utils.MyUtil import getAllMarkdownFileList


def load_link_mapping(excel_path):
    # 加载Excel文件，获取原链接和新链接的映射关系
    df = pd.read_excel(excel_path, dtype=str)  # 强制所有数据为字符串类型
    df.fillna('', inplace=True)  # 将NaN替换为空字符串

    # 创建映射字典，过滤掉空值
    mapping = {old.strip(): new.strip() for old, new in zip(df['原链接'], df['新链接']) if old and new}

    return mapping

def replace_links_in_files(file_paths, link_mapping):
    # 对每个文件路径进行处理
    for file_path in file_paths:
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # 替换文件中的链接
            for old_link, new_link in link_mapping.items():
                # 使用正则表达式做全局替换
                content = re.sub(re.escape(old_link), new_link, content)

            # 将更新后的内容写入文件
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)

            print(f"修改中: {file_path}")
        except Exception as e:
            print(f"发生错误： {file_path}: {e}")


def start():
    excel_path = input("请输入填写了新链接后的Excel文件路径：")
    mdFileList = getAllMarkdownFileList(os.path.join(MyConfig.PrivateConfig.repoPath,"docs"))
    link_mapping = load_link_mapping(excel_path)
    replace_links_in_files(mdFileList, link_mapping)

if __name__ == '__main__':
    start()

