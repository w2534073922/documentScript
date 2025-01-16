import json
import os
import re
import shutil
import time

import commonmark
import markdown_it
import pdfkit
from bs4 import BeautifulSoup
from flask import request, Response

from myConfig import MyConfig
from myConfig.MyConfig import PublicConfig, PrivateConfig
from src.utils.MyUtil import getAllMarkdownFileByFolder


class PdfParam:
    def __init__(self, markdownPath, pdfPath,isMerge,isRemoveDigit,isAddBookmark,isGenerateHtml,fontSize):
        self.markdownPath = markdownPath
        self.pdfPath = pdfPath
        self.isMerge = isMerge
        self.isRemoveDigit = isRemoveDigit
        self.isAddBookmark = isAddBookmark
        self.isGenerateHtml = isGenerateHtml
        self.fontSize = fontSize
def markdownToHtml(input_file_path, output_file_path):

    # 将 Markdown 转换为 HTML
    with open(input_file_path, 'r', encoding='utf-8') as f:
        markdown_text = f.read()

    # parser = commonmark.Parser()
    # renderer = commonmark.HtmlRenderer()
    # ast = parser.parse(markdown_text)
    # html_content = renderer.render(ast)

    html_content = markdown_it.MarkdownIt().enable('table').render(markdown_text)

    #对html进行格式化
    html_content = BeautifulSoup(html_content, 'html.parser').prettify()
    # print(html_content)
    mate = f'''
<head>
    <meta charset="utf-8" />
    <link rel="stylesheet" type="text/css" href="{PublicConfig.project_root}\config\pdf.css">
</head>
    '''
    html_content = mate + html_content

    #将details标签全部展开
    soup = BeautifulSoup(html_content, 'html.parser')
    details_tags = soup.find_all('details')
    for detail_tag in details_tags:
        detail_tag.attrs['open'] = True

    #移除文档中的创建人
    divs_to_remove = soup.find_all('div', style="text-align: right;font-size: 14px;")
    for div in divs_to_remove:
        div.decompose()

    #将a标签中的相对引用文档链接替换成文档中心链接
    # for a_tag in soup.find_all('a'):
    #     if a_tag.name == 'a' and a_tag.get('href') and a_tag['href'].endswith('.md'):
    #         base_url = "https://community.codewave.163.com/CommunityParent/fileIndex?filePath="
    #         relative_path = a_tag['href']
    #         # 使用正则表达式去除开头的 ../ 或 ./
    #         relative_path = re.sub(r'^(\.\./)+', '', relative_path)
    #         relative_path = re.sub(r'^\./', '', relative_path)
    #         new_href = base_url + relative_path
    #         a_tag['href'] = new_href

    html_content = soup.prettify()

    html_content = replaceAbsolutePath(html_content)
    # HTML内容写入到输出文件中
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    return output_file_path

def html_to_pdf(html_file, pdf_file):
    if not os.path.isfile(PrivateConfig.wkhtmltopdf):
        exit("请先安装wkhtmltopdf，并在配置文件中填入路径")
    config = pdfkit.configuration(wkhtmltopdf=PrivateConfig.wkhtmltopdf)
    # pdfkit.from_file(html_file, pdf_file, configuration=config,options={"enable-local-file-access":True})

    html_content = open(html_file, 'r', encoding='utf-8').read()
    # print(html_content)
    pdfkit.from_string(html_content, pdf_file, configuration=config,options={"enable-local-file-access":True})

#图片路径统一转换为绝对路径
def replaceAbsolutePath(content):
    def replace_path(match):
        if match.group(1)  is not None:
            relative_path = match.group(1)
        if match.group(2)  is not None:
            relative_path = match.group(2)
        label = str(match.group(0))
        newPath = label.replace(relative_path,""+str(os.path.join(PrivateConfig.repoPath,"assets" ,os.path.basename(relative_path))))
        return newPath

    imgPattern = r"!\[.*?\]\(([^)]*\.\.[^)]*)\)|<img.*?src=[\"\'](.*?)[\"\'].*?>"
    result = re.sub(imgPattern, replace_path, content)
    # print(result)
    return result

def batchToPdf(markdownFolder, outputFolder):
    #判断输出文件夹下是否有文件，如果有则让用户选择是否需要清空
    if os.listdir(outputFolder):
        print("输出文件夹不为空，是否清空？(y/n)")
        choice = input()
        if choice.lower() == 'y':
            shutil.rmtree(outputFolder)
            os.makedirs(outputFolder)

    # 清空或创建输出文件夹
    if os.path.exists(outputFolder):
        shutil.rmtree(outputFolder)
    os.makedirs(outputFolder)

    # 获取markdown文件路径列表
    markdownFileList = getAllMarkdownFileByFolder(markdownFolder)
    total_files = len(markdownFileList)  # 获取总文件数

    for index, markdownFile in enumerate(markdownFileList, start=1):
        # 获取文件名，不带后缀
        fileNameWithoutExtension = os.path.splitext(os.path.basename(markdownFile))[0]
        # 计算相对路径（不包括文件名）
        relativeDir = os.path.relpath(os.path.dirname(markdownFile), markdownFolder)
        # 创建输出文件夹结构
        outputDir = os.path.join(outputFolder, relativeDir)
        os.makedirs(outputDir, exist_ok=True)
        # 输出文件路径
        outputFilePath = os.path.join(outputDir, fileNameWithoutExtension + '.pdf')
        # 转换为HTML并生成PDF
        html_to_pdf(markdownToHtml(markdownFile, outputFilePath), outputFilePath)

        # 打印进度
        print(f"当前进度: {index}/{total_files}\tPDF生成成功：{outputFilePath}")



def startWeb():
    from flask import Flask
    from flask_cors import CORS
    app = Flask(__name__)
    CORS(app)
    @app.route('/outputPdf',methods=['GET', 'POST','OPTIONS'])
    def outputPdf():
        if request.method == "OPTIONS":  # 处理预检请求
            response = Response()
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            return response
        # 返回body内容
        def event_stream(content):
            while True:
                data = content
                yield f"{data}\n\n"
                time.sleep(3)
        print(json.dumps(request.json))
        return Response(event_stream(json.dumps(request.json)), mimetype="text/event-stream")

    app.run(port=8877)

def start():
    markdownFloder = input("请输入markdown文件夹路径：")
    outputFolder = input("请输入输出文件夹路径：")
    batchToPdf(markdownFloder, outputFolder)

if __name__ == '__main__':
    # input_file = r"D:\工作\文档相关\low-code-doc\docs\40.扩展与集成\10.扩展开发方式\30.服务端扩展开发\10.依赖库开发\10.服务端依赖库开发快速入门.md"
    # output_file = r"D:\工作\文档相关\low-code-doc\docs\40.扩展与集成\10.扩展开发方式\30.服务端扩展开发\10.依赖库开发\10.服务端依赖库开发快速入门.html"
    # markdownToHtml(input_file, output_file)
    #
    # input_file = r"D:\工作\文档相关\low-code-doc\docs\40.扩展与集成\10.扩展开发方式\30.服务端扩展开发\10.依赖库开发\10.服务端依赖库开发快速入门.html"
    # output_file = r"D:\工作\文档相关\low-code-doc\docs\40.扩展与集成\10.扩展开发方式\30.服务端扩展开发\10.依赖库开发\10.服务端依赖库开发快速入门.pdf"
    # html_to_pdf(input_file, output_file)

    # startWeb()
    pass
