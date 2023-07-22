"""从v2ray-core源码目录中寻找`.proto`文件并编译"""
import os
from pathlib import Path
import sys
import shutil
import tempfile
import distutils.dir_util

BASE_DIR = Path(Path(__file__).absolute()).parent
TEMP_DIR = tempfile.mkdtemp()
XRAY_DIR = Path(TEMP_DIR, 'xray.com')
XRAY_CORE_BASE =  Path(TEMP_DIR, 'xray')

def walk(src, dst):
    # 导入路径类似'v2ray.com/core/common/serial/typed_message.proto'
    # 需整理好目录树
    ## 创建缓存文件夹

    os.makedirs(XRAY_DIR)
    shutil.copytree(src, XRAY_CORE_BASE)

    # 扫描proto文件
    proto_files = ''
    for root, _, files in os.walk(XRAY_CORE_BASE):
        for file in files:
            if file.endswith(".proto"):
                proto_files += ' ' + str(Path(root, file))
    if not proto_files:
        raise FileNotFoundError("未找到任何proto文件")

    # 编译
    command = f'{sys.executable} -m grpc.tools.protoc ' \
              f'-I={XRAY_CORE_BASE} ' \
              f'--python_out={XRAY_DIR} ' \
              f'--grpc_python_out={XRAY_DIR} ' + proto_files
    result = os.system(command)
    print(result)
    # 编译后*_pb2_grpc.py和*_pb2.py分别在v2ray.com和v2ray目录中
    # 将他们合并到一个目录
    # print('start 1')
    distutils.dir_util.copy_tree(XRAY_DIR, str(dst))
    shutil.rmtree(TEMP_DIR)

if __name__ == '__main__':
    src = Path(BASE_DIR, "xray-core")
    dst = Path(BASE_DIR)
    if not os.path.exists(dst):
        os.mkdir(dst)
    walk(src, dst)
            