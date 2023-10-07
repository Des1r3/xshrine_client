from errors import *
from cryptography.fernet import Fernet, InvalidToken
from cryptography.exceptions import InvalidSignature
from uuid import uuid4
from port import get_open_port
import argparse
import requests
import socket
import base64
import os
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import socket

BASE_DIR = Path(Path(__file__).absolute()).parent

class Fernet_encipher:
    def __init__(self, key, ttl_time=60):
        self.fernet = Fernet(key.encode())
        self.ttl_time = ttl_time

    def encrypt(self, data):
        if type(data) == int:
            data = str(data)
        return self.fernet.encrypt(data.encode()).decode()

    def encrypt_dict(self, data: dict):
        encrypt_data = {}
        for key, value in data.items():
            encrypt_data.update({key: self.encrypt(value)})
        return encrypt_data

    def decrypt(self, data):
        return self.fernet.decrypt(data.encode(), self.ttl_time).decode()

    def decrypt_dict(self, data: dict):
        decrypt_data = {}
        for key, value in data.items():
            value = self.decrypt(value)
            if value.isdigit():
                value = int(value)
            decrypt_data.update(
                {key: value}
            )
        return decrypt_data

def get_shared_key(received_public_key, private_key):
    received_public_key = serialization.load_pem_public_key(received_public_key)
    return private_key.exchange(ec.ECDH(), received_public_key)

def ecdh_generater(received_public_key=None):
    # Generate private key
    private_key = ec.generate_private_key(ec.SECP256R1())

    # Get public key
    public_key = private_key.public_key()

    # Serialize public key to send to other party
    serialized_public_key = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Perform key exchange
    if received_public_key:
        # Deserialize public key received from other party
        shared_key = get_shared_key(received_public_key, private_key)
    else:
        shared_key = None
    
    return serialized_public_key, private_key, shared_key

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
    parser.add_argument('--init', help='Client first init.', action='store_true')
    parser.add_argument('-f', '--fast', help='Fast register mode.', action='store_true')
    parser.add_argument('-r', '--register', help='Client register to server.')
    parser.add_argument('-d', '--domain', help='Client domain.')
    return parser.parse_args()

def client_init(uuid, key, port=33459):

    # 判断文件是否存在
    settings_file = Path(BASE_DIR, 'settings.py')
    if os.path.exists(settings_file):
        print("Cannot execute initialization because <settings.py> is already exists.")
        return False
    
    # settings.py 文件模板
    settings_template = f"""
from pathlib import Path
BASE_DIR = Path(Path(__file__).absolute()).parent

# API port config
API_HOST = "127.0.0.1"
API_PORT = 20057

# Client config
CLIENT_KEY_TTLTIME = 30
CLIENT_LISTEN_PORT = {port}
CLIENT_UUID = "{uuid}"
CLIENT_KEY = "{key}"
"""

    with open(settings_file, 'w', encoding='utf-8') as f:
        f.write(settings_template)

    return True

def get_key(url):
    # 获取共享秘钥
    serialized_public_key, private_key, _ = ecdh_generater()
    response = requests.post(
        url = url,
        data = {
            'command': 'register_get_key',
            'public_key': serialized_public_key.decode()
        }
    )
    if response.status_code == 200:
        result = response.json()

        if result['status'] == 1:
            # 计算共享密钥
            shared_key = get_shared_key(result['message'].encode(), private_key)

            # 转换为base64
            return base64.b64encode(shared_key).decode('utf-8')

def client_register(url, host, port, uuid, shared_key, secret_key=None):
    if not secret_key:
        secret_key = shared_key

    # 向服务端进行注册
    fc = Fernet_encipher(key=shared_key)
    response = requests.post(
        url = url,
        data = {
            'command': 'register',
            'host': fc.encrypt(host),
            'port': fc.encrypt(port),
            'key': fc.encrypt(secret_key),
            'uuid': fc.encrypt(uuid)
        }
    )
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 1:
            print('客户端注册完成')
        else:
            print(f'客户端注册失败, error: {result}')

def main():
    args = arg_parser()

    if args.domain:
        host = args.domain
    else:
        host = 'none'

    # 配置文件初始化，随机生成 key
    if args.init:
        if client_init(
            uuid = uuid4(),
            key = Fernet.generate_key().decode()
        ):
            print('客户端初始化完成')

    # 注册，http://116.205.188.228:7777/processClientUpload/
    elif args.register:
        from settings import CLIENT_LISTEN_PORT, CLIENT_UUID, CLIENT_KEY
        url = args.register
        shared_key = get_key(url)
        client_register(url, host, CLIENT_LISTEN_PORT, CLIENT_UUID, shared_key, CLIENT_KEY)

    # 快速注册模式，无需手工配置就能完成注册
    elif args.register and args.fast:
        url = args.register

        # 获取随机 uuid/port/key
        uuid = str(uuid4())
        port = get_open_port()
        shared_key = get_key(url)

        # 初始化
        if client_init(uuid, shared_key, port):
            # 注册
            client_register(url, host, port, uuid, shared_key)
        else:
            return

    else:
        import runner
        from settings import API_HOST, API_PORT

        if connectInit(3, API_HOST, API_PORT):
            runner.main()

if __name__ == "__main__":
    main()
