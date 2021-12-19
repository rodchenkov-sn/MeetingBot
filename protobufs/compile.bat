@echo off
python -m grpc_tools.protoc -I%~dp0src --python_out=%~dp0../tg_api_adapter/src --grpc_python_out=%~dp0../tg_api_adapter/src %~dp0src\user_message.proto
python -m grpc_tools.protoc -I%~dp0src --python_out=%~dp0../frontend_server/src --grpc_python_out=%~dp0../frontend_server/src  %~dp0src/user_message.proto
python -m grpc_tools.protoc -I%~dp0src --python_out=%~dp0../frontend_server/src --grpc_python_out=%~dp0../frontend_server/src  %~dp0src/frontend_message.proto
echo Done.
