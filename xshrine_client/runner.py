from client import Client, User
from fastapi import FastAPI, Request, Body
import logging.config
from errors import *
from functools import wraps
from fastapi import FastAPI, Request, Body
from cryptography.fernet import Fernet, InvalidToken
from cryptography.exceptions import InvalidSignature
from settings import *
from log import config
from port import get_open_port
from typing import Optional, Union
from settings import *
import uvicorn
import re

logging.config.dictConfig(config.LOGGING_CONFIG)
logger = logging.getLogger("main")

app = FastAPI(docs_url=None, redoc_url=None)
client = Client(API_HOST, API_PORT)
fernet = Fernet(CLIENT_KEY.encode())

# API key check
def check_key(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except (InvalidToken, InvalidSignature):
            logger.warning(f"{func.__name__}: get a wrong key!")
            return {
                "result": -1,
            }
    return wrapper

# decrypt str/int value
def _decrypt(data: Union[str, int, None]):
    return fernet.decrypt(data.encode(), CLIENT_KEY_TTLTIME).decode()

# decryption dict value
def _decrypt_dict(data: dict):
    decryption_data = {}
    for key, value in data.items():
        if key == "level":
            value = int(_decrypt(value))
        else:
            value = _decrypt(value)
        decryption_data.update(
            {key: value}
        )
    return decryption_data
    
@app.post("/flowQuery")
@check_key
async def flowQuery(
    email: str = Body(title='email', embed=True),
):
    email = _decrypt(email)
    try:
        flow = client.return_total_flow(email)
        return {"result": 1, "details": flow}
    except EmailNotFoundError as error:
        logger.info(error)
        return {"result": 1, "details": 0}
    except Exception as error:
        logger.warning(error)
        return {"result": 0, "details": "节点 {node} 未知错误"}
    
@app.post("/userInterface/addUser")
@check_key
async def addUser(
    proto: str = Body(title='proto', embed=True),
    tag: str = Body(title='tag', embed=True),
    user: dict = Body(title='user', embed=True), 
):
    proto = _decrypt(proto)
    tag = _decrypt(tag)
    user = _decrypt_dict(user)
    try:
        if client.add_user(proto, tag, User(**user)):
            return {"result": 1, "details": '节点 {node} 用户添加成功'}
        else:
            return {"result": 0, "details": '节点 {node} 用户添加失败'}
    except EmailExistsError as error:
        logger.warning(error)
        return {"result": 0, "details": "节点 {node} 用户已经存在"}
    except InboundNotFoundError as error:
        logger.warning(error)
        return {"result": 0, "details": "不能在站点中找到节点 {node} 的标记，需要检查节点标记是否正确"}
    except Exception as error:
        logger.warning(error)
        return {"result": 0, "details": "节点 {node} 未知错误"}

@app.post("/userInterface/removeUser")
@check_key
async def removeUser(
    tag: str = Body(..., title='tag', embed=True),
    email: str = Body(..., title='email', embed=True),
):
    tag = _decrypt(tag)
    email = _decrypt(email)
    try:
        if client.remove_user(tag, email) == email:
            return {"result": 1}
        else:
            return {"result": 0, "details": '节点 {node} 移除用户失败'}
    except EmailNotFoundError as error:
        logger.warning(error)
        return {"result": 0, "details": "节点 {node} 没有这个用户"}
    except InboundNotFoundError as error:
        logger.warning(error)
        return {"result": 0, "details": "不能在站点中找到节点 {node} 的标记，需要检查节点标记是否正确"}
    except Exception as error:
        logger.warning(error)
        return {"result": 0, "details": "节点 {node} 未知错误"}

@app.post("/userInterface/addInbound")
@check_key
async def addInbound(
    proto: str = Body(..., title='proto', embed=True),
    config: str = Body(..., title='config', embed=True),
    tag: str = Body(..., title='tag', embed=True),
    users: list = Body(..., title='users', embed=True),
    port: str = Body(..., title='port', embed=True),
    random_port: str = Body(..., title='random_port', embed=True),
):
    if config:
        config = _decrypt(config)
    else:
        config = 'tcp'
    proto = _decrypt(proto)
    tag = _decrypt(tag)
    port = _decrypt(port)
    random_port = _decrypt(random_port)
    if users:
        users = [User(**_decrypt_dict(user)) for user in users]
    if random_port == "True":
        port = get_open_port()
    else:
        port = int(port)

    try:
        if client.add_inbound(proto, config, tag, "0.0.0.0", port, users):
            return {"result": 1, "details": port}
        else:
            return {"result": 0, "details": '节点 {node} 添加失败'}
    except InboundAlreadyExistsError as error:
        return {"result": 0, "details": '节点 {node} 添加失败，节点标记已存在，请更改节点标记'}
    except Exception as error:
        logger.warning(error)
        return {"result": 0, "details": "节点 {node} 未知错误"}


@app.post("/userInterface/removeInbound")
@check_key
async def removeInbound(
    tag: str = Body(..., title='tag', embed=True),
):
    tag = _decrypt(tag)
    try:
        client.remove_inbound(tag)
        return {"result": 1}
    except InboundNotFoundError as error:
        logger.warning(error)
        return {"result": 0, "details": "不能在站点中找到节点 {node} 的标记，需要检查节点标记是否正确"}
    except Exception as error:
        logger.warning(error)
        return {"result": 0, "details": "节点 {node} 未知错误"}

@app.get("/probeInterface")
@check_key
async def probeInterface():
    try:
        uptime = client.get_sys_stats()
        return {'result': 1, 'details': uptime}
    except Exception as error:
        logger.warning(error)
        return {"result": 0, "details": "service error"}
    

def main():
    uvicorn.run(app, host="0.0.0.0", port=CLIENT_LISTEN_PORT, access_log=True, log_config=config.LOGGING_CONFIG)