# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: transport/internet/tcp/config.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from common.serial import typed_message_pb2 as common_dot_serial_dot_typed__message__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n#transport/internet/tcp/config.proto\x12\x1bxray.transport.internet.tcp\x1a!common/serial/typed_message.proto\"h\n\x06\x43onfig\x12\x39\n\x0fheader_settings\x18\x02 \x01(\x0b\x32 .xray.common.serial.TypedMessage\x12\x1d\n\x15\x61\x63\x63\x65pt_proxy_protocol\x18\x03 \x01(\x08J\x04\x08\x01\x10\x02\x42s\n\x1f\x63om.xray.transport.internet.tcpP\x01Z0github.com/xtls/xray-core/transport/internet/tcp\xaa\x02\x1bXray.Transport.Internet.Tcpb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'transport.internet.tcp.config_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\037com.xray.transport.internet.tcpP\001Z0github.com/xtls/xray-core/transport/internet/tcp\252\002\033Xray.Transport.Internet.Tcp'
  _CONFIG._serialized_start=103
  _CONFIG._serialized_end=207
# @@protoc_insertion_point(module_scope)
