# Make module that verifies that we have all needed tools
$(info Checking for tools...)

# Check C++ compiler
ifndef CXX
    _gcc_version := $(shell g++ --version || echo NOTFOUND)
    ifneq ($(_gcc_version), NOTFOUND)
        export CXX = g++
        $(info Found g++ version $(shell g++ --version | head -n 1))
    endif
endif

ifndef CXX
    _clang_version := $(shell clang++ --version || echo NOTFOUND)
    ifneq ($(_clang_version), NOTFOUND)
        export CXX = clang++
        $(info Found clang version $(shell clang++ --version | head -n 1))
    endif
endif

ifndef CXX
    $(error No C++ compiler found! Please install either gcc or clang.)
else
    $(info - Will compile C++ files using $(CXX); set CXX to override.)
endif


# Check download tool (for downloading dependencies)
ifndef DOWNLOAD
    _wget_version := $(shell wget --version || echo NOTFOUND)
    ifneq ($(_wget_version), NOTFOUND)
        export DOWNLOAD = wget
        $(info Found wget version $(shell wget --version | head -n 1).)
    endif
endif

ifndef DOWNLOAD
    _curl_version := $(shell curl --version || echo NOTFOUND)
    ifneq ($(_curl_version), NOTFOUND)
        export DOWNLOAD = curl
        $(info Found curl version $(shell curl --version | head -n 1).)
    endif
endif

ifndef DOWNLOAD
    $(warning Could not find either wget or curl, so I won't be able to download dependencies.)
    $(warning To fix this, set DOWNLOAD to a command that can download http links.)
else
    $(info - Will download files using $(DOWNLOAD); set DOWNLOAD to override.)
endif


# Check tar tool (for unpacking dependencies)
ifndef TAR
    _tar_version := $(shell tar --version || echo NOTFOUND)
    ifneq ($(_tar_version), NOTFOUND)
        export TAR = tar
        $(info Found tar version $(shell tar --version | head -n 1).)
    endif
endif

ifndef TAR
    $(warning Could not find tar, so I won't be able to download dependencies.)
    $(warning To fix this, set TAR to a command that can extract tar archives.)
else
    $(info - Will extract archives using $(TAR); set TAR to override.)
endif

# Check number of cores
ifndef NCORES
	NCORES != nproc 2>/dev/null || echo 2
	export NCORES
endif
$(info Using $(NCORES) cores to build; set NCORES to override.)


