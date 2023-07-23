import requests
from cryptography.fernet import Fernet
from loguru import logger
import json
from functools import wraps
def retry(
    max_retry: int = 3,
    exception = (
        requests.ConnectTimeout,
        requests.ReadTimeout,
    )
):
    def warpper(func):
        @wraps(func)
        def closure(*args, **kwargs):
            for i in range(max_retry):
                try:
                    res = func(*args, **kwargs)
                except exception:
                    logger.error(f"第{i + 1}次重试, 尝试连接到服务器<{args[0]}:{args[1]}>超时")
                else:
                    return res
        return closure
    return warpper


class Client():
    def __init__(self, key: str, host: str, port: int) -> None:
        try:
            self.request_url = "http://{host}:{port}/{path}"
            self.fernet = Fernet(key)
            self.host = host
            self.port = port
        except ValueError:
            logger.error(f"<{host}:{port}>秘钥错误")
            raise KeyError(f"<{host}:{port}>秘钥错误")

    def _encrption(self, data):
        return self.fernet.encrypt(data.encode()).decode()

    def _encryption_dict(self, data: dict):
        new_data = {}
        for key, value in data.items():
            new_data.update({key: self._encrption(value)})
        return new_data

    @retry(max_retry=3)
    def add_user(self, proto: str, tag: str, user: dict):
        path = "userInterface/addUser"
        response = requests.post(self.request_url.format(host=self.host, port=self.port, path=path), json={
            'proto': self._encrption(proto),
            'tag': self._encrption(tag),
            'user': self._encryption_dict(user)
        }, timeout=3)
        if response.status_code == 200:
            result = json.loads(response.text)
            if result['result'] == -1:
                raise KeyError(f"服务器返回 -1")
            else:
                return result['result']
        else:
            raise Exception(f"请求<{self.host}:{self.port}>错误，状态码{response.status_code}")
        

    @retry(max_retry=3)
    def remove_user(self, tag: str, email: str):
        path = "userInterface/removeUser"
        response = requests.post(self.request_url.format(host=self.host, port=self.port, path=path), json={
            'tag': self._encrption(tag),
            'email': self._encrption(email),
        }, timeout=3)
        if response.status_code == 200:
            result = json.loads(response.text)
            if result['result'] == -1:
                raise KeyError(f"服务器返回 -1")
            else:
                return result['result']
        else:
            raise Exception(f"请求<{self.host}:{self.port}>错误，状态码{response.status_code}")

    @retry(max_retry=3)
    def add_inbound(self, proto: str, tag: str, port: int, users: list):
        path = "userInterface/addInbound"
        response = requests.post(self.request_url.format(host=self.host, port=self.port, path=path), json={
            'proto': self._encrption(proto),
            'tag': self._encrption(tag),
            'port': self._encrption(str(port)),
            'users': [self._encryption_dict(user) for user in users]
        }, timeout=3)
        if response.status_code == 200:
            result = json.loads(response.text)
            if result['result'] == -1:
                raise KeyError(f"服务器返回 -1")
            else:
                return result['result']
        else:
            raise Exception(f"请求<{self.host}:{self.port}>错误，状态码{response.status_code}")       
    # @retry(max_retry=3)
    # def init_all_user(self, node: str, user_json: list):
    #     path = "userInterface/initAllUser"
    #     cipher_user_json = [
    #         {
    #             self.fernet.encrypt(uuid.encode()).decode(): self.fernet.encrypt(email.encode()).decode() 
    #                 for uuid, email in user.items()
    #             } 
    #             for user in user_json
    #         ]

    #     response = requests.post(self.request_url.format(host=self.host, port=self.port, path=path), json={
    #         'node': self.fernet.encrypt(node.encode()).decode(),
    #         'user_json': cipher_user_json
    #     }, timeout=settings.V2PEND_REQUESTS_TIMEOUT)
    #     if response.status_code == 200:
    #         result = json.loads(response.text)
    #         if result['result'] == -1:
    #             raise KeyError(f"<{self.host}:{self.port}>秘钥错误，服务器返回 -1")
    #         else:
    #             return result['result']
    #     else:
    #         raise StatusCodeError(f"请求<{self.host}:{self.port}>错误，状态码{response.status_code}")

user = {
    "uuid": "d83d381d-6322-4d53-ad4f-8cdad8b20822",
    "level": "0",
    "email": "test@vshrine.com"
}
client = V2pendClient(b'J6ac9lMDx3ruWXjlwWVyfzyAKV1lvxx1No0uizGVK3s=', '23.254.132.133', 38909)
# # add user
# client.add_user(
#     "vless", "C",
#     {
#         "uuid": "d83d381d-6322-4d53-ad4f-8cdad8b20822",
#         "level": "0",
#         "email": "test@vshrine.com"
#     }
# )

# remove user
# client.remove_user("C", "test@vshrine.com")

# add inbound
client.add_inbound("vless", "1a12", 45808, [])