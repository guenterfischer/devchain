# ##############################################################################
# GENERAL SETTINGS
# ##############################################################################
cmake_minimum_required(VERSION 3.20)
project(cpp-example LANGUAGES CXX C)

set(CMAKE_SKIP_RPATH ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# ##############################################################################
# CODE ANALYSIS
# ##############################################################################
if(ANALYSIS MATCHES "clang-tidy")
  set(CMAKE_CXX_CLANG_TIDY "clang-tidy")
endif()

# ##############################################################################
# SANITIZERS
# ##############################################################################
if(SANITIZER MATCHES "asan")
  add_compile_options(-fsanitize=address)
  add_link_options(-fsanitize=address)
endif()

if(SANITIZER MATCHES "msan")
  add_compile_options(-fsanitize=memory)
  add_link_options(-fsanitize=memory)
endif()

if(SANITIZER MATCHES "tsan")
  add_compile_options(-fsanitize=thread)
  add_link_options(-fsanitize=thread)
endif()

# ##############################################################################
# SOURCE DIRECTORY
# ##############################################################################
add_subdirectory(source)
