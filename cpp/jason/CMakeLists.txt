cmake_minimum_required(VERSION 3.11)

set(project_name main)
project(${project_name} C CXX)

include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/jason
)

add_executable(${project_name} main.cpp)
target_compile_features(${project_name} PUBLIC cxx_std_17)

target_compile_definitions(${project_name} PRIVATE USE_PTHREAD)
set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS} -g -O0")
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS} -O3")

target_link_libraries(${project_name} jason)
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/jason ${CMAKE_CURRENT_BINARY_DIR}/jason)