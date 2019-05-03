.PHONY: all
all: cpp

.PHONY: configure
configure:
	cd libmuscle/cpp && $(MAKE) configure

.PHONY: test
test: all
	python3 setup.py test

.PHONY: install
install: all
	cd libmuscle/cpp && $(MAKE) install

.PHONY: clean
clean:
	cd libmuscle/cpp && $(MAKE) clean

.PHONY: distclean
distclean:
	cd libmuscle/cpp && $(MAKE) distclean

.PHONY: cpp
cpp:
	cd libmuscle/cpp && $(MAKE)

# This rebuilds the gRPC generated code; for development only.
.PHONY: grpc
grpc:
	# Python
	python -m grpc_tools.protoc -Imuscle_manager_protocol --python_out=muscle_manager_protocol --grpc_python_out=muscle_manager_protocol --mypy_out=muscle_manager_protocol muscle_manager_protocol/muscle_manager_protocol.proto
	@echo
	@echo "*** If you have modified the endpoints, you'll have to manually update muscle_manager_protocol/muscle_manager_protocol_pb2_grpc.pyi ***"
	# C++
	libmuscle/cpp/build/tools/protobuf/bin/protoc --cpp_out=libmuscle/cpp/src muscle_manager_protocol/muscle_manager_protocol.proto
