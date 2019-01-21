.PHONY: grpc
grpc:
	# Server
	python -m grpc_tools.protoc -Imuscle_manager_protocol --python_out=muscle_manager_protocol --grpc_python_out=muscle_manager_protocol --mypy_out=muscle_manager_protocol muscle_manager_protocol/muscle_manager_protocol.proto
	@echo
	@echo "*** If you have modified the endpoints, you'll have to manually update muscle_manager_protocol/muscle_manager_protocol_pb2_grpc.pyi ***"
