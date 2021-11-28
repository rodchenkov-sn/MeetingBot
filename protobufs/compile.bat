@echo off
python -m grpc_tools.protoc -I%~dp0src --python_out=%~dp0../tg_api_adapter/src --grpc_python_out=%~dp0../tg_api_adapter/src %~dp0src\user_message.proto
python -m grpc_tools.protoc -I./src --python_out=../frontend_server/src --grpc_python_out=../frontend_server/src  ./src/localized_string.proto
echo Done.
