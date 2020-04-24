# Make module that tries to detect a particular tool.

# Set tool_var to the variable containing the tool command, and
# tool_command to the command to try, then include this file.

ifndef $(tool_var)
    _version := $(shell $(tool_command) --version 2>/dev/null || echo NOTFOUND)
    ifneq ($(_version), NOTFOUND)
        export $(tool_var) := $(tool_command)
        $(info - Found version $(shell $(tool_command) --version | head -n 1))
    endif
endif

