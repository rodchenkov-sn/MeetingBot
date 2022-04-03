python -m grpc_tools.protoc -I./protobufs/src --python_out=./tg_api_adapter/src   --grpc_python_out=./tg_api_adapter/src   ./protobufs/src/user_message.proto
python -m grpc_tools.protoc -I./protobufs/src --python_out=./frontend_server/src  --grpc_python_out=./frontend_server/src  ./protobufs/src/user_message.proto
python -m grpc_tools.protoc -I./protobufs/src --python_out=./backend_server/src   --grpc_python_out=./backend_server/src   ./protobufs/src/backend_service.proto
python -m grpc_tools.protoc -I./protobufs/src --python_out=./frontend_server/src  --grpc_python_out=./frontend_server/src  ./protobufs/src/backend_service.proto
python -m grpc_tools.protoc -I./protobufs/src --python_out=./frontend_server/src  --grpc_python_out=./frontend_server/src  ./protobufs/src/calendar_service.proto
python -m grpc_tools.protoc -I./protobufs/src --python_out=./calendar_service/src --grpc_python_out=./calendar_service/src ./protobufs/src/calendar_service.proto
python -m grpc_tools.protoc -I./protobufs/src --python_out=./backend_server/src   --grpc_python_out=./backend_server/src   ./protobufs/src/calendar_service.proto
python -m grpc_tools.protoc -I./protobufs/src --python_out=./frontend_server/src  --grpc_python_out=./frontend_server/src  ./protobufs/src/file_repo_service.proto

python -m grpc_tools.protoc -I./protobufs/src --python_out=./test/integration_tests_adapter/src --grpc_python_out=./test/integration_tests_adapter/src ./protobufs/src/user_message.proto
python -m grpc_tools.protoc -I./protobufs/src --python_out=./test/mock_calendar_service/src     --grpc_python_out=./test/mock_calendar_service/src     ./protobufs/src/calendar_service.proto
python -m grpc_tools.protoc -I./protobufs/src --python_out=./test/mock_file_service/src         --grpc_python_out=./test/mock_file_service/src         ./protobufs/src/file_repo_service.proto
