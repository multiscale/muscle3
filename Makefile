.PHONY: grpc
grpc:
	# Server
	python -m grpc_tools.protoc -Imanager_protocol --python_out=muscle_manager/protocol --grpc_python_out=muscle_manager/protocol --mypy_out=muscle_manager/protocol manager_protocol/muscle_manager_protocol.proto
	# Clients
	python -m grpc_tools.protoc -Imanager_protocol --python_out=libmuscle/python/libmuscle/manager_protocol --grpc_python_out=libmuscle/python/libmuscle/manager_protocol --mypy_out=libmuscle/python/libmuscle/manager_protocol manager_protocol/muscle_manager_protocol.proto
