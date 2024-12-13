import os
import re
import pandas as pd


def generate_desensitization_table(md_folder_path, table_save_path):
    """
    读取指定文件夹下的md文档内容，生成文档脱敏对照表保存为Excel文件（不修改原md文档）
    :param md_folder_path: md文档所在文件夹路径
    :param table_save_path: 文档脱敏对照表保存的地址（.xlsx格式）
    """
    desensitization_table = []
    for root, dirs, files in os.walk(md_folder_path):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                doc_title = get_doc_title(content)  # 获取文档标题

                # 查找包含敏感词的文本段并记录脱敏信息（按照更细化的规则处理，排除各级标题、链接及特定包裹情况中的敏感词）
                table_entries = extract_sensitive_text(content, doc_title)
                desensitization_table.extend(table_entries)

    # 创建DataFrame并保存为Excel文件
    df = pd.DataFrame(desensitization_table, columns=["文档标题", "敏感字段列", "脱敏文案列"])
    df.to_excel(table_save_path, index=False)


def extract_sensitive_text(content, doc_title):
    """
    从文本内容中提取包含敏感词的文本段（严格按照给定规则排除各级标题和链接中的敏感词，以及被.包裹的敏感词等情况），并生成对应的脱敏对照表项
    :param content: 原始文本内容
    :param doc_title: 文档标题
    :return: 脱敏对照表项列表
    """
    table_entries = []
    # 定义敏感词和对应的脱敏替换词
    sensitive_words = {
        "网易": "公司",
        "codewave": "低代码平台"  # 按照需求替换codewave相关敏感词为"低代码平台"
    }
    # 构建正则表达式模式，用于匹配链接
    link_pattern = re.compile(r'https?://[^\s]+')
    # 构建正则表达式模式，用于匹配各级标题（这里简单匹配以#开头，可根据实际markdown标题格式调整）
    title_pattern = re.compile(r'^#+\s.*')
    # 构建正则表达式模式，用于匹配各种形式的codewave相关字符串（不区分大小写）
    codewave_pattern = re.compile(r'\bcodewave(s)?(智能开发平台)?\b', re.IGNORECASE)
    # 构建正则表达式模式，用于匹配被.包裹的codewave相关字符串（不区分大小写）
    codewave_in_quotes_pattern = re.compile(r'\.codewave(s)?(智能开发平台)?\.', re.IGNORECASE)

    for sensitive_word in sensitive_words.keys():
        if sensitive_word == "网易":
            # 构建正则表达式模式，用于匹配包含网易敏感词的文本段
            text_pattern = re.compile(r'\b' + re.escape(sensitive_word) + r'\b', re.IGNORECASE)
            matches = text_pattern.finditer(content)
            for match in matches:
                start_index = max(0, match.start() - 10)  # 计算起始索引，确保不越界
                end_index = min(len(content), match.end() + 10)  # 计算结束索引，确保不越界
                text_segment = content[start_index:end_index]  # 提取包含网易及其前后10个字符的文本段
                # 判断文本段是否属于链接或标题部分，如果是则跳过，不进行脱敏替换
                if link_pattern.search(text_segment) or title_pattern.match(text_segment):
                    continue
                desensitized_word = sensitive_words[sensitive_word]
                desensitized_text = text_segment.replace(sensitive_word, desensitized_word)
                table_entries.append([doc_title, text_segment, desensitized_text])
        elif sensitive_word == "codewave":
            codewave_matches = codewave_pattern.finditer(content)
            for match in codewave_matches:
                start_index = max(0, match.start() - 10)  # 计算起始索引，确保不越界
                end_index = min(len(content), match.end() + 10)  # 计算结束索引，确保不越界
                text_segment = content[start_index:end_index]  # 提取包含codewave及其前后10个字符的文本段
                # 判断是否在链接内或者被.包裹，如果在被.包裹的情况则跳过替换，符合需求要求
                if link_pattern.search(text_segment) or codewave_in_quotes_pattern.search(text_segment):
                    continue
                desensitized_text = text_segment.replace(match.group(0), sensitive_words[sensitive_word])
                table_entries.append([doc_title, text_segment, desensitized_text])

    return table_entries


def get_doc_title(content):
    """
    从文档内容中获取文档标题（这里简单获取第一行以#开头的内容作为标题，可根据实际情况调整）
    :param content: 文档内容
    :return: 文档标题
    """
    lines = content.split('\n')
    for line in lines:
        if line.startswith('#'):
            return line.strip()
    return ""


if __name__ == "__main__":
    md_folder_path = input("请输入md所在文件夹地址：")
    table_save_path = input("请输入对照表存储地址（.xlsx格式）：")
    generate_desensitization_table(md_folder_path, table_save_path)
    print("文档脱敏对照表生成完成！")