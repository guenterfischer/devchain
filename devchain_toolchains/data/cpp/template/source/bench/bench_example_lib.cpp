
#include <cstring>
#include <memory>

#include <benchmark/benchmark.h>

#include "cpp-example/example_lib.hpp"

namespace {

void BM_Add(benchmark::State &state) {
  auto lib = std::make_shared<cppexample::ExampleLib>();

  // NOLINTNEXTLINE
  for (auto _ : state) {
    lib->Add(42);  // NOLINT
  }
}

}  // namespace

BENCHMARK(BM_Add);
BENCHMARK_MAIN();
