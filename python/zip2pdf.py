import os
import zipfile
import tarfile
import rarfile  # 需要安装 pip install rarfile
from PIL import Image
import sys
import fitz
import importlib.util
# # 获取当前脚本的目录
# script_dir = os.path.dirname(os.path.abspath(__file__))

# # 获取 `LoFTR-master/Analysis_PDF` 目录的绝对路径
# parent_dir = os.path.abspath(os.path.join(script_dir, "..", "..", "LoFTR-master", "Analysis_PDF"))

# # 确保路径正确
# if not os.path.exists(parent_dir):
#     raise FileNotFoundError(f"Directory not found: {parent_dir}")

# # 添加到 Python 搜索路径
# sys.path.insert(0, parent_dir)



# 动态链接1
pdf2image_path = os.path.join('e:\\code\\LoFTR-master\\Analysis_PDF', 'PDF2image.py')
# 确保文件存在
if not os.path.exists(pdf2image_path):
    raise FileNotFoundError(f"File not found: {pdf2image_path}")
# 动态加载模块
spec = importlib.util.spec_from_file_location("PDF2image", pdf2image_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
# 现在可以使用 read_pdf
read_pdf_one_pdf = module.read_pdf_one_pdf

# 动态链接2
matchcsv_path = r"E:\code\LoFTR-master\demo\test_excel_image.py"  # 直接使用绝对路径
# 确保文件存在
if not os.path.exists(matchcsv_path):
    raise FileNotFoundError(f"File not found: {matchcsv_path}")
spec_2 = importlib.util.spec_from_file_location("test_excel_image", matchcsv_path)
module_2 = importlib.util.module_from_spec(spec_2)
spec_2.loader.exec_module(module_2)
# 获取模块中的函数
process_images_from_csv = module_2.process_images_from_csv  # 确保 test_excel_image.py 内有这个函数



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


            ### 用于判断pdf生成是否成功
            # print(f"Added {image_path} to the PDF.")

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
    return output_pdf 

def main():
    """主函数，获取 Node.js 传入的 ZIP/TAR/RAR 文件路径，并转换为 PDF"""
    if len(sys.argv) < 2:
        print("Error: 请提供压缩文件路径")
        sys.exit(1)

    archive_path = sys.argv[1]  # 获取 Node.js 传来的文件路径
    base_name = os.path.splitext(os.path.basename(archive_path))[0]  # 获取文件名（无扩展名）
    output_pdf = f"{base_name}.pdf"  # 生成 PDF 文件名
    
    try:
        # 解压缩，并获取解压路径
        extract_folder = extract_archive(archive_path)
        

        # 转换图片为 PDF
        pdf_path = images_to_pdf(extract_folder, output_pdf)

        # 输出 PDF 路径，Node.js 可读取
        print(f"Success: {output_pdf}")

        # 生成需要的csv文件
        csv_path = os.path.join(extract_pdf_path)  # 保存csv文件的路径，就和pdf路径在一起
        save_csv_path = read_pdf_one_pdf(pdf_path, csv_path)

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    
    # 设置一个输出路径，用于保存相似的图像
    base_name = os.path.splitext(os.path.basename(archive_path))[0]
    save_same_img_path = os.path.join(extract_pdf_path, base_name, "same_images")
    process_images_from_csv(save_csv_path, save_csv_path, save_same_img_path)

if __name__ == "__main__":
    main()
