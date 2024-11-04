import os.path
import subprocess

from config import MyConfig

isInit = False
def init():
    # 检查node版本是否大于等于18
    try:
        node_version_output = subprocess.check_output(['node', '--version'], encoding='utf-8',errors='replace')
        node_version = node_version_output.strip()
        #print(f"当前Node版本为：{node_version}")
        if node_version.startswith('v18.'):
            #print("Node版本符合要求，继续执行。")
            pass
        else:
            print("Node版本不符合要求，请升级到18以上版本。")
            exit(1)
    except subprocess.CalledProcessError:
        print("没有找到Node，请先安装Node。")
        exit(1)

# 检查 mdpdf 是否存在
    try:
        result = subprocess.run(['where', 'mdpdf'], cwd = MyConfig.PrivateConfig.repoPath,capture_output=True, text=True, check=True,encoding='utf-8',errors='replace')
        mdpdf_path = result.stdout.strip().split('\n')[0]  # 获取第一个匹配的路径
        print("mdpdf已安装于：", mdpdf_path)
        isInit = True
    except subprocess.CalledProcessError:
        print("没有安装mdpdf，现在安装...")

        # 安装 mdpdf
        install_result = subprocess.run(['npm', 'install', '-g', 'mdpdf'], cwd = MyConfig.PrivateConfig.repoPath,capture_output=True, text=True,encoding='utf-8',errors='replace')
        print("标准输出:"+install_result.stdout)
        print("标准错误:"+install_result.stderr)

        if install_result.returncode != 0:
            print("安装mdpdf失败")
            isInit = False
            return False

        print("mdpdf安装成功")

        # 再次检查 mdpdf 路径
        try:
            result = subprocess.run(['where', 'mdpdf'], cwd = MyConfig.PrivateConfig.repoPath,capture_output=True, text=True, check=True)
            mdpdf_path = result.stdout.strip().split('\n')[0]
            print("mdpdf已安装于：", mdpdf_path)
            isInit = True
        except subprocess.CalledProcessError:
            print("安装后仍无法找到mdpdf")
            isInit = False
            return False

    if not mdpdf_path:
        print("无法找到mdpdf路径")
        return False

def useNodeConvertPDF(mdPath, pdfPath, isDebug=False):
    if(not os.path.exists(mdPath)):
        print("md文件不存在："+mdPath)
        exit(1)
    if isInit == False:
        init()
    # 定义命令及其参数
    command = [
        'npx',
        'mdpdf',
        mdPath,
        '--output',
        pdfPath,  # 注意这里应该是.pdf而不是.md
        '--style',os.path.join(MyConfig.PublicConfig.project_root,'config/pdf.css'),
    ]
    if isDebug:
        command.append('--debug')
    print(command)
    # 执行命令
    result = subprocess.run(
        command,
        cwd = MyConfig.PublicConfig.project_root,
        capture_output=True,
        text=True,
        encoding='utf-8')

    #打印标准输出和标准错误
    if result.stderr is not None or result.stderr != '':
        print("导出成功："+result.stderr)
    if result.stderr is not None or result.stderr != '':
        print("\nStandard Error:"+result.stderr)

    #检查命令是否成功执行
    if result.returncode != 0:
        print(f"命令失败： {result.returncode}")

if __name__ == '__main__':
    # markdown文件路径
    mdPath = r"D:\工作\文档相关\low-code-doc\docs\40.扩展与集成\10.扩展开发方式\30.服务端扩展开发\10.依赖库开发\10.服务端依赖库开发快速入门.md"
    # 导出的pdf文件路径
    pdfPath = r"D:\工作\文档相关\low-code-doc\docs\40.扩展与集成\10.扩展开发方式\30.服务端扩展开发\10.依赖库开发\10.服务端依赖库开发快速入门.pdf"
    useNodeConvertPDF(mdPath,pdfPath)