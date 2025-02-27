import os.path
from urllib.parse import unquote

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from myConfig import MyConfig


def get_links_from_page(url):
    # 指定 ChromeDriver 的路径，如果已添加到环境变量可省略
    service = Service()
    # 创建 Chrome 浏览器实例
    driver = webdriver.Chrome(service=service)

    try:
        # 打开指定的网页
        driver.get(url)

        # 等待页面加载完成，这里可以根据实际情况调整等待时间或使用更复杂的等待机制
        #driver.implicitly_wait(6)

        wait = WebDriverWait(driver, 4)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'a')))
        # 获取页面的 HTML 内容
        page_source = driver.page_source

        # 使用 BeautifulSoup 解析 HTML 内容
        soup = BeautifulSoup(page_source, 'html.parser')

        # 查找所有的链接
        links = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                links.append(href)

        return links

    except Exception as e:
        print(f"出现异常: {e}")
    finally:
        # 关闭浏览器
        driver.quit()

# chechDoc

def start():
    # 替换为你要获取链接的网页 URL
    url = 'https://wd-cwdoc.lcap.163yun.com/index2'
    links = get_links_from_page(url)
    if links:
        for link in links:
            # 如果连接中包含fileIndex?filePath=，则将其添加到结果列表中
            if 'fileIndex?filePath=' in link:
                encodeUrl = link.split('fileIndex?filePath=')[1]
                #对URL进行转义
                encodeUrl = unquote(encodeUrl)
                # print(link)
                # print(encodeUrl)
                filePath = os.path.join(MyConfig.PrivateConfig.repoPath,'docs',encodeUrl)
                # print(filePath)
                if not os.path.exists(filePath):
                    print("发现失效的成长地图链接：", unquote(link))


if __name__ == '__main__':
    start()


