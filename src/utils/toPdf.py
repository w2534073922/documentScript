import os
import re
import pdfplumber
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, PageBreak
from reportlab.lib.units import inch


def clean_html_tags(text):
    """
    简单清理文本中的HTML标签，确保标签闭合。

    参数:
    text (str): 输入的包含可能HTML标签的文本

    返回:
    cleaned_text (str): 清理后的文本
    """
    # 匹配未闭合的HTML标签，这里只是简单匹配常见的标签开头格式，可根据实际扩展
    pattern = r"<[a-zA-Z][^>]*$"
    while re.search(pattern, text):
        text = re.sub(pattern, "", text)
    return text


def extract_titles_and_content(pdf_path):
    """
    从给定的PDF文件中提取各级标题和正文内容。

    参数:
    pdf_path (str): 输入的PDF文件路径

    返回:
    titles (list): 提取的各级标题列表
    content (list): 提取的正文内容列表
    """
    titles = []
    content = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            lines = text.splitlines()
            page_titles = []
            page_content = []
            for line in lines:
                # 以行首字母大写且该行长度大于一定值（这里设为5）来简单判断标题，可按需优化
                if line[0].isupper() and len(line) > 5:
                    page_titles.append(line)
                else:
                    page_content.append(line)
            titles.extend(page_titles)
            content.extend(page_content)
    return titles, content


def create_pdf_with_toc(input_pdf_path, output_pdf_path):
    """
    创建包含可跳转大纲的新PDF文件。

    参数:
    input_pdf_path (str): 输入的PDF文件路径
    output_pdf_path (str): 输出的新PDF文件路径
    """
    try:
        titles, content = extract_titles_and_content(input_pdf_path)

        # 创建新的PDF对象，设置页面大小等属性
        doc = SimpleDocTemplate(output_pdf_path, pagesize=letter)

        # 获取样式表，用于设置标题和正文等样式
        styles = getSampleStyleSheet()

        # 创建一个列表用于存储要添加到PDF的元素
        story = []

        # 添加目录（可跳转大纲）
        toc = []
        level = 1
        for title in titles:
            toc.append((level, title, ""))
            level += 1 if len(title) > 10 else 0  # 简单根据标题长度判断层级（可优化）

        story.append(Paragraph("<b>目录</b>", styles["Heading1"]))
        for t in toc:
            story.append(Paragraph(t[1], styles["Normal"]))
        story.append(PageBreak())

        # 将提取的标题和内容添加到PDF元素列表中
        for title in titles:
            cleaned_title = clean_html_tags(title)
            story.append(Paragraph(cleaned_title, styles["Heading1"]))
        for line in content:
            cleaned_line = clean_html_tags(line)
            story.append(Paragraph(cleaned_line, styles["Normal"]))

        # 构建PDF文档
        doc.build(story)
        print(f"已成功生成包含大纲的新PDF文件: {output_pdf_path}")
    except Exception as e:
        print(f"生成新PDF文件过程中出现错误: {e}")


if __name__ == "__main__":
    input_pdf_path = input("请输入输入PDF文件的路径: ")
    if not os.path.exists(input_pdf_path) or not os.path.isfile(input_pdf_path):
        print("输入的PDF文件路径不存在或不是文件，请重新输入。")
    else:
        output_pdf_path = input("请输入输出新PDF文件的路径（包含文件名和.pdf扩展名）: ")
        create_pdf_with_toc(input_pdf_path, output_pdf_path)