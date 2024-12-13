import os
import pandas as pd
import chardet
import re


def replace_links(table_file_path, md_folder_path):
    """
    根据表格中的原链接和新链接替换文件夹下所有文档中的链接
    :param table_file_path: 表格文件路径（这里支持Excel格式等）
    :param md_folder_path: 存放文档的文件夹地址
    """
    # 用于存储原链接和新链接对应关系的字典
    link_mapping = {}
    try:
        # 使用pandas读取Excel文件（支持.xlsx等格式），这里假设原链接在第一列，新链接在第二列，可根据实际调整列索引
        df = pd.read_excel(table_file_path)
        for index, row in df.iterrows():
            original_link = row.iloc[1]
            new_link = row.iloc[2]
            link_mapping[original_link] = new_link
    except Exception as e:
        print(f"读取表格文件时出现错误: {e}，请检查文件格式及内容是否正确。")
        return

    total_replace_count = 0  # 记录实际替换总数量
    success_replace_count = 0  # 记录替换成功数量
    success_replace_content = []  # 记录替换成功的原链接、新链接及文档名称
    failed_replace_count = 0  # 记录真正替换失败数量
    failed_replace_content = []  # 记录替换失败的原链接、对应文档名称

    for root, dirs, files in os.walk(md_folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_extension = os.path.splitext(file)[-1].lower()  # 获取文件扩展名并转为小写
            if file_extension not in ['.md']:  # 可根据实际支持的文本文件类型添加更多扩展名
                continue  # 跳过非文本文件
            doc_name = file
            # 检测文档文件编码
            with open(file_path, 'rb') as f:
                encoding_result = chardet.detect(f.read())
            detected_encoding = encoding_result.get('encoding')
            if detected_encoding is None:
                print(f"无法检测文档 {file_path} 的编码格式，请检查文件是否正确。")
                continue
            try:
                with open(file_path, 'r', encoding=detected_encoding) as f:
                    content = f.read()
            except UnicodeDecodeError:
                print(f"按照检测的编码 {detected_encoding} 无法正确读取文档 {file_path}，尝试使用其他通用编码进行读取。")
                fallback_encoding = 'latin-1'
                with open(file_path, 'r', fallback_encoding) as f:
                    content = f.read()

            # 使用正则表达式更精准地匹配和替换链接（假设文档中的链接格式比较规范，可根据实际调整正则表达式）
            link_pattern = re.compile(r'\[.*?\]\((.*?)\)')  # 匹配类似Markdown链接格式的正则表达式，如果链接格式不同需调整

            def replace_link(match):
                nonlocal success_replace_count, failed_replace_count
                old_link = match.group(1)
                if old_link in link_mapping:
                    success_replace_count += 1
                    success_replace_content.append((doc_name, old_link, link_mapping[old_link]))
                    try:
                        return match.group(0).replace(old_link, link_mapping[old_link])
                    except:
                        failed_replace_count += 1
                        failed_replace_content.append((doc_name, old_link))
                        return match.group(0)
                return match.group(0)

            updated_content = link_pattern.sub(replace_link, content)
            if updated_content!= content:
                current_replace_count = 0
                for key in link_mapping.keys():
                    current_replace_count += updated_content.count(key)
                total_replace_count += current_replace_count

            # 将替换后的内容写回原文件
            with open(file_path, 'w', encoding=detected_encoding) as f:
                f.write(updated_content)

    print(f"实际替换总数量: {total_replace_count}")
    print(f"替换成功数量: {success_replace_count}")
    print("替换成功的内容（文档名称 - 原链接 -> 新链接）:")
    for item in success_replace_content:
        print(f"{item[0]} - {item[1]} -> {item[2]}")
    print(f"替换失败数量: {failed_replace_count}")
    print("替换失败的内容（文档名称 - 原链接 -> 新链接）:")
    for item in failed_replace_content:
        print(f"{item[0]} - {item[1]}")


if __name__ == "__main__":
    table_file_path = input("请输入表格文件的地址（CSV格式等）：")
    md_folder_path = input("请输入存放文档的文件夹地址：")
    replace_links(table_file_path, md_folder_path)
    print("链接替换完成！")