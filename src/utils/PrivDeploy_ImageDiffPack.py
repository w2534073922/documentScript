import os
import re
import tarfile
import shutil
import subprocess


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


def copy_new_images(new_images, new_assets_dir, storage_dir):
    """
    将新增图片复制到指定的存储目录下的 assets 文件夹中
    :param new_images: 新增图片名称列表
    :param new_assets_dir: 新增图片所在目录
    :param storage_dir: 存储新增图片的根目录
    """
    assets_folder = os.path.join(storage_dir, 'assets')
    if not os.path.exists(assets_folder):
        os.makedirs(assets_folder)
    for image in new_images:
        source_path = os.path.join(new_assets_dir, image)
        if os.path.exists(source_path):
            destination_path = os.path.join(assets_folder, image)
            shutil.copy2(source_path, destination_path)
            print(f"已复制 {image} 到 {destination_path}")
    return assets_folder


def compress_7z(tar_file_path, max_size=200 * 1024 * 1024):
    """
    使用 7z 对 tar 文件进行分卷压缩
    :param tar_file_path: tar 文件路径
    :param max_size: 最大分卷大小（字节），默认 200MB
    """
    max_size_str = f"{max_size // (1024 * 1024)}m"
    output_7z_path = f"{tar_file_path}.7z"
    try:
        cmd = ['7z', 'a', '-v' + max_size_str, output_7z_path, tar_file_path]
        subprocess.run(cmd, check=True)
        print(f"7z 分卷压缩完成，输出文件以 {output_7z_path} 开头")
    except subprocess.CalledProcessError as e:
        print(f"7z 压缩过程中出现错误: {e}")


def compress_assets_dir(assets_dir, output_base_name):
    """
    将 assets 文件夹打包为 tar 文件，再将 tar 文件以 7z 格式分卷压缩
    :param assets_dir: 要压缩的 assets 文件夹
    :param output_base_name: 输出文件名基础部分
    """
    storage_dir = os.path.dirname(assets_dir)
    tar_file_name = os.path.join(storage_dir, f"{output_base_name}.tar")
    with tarfile.open(tar_file_name, "w") as tar:
        for root, dirs, files in os.walk(assets_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, assets_dir)
                tar.add(file_path, arcname=arcname)
    print(f"第一次打包完成，输出文件: {tar_file_name}")

    # 7z 分卷压缩
    compress_7z(tar_file_name)


def main(old_md_dir, new_md_dir, new_assets_dir, storage_dir):
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
    print(f"新增图片总大小: {total_size} 字节")

    # 复制新增图片到指定存储目录下的 assets 文件夹
    assets_folder = copy_new_images(new_images, new_assets_dir, storage_dir)

    # 压缩 assets 文件夹
    output_base_name = "assets"
    compress_assets_dir(assets_folder, output_base_name)


if __name__ == "__main__":
    # 输入原文档地址
    old_md_dir = input("请输入原 docs 文件夹地址: ")
    # 输入新文档地址
    new_md_dir = input("请输入新 docs 文件夹地址: ")
    # 输入新版 assets 地址
    new_assets_dir = input("请输入新版 assets 地址: ")
    # 输入存储新增图片的地址
    storage_dir = input("请输入存储新增图片的地址: ")

    main(old_md_dir, new_md_dir, new_assets_dir, storage_dir)