add_executable(tooling_test test_tooling.cpp)

target_link_libraries(tooling_test
  PUBLIC
    muscle3-static
    gtest_main
)

add_test(NAME tooling_test COMMAND $<TARGET_FILE:tooling_test>)

