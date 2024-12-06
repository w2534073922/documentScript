import os
from datetime import timedelta, datetime, time

# 这是配置文件的模板，使用者需要创建自己的MyConfig.py文件
class PrivateConfig:
    # 文档的文件夹路径
    repoPath = r''
    # 昵称，用于文末的署名
    nickname = ''
    # 仓库分支
    branchList = [
        # "文档3.3新结构v1",
        # "文档3.4",
        "文档3.6",
        "文档3.7",
        "文档3.8",
        "文档3.9",
        "文档3.10",
        "文档3.11"
    ]
    # 导出资源文件变更的起始时间，默认为两天前
    startCommitTime = (datetime.now() - timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M:%S')
    # 导出资源文件变更的截止时间，默认为今天的最后一刻
    endCommitTime = (datetime.combine(datetime.now().date(), time.max) - timedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S')
    # 租户地址，用于检查IDE中失效链接，例如：https://xxx.codewave.163.com
    codewaveUrl = ''
    # 租户账号cookie，登录租户后从document-mappings接口中拿
    accountCookie = ''
    # popo文档下载图片用的cookie，包含SESSION参数即可
    popoDocumentImageCookie = ''
    #使用多线程时的线程数，默认为cpu逻辑核心数，配置较低的电脑可以修改成2~4
    threadsNum = os.cpu_count()
    #wkhtmltopdf的位置，这是用于生成PDF的工具
    wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"

class PublicConfig:
    # 获取项目文件夹路径
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    # 需要排除的泡泡文档链接
    needExcludedPopoLinkList = [
        'https://docs.popo.netease.com/lingxi/cf56d061f7f04559acb331b9e476849f',
    ]
    # 下载文档附件时需要下载的文件类型
    download_supported_types = ['.zip', '.pdf', '.jar', '.rar']
    # 批量添加的文档样式
    markdownStyle = ('''
<style>
    /* markdown组件下的图片样式 */
    .theme-default-content img{
        border: 1px solid #eee !important; /* 灰色边框 */
        border-radius: 10px; /* 圆角 */
        box-shadow:  6px 6px 12px #d9d9d985,-6px -6px 12px #e7e7e76e; /* 阴影 */
    }
    /* 标题下的图片增加间距 */
    h1 + img,h2 + img,h3 + img,h4 + img,h5 + img {
        margin-top: 10px;
    }
    /* h4和h5标题的字号加大 */
    h4 {
        font-size: 18px;
    }
    h5 {
        font-size: 16px;
    }
    h5 {
        font-size: 16px;
    }
    h6 {
        font-size: 14px;
    }
    /* 折叠块加边框、背景色、边距 */
    details {
      border: 1px solid #679CF8; /* 边框 */
      border-radius: 6px;/* 圆角 */
      background-color: #F8FCFF; /* 底色 */
      padding: 10px 40px 10px 40px; /* 内边距 */
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    details summary {  
      margin: 0 0 0 -20px; /* 折叠块标题不需要内边距 */
      font-weight: bold; /* 字体加粗 */
      color: #679CF8; /* 字体蓝色 */
      cursor: pointer; /* 手型鼠标指针 */
    }
</style>''')