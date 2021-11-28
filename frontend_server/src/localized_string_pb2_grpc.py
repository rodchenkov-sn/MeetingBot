# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import localized_string_pb2 as localized__string__pb2


class LocalizationHandlerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.getString = channel.unary_unary(
                '/LocalizationHandler/getString',
                request_serializer=localized__string__pb2.StringRequest.SerializeToString,
                response_deserializer=localized__string__pb2.LocalizedString.FromString,
                )


class LocalizationHandlerServicer(object):
    """Missing associated documentation comment in .proto file."""

    def getString(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_LocalizationHandlerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'getString': grpc.unary_unary_rpc_method_handler(
                    servicer.getString,
                    request_deserializer=localized__string__pb2.StringRequest.FromString,
                    response_serializer=localized__string__pb2.LocalizedString.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'LocalizationHandler', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class LocalizationHandler(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def getString(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/LocalizationHandler/getString',
            localized__string__pb2.StringRequest.SerializeToString,
            localized__string__pb2.LocalizedString.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
