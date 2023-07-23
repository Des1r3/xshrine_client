import os
import sys
from traceback import print_exc
sys.path.append(os.path.dirname(__file__))
import grpc
from typing import Optional, List
from grpc._channel import _Rendezvous, _InactiveRpcError
from errors import *
from attr import attrs, attrib
from core import config_pb2 as core_config_pb2
from common.net import port_pb2, address_pb2
from proxy.vmess import account_pb2 as vmess_account_pb2
from proxy.vless import account_pb2 as vless_account_pb2
from proxy.shadowsocks import config_pb2 as ss_config_pb2
from proxy.trojan import config_pb2 as trojan_config_pb2
from proxy.vmess.inbound import config_pb2 as vmess_inbound_config_pb2
from proxy.vless.inbound import config_pb2 as vless_inbound_config_pb2
from proxy.trojan import config_pb2 as trojan_config_pb2
from transport.internet import config_pb2 as internet_config_bp2
from transport.internet.kcp import config_pb2 as kcp_config_pb2
from transport.internet.websocket import config_pb2 as ws_config_pb2
from transport.internet.headers.wechat import config_pb2 as video_config_pb2
from transport.internet.tls import config_pb2 as tls_config_pb2
from common.protocol import user_pb2
from common.serial import typed_message_pb2
from app.proxyman import config_pb2 as proxyman_config_pb2
from app.proxyman.command import command_pb2
from app.proxyman.command import command_pb2_grpc
from app.stats.command import command_pb2 as stats_command_pb2
from app.stats.command import command_pb2_grpc as stats_command_pb2_grpc

def to_typed_message(message):
    return typed_message_pb2.TypedMessage(
        type=message.DESCRIPTOR.full_name,
        value=message.SerializeToString()
    )

def ip2bytes(ip: str):
    return bytes([int(i) for i in ip.split('.')])

@attrs
class User(object):
    email = attrib(type=str, default=None)
    uuid = attrib(type=str, default=None) # be use for Vmess/Vless or act as trojan's password
    level = attrib(type=int, default=0, converter=int)
    alter_id = attrib(type=int, default=0, converter=int) # be use for Vmess
    cipherType = attrib(type=str, default=None) # be use for ShadowSocks
    password = attrib(type=str, default="none") # be use for ShadowSocks or act as Vless's Encryption
    flow = attrib(type=str, default="none") # be use for Vless

class Client(object):
    def __init__(self, address, port):
        self._channel = grpc.insecure_channel(f"{address}:{port}")

    def get_sys_stats(self):
        stub = stats_command_pb2_grpc.StatsServiceStub(self._channel)
        try:
            return stub.GetSysStats(stats_command_pb2.SysStatsRequest()).Uptime
        except (_Rendezvous, _InactiveRpcError) as e:
            details = e.details()
            raise XRayError(details)

    def get_user_traffic_downlink(self, email, reset=False):
        """
        :param email: 邮箱
        :param reset: 是否重置计数器
        """
        stub = stats_command_pb2_grpc.StatsServiceStub(self._channel)
        try:
            return stub.GetStats(stats_command_pb2.GetStatsRequest(
                name=f"user>>>{email}>>>traffic>>>downlink",
                reset=reset
            )).stat.value
        except (_Rendezvous, _InactiveRpcError) as e:
            details = e.details()
            if details.endswith(f"user>>>{email}>>>traffic>>>downlink not found."):
                raise EmailNotFoundError(details, email)
            else:
                raise XRayError(details)

    def get_user_traffic_uplink(self, email, reset=False):
        """
        :param email: 邮箱
        :param reset: 是否重置计数器
        """
        stub = stats_command_pb2_grpc.StatsServiceStub(self._channel)
        try:
            return stub.GetStats(stats_command_pb2.GetStatsRequest(
                name=f"user>>>{email}>>>traffic>>>uplink",
                reset=reset
            )).stat.value
        except (_Rendezvous, _InactiveRpcError) as e:
            details = e.details()
            if details.endswith(f"user>>>{email}>>>traffic>>>uplink not found."):
                raise EmailNotFoundError(details, email)
            else:
                raise XRayError(details)

    def return_total_flow(self, email: str) -> int:
        uplink = self.get_user_traffic_uplink(email, reset=True)
        downlink = self.get_user_traffic_downlink(email, reset=True)
        return uplink + downlink

    def add_user(
            self, 
            proto: str, 
            tag: str,
            user: User,
        ) -> Optional[bool]:
        """
        Add a user in inbound.
        
        :param proto: (Vmess|Vless|Trojan), not support ShadowSocks temporarily
        :param tag: inbound's tag

        raise:       
            if email already exist, raise EmailExistsError
            if tag not exist, raise InboundNotFoundError
            if proto not support, raise NotSupportProtocolError

        return:
            bool or None. if action is completing correctly, will return True.
        """
        stub = command_pb2_grpc.HandlerServiceStub(self._channel)
        try:
            if proto.lower() == "vmess":
                stub.AlterInbound(command_pb2.AlterInboundRequest(
                    tag=tag,
                    operation=to_typed_message(command_pb2.AddUserOperation(
                        user=user_pb2.User(
                            email=user.email,
                            level=user.level,
                            account=to_typed_message(vmess_account_pb2.Account(
                                id=user.uuid,
                                alter_id=user.alter_id,
                            ))
                        )
                    ))
                ))
                return True
            elif proto.lower() == "vless":
                stub.AlterInbound(command_pb2.AlterInboundRequest(
                    tag=tag,
                    operation=to_typed_message(command_pb2.AddUserOperation(
                        user=user_pb2.User(
                            email=user.email,
                            level=user.level,
                            account=to_typed_message(vless_account_pb2.Account(
                                id=user.uuid,
                                flow=user.flow,
                                encryption=user.password
                            ))
                        )
                    ))
                ))
                return True
            elif proto.lower() == "trojan":
                stub.AlterInbound(command_pb2.AlterInboundRequest(
                    tag=tag,
                    operation=to_typed_message(command_pb2.AddUserOperation(
                        user=user_pb2.User(
                            email=user.email,
                            level=user.level,
                            account=to_typed_message(trojan_config_pb2.Account(
                                password=user.uuid,
                            ))
                        )
                    ))
                ))
                return True
            else:
                raise NotSupportProtocolError(f"Not support protocol: {proto}")
            
        except _InactiveRpcError as e:
            details = e.details()
            if details.endswith(f"User {user.email} already exists."):
                raise EmailExistsError(details, user.email)
            elif details.endswith(f"handler not found: {tag}"):
                raise InboundNotFoundError(details, tag)
            elif details.endswith(f"failed to get handler: {tag}"):
                raise InboundNotFoundError(details, tag)
            else:
                raise XRayError(details)

    def remove_user(self, tag: str, email: str) -> Optional[bool]:
        """
        Remove a user in inbound.

        raise:       
            if email already exist, raise EmailExistsError
            if tag not exist, raise InboundNotFoundError
            if proto not support, riase NotSupportProtocolError

        return:
            bool or None, if action is completing correctly, will return True.
        """
        stub = command_pb2_grpc.HandlerServiceStub(self._channel)
        try:
            stub.AlterInbound(command_pb2.AlterInboundRequest(
                tag=tag,
                operation=to_typed_message(command_pb2.RemoveUserOperation(
                    email=email
                ))
            ))
            return email
        except _InactiveRpcError as e:
            details = e.details()
            if details.endswith(f"User {email} not found."):
                raise EmailNotFoundError(details, email)
            elif details.endswith(f"handler not found: {tag}"):
                raise InboundNotFoundError(details, tag)
            else:
                raise XRayError(details)
    
    def add_inbound(
            self,
            proto: str,
            config: str,
            tag: str,
            listen_address: str,
            listen_port: int,   
            users: List[User],
        ):
        """
        Add a inbound.

        :param tansport: Only support tcp temporarily

        raise:       
            if email already exist, raise EmailExistsError
            if tag not exist, raise InboundNotFoundError
            if proto not support, riase NotSupportProtocolError

        return:
            bool or None, if action is completing correctly, will return True.
        """
        stub = command_pb2_grpc.HandlerServiceStub(self._channel)
        try:
            if proto.lower() == "vmess":
                proxy_settings = to_typed_message(vmess_inbound_config_pb2.Config(
                            user = [
                                    user_pb2.User(
                                        email=user.email,
                                        level=user.level,
                                        account=to_typed_message(vmess_account_pb2.Account(
                                            id=user.uuid,
                                            alter_id=user.alter_id
                                        ))
                                    ) for user in users
                                ]
                            ))
            elif proto.lower() == "vless":
                proxy_settings = to_typed_message(vless_inbound_config_pb2.Config(
                            clients = [
                                    user_pb2.User(
                                        email=user.email,
                                        level=user.level,
                                        account=to_typed_message(vless_account_pb2.Account(
                                            id=user.uuid,
                                            flow=user.flow,
                                            encryption=user.password
                                        ))
                                    ) for user in users
                                ]
                            ))
            elif proto.lower() == "trojan":
                proxy_settings = to_typed_message(trojan_config_pb2.Config(
                            user = [
                                    user_pb2.User(
                                        email=user.email,
                                        level=user.level,
                                        account=to_typed_message(trojan_config_pb2.Account(
                                            flow=user.flow,
                                            password=user.password
                                        ))
                                    ) for user in users
                                ]
                            ))
            else:
                raise NotSupportProtocolError(f"Not support protocol: {proto}")
            
            if config == 'tcp':
                stream_settings = None
            elif config == 'mkcp':
                stream_settings = internet_config_bp2.StreamConfig(
                    protocol_name='mkcp',
                    transport_settings=[
                        internet_config_bp2.TransportConfig(
                            protocol_name='mkcp',
                            settings=to_typed_message(kcp_config_pb2.Config(
                                mtu=kcp_config_pb2.MTU(
                                    value=1460
                                ),
                                tti=kcp_config_pb2.TTI(
                                    value=10
                                ),
                                uplink_capacity=kcp_config_pb2.UplinkCapacity(
                                    value=5
                                ),
                                downlink_capacity=kcp_config_pb2.DownlinkCapacity(
                                    value=20
                                ),
                                congestion=False,
                                write_buffer=kcp_config_pb2.WriteBuffer(
                                    size=2
                                ),
                                read_buffer=kcp_config_pb2.ReadBuffer(
                                    size=2
                                ),  
                                seed=kcp_config_pb2.EncryptionSeed(
                                    seed="xshrine!project"
                                ),
                                header_config=to_typed_message(video_config_pb2.VideoConfig()),
                            ))
                        )
                    ]
                )
            stub.AddInbound(command_pb2.AddInboundRequest(
                inbound=core_config_pb2.InboundHandlerConfig(
                    tag=tag,
                    receiver_settings=to_typed_message(proxyman_config_pb2.ReceiverConfig(
                            port_list=port_pb2.PortList(
                                range=[port_pb2.PortRange(
                                    From=listen_port,
                                    To=listen_port,
                                    )]
                                ),
                            listen=address_pb2.IPOrDomain(
                                ip=ip2bytes(listen_address),
                            ),   
                            stream_settings=stream_settings,
                            allocation_strategy=None,
                            receive_original_destination=None,
                            domain_override=None,
                            sniffing_settings=None
                        )
                    ),
                    proxy_settings=proxy_settings
                )
            ))
            return True
        except (_Rendezvous, _InactiveRpcError) as e:
            details = e.details()
            if details.endswith("address already in use"):
                raise AddressAlreadyInUseError(details, listen_port)
            elif details.endswith(f"existing tag found: {tag}"):
                raise InboundAlreadyExistsError(details, tag)
            else:
                raise XRayError(details)

    def remove_inbound(self, tag):
        stub = command_pb2_grpc.HandlerServiceStub(self._channel)
        try:
            stub.RemoveInbound(command_pb2.RemoveInboundRequest(
                tag=tag
            ))
        except (_Rendezvous, _InactiveRpcError) as e:
            details = e.details()
            if 'not enough information for making a decision' in details:
                raise InboundNotFoundError(details, tag)
            else:
                raise XRayError(details)
                
    # def add_user(self, node, uuid, email):
    #     try:
    #         self.add_user(node, uuid, email, 0, 32)
    #         return True
    #     except Exception as e:
    #         return False

    # def delete_user(self, node, email):
    #     try:
    #         self.remove_user(email)
    #         return True
    #     except Exception as e:
    #         return False
    


