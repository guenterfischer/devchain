

#include "cpp-example/example_lib.hpp"

namespace cppexample {

ExampleLib::ExampleLib(uint32_t value) : value_{value} {}

uint32_t ExampleLib::Add(uint32_t value) {
  value_ += value;
  return value_;
}

}  // namespace cppexample
