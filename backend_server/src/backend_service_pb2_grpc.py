# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import backend_service_pb2 as backend__service__pb2


class BackendServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.CreateTeam = channel.unary_unary(
                '/BackendService/CreateTeam',
                request_serializer=backend__service__pb2.CreateTeamMsg.SerializeToString,
                response_deserializer=backend__service__pb2.EntityId.FromString,
                )
        self.GetOwnedTeams = channel.unary_stream(
                '/BackendService/GetOwnedTeams',
                request_serializer=backend__service__pb2.EntityId.SerializeToString,
                response_deserializer=backend__service__pb2.NamedInfo.FromString,
                )
        self.GetTeamInfo = channel.unary_unary(
                '/BackendService/GetTeamInfo',
                request_serializer=backend__service__pb2.EntityId.SerializeToString,
                response_deserializer=backend__service__pb2.NamedInfo.FromString,
                )
        self.AddTeamMember = channel.unary_unary(
                '/BackendService/AddTeamMember',
                request_serializer=backend__service__pb2.Participating.SerializeToString,
                response_deserializer=backend__service__pb2.SimpleResponse.FromString,
                )
        self.CreateMeeting = channel.unary_unary(
                '/BackendService/CreateMeeting',
                request_serializer=backend__service__pb2.MeetingInfo.SerializeToString,
                response_deserializer=backend__service__pb2.EntityId.FromString,
                )
        self.UpdateMeetingInfo = channel.unary_unary(
                '/BackendService/UpdateMeetingInfo',
                request_serializer=backend__service__pb2.MeetingInfo.SerializeToString,
                response_deserializer=backend__service__pb2.SimpleResponse.FromString,
                )
        self.GetOwnedMeetings = channel.unary_stream(
                '/BackendService/GetOwnedMeetings',
                request_serializer=backend__service__pb2.EntityId.SerializeToString,
                response_deserializer=backend__service__pb2.NamedInfo.FromString,
                )
        self.AddParticipant = channel.unary_unary(
                '/BackendService/AddParticipant',
                request_serializer=backend__service__pb2.Participating.SerializeToString,
                response_deserializer=backend__service__pb2.SimpleResponse.FromString,
                )
        self.GetMeetingInfo = channel.unary_unary(
                '/BackendService/GetMeetingInfo',
                request_serializer=backend__service__pb2.EntityId.SerializeToString,
                response_deserializer=backend__service__pb2.MeetingInfo.FromString,
                )


class BackendServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def CreateTeam(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetOwnedTeams(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetTeamInfo(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AddTeamMember(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CreateMeeting(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateMeetingInfo(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetOwnedMeetings(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AddParticipant(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetMeetingInfo(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_BackendServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'CreateTeam': grpc.unary_unary_rpc_method_handler(
                    servicer.CreateTeam,
                    request_deserializer=backend__service__pb2.CreateTeamMsg.FromString,
                    response_serializer=backend__service__pb2.EntityId.SerializeToString,
            ),
            'GetOwnedTeams': grpc.unary_stream_rpc_method_handler(
                    servicer.GetOwnedTeams,
                    request_deserializer=backend__service__pb2.EntityId.FromString,
                    response_serializer=backend__service__pb2.NamedInfo.SerializeToString,
            ),
            'GetTeamInfo': grpc.unary_unary_rpc_method_handler(
                    servicer.GetTeamInfo,
                    request_deserializer=backend__service__pb2.EntityId.FromString,
                    response_serializer=backend__service__pb2.NamedInfo.SerializeToString,
            ),
            'AddTeamMember': grpc.unary_unary_rpc_method_handler(
                    servicer.AddTeamMember,
                    request_deserializer=backend__service__pb2.Participating.FromString,
                    response_serializer=backend__service__pb2.SimpleResponse.SerializeToString,
            ),
            'CreateMeeting': grpc.unary_unary_rpc_method_handler(
                    servicer.CreateMeeting,
                    request_deserializer=backend__service__pb2.MeetingInfo.FromString,
                    response_serializer=backend__service__pb2.EntityId.SerializeToString,
            ),
            'UpdateMeetingInfo': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateMeetingInfo,
                    request_deserializer=backend__service__pb2.MeetingInfo.FromString,
                    response_serializer=backend__service__pb2.SimpleResponse.SerializeToString,
            ),
            'GetOwnedMeetings': grpc.unary_stream_rpc_method_handler(
                    servicer.GetOwnedMeetings,
                    request_deserializer=backend__service__pb2.EntityId.FromString,
                    response_serializer=backend__service__pb2.NamedInfo.SerializeToString,
            ),
            'AddParticipant': grpc.unary_unary_rpc_method_handler(
                    servicer.AddParticipant,
                    request_deserializer=backend__service__pb2.Participating.FromString,
                    response_serializer=backend__service__pb2.SimpleResponse.SerializeToString,
            ),
            'GetMeetingInfo': grpc.unary_unary_rpc_method_handler(
                    servicer.GetMeetingInfo,
                    request_deserializer=backend__service__pb2.EntityId.FromString,
                    response_serializer=backend__service__pb2.MeetingInfo.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'BackendService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class BackendService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def CreateTeam(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/BackendService/CreateTeam',
            backend__service__pb2.CreateTeamMsg.SerializeToString,
            backend__service__pb2.EntityId.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetOwnedTeams(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/BackendService/GetOwnedTeams',
            backend__service__pb2.EntityId.SerializeToString,
            backend__service__pb2.NamedInfo.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetTeamInfo(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/BackendService/GetTeamInfo',
            backend__service__pb2.EntityId.SerializeToString,
            backend__service__pb2.NamedInfo.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def AddTeamMember(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/BackendService/AddTeamMember',
            backend__service__pb2.Participating.SerializeToString,
            backend__service__pb2.SimpleResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def CreateMeeting(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/BackendService/CreateMeeting',
            backend__service__pb2.MeetingInfo.SerializeToString,
            backend__service__pb2.EntityId.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def UpdateMeetingInfo(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/BackendService/UpdateMeetingInfo',
            backend__service__pb2.MeetingInfo.SerializeToString,
            backend__service__pb2.SimpleResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetOwnedMeetings(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/BackendService/GetOwnedMeetings',
            backend__service__pb2.EntityId.SerializeToString,
            backend__service__pb2.NamedInfo.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def AddParticipant(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/BackendService/AddParticipant',
            backend__service__pb2.Participating.SerializeToString,
            backend__service__pb2.SimpleResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetMeetingInfo(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/BackendService/GetMeetingInfo',
            backend__service__pb2.EntityId.SerializeToString,
            backend__service__pb2.MeetingInfo.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)