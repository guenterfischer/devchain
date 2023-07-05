
#include <cstring>
#include <memory>

#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include "cpp-example/example_lib.hpp"

class TestExampleLib : public ::testing::Test {
 protected:
  void SetUp() override {}
  void TearDown() override {}
};

TEST_F(TestExampleLib, Add) {
  // clang-tidy will complain regarding magic-number
  auto lib = std::make_shared<cppexample::ExampleLib>(12);

  EXPECT_EQ(lib->Add(4), 16);
  EXPECT_EQ(lib->Add(7), 23);
}
