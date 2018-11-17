.PHONY: test
test: export MYPYPATH=libmuscle/python
test:
	python3 setup.py test

.PHONY: docs-clean
docs-clean:
	rm -rf docs/source/apidocs/*
	rm -rf docs/build/*

.PHONY: docs
docs:
	sphinx-build -a docs/source/ docs/build

.PHONY: grpc
grpc:
	# Server
	python -m grpc_tools.protoc -Imanager_protocol --python_out=muscle_manager/protocol --grpc_python_out=muscle_manager/protocol manager_protocol/muscle_manager_protocol.proto
	# Clients
	python -m grpc_tools.protoc -Imanager_protocol --python_out=libmuscle/python/libmuscle/manager_protocol --grpc_python_out=libmuscle/python/libmuscle/manager_protocol manager_protocol/muscle_manager_protocol.proto
