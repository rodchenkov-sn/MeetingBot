import asyncio
import logging
import filehost



async def serve():
    # server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # file_repo_service_pb2_grpc.add_FileRepoServiceServicer_to_server(
    #     file_repo_servicer.FileRepoServicer(), server)
    # server.add_insecure_port('[::]:50051')
    # server.start()
    filehost.api.run(debug=True, port=10800)
    filehost.api.config['SERVER_NAME'] = 'fileservice.com'
    # server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.get_event_loop().run_until_complete(serve())


