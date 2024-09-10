import os
import random
import string
import qrcode
from qrcode.constants import ERROR_CORRECT_H
import hashlib
from .config import keyStr
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
import json
import re

def convert_seconds(seconds,show_seconds=False):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if show_seconds:
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
    
    return f"{int(hours):02d}:{int(minutes):02d}"


def get_serial_number():
    if is_linux():
        # Linux 识别码
        with open('/sys/class/dmi/id/product_serial', "r") as f:
            return f.read().strip()
    else:
        # Windows 识别码
        import subprocess
        result = subprocess.run(['wmic', 'bios', 'get', 'serialnumber'], capture_output=True, text=True)
        return result.stdout.strip()
    
def get_local_ip():
    """
    获取本机内网IP地址
    """
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def is_linux():
    """ 判断设备是否是linux """
    if os.path.exists('/sys/class/dmi/id/product_serial'):
        return True
    else:
        return False

def filter_str(filename):
    filename = remove_special_characters(filename)
    invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|','#','\n','\r','\t',"'"]
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    if filename[-1] == '_':
        filename = filename[:-1]
        
    return filename

def remove_special_characters(text):
    # 定义特殊字符的正则表达式
    special_characters_pattern = re.compile(r'[^\w\s]')
    
    # 使用sub方法替换特殊字符为空字符
    result = special_characters_pattern.sub('', text)
    
    return result

def QRcode(data, file_dir = None):
    qr = qrcode.QRCode(
        version=1,
        error_correction=ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    if file_dir is None:
        img.show()
    else:
        img.save(file_dir)

def url_params(url):
    import urllib
    from urllib.parse import parse_qs
    params = parse_qs(urllib.parse.urlparse(url).query)

    data = {k: v[0] for k, v in params.items()}
    return data

def load_json(path:str):
    if os.path.exists(path) and path.endswith(".json"):
        with open(path, "r", encoding='utf-8') as infile:
            data = json.load(infile)
        
        return data
    else:
        return {}

def find_dict_key(data:list,dict_key:str):
    """
    在data中查找包含dict_key的键值，并返回一个包含该键值的列表。

    参数:
    data (list): 包含多个字典的的列表
    dict_key (str): 列表中某个字典的键的内容，支持模糊查询

    返回:
    list: 查询到的键值对的列表
    """
    result = []
    for college in data:
        for key in college:
            if dict_key in key:
                result.append(college)
                break
    return result

def get_list_dict(data):
    """
    获取包含字典的列表中的键和值。

    参数:
    data (list): 包含字典的列表

    返回:
    list: 包含键和值的列表
    """
    result = []
    for item in data:
        for key, value in item.items():
            result.append((key, value))
    return result


def save_json(path:str,data:dict,ensure_ascii=False) -> bool:
    if path.endswith(".json"):
        try:
            with open(path, "w", encoding='utf-8') as outfile:
                json.dump(data, outfile, ensure_ascii=ensure_ascii, indent=4)
            return True
        except:
            return False
    else:
        return False

def get_files(directory:str, reverse=False, exclude_prefixes:list=None) -> list:
    """ 获取目录下的所有文件

    Args:
        directory: 路径
        reverse: False:按创建日期正序排列,反之为逆序排列
        exclude_prefixes: 要排除的文件前缀列表

    Returns:
        list
    """
    # 获取目录下的所有文件
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    
    # 如果有指定要排除的文件前缀
    if exclude_prefixes:
        files = [f for f in files if not any(f.startswith(prefix) for prefix in exclude_prefixes)]
    
    # 根据文件的创建日期进行排序
    files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=reverse)
    
    return files

def get_redirect(response,show_history=False):
    if response.history:
        if show_history:
            # 打印重定向历史
            for r in response.history:
                print(f'Redirected from {r.url} to {r.headers["Location"]}')

        # 最终的网页URL
        final_url = response.url
        return final_url
    else:
        return None

def md5(data,short=False):
    """
    MD5 加密
    """
    md5_hash = hashlib.md5()
    md5_hash.update(str(data).encode('utf-8'))
    if short:
        return md5_hash.hexdigest()[:16]
    else:
        return md5_hash.hexdigest()

def sha256(string):
    hash_object = hashlib.sha256(string.encode())

    hash_hex = hash_object.hexdigest()

    return hash_hex

def rand():
    """
    输出随机字符串
    """
    return ''.join(random.choices(string.digits, k=10))

def getDirFiles(directory='./'):
    # 获取目录下的所有文件和文件夹
    all_files = os.listdir(directory)[::-1]

    # 获取目录下的所有文件（不包括子目录）
    files = [f for f in all_files if os.path.isfile(os.path.join(directory, f))]
    
    return files

def __add_to_16( text):
    """ 如果string不足16位则用空格补齐16位 """
    if len(text.encode()) % 16:
        add = 16 - (len(text.encode()) % 16)
    else:
        add = 0
    text += ("\0" * add)
    return text.encode()

def encode_aes(text):
    cryptos = AES.new(key=md5(get_serial_number()+keyStr,True).encode(), mode=AES.MODE_CBC, iv=get_iv())
    cipher_text = cryptos.encrypt(__add_to_16(text))
    return b2a_hex(cipher_text).decode('utf-8')

def decode_aes(text):
    try:
        cryptos = AES.new(key=md5(get_serial_number()+keyStr,True).encode(), mode=AES.MODE_CBC, iv=get_iv())
        plain_text = cryptos.decrypt(a2b_hex(text))
        return bytes.decode(plain_text).rstrip("\0")
    except:
        return 'Null'

def get_iv():
    hash_hex = sha256(md5(get_serial_number()+keyStr))
    iv = hash_hex[4:20].encode()

    return iv
