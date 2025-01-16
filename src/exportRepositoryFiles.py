import json
import sys
import tarfile
from collections import OrderedDict
import git
import os
import shutil
from datetime import datetime
from PySide6.QtCore import QDateTime, Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import QApplication, QMessageBox, QFileDialog, QHBoxLayout, QPushButton, QLabel, QCheckBox, \
    QLineEdit, QDateTimeEdit, QVBoxLayout, QDialog
from myConfig import MyConfig
from myConfig.MyConfig import PrivateConfig, PublicConfig
from src.utils import MyUtil, z7_pack


class OutputRepoForm:
    def __init__(self,startCommitTime:int, endCommitTime:int, branchList:list[str], isOutputDoc:bool, isAddDocStyle:bool,export_directory:str):
        self.startCommitTime = startCommitTime
        self.endCommitTime = endCommitTime
        self.branchList = branchList
        self.isOutputDoc = isOutputDoc
        self.isAddDocStyle = isAddDocStyle
        self.export_directory = export_directory

    def __str__(self):
        data_dict = {key: value for key, value in self.__dict__.items()}
        return json.dumps(data_dict, indent=4, ensure_ascii=False)

class MyForm(QDialog):
    def __init__(self):
        super().__init__()
        self.resule = None  # 新增成员变量存储表单数据
        self.init_ui()

    def init_ui(self):

        # imgBase64Str = ''
        # # 解码 base64 字符串
        # byte_data = base64.b64decode(imgBase64Str)
        # # 将字节数据转换为 QByteArray
        # q_byte_array = QByteArray(byte_data)
        # # 从 QByteArray 创建 QPixmap
        # pixmap = QPixmap()
        # pixmap.loadFromData(q_byte_array)

        # 图片标签
        # image_label = QLabel(self)
        # image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../ui/img/图片.png')
        # pixmap = QPixmap(image_path)  # 替换为实际的图片路径
        # image_label.setPixmap(pixmap.scaledToWidth(250))  # 设置图片大小
        # image_label.setAlignment(Qt.AlignCenter)  # 居中显示

        # 创建表单布局
        form_layout = QVBoxLayout()

        if os.path.exists(PrivateConfig.repoPath):
            if os.path.exists(os.path.join(PrivateConfig.repoPath, '.git')):
                self.text_label2 = QLabel(f"仓库路径：\t{PrivateConfig.repoPath}")
            else:
                self.text_label2 = QLabel(f"仓库路径：\t{PrivateConfig.repoPath} （该文件不是git仓库）")
        else:
            self.text_label2 = QLabel(f"仓库路径：\t{PrivateConfig.repoPath} （无效路径）")


        self.text_label2.setFixedHeight(20)
        form_layout.addWidget(self.text_label2)

        # 开始日期时间选择器
        self.start_datetime_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.start_datetime_edit.setCalendarPopup(True)
        self.start_datetime_edit.setDateTime(QDateTime.fromString(PrivateConfig.startCommitTime, "yyyy-MM-dd HH:mm:ss"))
        start_datetime_layout = QHBoxLayout()
        start_datetime_layout.addWidget(QLabel("开始日期时间:"))
        start_datetime_layout.addWidget(self.start_datetime_edit)
        form_layout.addLayout(start_datetime_layout)

        # 结束日期时间选择器
        self.end_datetime_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.end_datetime_edit.setCalendarPopup(True)
        self.end_datetime_edit.setDateTime(QDateTime.fromString(PrivateConfig.endCommitTime, "yyyy-MM-dd HH:mm:ss"))
        end_datetime_layout = QHBoxLayout()
        end_datetime_layout.addWidget(QLabel("结束日期时间:"))
        end_datetime_layout.addWidget(self.end_datetime_edit)
        form_layout.addLayout(end_datetime_layout)

        # # 创建表单项用于展示文本
        # self.text_label = QHBoxLayout()
        # label_name = QLabel("表单项名称")
        # label_content = QLabel("表单项内容")
        # self.text_label.addWidget(label_name)
        # self.text_label.addWidget(label_content)
        # form_layout.addLayout(self.text_label)



        # 文件夹选择
        self.folder_input = QLineEdit()
        choose_folder_button = QPushButton("选择文件夹")
        choose_folder_button.clicked.connect(self.choose_folder)
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(QLabel("导出的文件夹路径:"))
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(choose_folder_button)
        form_layout.addLayout(folder_layout)

        #是否需要导出资源文件
        self.is_output_assets_checkbox = QCheckBox("导出资源文件压缩包")
        self.is_output_assets_checkbox.setChecked(True)
        # 设置为只读
        self.is_output_assets_checkbox.setEnabled(False)
        form_layout.addWidget(self.is_output_assets_checkbox)

        #是否需要导出文档压缩包
        self.is_output_doc_checkbox = QCheckBox("导出文档压缩包")
        self.is_output_doc_checkbox.setChecked(True)
        form_layout.addWidget(self.is_output_doc_checkbox)

        self.add_doc_style_checkbox = QCheckBox("为文档添加统一样式")
        self.add_doc_style_checkbox.setChecked(True)

        # 当第一个选择框被选中时，第二个选择框才显示，否则不显示第二个选择框
        self.is_output_doc_checkbox.stateChanged.connect(
            lambda:
                self.add_doc_style_checkbox.setVisible(
                    self.is_output_doc_checkbox.isChecked()
                )
        )
        if self.is_output_doc_checkbox.isChecked():
            form_layout.addWidget(self.add_doc_style_checkbox)

        # 多选框
        self.checkboxes = []
        options = PrivateConfig.branchList
        checkbox_layout = QHBoxLayout()
        checkbox_layout.addWidget(QLabel("分支:"))
        for option in options:
            checkbox = QCheckBox(option)
            checkbox_layout.addWidget(checkbox)
            self.checkboxes.append(checkbox)
        form_layout.addLayout(checkbox_layout)

        # 确定按钮
        self.submit_button = QPushButton("开始导出")
        self.submit_button.clicked.connect(self.validate_and_submit)
        form_layout.addWidget(self.submit_button)
        #修改按钮的字体大小。
        self.submit_button.setFont(QFont("Arial", 16))

        # 将图片和表单布局组合在一起
        main_layout = QHBoxLayout()
        #main_layout.addWidget(image_label)
        main_layout.addLayout(form_layout)

        # 设置主布局
        self.setLayout(main_layout)
        self.setWindowTitle('从仓库中导出图片或文档')
        self.setFont(QFont("Arial", 12))  # 设置字体和大小
        self.resize(700, 400)  # 设置窗口大小

    def choose_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder_path:
            self.folder_input.setText(folder_path)

    def validate_and_submit(self):
        output_assets_start_datetime = self.start_datetime_edit.dateTime().toSecsSinceEpoch()
        output_assets_end_datetime = self.end_datetime_edit.dateTime().toSecsSinceEpoch()
        folder_value = self.folder_input.text()
        checkboxes_checked = any(cb.isChecked() for cb in self.checkboxes)

        if not (output_assets_start_datetime and output_assets_end_datetime  and folder_value and checkboxes_checked):
            QMessageBox.warning(self, '警告', '请填写所有必填项！')
        else:
            self.resule = OutputRepoForm(output_assets_start_datetime,
                                    output_assets_end_datetime,
                                    [cb.text() for cb in self.checkboxes if cb.isChecked()],
                                    self.is_output_doc_checkbox.isChecked(),
                                    self.add_doc_style_checkbox.isChecked(),
                                    folder_value
                                    )
            # 关闭对话框
            self.accept()

def openForm() -> OutputRepoForm:
    app = QApplication(sys.argv)
    form = MyForm()
    result = form.exec()
    if result:
        # 获取表单数据
        resule = form.resule
        print(type(resule))
        print("Form data:", resule)
        return resule
    else:
        sys.exit()


def extract_changed_files(repo_path,branchList, start_datetime_timestamp, end_datetime_timestamp, target_directory,isOutputDoc,isAddDocStyle:bool,outputPath):
    print("仓库路径：", repo_path)
    # print("开始时间：", start_datetime_str)
    # print("结束时间：", end_datetime_str)

    print("正在检索git仓库，请稍等...")

    # 初始化仓库对象
    repo = git.Repo(repo_path)
    # 如果工作区或暂存区有内容，则报提示
    if repo.is_dirty() or repo.index.diff('HEAD'):
        print(f"\033[31m当前工作区或暂存区有未提交的改动，请提交或储藏后再操作\033[m")
        print("程序结束")
        exit()

    #outputPath = input("请输入导出的文件夹路径：")
    if not (len(outputPath) > 0 and os.path.exists(outputPath)):
        print(f"\033[31m输入的文件夹路径不存在，请重新输入\033[m")
        print("程序结束")
        exit()
    assetsOutputPath = os.path.join(outputPath, "assets")
    # isAddStyle = input("是否需要添加样式？(y)")


    #记录执行脚本前的分支
    first_branch = repo.active_branch.name

    # 将输入的开始和结束日期时间字符串转换为datetime对象
    # start_datetime = datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M:%S")
    # end_datetime = datetime.strptime(end_datetime_str, "%Y-%m-%d %H:%M:%S")

    start_datetime = datetime.fromtimestamp(start_datetime_timestamp)
    end_datetime = datetime.fromtimestamp(end_datetime_timestamp)

    # 确保导出目录存在
    os.makedirs(assetsOutputPath, exist_ok=True)
    shutil.rmtree(assetsOutputPath)
    os.makedirs(assetsOutputPath, exist_ok=True)
    imgList = []
    exclude_list = ['README.md', '.vuepress',".vitepress",'.idea','vx_notebook']

    currentHhmmss = datetime.now().strftime("%H%M%S")

    for branch in branchList:
        # 签出
        repo.git.checkout(branch)
        print(f"\n切换到分支: {branch}")

        #打包docs
        if isOutputDoc:
            currTempFolder = os.path.join(outputPath, currentHhmmss + '_' + branch)
            os.makedirs(currTempFolder)
            output_docsTargz = os.path.join(currTempFolder, "docs.tar.gz")

            MyUtil.copyFolder(os.path.join(repo_path, "docs"), os.path.join(currTempFolder, "docs"), exclude_list)
            if isAddDocStyle:
                MyUtil.batchAddMarkdownStyle(os.path.join(currTempFolder, "docs"), PublicConfig.markdownStyle)
            MyUtil.compress_to_tar_gz(os.path.join(currTempFolder, "docs"), currTempFolder, "docs", "docs")
            print(f"tar.gz文件“{output_docsTargz}”创建成功。")


        currentImgList =[]
        # 遍历所有提交
        for commit in repo.iter_commits(rev=branch, no_merges=True):
            commit_date = datetime.fromtimestamp(commit.committed_date)

            # 检查提交日期是否在指定的开始和结束日期时间之间
            if start_datetime <= commit_date <= end_datetime:
                print(f"\t提交记录: {commit.hexsha} \t时间 {commit_date.strftime('%Y-%m-%d %H:%M:%S')} \t备注：{commit.message}",end="")

                # 获取此提交与上一提交之间的差异
                diff = commit.diff(commit.parents[0] if commit.parents else None)

                # 遍历差异中的每个变更
                for change in diff:
                    # 检查变更的文件是否位于目标目录下
                    if change.a_path.startswith(target_directory) or (
                            change.b_path and change.b_path.startswith(target_directory)):
                        # 根据情况选择a_path或b_path
                        file_path = change.b_path if change.b_path else change.a_path

                        currentImgList.append(os.path.basename(file_path))

                        # 导出文件
                        for img in currentImgList:
                            if img not in imgList:
                                shutil.copy(os.path.join(repo_path, "assets", img), assetsOutputPath)
                                print(f"文件成功导出：{img}")
                            else:
                                print(f"文件已经导出过了：{img}")
                        imgList = list(OrderedDict.fromkeys(imgList + currentImgList))

    if branchList[-1] != first_branch:
        repo.git.checkout(first_branch)
        print(f"操作完成，回到分支: {first_branch}")

    if len(imgList) > 0:
        compress_files_to_tar_gz(assetsOutputPath, outputPath)
        print(f"导出成功：{outputPath}/assets.tar.gz")
        print("导出图片数量:", len(imgList))
        print("图片列表:\n", imgList)
        print("导出完成")
        # 弹出存放文件的文件夹
        os.startfile(outputPath)
    else:
        print("没有找到增加的图片")
def check(pyOutputFiles,manuaOutputFiles):
    # 判断两个列表哪个数量更多，并输出两个列表的差异
    if len(pyOutputFiles) > len(manuaOutputFiles):
        print(f"Python脚本导出的图片数量更多，数量{len(pyOutputFiles)}")
        print("差异文件：")
        print(list(set(pyOutputFiles) - set(manuaOutputFiles)))
    else:
        print(f"手动导出的图片数量更多，数量{len(manuaOutputFiles)}")
        print("差异文件：")
        print(list(set(manuaOutputFiles) - set(pyOutputFiles)))


import os
import tarfile
import shutil
import os
import tarfile

import os
import tarfile


def compress_files_to_tar_gz(source_folder, output_basePath, is_compress_volumes=False):
    """
    将指定文件夹下的所有文件压缩打包成tar.gz格式。

    :param source_folder: 文件所在的源文件夹路径
    :param output_basePath: 输出的tar.gz文件名的基本路径（不包括卷号和扩展名）
    :param is_compress_volumes: 是否启用分卷压缩，默认为False
    """
    # 计算源文件夹的总大小
    total_size = sum(
        os.path.getsize(os.path.join(root, file)) for root, _, files in os.walk(source_folder) for file in files)

    # 大于50MB时启用分卷压缩
    if is_compress_volumes and total_size > 50 * 1024 * 1024:
        z7_pack.split_compression(source_folder,output_basePath)
    else:
        output_filename = f"{output_basePath}/assets.tar.gz"
        # 不进行分卷压缩
        with tarfile.open(output_filename, 'w:gz') as tar:
            # 在压缩包内创建一个assets文件夹
            assets_info = tarfile.TarInfo('assets/')
            assets_info.type = tarfile.DIRTYPE
            tar.addfile(assets_info)

            # 遍历源文件夹，将所有文件添加到压缩包的assets文件夹下
            for root, _, files in os.walk(source_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    # 使用os.path.relpath确保文件被放置在assets目录下
                    arcname = os.path.join('assets', os.path.relpath(file_path, source_folder))
                    tar.add(file_path, arcname=arcname)
# 导出文件夹下的图片到目标文件夹
def outputImgList(srcDir,imgList,outputPath):
    for img in imgList:
        if os.path.isfile(os.path.join(srcDir, img)):
            shutil.copy(os.path.join(srcDir, img), outputPath)
        else:
            print(f"文件不存在：{img}")
def start():
    # # 文档仓库路径
    # repo_path = PrivateConfig.repoPath
    # # 要查找资源文件变更的起始时间
    # start_date_str = PrivateConfig.startCommitTime
    # # 要查找资源文件变更的截止时间
    # end_date_str = PrivateConfig.endCommitTime
    # # 要导出的分支
    # branchList = PrivateConfig.branchList
    #
    # if input("是否需要导出文档压缩包？（y/n） ：").strip().lower() == 'y':
    #     isOutputDoc = True
    # else:
    #     isOutputDoc = False

    form_data = openForm()
    pyOutputFiles = extract_changed_files(
        repo_path = PrivateConfig.repoPath,
        start_datetime_timestamp = form_data.startCommitTime,
        end_datetime_timestamp = form_data.endCommitTime,
        branchList = form_data.branchList,
        target_directory = "assets",
        isOutputDoc = form_data.isOutputDoc,
        isAddDocStyle = form_data.isAddDocStyle,
        outputPath=form_data.export_directory
    )


    #检查脚本与实际导出图片
    #checkOutputFilesFolder = "C:\\Users\\25340\\Desktop\\AAA\\assets"
    #check(pyOutputFiles,os.listdir(checkOutputFilesFolder))


# 示例用法
if __name__ == '__main__':
    start()
    # compress_files_to_tar_gz(r"D:\工作\文档相关\上传\1029\assets", r"D:\工作\文档相关\上传\1029\assets", is_compress_volumes=True)