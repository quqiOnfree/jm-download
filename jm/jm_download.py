from jmcomic import *
import os
import pyzipper
import shutil
from PIL import Image
from fpdf import FPDF

def create_encrypted_zip(input_path, output_zip, password):
    """
    创建分卷压缩的AES-256加密ZIP文件
    
    :param input_path: 要压缩的文件/目录路径
    :param output_zip: 输出ZIP文件名（含后缀）
    :param password: 加密密码
    """
    
    # 创建加密的临时ZIP
    with pyzipper.AESZipFile(
        output_zip, 'w', 
        compression=pyzipper.ZIP_DEFLATED,
        encryption=pyzipper.WZ_AES
    ) as zf:
        zf.setpassword(password.encode())
        zf.setencryption(pyzipper.WZ_AES, nbits=256)
        
        if os.path.isdir(input_path):
            for root, dirs, files in os.walk(input_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, input_path)
                    zf.write(file_path, arcname)
        else:
            zf.write(input_path, os.path.basename(input_path))

def create_encrypted_split_zip(input_path, output_zip, password, volume_size):
    """
    创建分卷压缩的AES-256加密ZIP文件
    
    :param input_path: 要压缩的文件/目录路径
    :param output_zip: 输出ZIP文件名（不含后缀）
    :param password: 加密密码
    :param volume_size: 每个分卷大小（B）
    """
    # 计算字节大小
    chunk_size = volume_size
    
    # 临时ZIP路径
    temp_zip = f"{output_zip}_temp.zip"
    
    create_encrypted_zip(input_path, temp_zip, password)
    
    # 分割临时ZIP文件
    split_zip(temp_zip, output_zip, chunk_size)
    
    # 清理临时文件
    os.remove(temp_zip)

def split_zip(input_file, output_prefix, chunk_size):
    """
    分割ZIP文件为多个分卷
    
    :param input_file: 输入文件路径
    :param output_prefix: 输出文件前缀
    :param chunk_size: 每个分卷大小（字节）
    """
    part_num = 1
    with open(input_file, 'rb') as f:
        chunk = f.read(chunk_size)
        while chunk:
            part_name = f"{output_prefix}.zip.{str(part_num).zfill(3)}"
            with open(part_name, 'wb') as part_file:
                part_file.write(chunk)
            part_num += 1
            chunk = f.read(chunk_size)

def webp_to_pdf(input_folder, output_pdf, margin=10):
    """
    将文件夹中的WebP图片转换为PDF文件
    
    :param input_folder: 包含WebP图片的文件夹路径
    :param output_pdf: 输出的PDF文件路径
    :param margin: 页面边距(毫米)
    """
    webp_files = os.listdir(input_folder)
    webp_files.sort(key=lambda x: int(os.path.splitext(x)[0]))

    pdf = FPDF(unit="mm", format="A4")
    
    # 处理每张图片
    for filename in webp_files:
        img_path = os.path.join(input_folder, filename)
        
        try:
            with Image.open(img_path) as img:
                # 处理透明度（转换为白色背景）
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background
                else:
                    img = img.convert('RGB')
                
                # 保存为临时JPEG文件
                temp_path = f"temp_{filename}.jpg"
                img.save(temp_path, "JPEG")
                
                # 获取图片尺寸
                img_width, img_height = img.size
                aspect_ratio = img_width / img_height
                
                # 计算在PDF中的尺寸（保留宽高比）
                max_width = 210 - 2 * margin  # A4宽度减去边距
                max_height = 297 - 2 * margin # A4高度减去边距
                
                pdf_width = max_width
                pdf_height = pdf_width / aspect_ratio
                
                # 如果高度超过页面，调整宽度
                if pdf_height > max_height:
                    pdf_height = max_height
                    pdf_width = pdf_height * aspect_ratio
                
                # 计算居中位置
                x = (210 - pdf_width) / 2
                y = (297 - pdf_height) / 2
                
                # 添加新页面
                pdf.add_page()
                
                # 添加图片到PDF
                pdf.image(temp_path, x=x, y=y, w=pdf_width)
                
                # 删除临时文件
                os.remove(temp_path)
                
        except Exception as e:
            print(f"处理图片 {filename} 时出错: {str(e)}")
    
    # 保存PDF
    pdf.output(output_pdf)

def compress(jm_id, password):
    album, downloader = download_album(jm_id, check_exception=True)
    if "temp" not in os.listdir():
        os.mkdir("./temp")
    if "pdftemp" not in os.listdir():
        os.mkdir("./pdftemp")
    webp_to_pdf(os.path.join("./", album.name), os.path.join("./pdftemp", album.name) + ".pdf")
    create_encrypted_split_zip(
        input_path="./pdftemp",
        output_zip=os.path.join("./temp", album.name),
        password=password,
        volume_size=os.stat(os.path.join("./pdftemp", album.name) + ".pdf").st_size // 3
    )
    shutil.rmtree("./" + album.name)
    create_encrypted_zip(
        input_path="./temp",
        output_zip=os.path.join("./", "pwd" + password) + ".zip",
        password=password)
    for i in os.listdir("./temp"):
        if os.path.splitext(i)[0] == album.name + ".zip":
            os.remove(os.path.join("./temp", i))
    for i in os.listdir("./pdftemp"):
        if os.path.splitext(i)[0] == album.name:
            os.remove(os.path.join("./pdftemp", i))
    return os.path.abspath(os.path.join(os.getcwd(), "pwd" + password + ".zip"))
