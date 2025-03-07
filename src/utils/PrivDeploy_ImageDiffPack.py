import os
import re
import shutil
import tarfile
from math import ceil


def get_image_names_from_md_files(md_dir):
    """
    从指定目录下的所有 Markdown 文件中提取引用的图片名称
    :param md_dir: Markdown 文件所在目录
    :return: 图片名称列表
    """
    image_names = []
    for root, dirs, files in os.walk(md_dir):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as md_file:
                        content = md_file.read()
                        pattern = r'([\w._-]+\.(?:jpg|jpeg|png|gif|bmp))'
                        found_images = re.findall(pattern, content)
                        image_names.extend(found_images)
                except FileNotFoundError:
                    print(f"文件 {file_path} 未找到。")
    return image_names


def get_new_images(old_image_names, new_image_names):
    """
    获取新版本新增的图片
    :param old_image_names: 原文档引用的图片名称列表
    :param new_image_names: 新文档引用的图片名称列表
    :return: 新增图片名称列表
    """
    return [image for image in new_image_names if image not in old_image_names]


def get_total_size(files, assets_dir):
    """
    计算文件列表的总大小
    :param files: 文件列表
    :param assets_dir: 图片所在目录
    :return: 总大小（字节）
    """
    total_size = 0
    for file in files:
        file_path = os.path.join(assets_dir, file)
        if os.path.exists(file_path):
            total_size += os.path.getsize(file_path)
    return total_size


def split_files_by_size(files, assets_dir, max_size=200 * 1024 * 1024):
    """
    按指定大小分割文件列表
    :param files: 文件列表
    :param assets_dir: 图片所在目录
    :param max_size: 最大分卷大小（字节），默认 200MB
    :return: 分割后的文件列表
    """
    # 过滤不存在的文件
    valid_files = [file for file in files if os.path.exists(os.path.join(assets_dir, file))]

    split_files = []
    current_files = []
    current_size = 0
    for file in valid_files:
        file_path = os.path.join(assets_dir, file)
        file_size = os.path.getsize(file_path)
        if current_size + file_size > max_size:
            split_files.append(current_files)
            current_files = [file]
            current_size = file_size
        else:
            current_files.append(file)
            current_size += file_size
    if current_files:
        split_files.append(current_files)
    return split_files


def compress_files(files, assets_dir, output_base_name):
    """
    压缩文件
    :param files: 文件列表
    :param assets_dir: 图片所在目录
    :param output_base_name: 输出文件名基础部分
    """
    for i, part_files in enumerate(files, start=1):
        output_name = f"{output_base_name}.tar.gz.{str(i).zfill(3)}"
        with tarfile.open(output_name, "w:gz") as tar:
            for file in part_files:
                file_path = os.path.join(assets_dir, file)
                tar.add(file_path, arcname=file)
        print(f"压缩完成，输出文件: {output_name}")


def main(old_md_dir, new_md_dir, new_assets_dir):
    # 获取原文档和新文档中引用的图片名称
    old_image_names = get_image_names_from_md_files(old_md_dir)
    new_image_names = get_image_names_from_md_files(new_md_dir)

    # 获取新版本新增的图片
    new_images = get_new_images(old_image_names, new_image_names)

    print("新版本新增的图片:")
    for image in new_images:
        print(image)

    # 计算新增图片总大小
    total_size = get_total_size(new_images, new_assets_dir)

    # 按 200MB 分卷
    if total_size > 200 * 1024 * 1024:
        split_new_images = split_files_by_size(new_images, new_assets_dir)
    else:
        split_new_images = [new_images]

    # 压缩文件
    output_base_name = "assets"
    compress_files(split_new_images, new_assets_dir, output_base_name)


if __name__ == "__main__":
    # 输入原文档地址
    old_md_dir = input("请输入原 docs 文件夹地址: ")
    # 输入新文档地址
    new_md_dir = input("请输入新 docs 文件夹地址: ")
    # 输入新版 assets 地址
    new_assets_dir = input("请输入新版 assets 地址: ")

    main(old_md_dir, new_md_dir, new_assets_dir)