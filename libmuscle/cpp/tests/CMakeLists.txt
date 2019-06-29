cmake_minimum_required(VERSION 3.5 FATAL_ERROR)

set(THREAD_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)
find_package(GTest ${GoogleTest_MINIMUM_REQUIRED} REQUIRED)
find_package(YMMSL 0.1.0 REQUIRED)
find_package(MUSCLE3 0.1.0 REQUIRED)

add_executable(test_ymmsl test_ymmsl_compute_element.cpp)

target_include_directories(test_ymmsl BEFORE
  PRIVATE
    ${YMMSL_INCLUDE_DIRS}
  )

target_link_libraries(test_ymmsl
  PUBLIC
    Threads::Threads
    ${YMMSL_LIBRARIES}
    ${GTEST_BOTH_LIBRARIES}
  )

add_executable(test_muscle3 test_tooling.cpp test_extra.cpp)

target_include_directories(test_muscle3 BEFORE
  PRIVATE
    ${MUSCLE3_INCLUDE_DIRS}
    ${GTEST_INCLUDE_DIRS}
  )

target_link_libraries(test_muscle3
  PUBLIC
    Threads::Threads
    ${MUSCLE3_LIBRARIES}
    ${GTEST_BOTH_LIBRARIES}
)

