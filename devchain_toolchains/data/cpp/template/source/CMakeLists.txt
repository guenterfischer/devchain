# ##############################################################################
# GENERAL SETTINGS
# ##############################################################################
set(TARGET "cpp-example")
project(${TARGET})

# ##############################################################################
# DEPENDENCIES
# ##############################################################################

# ##############################################################################
# TARGETS
# ##############################################################################
add_library(${TARGET} STATIC "")
add_library(cpp::example ALIAS ${TARGET})

set_target_properties(${TARGET} PROPERTIES POSITION_INDEPENDENT_CODE ON)
set_target_properties(${TARGET} PROPERTIES LINKER_LANGUAGE CXX)
target_compile_features(${TARGET} PRIVATE cxx_std_20)

target_compile_options(${TARGET} PUBLIC $<IF:$<NOT:$<CXX_COMPILER_ID:MSVC>>,
                                        -fPIC,>)

target_sources(
  ${TARGET}
  PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src/example_lib.cpp
  PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include/cpp-example/example_lib.hpp)

# ##############################################################################
# LINKED LIBRARIES
# ##############################################################################

# ##############################################################################
# INCLUDE DIRECTORIES
# ##############################################################################
target_include_directories(
  ${TARGET}
  PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
         $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src>
         $<INSTALL_INTERFACE:include>
  INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/include)

# ##############################################################################
# TEST
# ##############################################################################
add_subdirectory(test)

# ##############################################################################
# BENCHMARK
# ##############################################################################
add_subdirectory(bench)
