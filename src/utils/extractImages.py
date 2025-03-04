import os
import markdown
import re


def extract_images_from_md():
    md_folder = input("请输入md文件所在文件夹的路径：")
    destination_folder = input("请输入图片复制存储的路径：")
    # 在目标路径下创建 assets 文件夹
    assets_folder = os.path.join(destination_folder, "assets")
    image_extensions = [".jpg", ".jpeg", ".png", ".gif"]
    for root, dirs, files in os.walk(md_folder):
        for file in files:
            if file.endswith(".md"):
                md_file_path = os.path.join(root, file)
                with open(md_file_path, 'r', encoding='utf-8') as md_file:
                    content = md_file.read()
                    html = markdown.markdown(content)
                    # 使用正则表达式提取图片路径
                    img_tags = re.findall('<img.*?src="(.*?)"', html)
                    for img_path in img_tags:
                        # 处理相对路径
                        if not os.path.isabs(img_path):
                            img_path = os.path.join(os.path.dirname(md_file_path), img_path)
                        img_extension = os.path.splitext(img_path)[1].lower()
                        if img_extension in image_extensions:
                            try:
                                # 创建 assets 文件夹
                                if not os.path.exists(assets_folder):
                                    os.makedirs(assets_folder)
                                img_file_name = os.path.basename(img_path)
                                destination_path = os.path.join(assets_folder, img_file_name)
                                # 复制图片文件
                                with open(img_path, 'rb') as source_img, open(destination_path, 'wb') as destination_img:
                                    destination_img.write(source_img.read())
                            except Exception as e:
                                print(f"无法复制图片 {img_path}，原因是：{e}")


if __name__ == "__main__":
    extract_images_from_md()