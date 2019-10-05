cpp_test_files := libmuscle/cpp/build/ymmsl/tests/test_* libmuscle/cpp/build/libmuscle/tests/test_*

.PHONY: all
all: cpp

.PHONY: test
test: test_python test_cpp

.PHONY: test_python
test_python: cpp_tests
	python3 setup.py test

.PHONY: test_cpp
test_cpp:
	cd libmuscle/cpp && $(MAKE) test

.PHONY: install
install: all
	cd libmuscle/cpp && $(MAKE) install

.PHONY: docs
docs:
	python3 setup.py build_sphinx

.PHONY: clean
clean:
	cd libmuscle/cpp && $(MAKE) clean

.PHONY: distclean
distclean:
	cd libmuscle/cpp && $(MAKE) distclean

.PHONY: cpp
cpp:
	cd libmuscle/cpp && $(MAKE)

.PHONY: cpp_tests
cpp_tests: cpp
	cd libmuscle/cpp && $(MAKE) tests

# This rebuilds the gRPC generated code; for development only.
.PHONY: grpc
grpc:
	# Python
	python -m grpc_tools.protoc -Imuscle_manager_protocol --python_out=muscle_manager_protocol --grpc_python_out=muscle_manager_protocol --mypy_out=muscle_manager_protocol muscle_manager_protocol/muscle_manager_protocol.proto

	# C++
	pb_prefix=$$(PKG_CONFIG_PATH=libmuscle/cpp/build/protobuf/protobuf/lib/pkgconfig pkg-config --variable=prefix protobuf) && \
			grpc_prefix=$$(PKG_CONFIG_PATH=libmuscle/cpp/build/grpc/grpc/lib/pkgconfig pkg-config --variable=prefix grpc) && \
			PATH=$${pb_prefix}/bin:$${PATH} && export LD_LIBRARY_PATH=$${pb_prefix}/lib && \
			protoc --grpc_out=libmuscle/cpp/src --plugin=protoc-gen-grpc=$${grpc_prefix}/bin/grpc_cpp_plugin muscle_manager_protocol/muscle_manager_protocol.proto
	pb_prefix=$$(PKG_CONFIG_PATH=libmuscle/cpp/build/protobuf/protobuf/lib/pkgconfig pkg-config --variable=prefix protobuf) && \
			PATH=$${pb_prefix}/bin:$${PATH} && export LD_LIBRARY_PATH=$${pb_prefix}/lib && \
			protoc --cpp_out=libmuscle/cpp/src muscle_manager_protocol/muscle_manager_protocol.proto
