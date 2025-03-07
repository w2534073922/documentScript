import os.path
import shutil
import urllib
from datetime import datetime

from urllib.parse import urlparse, unquote
import mistune
from bs4 import BeautifulSoup
from openpyxl.workbook import Workbook

from myConfig.MyConfig import PublicConfig
from src.utils.MyUtil import getAllDocContent

import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, \
    QMessageBox, QHBoxLayout


class DeploymentResourceForm(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.resize(600, 300)

    def initUI(self):
        layout = QVBoxLayout()

        # 创建标签和输入框
        self.oldDocFolderLabel = QLabel('旧文档文件夹:')
        self.oldDocFolderInput = QLineEdit()
        self.oldDocFolderButton = QPushButton('浏览')
        self.oldDocFolderButton.clicked.connect(self.selectOldDocFolder)

        self.newDocFolderLabel = QLabel('新文档文件夹:')
        self.newDocFolderInput = QLineEdit()
        self.newDocFolderButton = QPushButton('浏览')
        self.newDocFolderButton.clicked.connect(self.selectNewDocFolder)

        self.assetsFolderLabel = QLabel('资源文件夹（assets）:')
        self.assetsFolderInput = QLineEdit()
        self.assetsFolderButton = QPushButton('浏览')
        self.assetsFolderButton.clicked.connect(self.selectAssetsFolder)

        self.outputFolderLabel = QLabel('导出文件夹:')
        self.outputFolderInput = QLineEdit()
        self.outputFolderButton = QPushButton('浏览')
        self.outputFolderButton.clicked.connect(self.selectOutputFolder)

        self.startButton = QPushButton('开始')
        self.startButton.clicked.connect(self.onStartClicked)

        # 设置按钮的固定宽度
        button_width = 80

        # 创建水平布局并将输入框和按钮添加进去
        oldDocLayout = QHBoxLayout()
        oldDocLayout.addWidget(self.oldDocFolderLabel)
        oldDocLayout.addWidget(self.oldDocFolderInput)
        oldDocLayout.addWidget(self.oldDocFolderButton)
        self.oldDocFolderButton.setFixedWidth(button_width)

        newDocLayout = QHBoxLayout()
        newDocLayout.addWidget(self.newDocFolderLabel)
        newDocLayout.addWidget(self.newDocFolderInput)
        newDocLayout.addWidget(self.newDocFolderButton)
        self.newDocFolderButton.setFixedWidth(button_width)

        assetsLayout = QHBoxLayout()
        assetsLayout.addWidget(self.assetsFolderLabel)
        assetsLayout.addWidget(self.assetsFolderInput)
        assetsLayout.addWidget(self.assetsFolderButton)
        self.assetsFolderButton.setFixedWidth(button_width)

        outputLayout = QHBoxLayout()
        outputLayout.addWidget(self.outputFolderLabel)
        outputLayout.addWidget(self.outputFolderInput)
        outputLayout.addWidget(self.outputFolderButton)
        self.outputFolderButton.setFixedWidth(button_width)

        # 添加到主布局
        layout.addLayout(oldDocLayout)
        layout.addLayout(newDocLayout)
        layout.addLayout(assetsLayout)
        layout.addLayout(outputLayout)

        layout.addWidget(self.startButton)

        self.setLayout(layout)
        self.setWindowTitle('私有化文档增量资源导出')
        self.show()


    def selectOldDocFolder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择旧文档文件夹")
        if folder:
            self.oldDocFolderInput.setText(folder)

    def selectNewDocFolder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择新文档文件夹")
        if folder:
            self.newDocFolderInput.setText(folder)

    def selectAssetsFolder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择资源文件夹")
        if folder:
            self.assetsFolderInput.setText(folder)

    def selectOutputFolder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if folder:
            self.outputFolderInput.setText(folder)

    def onStartClicked(self):
        oldDocFolder = self.oldDocFolderInput.text()
        newDocFolder = self.newDocFolderInput.text()
        assetsFolder = self.assetsFolderInput.text()
        outputFolder = self.outputFolderInput.text()

        if not oldDocFolder or not newDocFolder or not assetsFolder or not outputFolder:
            QMessageBox.warning(self, '警告', '请填写所有字段')
            return

        try:
            run(oldDocFolder, newDocFolder, assetsFolder, outputFolder)
            QMessageBox.information(self, '成功', '操作完成')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'操作失败: {str(e)}')

class AttachmentExcel:
    title = ["文件名","原链接","转义链接","新链接"]
    def __init__(self,title):
        self.title = title

class AttachmentExcelItem:
    def __init__(self,fileName,oldLink,decodeLink,newLink):
        self.fileName = fileName
        self.oldLink = oldLink
        self.decodeLink = decodeLink
        self.newLink = newLink

def getAllDocumentMergeHTML(docFolder:str):

    markdown_text = getAllDocContent(docFolder)
    html = BeautifulSoup(mistune.html(markdown_text), 'html.parser')
    return html

def getAllDocumentImg(html:BeautifulSoup):
    # 获取所有图片名称清单
    img_tags = html.find_all('img')
    img_names = [os.path.basename(img['src']) for img in img_tags]
    return img_names

def getAllDocumentAttachment(html:BeautifulSoup):
    # 获取所有视频名称清单
    video_tags = html.find_all('source')
    video_names = [video['src'] for video in video_tags]
    a_tags = html.find_all('a')
    extensions = PublicConfig.download_supported_types
    files = []
    for a in a_tags:
        if any(a['href'].endswith(ext) for ext in extensions):
            files.append(a['href'])
    return files

    # 返回newFiles列表中存在但oldFiles中不存在的文件链接，注意，由于链接可能是经过URL编码的，所以不能直接比较字符串，应该比较解码后的文件名称。

def diffFiles(oldFiles: list, newFiles: list) -> list[str]:
    # 创建旧文件basename的集合（解码后的）
    old_basenames = set()
    for url in oldFiles:
        parsed = urlparse(url)
        path = parsed.path
        basename = path.split('/')[-1]
        decoded_basename = unquote(basename)
        old_basenames.add(decoded_basename)

    # 遍历新文件，检查basename是否不在旧集合中
    result = []
    for url in newFiles:
        parsed = urlparse(url)
        path = parsed.path
        basename = path.split('/')[-1]
        decoded_basename = unquote(basename)
        if decoded_basename not in old_basenames:
            result.append(url)

    return result

def writeExcel(diffFiles,outputPath):
    # 创建一个新的工作簿
    wb = Workbook()
    # 默认情况下，新工作簿会有一个名为'Sheet'的工作表
    ws = wb.active
    # 可以更改工作表的名字
    ws.title = "差异附件清单"
    filesList = list(
        map(lambda x: [os.path.basename(urllib.parse.unquote(x)), x, urllib.parse.unquote(x), ''], diffFiles))

    # 根据文件名进行去重
    filesList = list({sub_list[0]: sub_list for sub_list in filesList}.values())

    data = [['文件名', '原链接', '转义链接', '新链接']] + filesList
    for row in data:
        ws.append(row)
    # outputPath = input("输入导出表格的文件夹：")
    excelPath = os.path.join(outputPath, "增量附件清单_" + datetime.now().strftime("%Y%m%d%H%M%S") + ".xlsx")
    wb.save(excelPath)
    os.startfile(os.path.dirname(excelPath))
def run(oldDocFolder:str,newDocFolder:str,assetsFolder:str,outputFolder:str):
    oldHtml = getAllDocumentMergeHTML(oldDocFolder)
    newHtml = getAllDocumentMergeHTML(newDocFolder)
    oldImgList = getAllDocumentImg(oldHtml)
    newImgList = getAllDocumentImg(newHtml)
    addImgList = list(set(newImgList) - set(oldImgList))
    # print(len(addImgList))
    oldattAchmentList = getAllDocumentAttachment(oldHtml)
    # print(oldattAchmentList)
    newattAchmentList = getAllDocumentAttachment(newHtml)
    diffFilesList = diffFiles(oldattAchmentList, newattAchmentList)

    if os.path.isdir(outputFolder):
        shutil.rmtree(outputFolder)
    os.makedirs(os.path.join(outputFolder, "assets"))
    # 将assetsFolder文件夹下的addImgList图片复制到outputFolder文件夹下
    for img in addImgList:
        source_path = os.path.normpath(os.path.join(assetsFolder, img))
        target_path = os.path.normpath(os.path.join(outputFolder, "assets",img))
        # 检查源文件是否存在
        if os.path.isfile(source_path):
            # print(f"正在复制: {source_path} -> {target_path}")
            shutil.copy(source_path, target_path)  # 复制文件
        else:
            print(f"警告：文件不存在，跳过复制：{img}")

    #增量附件清生成表格
    writeExcel(diffFilesList, outputFolder)

def start():
    app = QApplication(sys.argv)
    ex = DeploymentResourceForm()
    sys.exit(app.exec())

if __name__ == '__main__':
    start()
    # start(
    #     r"C:\Users\25340\Desktop\私有化文档\docs",
    #     r"C:\Users\25340\Desktop\私有化文档\docs - 副本",
    #     r"D:\工作\文档相关\low-code-doc\assets",
    #     r"C:\Users\25340\Desktop\私有化文档\assets")