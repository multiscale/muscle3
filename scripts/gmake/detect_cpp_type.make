# Note that Cray C++ seems to be a rebadged clang and can be treated as such,
# so that we don't detect it separately.

$(info )

ifeq ($(shell $(CXX) --version | grep -q -i g++ && echo FOUND),FOUND)
    MUSCLE_CXX_GNU := 1
    export MUSCLE_CXX_GNU
    $(info C++ compiler detected as GNU)
else ifeq ($(shell $(CXX) --version | grep -q -i clang && echo FOUND),FOUND)
    MUSCLE_CXX_CLANG := 1
    export MUSCLE_CXX_CLANG
    $(info C++ compiler detected as Clang)
else ifeq ($(shell $(CXX) --version | grep -q -i Intel && echo FOUND),FOUND)
    MUSCLE_CXX_INTEL := 1
    export MUSCLE_CXX_INTEL
    $(info C++ compiler detected as Intel)
else
    MUSCLE_CXX_GNU := 1
    export MUSCLE_CXX_GNU
    $(info C++ compiler type could not be detected, trying GNU)
    $(info Please report an issue, and include this:)
    $(info $(shell $(CXX) --version))
endif

