# Checks whether a particular tool is overridden and prints useful output.

ifeq ($(origin $(tool_var)), environment)
    ifeq ($($(tool_var)),)
        $(info - $(tool_var) set empty by the user.)
    else
        $(info - $(tool_var) set to $($(tool_var)) by user)
        $(info - Using version $(shell $($(tool_var)) --version | head -n 1))
    endif
else
    $(info - Set $(tool_var) to override the detected value below.)
endif

