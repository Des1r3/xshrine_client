# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: proxy/freedom/config.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from common.protocol import server_spec_pb2 as common_dot_protocol_dot_server__spec__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1aproxy/freedom/config.proto\x12\x12xray.proxy.freedom\x1a!common/protocol/server_spec.proto\"K\n\x13\x44\x65stinationOverride\x12\x34\n\x06server\x18\x01 \x01(\x0b\x32$.xray.common.protocol.ServerEndpoint\"\xff\x01\n\x06\x43onfig\x12\x42\n\x0f\x64omain_strategy\x18\x01 \x01(\x0e\x32).xray.proxy.freedom.Config.DomainStrategy\x12\x13\n\x07timeout\x18\x02 \x01(\rB\x02\x18\x01\x12\x45\n\x14\x64\x65stination_override\x18\x03 \x01(\x0b\x32\'.xray.proxy.freedom.DestinationOverride\x12\x12\n\nuser_level\x18\x04 \x01(\r\"A\n\x0e\x44omainStrategy\x12\t\n\x05\x41S_IS\x10\x00\x12\n\n\x06USE_IP\x10\x01\x12\x0b\n\x07USE_IP4\x10\x02\x12\x0b\n\x07USE_IP6\x10\x03\x42X\n\x16\x63om.xray.proxy.freedomP\x01Z\'github.com/xtls/xray-core/proxy/freedom\xaa\x02\x12Xray.Proxy.Freedomb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'proxy.freedom.config_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\026com.xray.proxy.freedomP\001Z\'github.com/xtls/xray-core/proxy/freedom\252\002\022Xray.Proxy.Freedom'
  _CONFIG.fields_by_name['timeout']._options = None
  _CONFIG.fields_by_name['timeout']._serialized_options = b'\030\001'
  _DESTINATIONOVERRIDE._serialized_start=85
  _DESTINATIONOVERRIDE._serialized_end=160
  _CONFIG._serialized_start=163
  _CONFIG._serialized_end=418
  _CONFIG_DOMAINSTRATEGY._serialized_start=353
  _CONFIG_DOMAINSTRATEGY._serialized_end=418
# @@protoc_insertion_point(module_scope)
