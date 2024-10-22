import codecs
import datetime
import json
import os
import re
import shutil
import subprocess
import time
from urllib.parse import unquote
from prettytable import PrettyTable
import requests
import win32api
# from func_timeout import func_timeout, FunctionTimedOut, func_set_timeout
#from inputimeout import inputimeout, TimeoutOccurred
from git import Repo
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from config import MyConfig
from src.exportRepositoryFiles import outputImgList

docCount = 0
docImgSet = set()
invalidMappingTable = PrettyTable()
invalidMappingTable.field_names = ["name","path","启用中","当前映射的文档路径"]
mergeDocumentCcontent = ""
'''
该函数用于检查文档中引用的相对路径其他文档是否存在
目前有两点问题：
    1、一些链接使用了url转义，实际上url转以后是可以找到该文件的，脚本会将其错误地识别为文件不存在。无碍，看转义的路径也不顺眼，找到后将其换成正常路径即可。
    2、可能有一些脚本扫描不到的错误路径，需要收集这类情况，补充完善脚本。
'''
def search_markdown_files(folder_path,spikNote):
    global mergeDocumentCcontent
    # 判断传入的路径是否正确
    if not os.path.exists(folder_path):
        print("\033[31m该文件夹不存在：\033[0m"+folder_path)
        exit()
    elif not os.path.isdir(folder_path):
        print("\033[31m该路径不是一个文件夹：\033[0m"+folder_path)
        exit()
    #统计错误数
    i =0
    j=0
    #结果集
    errorDict = {}
    imgDict = {}


    #imgPattern = r"!\[.*?\]\((.*?)\)|<img.*?src=[\"\'](.*?)[\"\'].*?>"
    imgPattern = r"!\[.*?\]\(([^)]*\.\.[^)]*)\)|<img.*?\ssrc=[\"\'](.*?)[\"\'].*?>"
    #需要跳过读取的文件或文件夹
    skip_items = [".vuepress", "999.others", "README.md","0.成长地图.md"]

    global docCount
    for root, dirs, files in os.walk(os.path.join(folder_path,"docs")):
        #跳过该文件/夹
        #print("root=",os.path.basename(root))
        if os.path.basename(root) in skip_items:
            #print("跳过：",os.path.basename(root))
            dirs[:] = []
            continue

        # if any(blocked_item in root for blocked_item in skip_items):
        #     continue

        for file in files:
            #print("文件：" + os.path.basename(file))
            if os.path.basename(file) in skip_items:
                #print("跳过：", os.path.basename(file))
                continue

            if file.endswith('.md'):
                docCount = docCount + 1
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    mergeDocumentCcontent = mergeDocumentCcontent + "\n\n" +f.read()
                    f.seek(0)
                    content = f.readlines()
                    skip = False
                    for line_num, line in enumerate(content, start=1):
                        #HTML注释的内容会跳过读取，根据入参决定是否开启
                        if spikNote:
                            if "<!--" in line and "-->" in line:
                                skip = True
                            elif "<!--" in line:
                                skip = True
                                continue
                            elif "-->" in line:
                                skip = False
                                continue
                            if skip:
                                continue

                        #这个是考试认证的popo文档链接，需要排除掉
                        excludedLinkList = MyConfig.PublicConfig.needExcludedPopoLinkList
                        # 检查是否有popo文档链接
                        if "docs.popo.netease.com" in line and not any(
                            excludedLink in line for excludedLink in excludedLinkList):
                            print(f"\033[31m发现popo文档链接：\033[0m"+f"行数\033[34m{line_num}\033[0m\t"+"\033[33m"+file_path.split("docs"+os.path.sep)[1] )
                        # 检查是否有文档中心链接
                        if "/CommunityParent/fileIndex" in line or "%2FCommunityParent%2FfileIndex" in line:
                            print(f"\033[31m发现文档中心链接：\033[0m"+f"行数\033[34m{line_num}\033[0m\t"+"\033[33m"+file_path.split("docs"+os.path.sep)[1] )

                        # 检查引用的md文件
                        pattern = r'\[.*?\]\((\.{1,2}/.*?\.md)\)'
                        matches = re.finditer(pattern, line)
                        for match in matches:
                            relative_path_list = match.groups()
                            for relative_path in relative_path_list:
                                # relative_path = match.group(1)
                                absolute_path = os.path.abspath(os.path.join(root, relative_path))
                                # 判断匹配到被引用md的路径是否存在，存在则假如到结果集中
                                if not os.path.exists(absolute_path):
                                    if file_path.split("docs"+os.path.sep)[1] not in errorDict:
                                        errorDict[file_path.split("docs"+os.path.sep)[1]] = []
                                    errorDict[file_path.split("docs"+os.path.sep)[1]].append((relative_path, line_num))
                                    # print("发现错误的引用链接-> \033[33m"+file_path.split("docs"+os.path.sep)[1] + "\033[0m" + "    " + "\033[31m"+relative_path+"\033[0m    出现在第 \033[34m"+str(line_num)+"\033[0m 行")
                                    i = i + 1
                                    # print(f"\033[31m{relative_path}\033[0m  \033[34m{file_path}\033[0m")


                        #匹配文档中失效的图片
                        #print("\033[36m开始扫描文档中的失效图片...\033[0m")
                        imgMatches = re.finditer(imgPattern, line)
                        for imgMatch in imgMatches:
                            img_path_list = imgMatch.groups()
                            img_path_list = [x for x in img_path_list if x is not None]
                            #print(img_path_list)
                            #print(file_path)
                            for img_path in img_path_list:
                                # if "sy_pc2.png" in img_path:
                                #     print("目标字符串包含子串",img_path)
                                #print("图片：",img_path)
                                docImgSet.add(os.path.basename(img_path))

                                absolute_ImgPath = os.path.abspath(os.path.join(root, img_path))
                                #print(absolute_ImgPath)

                                #由于在Windows中不区分文件名大小写，本地预览markdown时，图片名称中的大小写无关紧要，但是在线上是区分大小写的，此步骤基于区分大小写来判断文档中引用的图片是否存在
                                if os.path.exists(absolute_ImgPath):
                                    actualFileName = os.path.basename(win32api.GetLongPathNameW(win32api.GetShortPathName(absolute_ImgPath)))
                                    actualFileName = re.split("\.", os.path.basename(actualFileName), 1)[0]
                                    fname = re.split("\.", os.path.basename(absolute_ImgPath), 1)[0]
                                    if  actualFileName!= fname:

                                        if file_path.split("docs"+os.path.sep)[1] not in imgDict:
                                            imgDict[file_path.split("docs"+os.path.sep)[1]] = []
                                        imgDict[file_path.split("docs"+os.path.sep)[1]].append(("文件名大小写真实文件名不匹配   "+img_path, line_num))
                                        j = j + 1
                                else:
                                    # print(f"路径不存在：{absolute_ImgPath}")

                                    if file_path.split("docs"+os.path.sep)[1] not in imgDict:
                                        imgDict[file_path.split("docs"+os.path.sep)[1]] = []
                                    imgDict[file_path.split("docs"+os.path.sep)[1]].append((img_path, line_num))
                                    j = j + 1

    print("\n\033[32m输入的文档文件夹路径：\033[0m", folder_path)
    # 输出文档当前分支
    try:
        # 尝试在指定目录下运行git的version命令
        subprocess.run(["git", "--version"], check=True, capture_output=True, cwd=folder_path)
        # 查询文档的版本号
        gitOutput = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],  cwd=folder_path,check=True,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
        #branch_name = gitOutput.decode("utf-8").strip()
        #branch_name = gitOutput.stdout
        print("\033[32m文档所在分支：\033[0m",gitOutput.stdout.decode("utf-8").strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\033[32m文档所在分支：\033[0m", "Git未安装或该目录不是Git仓库")
        pass

    # 统计中文字符数
    print("\033[32m文档数量：\033[0m", docCount)
    print("\033[32m文档中文字符数：\033[0m", len(re.compile('[\u4e00-\u9fa5]').findall(mergeDocumentCcontent)))


    print("\n\033[36m搜索文档中的失效内部跳转...\033[0m")
    # 打印结果集
    # print中这些奇怪的内容是用于控制打印颜色
    if len(errorDict) > 0:
        print(f"合计 \033[31m{i}\033[0m 个错误引用链接")
        for file_path, lines in errorDict.items():
            print(f'\t文件: \033[33m{file_path}\033[0m')
            for line, line_num in lines:
                print(f'\t\t行数 \033[34m{line_num}\033[0m: \033[31m{line}\033[0m')
    else:
        print("\033[32m未发现\033[0m")

    print("\n\033[36m搜索文档中的失效图片地址...\033[0m")
    if len(imgDict) > 0:
        print(f"合计 \033[31m{j}\033[0m 个无效图片地址")
        for file_path, lines in imgDict.items():
            print(f'\t文件: \033[33m{file_path}\033[0m')
            for line, line_num in lines:
                print(f'\t\t行数 \033[34m{line_num}\033[0m: \033[31m{line}\033[0m')
        invalidImgList = []
        for images in imgDict.values():
            for image_path, _ in images:
                # 使用 os.path.basename() 提取文件名
                invalidImgList.append(os.path.basename(image_path))
        print("\033[32m无效图片列表：\033[0m", invalidImgList)
    else:
        print("\033[32m未发现\033[0m")

    #print(docImgSet)



# 检测平台配置的文档映射链接是否有效
# 先调用平台的接口获取映射列表，再拿列表中的项与本地文件做对比，如果找不到文件则认为是失效的映射
def checkDocumentMappings(documentProjectPath,tenementUrl, cookie ,isDebug=False):
    print(f'\n\033[36m搜索平台配置的文档映射链接是否有失效，当前输入的租户地址： {tenementUrl}\033[0m')
    if tenementUrl.endswith("/"):
        documentMappingsInterfaceURL = tenementUrl + "api/v1/config/document-mappings"
    else:
        documentMappingsInterfaceURL = tenementUrl + "/api/v1/config/document-mappings"

    headers = {'content-type': 'application/json;charset=UTF-8','Cookie':cookie}
    response = requests.post(documentMappingsInterfaceURL, data='{}',headers = headers)
    if response.status_code == 200:
        response_data = response.json()
        json_string = json.dumps(response_data, ensure_ascii=False)
        if response_data['code'] == 200:
            mappingList = response_data['result']
            #print(json.dumps(mappingList,ensure_ascii=False))
            for mapping in mappingList:
                #如果该项映射启用了
                if mapping['isUsed'] == True:
                    #且是跳到文档中心的
                    if len(mapping['href'].split('/fileIndex?filePath='))==2:
                        #对文件路径进行解码，得到的结果类似于： 20.应用开发/10.页面设计/20.PC端页面组件使用/01.布局/020.线性布局.md
                        file_path = unquote(mapping['href'].split('/fileIndex?filePath=')[1])
                        #print(file_path)
                        if os.path.exists(os.path.join(documentProjectPath,'docs',file_path)):
                            pass
                        # 如果文档存在但是带了version后缀
                        elif "version" in file_path and os.path.exists(os.path.join(documentProjectPath,'docs',file_path.split('&version')[0])):
                            print("\033[31m路径不应带版本号后缀:\033[0m"+str(mapping))
                        else:
                            #print("\033[31m路径失效:\033[0m"+str(mapping))
                            #temp = list(mapping.values())
                            temp =dict(mapping)
                            temp.pop("comment")
                            temp.pop("description")
                            temp.pop("previewHref")
                            temp = list(temp.values())
                            temp[3] = unquote(temp[3])
                            invalidMappingTable.add_row(temp)
        else:
            if response_data["msg"] == "用户未登录或已失效":
                print(f'\033[31m用户未登录或登录状态已失效，可能是Cookie过期了，去浏览器里重新拿cookie试试，接口为document-mappings（确认拿cookie的租户与检测的租户地址一致）\033[0m')
            else:
                print(f'\033[31m{response_data["msg"]}\033[31m')
    else:
        print("\033[31m调用获取文档映射的接口出错\033[0m")

#将文档中有引用过的图片复制出来
def copyValidImg(documentProjectPath):
    #复制图片文件夹
    print("\n\033[36m（可选）复制出文档中的有效图片，应确保没有无效的图片地址\033[0m")
    newImgPath =  input("\033[35m输入图片文件夹待粘贴的文件夹路径：\033[0m")
    if newImgPath == "":
        print("\033[31m输入不能为空\033[0m")
        exit()
    newImgPath = os.path.join(newImgPath,"assets")
    oldImgPath = os.path.join(documentProjectPath,"assets")
    print("复制中，请等待...")

    # # 确保目标文件夹不存在
    # if not os.path.exists(newImgPath):
    #     # 创建目标文件夹
    #     os.makedirs(newImgPath)

    if os.path.exists(newImgPath):
        #如果已存在该文件则结束
        print(f"\033[31m目标文件夹已存在，操作失败：{newImgPath}\033[0m")
        return
    shutil.copytree(oldImgPath, newImgPath)
    print("复制完成，开始删除失去引用的图片...")
    removeNum = 0
    global docImgSet
    #删除没有引用的图片
    for file_name in os.listdir(newImgPath):
        file_path = os.path.join(newImgPath, file_name)
        if os.path.isfile(file_path) and os.path.basename(file_name) not in docImgSet:
            os.remove(file_path)
            #print(file_path)
            removeNum = removeNum+1
    print(f"删除\033[31m{removeNum}\033[0m个无效图片")
    os.startfile(newImgPath)

#将所有markdown合并成一个markdown，并将所有图片路径进行统一的转换
def mergeDocument(documentProjectPath):

    def replace_path(match):
        if match.group(1)  is not None:
            relative_path = match.group(1)
        if match.group(2)  is not None:
            relative_path = match.group(2)
        label = str(match.group(0))
        newPath = label.replace(relative_path,os.path.join(documentProjectPath,"assets",os.path.basename(relative_path)))
        return newPath

    global mergeDocumentCcontent
    imgPattern = r"!\[.*?\]\(([^)]*\.\.[^)]*)\)|<img.*?src=[\"\'](.*?)[\"\'].*?>"
    markdownName = "Codewave智能开发平台使用手册_" + datetime.datetime.now().strftime("%Y-%m%d-%H%M") + ".md"
    outputPath = input("输入导出合并后文档的文件夹路径：")
    if not os.path.isdir(outputPath):
        print("输入的导出文件夹不存在")
        exit()
    else:
        #将文档中的相对路径转换成一致
        result = re.sub(imgPattern, replace_path, mergeDocumentCcontent)
        outputFilePath = os.path.join(outputPath,markdownName)
        file = open(outputFilePath, "w", encoding="utf-8")
        file.write(result)
        file.close()
        print("合并完成：",outputFilePath)
        os.startfile(outputPath)

#强制修改所有文件
def append_line_to_markdowns(line):

    dir_path = input("输入要修改的文件夹路径：")
    # 遍历指定目录及其子目录
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.md'):
                # 构建文件完整路径
                file_path = os.path.join(root, file)

                with codecs.open(file_path, 'r+', encoding='utf-8') as f:
                    content = f.read()
                    # 在末尾追加指定行，并写回文件
                    f.seek(0, os.SEEK_END)  # 移动到文件末尾
                    f.write('\n' + line)
                    f.truncate()  # 截断文件以现在的文件指针位置为准
    print("修改完成")

#还原所有文件
def remove_line_from_markdowns(dir_path, target_line):
    pattern = re.compile(r'\s*{}(\s*)$'.format(re.escape(target_line)), re.MULTILINE)
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)

                with codecs.open(file_path, 'r+', encoding='utf-8') as f:
                    content = f.read()
                    # 使用正则表达式替换掉末尾的指定行
                    new_content = pattern.sub('', content)

                    # 如果内容发生改变，则写回新的内容
                    if new_content != content:
                        f.seek(0)
                        f.write(new_content)
                        f.truncate()

# 速度太慢，已经废弃，使用另一个函数以多线程处理
def find_oldest_updated_docs(repo_path, count=50):
    """
    查找Git仓库中docs文件夹内最近变更时间最久远的文件。

    参数:
    repo_path (str): 仓库的本地路径。
    count (int): 需要返回的文件数量，默认为50。

    返回:
    list[str]: 最近变更时间最久远的文件路径列表。
    """
    repo = Repo(repo_path)
    if repo.bare:
        raise ValueError("提供的路径没有指向有效的Git存储库。")

    docs_path = os.path.join(repo_path, 'docs')
    if not os.path.isdir(docs_path):
        print("在存储库中找不到“docs”目录")
        return []

    # 初始化一个字典来存储每个文件的最后修改日期
    file_dates = {}
    filesCount = 0
    filesSum = sum(1 for _, _, files in os.walk(docs_path) for file in files if file.endswith(('.md')))-2
    skip_items = [".vuepress","README.md","0.成长地图.md"]
    # 遍历docs目录下的所有文件
    for root, dirs, files in os.walk(docs_path):
        if os.path.basename(root) in skip_items:
            continue
        for file in files:
            if os.path.basename(file) in skip_items:
                continue
            if file.endswith('.md'):
                filesCount = filesCount+1
                print(f"当前统计到：{filesCount}/{filesSum} ,{file}")
                full_path = os.path.join(root, file)
                # 获取该文件在仓库中的最后一次提交信息
                commit = repo.git.log('--follow', '--max-count=1', '--format=%ct', full_path)
                if commit:
                    commit_time = int(commit.strip())  # 提交时间戳
                    # 存储或更新文件的最后修改时间
                    relative_path = os.path.relpath(full_path, repo.working_dir)
                    file_dates[relative_path] = commit_time

    print(file_dates)
    oldest_files = {k: v for k, v in file_dates.items() if "版本更新说明" not in k}
    # 根据最后修改日期排序并取前count个文件
    oldest_files = sorted(oldest_files.items(), key=lambda x: x[1])[:count]
    print("\033[36m最近变更时间最久远的文件：\033[m")
    for oldest_file in oldest_files:
        print(f"{datetime.datetime.fromtimestamp(oldest_file[1])}\t\t{oldest_file[0]}")
    # 构建最终结果路径，并返回
    return [os.path.join('docs', filename) for filename, _ in oldest_files]


def get_commit_date_for_files(repo_path, files,thread_id):
    """线程工作函数，获取一组文件的最后提交日期，并打印执行时间"""
    start_time = time.time()
    file_dates = defaultdict(int)
    repo = Repo(repo_path)
    with repo.git.custom_environment():
        for file in files:
            full_path = os.path.join(repo.working_dir, file)
            commit = repo.git.log('--follow', '--max-count=1', '--format=%ct', full_path)
            if commit:
                commit_time = int(commit.strip())
                file_dates[file] = commit_time
    end_time = time.time()
    print(f"数量{len(files)}")
    print(f"Thread {thread_id} finished in {end_time - start_time:.2f} seconds.")
    return file_dates

def find_oldest_updated_docs_multithread(repo_path, count=50, num_threads=MyConfig.PrivateConfig.threadsNum):
    print(f"开始获取文档最后的提交日期，线程数{num_threads}，处理中请等待...")
    start_time_total = time.time()
    """
    使用多线程查找Git仓库中docs文件夹内最近变更时间最久远的文件。
    """
    repo = Repo(repo_path)
    if repo.bare:
        raise ValueError("提供的路径没有指向有效的Git存储库。")

    docs_path = os.path.join(repo_path, 'docs')
    if not os.path.isdir(docs_path):
        print("在存储库中找不到“docs”目录")
        return []

    skip_items = [".vuepress", "README.md", "0.成长地图.md"]
    all_files = [
        os.path.join(root[len(repo.working_dir)+1:], file)
        for root, dirs, files in os.walk(docs_path)
        for file in files if file.endswith('.md') and
        os.path.basename(root) not in skip_items and
        file not in skip_items
    ]

    # 分割文件列表给多个线程
    start_time_split = time.time()
    chunk_size = len(all_files) // num_threads + 1
    chunks = [all_files[i:i + chunk_size] for i in range(0, len(all_files), chunk_size)]
    #print(f"Splitting files into chunks took {time.time() - start_time_split:.2f} seconds.")

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = {executor.submit(get_commit_date_for_files, repo_path, chunk, i): chunk for i, chunk in enumerate(chunks)}

    # 合并结果与排序
    start_time_merge_sort = time.time()
    file_dates = defaultdict(int)
    for future in futures:
        for file, date in future.result().items():
            file_dates[file] = date
    #print(f"Merging and sorting results took {time.time() - start_time_merge_sort:.2f} seconds.")

    # 输出结果与结束总时间
    oldest_files = {k: v for k, v in file_dates.items() if "版本更新说明" not in k}
    oldest_files = sorted(oldest_files.items(), key=lambda x: x[1])[:count]
    print("\033[36m最近变更时间最久远的文件（不包含版本更新说明）：\033[m")
    for oldest_file in oldest_files:
        print(f"{datetime.datetime.fromtimestamp(oldest_file[1])} \t\t {oldest_file[0]}")
    print(f"执行时间: {time.time() - start_time_total:.2f} 秒")

    return [os.path.join('docs', filename) for filename, _ in oldest_files]

def start():
    #必填，项目文件夹路径
    documentProjectPath = MyConfig.PrivateConfig.repoPath
    #documentProjectPath = 'D:\\工作\\文档相关\\客户部署\\codewave文档3.8-markdown包-20240705'
    #以下参数为可选，检测IDE中的文档映射链接时用到

    #租户地址
    #tenementUrl="https://newtest.lcap.codewave-test.163yun.com/"
    tenementUrl = MyConfig.PrivateConfig.codewaveUrl
    #cookie
    cookie = MyConfig.PrivateConfig.accountCookie

    search_markdown_files(documentProjectPath, True)

    checkDocumentMappings(documentProjectPath=documentProjectPath,tenementUrl=tenementUrl,isDebug=False,cookie=cookie)
    if len(invalidMappingTable.rows) > 0:
        print("\033[31m以下路径疑似失效:\033[0m")
        print(invalidMappingTable)
    hintText = '''
\033[36m其他\033[0m
\t1、导出assets下的有效引用图片（用于减少打压缩包体积）
\t2、所有文档合并成一个md文件（用于typora生成PDF）
\t3、修改所有markdown文件（用于让文档中心上传时识别文档内容有变动）
\t4、为所有文档添加img样式（仅在文档中心的markdown组件下生效）
\t5、搜索前50名最久未更新的文档（执行时间较长）
\t6、按图片列表导出图片（用于提取其他分支没有的图片）
\n输入数字选择：'''

    #select = inputimeout(prompt=hintText,timeout=12)
    #select = func_timeout(3, input(hintText))
    select = input(hintText)
    if select == "1":
        copyValidImg(documentProjectPath)
    elif select == "2":
        mergeDocument(documentProjectPath)
    elif select == "3":
        append_line_to_markdowns("<!-- 强制更新文档用 -->")
    elif select == "4":
        append_line_to_markdowns(MyConfig.PublicConfig.markdownStyle)
    elif select == "5":
        #find_oldest_updated_docs(documentProjectPath)
        # num_threads参数为线程数，根据自己的电脑性能来配置
        find_oldest_updated_docs_multithread(documentProjectPath,num_threads=16)
    elif select == "6":
        outputPath = input("输入导出图片的路径：")
        imgList = input("输入图片列表：")
        outputImgList(srcDir=os.path.join(documentProjectPath, "assets"),outputPath=outputPath,imgList=eval(imgList))
    else:
        print("\033[31m输入有误\033[0m")
        exit(0)
