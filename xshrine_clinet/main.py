from errors import *
from cryptography.fernet import Fernet, InvalidToken
from cryptography.exceptions import InvalidSignature
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from uuid import uuid4
from port import get_open_port
from settings import *
import argparse
import requests
import socket
import binascii
import json

class CryptoHandle():
    def __init__(self, key):
        self.cipher = AES.new(self._pad(key), AES.MODE_ECB)
    
    # 16转2进制
    def _unhexlify(self, hex):
        return binascii.unhexlify(hex)
    
    # 填充
    def _pad(self, text):
        return pad(text.encode(), 16, style='pkcs7')
    
    # 去填充
    def _unpad(self, text):
        return unpad(text, 16, style='pkcs7').decode()

    # 加密
    def encrypt(self, message):
        return self.cipher.encrypt(self._pad(message)).hex()

    # 解密
    def decrypt(self, ciphertext):
        return self._unpad(self.cipher.decrypt(self._unhexlify(ciphertext)))
    
# try to connect api port
def connectInit(timeout, host, port):
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk.settimeout(timeout)
    try:
        sk.connect((host, port))
        print(f"{host}:{port} connect OK! ")
        sk.close()
        return True
    except:
        print(f"{host}:{port} connect ERROR! ")
        return False

def arg_parser():
    parser = argparse.ArgumentParser(description='Xshrine client project.')
    parser.add_argument('-i', '--init', help='Client first init.', action='store_true')
    parser.add_argument('-r', '--register', help='Client register to server.')
    parser.add_argument('-d', '--domain', help='Client domain.')
    return parser.parse_args()

def client_init():
    BASE_DIR = Path(Path(__file__).absolute()).parent
    setting_file = Path(BASE_DIR, 'settings.py')
    key = Fernet.generate_key().decode()
    uuid = uuid4()
    port = get_open_port()

    with open(setting_file, 'r', encoding='utf-8') as f:
        content = f.readlines()

    switches = [False, False, False]
    new_content = []

    for line in content:
        if line.startswith('CLIENT_LISTEN_PORT'):
            new_line = f'CLIENT_LISTEN_PORT = {port}\n'
            switches[0]= True
        elif line.startswith('CLIENT_UUID'):
            new_line = f'CLIENT_UUID = "{uuid}"\n'
            switches[1]= True
        elif line.startswith('CLIENT_KEY'):
            new_line = f'CLIENT_KEY = "{key}"\n'
            switches[2]= True
        else:
            new_line = line
        new_content.append(new_line)
    
    if not switches[0]:
        new_content.append(f'CLIENT_LISTEN_PORT = {port}\n')
    if not switches[1]:
        new_content.append(f'CLIENT_UUID = "{uuid}"\n')
    if not switches[2]:
        new_content.append(f'CLIENT_KEY = "{key}"\n')

    with open(setting_file, 'w', encoding='utf-8') as f:
        f.writelines(new_content)

    return True

def client_register(url, host, port, key, uuid):
    data = {
        'command': 'register',
        'host': host,
        'port': port,
        'key': key,
        'uuid': uuid,
    }
    return requests.post(url, data=data)

def main():
    args = arg_parser()

    if args.init:
        if client_init():
            print('客户端初始化完成')
            return

    if args.register:
        crypto_handle = CryptoHandle('register')
        if args.domain:
            host=args.domain
        else:
            host='none'

        response = client_register(
            url=args.register,
            host=crypto_handle.encrypt(host),
            port=crypto_handle.encrypt(str(CLIENT_LISTEN_PORT)),
            key=crypto_handle.encrypt(CLIENT_KEY),
            uuid=crypto_handle.encrypt(CLIENT_UUID)
        )

        if response.status_code == 200:
            result = json.loads(response.text)
            if result['status'] == 1:
                print('客户端注册完成')
            else:
                print(result)
                print('客户端注册失败')
        return 

    from runner import main
    if connectInit(3, API_HOST, API_PORT):
        main()

if __name__ == "__main__":
    main()