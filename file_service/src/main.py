import grpc
from concurrent import futures

import file_repo_service_pb2_grpc
import file_repo_servicer


if __name__ == '__main__':
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    file_repo_service_pb2_grpc.add_FileRepoServiceServicer_to_server(
        file_repo_servicer.FileRepoServicer(), server)
    server.add_insecure_port('[::]:50054')
    server.start()
    server.wait_for_termination()
