import os
import zipfile
import tarfile
import rarfile  # 需要安装 pip install rarfile
from PIL import Image
import sys
import fitz

extract_image_path = r"E:\code\QD\output\images"
extract_pdf_path = r"E:\code\QD\output\pdf"

def extract_archive(archive_path):
    """解压 ZIP、TAR、RAR 文件，并将解压目录命名为 '原文件名_img' """
    base_name = os.path.splitext(os.path.basename(archive_path))[0]  # 获取文件名（无扩展名）
    extract_to = os.path.join(extract_image_path, f"{base_name}_img") # 目标解压文件夹
    os.makedirs(extract_to, exist_ok=True)  # 创建解压目录
    
    if archive_path.endswith('.zip'):
        with zipfile.ZipFile(archive_path, 'r') as archive:
            archive.extractall(extract_to)
    elif archive_path.endswith(('.tar.gz', '.tar', '.tgz')):
        with tarfile.open(archive_path, 'r') as archive:
            archive.extractall(extract_to)
    elif archive_path.endswith('.rar'):
        with rarfile.RarFile(archive_path, 'r') as archive:
            archive.extractall(extract_to)
    else:
        raise ValueError("不支持的压缩文件格式，仅支持 ZIP、TAR、RAR")

    return extract_to  # 返回解压后的文件夹路径


def images_to_pdf(input_folder, output_pdf=None):
    supported_formats = {".tif", ".tiff", ".jpg", ".jpeg", ".png"}

    # 目标图片文件夹
    input_folder2 = os.path.join(input_folder, "images")
    print(f"input_folder2: {input_folder2}")

    if not os.path.exists(input_folder2):
        print("Error: The specified folder does not exist.")
        return

    # 获取所有符合格式的图片文件
    image_files = [os.path.join(input_folder2, f) for f in os.listdir(input_folder2)
                   if os.path.splitext(f)[1].lower() in supported_formats]

    if not image_files:
        print("Error: No supported image files found in the specified folder.")
        return

    image_files.sort()

    if output_pdf is None:
        base_name = os.path.basename(input_folder)
        output_pdf = os.path.join(input_folder, f"{base_name}_pdf.pdf")

    pdf_document = fitz.open()

    for image_path in image_files:
        try:
            img = Image.open(image_path)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # **修复方式：确保图片格式正确**
            temp_image_path = image_path + "_converted.jpg"
            img.save(temp_image_path, "JPEG")  # 重新保存为标准 JPEG
            
            img_temp = fitz.open()
            rect = fitz.Rect(0, 0, img.width, img.height)
            page = img_temp.new_page(width=img.width, height=img.height)
            page.insert_image(rect, filename=temp_image_path)  # 使用转换后的图片

            pdf_document.insert_pdf(img_temp)
            img_temp.close()

            print(f"Added {image_path} to the PDF.")

            # 删除临时文件
            os.remove(temp_image_path)

        except Exception as e:
            print(f"Error processing {image_path}: {e}")

            
    # 保存最终 PDF 文档
    base_name = os.path.splitext(os.path.basename(input_folder))[0]
    output_pdf = os.path.join(extract_pdf_path, f"{base_name}_pdf.pdf") 
    pdf_document.save(output_pdf)
    pdf_document.close()
    print(f"PDF file created successfully at {output_pdf}")


image_path = r"E:\code\QD\output\images\1740464347957_img"
out_path = r"E:\code\QD\output\pdf"
images_to_pdf(image_path, out_path)