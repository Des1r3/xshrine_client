# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: proxy/wireguard/config.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1cproxy/wireguard/config.proto\x12\x14xray.proxy.wireguard\"s\n\nPeerConfig\x12\x12\n\npublic_key\x18\x01 \x01(\t\x12\x16\n\x0epre_shared_key\x18\x02 \x01(\t\x12\x10\n\x08\x65ndpoint\x18\x03 \x01(\t\x12\x12\n\nkeep_alive\x18\x04 \x01(\x05\x12\x13\n\x0b\x61llowed_ips\x18\x05 \x03(\t\"\x99\x01\n\x0c\x44\x65viceConfig\x12\x12\n\nsecret_key\x18\x01 \x01(\t\x12\x10\n\x08\x65ndpoint\x18\x02 \x03(\t\x12/\n\x05peers\x18\x03 \x03(\x0b\x32 .xray.proxy.wireguard.PeerConfig\x12\x0b\n\x03mtu\x18\x04 \x01(\x05\x12\x13\n\x0bnum_workers\x18\x05 \x01(\x05\x12\x10\n\x08reserved\x18\x06 \x01(\x0c\x42^\n\x18\x63om.xray.proxy.wireguardP\x01Z)github.com/xtls/xray-core/proxy/wireguard\xaa\x02\x14Xray.Proxy.WireGuardb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'proxy.wireguard.config_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\030com.xray.proxy.wireguardP\001Z)github.com/xtls/xray-core/proxy/wireguard\252\002\024Xray.Proxy.WireGuard'
  _PEERCONFIG._serialized_start=54
  _PEERCONFIG._serialized_end=169
  _DEVICECONFIG._serialized_start=172
  _DEVICECONFIG._serialized_end=325
# @@protoc_insertion_point(module_scope)
