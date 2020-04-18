# Checks whether a particular tool is overridden and prints useful output.

ifeq ($(origin $(tool_var)), environment)
    $(info - $(tool_var) set to $($(tool_var)))
else
    $(info - Set $(tool_var) to override the detected value below.)
endif

