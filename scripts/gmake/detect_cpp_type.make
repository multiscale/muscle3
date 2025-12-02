# Note that Cray C++ seems to be a rebadged clang and can be treated as such,
# so that we don't detect it separately.

$(info )
$(info Detecting C++ compiler features)

ifeq ($(shell $(CXX) --version | grep -q -i g++ && echo FOUND),FOUND)
    MUSCLE_CXX_GNU := 1
    export MUSCLE_CXX_GNU
    $(info - C++ compiler detected as GNU)
else ifeq ($(shell $(CXX) --version | grep -q -i clang && echo FOUND),FOUND)
    MUSCLE_CXX_CLANG := 1
    export MUSCLE_CXX_CLANG
    $(info - C++ compiler detected as Clang)
else ifeq ($(shell $(CXX) --version | grep -q -i Intel && echo FOUND),FOUND)
    MUSCLE_CXX_INTEL := 1
    export MUSCLE_CXX_INTEL
    $(info - C++ compiler detected as Intel)
else
    MUSCLE_CXX_GNU := 1
    export MUSCLE_CXX_GNU
    $(info - C++ compiler type could not be detected, trying GNU)
    $(info - Please report an issue, and include this:)
    $(info - $(shell $(CXX) --version))
endif


# Check C++ standard library
_libstdcpp := $(shell printf 'int main() {}' | $(CXX) -o muscle3_tmp -v -x c++ - 2>&1 | grep -F -- '-lstdc++' >/dev/null && printf 'FOUND' ; rm muscle3_tmp)
_libcpp := $(shell printf 'int main() {}' | $(CXX) -o muscle3_tmp -v -x c++ - 2>&1 | grep -F -- '-lc++' >/dev/null && printf 'FOUND' ; rm muscle3_tmp)

ifeq ($(_libstdcpp),FOUND)
    MUSCLE_CXX_STDLIB := -lstdc++
else ifeq ($(_libcpp),FOUND)
    MUSCLE_CXX_STDLIB := -lc++
else
    $(info - Could not detect C++ standard library, using OS default)
    ifdef MUSCLE_LINUX
        MUSCLE_CXX_STDLIB := -lstdc++
    else ifdef MUSCLE_MACOS
        MUSCLE_CXX_STDLIB := -lc++
    endif
endif

export MUSCLE_CXX_STDLIB

$(info - Using C++ standard library $(MUSCLE_CXX_STDLIB))

