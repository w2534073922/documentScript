import os
import re
import pandas as pd
from pathlib import Path

# 配置项（可根据需要修改）
OUTPUT_EXCEL = "dify_脱敏对照表.xlsx"  # 输出文件名
LINK_PATTERN = re.compile(r'https?://[^\s\)]+')  # 完整链接匹配
DIFY_PATTERN = re.compile(r'(dify)', flags=re.IGNORECASE)  # 不区分大小写的dify匹配

def get_folder_path():
    """交互式获取文件夹路径"""
    while True:
        path = input("请输入MD文件所在文件夹路径（按回车使用默认示例）: ").strip()
        if not path:
            path = r"C:\Users\wb.jiangyuan03\Desktop\new文档中心\low-code-doc\docs"  # 默认示例路径
        if Path(path).is_dir():
            return path
        print(f"错误：路径不存在，请重新输入\n")

def process_file(file_path):
    """处理单个MD文件，返回脱敏记录"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
            title = get_document_title(content)
            link_ranges = [(m.start(), m.end()) for m in LINK_PATTERN.finditer(content)]
            return extract_sensitive_records(content, title, link_ranges)
    except Exception as e:
        print(f"⚠️ 跳过损坏文件 {file_path}: {str(e)}")
        return []

def get_document_title(content):
    """提取文档标题（首个#开头的行）"""
    for line in content.splitlines():
        if line.lstrip().startswith('#'):
            return line.lstrip('#').strip()[:50]  # 截断过长标题
    return "无标题文档"

def extract_sensitive_records(content, title, link_ranges):
    """提取所有非链接dify的记录"""
    records = []
    for match in DIFY_PATTERN.finditer(content):
        if is_in_link(link_ranges, match.start(), match.end()):
            continue  # 跳过链接内的dify
        segment = extract_meaningful_segment(content, match.start())
        desensitized = DIFY_PATTERN.sub('CoAgent', segment)
        records.append({
            '文档标题': title,
            '原文路径': file_path.relative_to(folder_path),  # 显示相对路径
            '含dify原文': segment,
            '脱敏后内容': desensitized
        })
    return records

def is_in_link(link_ranges, start, end):
    """判断dify是否完全在某个链接内"""
    for (l_start, l_end) in link_ranges:
        if l_start <= start and end <= l_end:
            return True
    return False

def extract_meaningful_segment(content, pos, max_len=200):
    """提取包含dify的有意义文本段（句子或短语）"""
    # 向前找句子起始（标点或换行）
    start = pos
    while start > 0 and start > pos - 100 and content[start] not in '。！？\n\r“”\'\'()[]{}':
        start -= 1
    # 向后找句子结束
    end = pos
    while end < len(content) and end < pos + 100 and content[end] not in '。！？\n\r“”\'\'()[]{}':
        end += 1
    return content[start:end].strip() or content[pos-5:pos+5].strip()  # 兜底处理

# 主流程
if __name__ == "__main__":
    print("\n=== Dify脱敏工具 v1.2 ===")
    folder_path = Path(get_folder_path())
    print(f"\n正在处理文件夹：{folder_path}\n")
    
    all_records = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.md'):
                file_path = Path(root, file)
                all_records.extend(process_file(file_path))
    
    if all_records:
        df = pd.DataFrame(all_records)
        output_path = folder_path / OUTPUT_EXCEL
        df.to_excel(output_path, index=False, engine='openpyxl')
        print(f"✅ 处理完成！共脱敏 {len(all_records)} 处")
        print(f"对照表已保存：{output_path}")
        print("\n示例数据：")
        print(df[['原文路径', '含dify原文', '脱敏后内容']].head())
    else:
        print("⚠️ 未发现需要脱敏的dify内容")
    
    input("\n按回车键退出...")    