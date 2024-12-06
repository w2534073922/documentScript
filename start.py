from src import exportRepositoryFiles, checkDocumentContent_andOther, downloadMarkdownImageToLocal
from src.utils import downloadAttachment, markdownToPdf

if __name__ == '__main__':

    print('''
    1、扫描文档错误与其他
    2、下载popo文档
    3、导出仓库资源文件
    4、导出文档中的附件和视频
    5、markdown文件夹生成PDF
    ''')
    select = input("输入选择：")
    if select == "1":
        checkDocumentContent_andOther.start()
    elif select == "2":
        downloadMarkdownImageToLocal.start()
    elif select == "3":
        exportRepositoryFiles.start()
    elif select == "4":
        downloadAttachment.start()
    elif select == "5":
        markdownToPdf.start()