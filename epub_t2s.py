#!/usr/bin/env python
import os
import zipfile
import opencc
import shutil
import argparse

# 创建一个ArgumentParser对象
parser = argparse.ArgumentParser(description='文件繁转简')

# 添加命令行参数
parser.add_argument('epub_t2s', help='输入文件夹的路径')

# 解析命令行参数
args = parser.parse_args()

# 指定路径和文件扩展名
source_folder = args.epub_t2s
archive_extensions = '.epub'
converter_file = 't2s.json'
file_extensions = ['.xhtml', '.html', '.ncx', '.opf']
#['.xhtml', '.html', '.ncx', '.opf']

#将指定路径的epub文件进行解压
def extract_archive(archive_path, destination_folder, archive_extensions):
    if archive_path.endswith(archive_extensions):
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(destination_folder)
        os.remove(archive_path)

#对一串字符进行繁简转换
def convert_text(text, converter_file):
    # 创建OpenCC转换器
    converter = opencc.OpenCC(converter_file)
    # 进行繁简转换
    converted_text = converter.convert(text)
    return converted_text

#对单个文件进行繁简转换
def convert_file_content(file_path, converter):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    converted_content = converter.convert(content)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(converted_content)

#对指定路径的所有指定格式文件进行繁简转换
def convert_files(path, file_extension, json_file):
    converter = opencc.OpenCC(json_file)  # 创建繁简转换器
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(tuple(file_extension)):
                file_path = os.path.join(root, file)
                print(f"Converting file: {file_path}")
                convert_file_content(file_path, converter)

#对指定路径文件夹进行压缩
def zip_folder(folder_path, archive_extensions):
    # 创建一个ZipFile对象，用于写入压缩文件
    zipf = zipfile.ZipFile(folder_path + archive_extensions, 'w', zipfile.ZIP_DEFLATED)
    # 遍历文件夹中的所有文件和子文件夹
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # 构建文件的完整路径
            file_path = os.path.join(root, file)
            # 将文件添加到压缩文件中
            zipf.write(file_path, arcname=os.path.relpath(file_path, folder_path))
    # 关闭压缩文件
    zipf.close()
    shutil.rmtree(folder_path)

# 遍历指定文件夹下的所有文件
files = os.listdir(source_folder)
for file in files:
    if file.endswith(tuple(archive_extensions)):
        archive_path = os.path.join(source_folder, file)
        print(f"Extracting archive: {archive_path}")
        new_folder = convert_text(os.path.splitext(file)[0], converter_file)
        destination_folder = os.path.join(source_folder, new_folder)
        try:
            os.makedirs(destination_folder)
        except FileExistsError:
            continue
        extract_archive(archive_path, destination_folder, archive_extensions)
        convert_files(destination_folder, file_extensions, converter_file)
        zip_folder(destination_folder, archive_extensions)
        print(f"Finished: {destination_folder}")