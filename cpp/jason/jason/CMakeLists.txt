cmake_minimum_required(VERSION 3.11)

set(project_name jason)
project(${project_name} C CXX)

option(USE_PTHREAD "Use pthread instead of std::thread." ON)

SET(USE_PTHREAD ON) 

include_directories(${CMAKE_CURRENT_SOURCE_DIR})

file(GLOB_RECURSE source *.cpp **/.cpp)

if (CMAKE_SYSTEM_NAME STREQUAL "Linux")
  message(STATUS "Current system is Linux")
  file(GLOB_RECURSE PLATFORM_DIR_SRC platform/linux/*.cpp)
else()
  message(STATUS "Current system is not Linux")
endif()

add_library(${project_name} SHARED ${source} ${PLATFORM_DIR_SRC})

if(USE_PTHREAD)
    # message(FATAL_ERROR "USE_PTHREAD: ${USE_PTHREAD}")
    target_compile_definitions(${project_name} PRIVATE USE_PTHREAD)
endif()

target_compile_features(${project_name} PUBLIC cxx_std_17)