import asyncio
import logging
from concurrent import futures

import grpc

import bd
import file_repo_service_pb2_grpc
import filehost
import file_repo_servicer


async def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    file_repo_service_pb2_grpc.add_FileRepoServiceServicer_to_server(
        file_repo_servicer.FileRepoServicer(), server)
    server.add_insecure_port('[::]:50054')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.get_event_loop().run_until_complete(serve())
    filehost.api.run(debug=True, port=10800)


