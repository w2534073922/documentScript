import os
from datetime import timedelta, datetime, time


class PrivateConfig:
    # codewave文档仓库路径
    repoPath = r'D:\工作\文档相关\low-code-doc'
    # CoreAgent文档仓库路径
    coreAgentRepoPath = r'D:\工作\文档相关\CoAgent-Doc'
    # 昵称，用于文末的署名
    nickname = '老王'
    # 仓库分支
    branchList = [
        "文档3.6",
        "文档3.7",
        "文档3.8",
        "文档3.9",
        "文档3.10",
        "文档3.11",
        "文档3.12",
        "文档3.13",
        "文档4.0"
    ]
    # 导出资源文件变更的起始时间
    startCommitTime = (datetime.now() - timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M:%S')    # 导出资源文件变更的截止时间
    endCommitTime = (datetime.combine(datetime.now().date(), time.max) - timedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S')    # 租户地址，用于检查IDE中失效链接
    codewaveUrl = 'https://wangfeng.codewave.163.com/'
    # 租户账号cookie
    accountCookie = 'wyy_uid=cb662e7a-d5af-45d4-87b8-8ad20ef5c5bb; NTES_CMT_USER_INFO=73984784%7C%E6%9C%89%E6%80%81%E5%BA%A6%E7%BD%91%E5%8F%8B04qeIg%7Chttp%3A%2F%2Fcms-bucket.nosdn.127.net%2F2018%2F08%2F13%2F078ea9f65d954410b62a52ac773875a1.jpeg%7Cfalse%7CbTE1OTcxMzc3MTEyQDE2My5jb20%3D; nts_mail_user=15971377112@163.com:-1:1; __root_domain_v=.163.com; _qddaz=QD.871424049965538; _ga=GA1.1.757907799.1725354194; _ga_Z0JVTF6WF2=GS1.1.1725354193.1.1.1725354250.0.0.0; _ntes_nnid=2aefb1c0c36ceb8e8d1f78f06ca46c39,1725552133677; _ntes_nuid=2aefb1c0c36ceb8e8d1f78f06ca46c39; NTES_P_UTID=H7xgon5EQVfiDlhY67PSf70hw8nGxEof|1735375391; P_INFO=m15971377112@163.com|1735375391|1|mail163|00&99|zhj&1733077814&mail163#zhj&330100#10#0#0|159112&1|newsclient|15971377112@163.com; pageContentBiz=GONG_GONG; pageContentBizProduct=""; abH=-414347427; abTest=1; hb_MA-AAAB-2D9387BB219C_source=community1.codewave.163.com; fsWebsiteUid=58447a7385794b35a324c5533335e7da; timing_user_id=time_QsPp8UKW1f; hb_MA-93D5-9AD06EA4329A_source=docs.popo.netease.com; hb_MA-9621-47269121E701_source=community.codewave.163.com; Hm_lvt_266c1eb59e093c5981d1274d3866bece=1736321266,1736851692,1737617560; hb_MA-87CB-27B1B933E5F6_source=codewave.163.com; urs_t=fIyArD87hwoN0r4pH1IuuvWg; urs_u=/twlvBC8p5fMOzyWmfOglYVerDrc-rzQw4Vh1XvgXvF-idEisEOo03CJwYZFJuMjzMR-9uuV9IJFDczJY5gEYiQWqFS1LJcoF6GglJkrC-sc3nn5rHlTVXqna3DGVNZNVONUVTgWv66gLQE5P7XPKHFvhFwP/nJGqQl4Vbit/u1LYDvf2ei1JMOwXhcmaajPl5WYvSwfM0-38r1dE7XK4E2FlJxGH8VBLacfQsp1r6/krqz2fmIQb7wVPbVNHd0pg1FlixgO5O5eQqoGVdi6R9CIau7rMIjtV2HwHDe3UzEOEJpenvEFmI038B7RDETJ; authorization=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJc1NlcnZpY2VBY2NvdW50IjoiZmFsc2UiLCJBdXRoVHlwZVRva2VuRXhwaXJlIjoiODY0MDAiLCJVc2VySWQiOiJmYWVjNGVmNTg2Yjk0YzMzYjZhZTE3MmE1MTA0ZGEzNiIsIlRoaXJkVXNlcklkIjoiZTI4NTg2NDQ2ZTc1NDYzN2IwYWY1ZWI4NmY5Mzc0ZDQ3NjI1NjI2MjYzNTE5MjY3MDMyIiwiQXV0aFR5cGUiOiJTaHVmYW4iLCJleHAiOjE3Mzg4OTQwNjUsIklzVGhpcmRQYXJ0eUNvb2tpZSI6ImZhbHNlIiwiaWF0IjoxNzM4ODA3NjY1fQ.p1KbLwBmlowT1VJXYmBDhs6hIzGz34ss-_UkKnSxuig; exdays=2; LoginType=Other; _ntes_origin_from=baidu; hb_MA-9C94-022F7E5CC36D_source=dogfood.lcap.163yun.com'
    # popo文档下载图片用的cookie，包含SESSION参数即可
    popoDocumentImageCookie = 'SESSION=MTU1M2M4ZDEtOTQxMy00MGRhLTk4ZWUtOTA0YjBhMDc5MjAy;'
    #使用多线程时的线程数，默认为cpu逻辑核心数
    threadsNum = os.cpu_count()
    #wkhtmltopdf的位置，这是用于生成PDF的工具
    wkhtmltopdf = r"D:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"

class PublicConfig:
    # 获取项目文件夹路径
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    # 需要排除的泡泡文档链接
    needExcludedPopoLinkList = [
        'https://docs.popo.netease.com/lingxi/cf56d061f7f04559acb331b9e476849f',
    ]
    # 下载文档附件时需要下载的文件类型
    download_supported_types = ['.zip', '.pdf', '.jar','.rar']
    # 需要排除的文档链接
    skip_items = [".vuepress",".vitepress", "999.others", "README.md", "99.参考","node_modules",".git"]
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
    .yellowBlock {
        background-color: #fcf5e1 !important;
        border-color: #eaaa08 !important;
        border-left-width: 0.2rem !important;
        border-left-style: solid !important;
        padding: 1rem 1rem 1rem 1rem !important;
        margin: 1rem 0px !important;
    }
    .blueBlock , .highlight{
        background-color: #eff8ff !important;
        border-color: #c9dcff !important;
        border-left-width: 0.2rem !important;
        border-left-style: solid !important;
        padding: 1rem 1rem 1rem 1rem !important;
        margin: 1rem 0px !important;
    }
</style>''')
    #导出markdown时额外修改的样式
    outputPDFStyle = '''
.markdown-body {
    font-size: 16px;
}
body .markdown-body a {
    background-color: initial;
}
.downloadButton {
color: #ffffff !important;
background-color: #93CDFF !important;
}
'''