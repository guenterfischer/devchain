
#ifndef CPP_EXAMPLE_EXAMPLE_LIB_HPP
#define CPP_EXAMPLE_EXAMPLE_LIB_HPP

#include <cstdint>

namespace cppexample {

/*!
 * \brief  Example library
 */
class ExampleLib {
 public:
  /*!
   * \brief  Constructor
   *
   * \param  value  Initial value
   */
  explicit ExampleLib(uint32_t = 42);  // NOLINT

  /*!
   * \brief  Destructor
   */
  ~ExampleLib() = default;

  // Copy/move constructors and operators
  ExampleLib(const ExampleLib &) = default;
  ExampleLib(ExampleLib &&) = delete;
  ExampleLib &operator=(const ExampleLib &) = default;
  ExampleLib &operator=(ExampleLib &&) = delete;

  /*!
   * \brief  Example method
   *
   * \param  value  Value to be added
   * \return New value
   */
  uint32_t Add(uint32_t value);

 private:
  /*!
   * \brief  Example variable
   */
  uint32_t value_{0};
};

}  // namespace cppexample

#endif
