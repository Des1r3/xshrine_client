import json
from typing import Optional
from settings import *
from client import User
from errors import InboundNotFoundError, UserExistsError, NotSupportProtocolError, InboundAlreadyExistsError
import base64
from urllib.parse import quote

def get_link(
    node: str,
    id: str,
    ip: str,
    domain: Optional[str] = None,
    isBase64: bool = False
    ):
    if NODES[node]["proto"] == "vmess":
        if NODES[node]["config"] == "ws+tls":
            data = json.dumps({
                "v": "2",
                "ps": NODES[node]["name"],
                "add": ip,
                "port": NODES[node]["port"],
                "aid": NODES[node]["default_user_alertID"],
                "type": NODES[node]["header"],
                "net": "ws",
                "path": NODES[node]["ws_path"],
                "host": domain,
                "id": id,
                "tls": "tls",
            })
        elif NODES[node]["config"] == "kcp":
            data = json.dumps({
                "v": "2",
                "ps": NODES[node]["name"],
                "add": ip,
                "port": NODES[node]["port"],
                "aid": NODES[node]["default_user_alertID"],
                "type": NODES[node]["header"],
                "net": "kcp",
                "id": id,
            })
        elif NODES[node]["config"] == "tcp":
            data = json.dumps({
                "v": "2",
                "ps": NODES[node]["name"],
                "add": domain,
                "port": NODES[node]["port"],
                "aid": NODES[node]["default_user_alertID"],
                "type": NODES[node]["header"],
                "net": "tcp",
                "id": id,
            })
        link = "{}://{}".format(NODES[node]["proto"], bytes.decode(base64.b64encode(bytes(data, 'utf-8'))))

    elif NODES[node]["proto"] == "vless":
        if NODES[node]["config"] == "tcp":
            port = NODES[node]["port"]
            link = "vless://{id}@{ip}:{port}?encryption={encryption}&type=tcp".format(
                id=id, ip=ip, port=port, encryption=NODES[node]["encryption"]
            )
            link += "#{}".format(quote(NODES[node]["name"]))
    if isBase64:
        link = bytes.decode(base64.b64encode(link.encode()))
    return link

class Config:
    def __init__(self):
        self.config = self.config_reader()

    def clients(self, index) -> list:
        return self.config["inbounds"][index]["settings"]["clients"]

    ##读取config.json
    def config_reader(self):
        with open(LOCAL_V2RAY_CONFIG_PATH, 'r') as json_file:
            config = json.load(json_file)
        return config

    ##保存config.json
    def config_saver(self):
        json_dump = json.dumps(self.config, indent=2)
        with open(LOCAL_V2RAY_CONFIG_PATH, 'w') as writer:
            writer.writelines(json_dump)

    ##添加用户
    def add_user(self, tag: str, user: User):
        for index, inbound in enumerate(self.config["inbounds"]):
            if 'tag' in inbound.keys() and inbound['tag'] == tag:
                for u in self.clients(index):
                    if u["id"] == user.uuid:
                        raise UserExistsError("uuid 已存在 -> {uuid}")
                    elif u["email"] == user.email:
                        raise UserExistsError("Email 已存在 -> {email}")
                    else:
                        self.clients(index).append(user)
                        self.config_saver()
                        return True
            else:
                raise InboundNotFoundError(f"无法通过 tag->{tag} 找到传入连接")

    ##删除用户
    def delete_user(self, tag: str, email: str = None, all: bool = False):
        for index, inbound in enumerate(self.config["inbounds"]):
            if 'tag' in inbound.keys() and inbound['tag'] == tag:
                if all:
                    self.config["inbounds"][index]["settings"]["clients"] = []
                    return True
                for client in self.clients(index):
                    if email == client['email']:
                        self.clients(index).remove(client)
                        self.config_saver()
                        return True
                raise UserExistsError("Email 已存在 -> {email}")
            else:
                raise InboundNotFoundError(f"无法通过 tag->{tag} 找到传入连接")
            
    ##添加传入连接
    def add_inbound(self, tag: str, ip: str, 
                    port: int, proto: str, 
                    special_config: Optional[dict] = None):
        template = {
            "port": port,
            "listen": ip,
            "protocol": proto,
            "settings": {
                "clients": []
            },
            "tag": tag,
        }
        if "proto" == "vmess":
            pass
        elif "proto" == "vless":
            if special_config:
                template.update(special_config)
            else:
                template.update({"decryption": "none"})
        else:
            raise NotSupportProtocolError(f"不支持的协议：{proto}")
        
        for _, inbound in enumerate(self.config["inbounds"]):
            if 'tag' in inbound.keys() and inbound['tag'] == tag:

                raise InboundAlreadyExistsError(f"tag->{tag} 已经存在")
            
        self.config["inbounds"].append(template)
        self.config_saver()
        return True
    
    ##删除传入连接
    def remove_inbound(self, tag: str):
        for index, inbound in enumerate(self.config["inbounds"]):
            if 'tag' in inbound.keys() and inbound['tag'] == tag:
                self.config["inbounds"].remove(index)
                return True