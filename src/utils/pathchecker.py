import os
import re


def find_md_files(directory):
    md_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))
    return md_files


def check_md_references(md_files):
    error_count = 0
    print(" . 搜索文档中的失效内部跳转...")
    for md_file in md_files:
        with open(md_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line_num, line in enumerate(lines, start=1):
                # 查找所有Markdown链接和HTML链接
                markdown_links = re.findall(r'\[.*?\]\((.*?)\)', line)
                html_links = re.findall(r'<a href="(.*?)">.*?</a>', line)
                all_links = markdown_links + html_links

                for link in all_links:
                    if link.endswith('.md') and not link.startswith(('http://', 'https://')):
                        # 构建引用文件的绝对路径
                        link_path = os.path.normpath(os.path.join(os.path.dirname(md_file), link))
                        if not os.path.exists(link_path):
                            error_count += 1
                            print(f"文件: {md_file}")
                            print(f"    行数 {line_num}: {link}")
    print(f"合计 {error_count} 个错误引用链接")


if __name__ == "__main__":
    directory = input("请输入文件路径: ")
    if os.path.exists(directory):
        md_files = find_md_files(directory)
        check_md_references(md_files)
    else:
        print("输入的路径不存在，请检查后重新输入。")
