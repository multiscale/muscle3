#pragma once

#include <libmuscle/util.hpp>

#include <gtest/gtest.h>

#include <functional>
#include <sstream>
#include <tuple>
#include <type_traits>
#include <utility>
#include <vector>


namespace mock_support {

template <typename T>
struct remove_ptr_ref_const {
    using type = typename std::remove_cv<
        typename std::remove_pointer<
            typename std::remove_reference<T>::type>::type>::type;
};


template <typename... Args>
struct StorageType {
    using type = std::tuple<typename Args::StorageType...>;
};


// convert an argument to the given type by (de)referencing as needed
template <typename T>
T convert(T const & t) {
    return t;
}

template <typename T>
typename std::enable_if<!std::is_pointer<T>::value, T>::type
convert(typename std::remove_reference<T>::type * t) {
    return *t;
}

template <typename T>
typename std::enable_if<std::is_pointer<T>::value, T const>::type
convert(typename std::remove_pointer<T>::type const & t) {
    return &t;
}

template <typename T>
typename std::enable_if<std::is_pointer<T>::value, T>::type
convert(typename std::remove_pointer<T>::type & t) {
    return &t;
}


// convert Args to storage types and construct a tuple of them
template <typename... Args>
typename StorageType<Args...>::type store(typename Args::ArgType... args)
{
    return std::tuple<typename Args::StorageType...>(Args::arg_to_store(args)...);
}

}   // namespace mock_support


/* Tag base type for arguments and return types. */
template <typename ArgT, typename StorageT = ArgT>
struct TagBase {
    using ArgType = ArgT;
    using StorageType = StorageT;

    static StorageType arg_to_store(ArgType const & arg) {
        return ::mock_support::convert<StorageType>(arg);
    }

    static ArgType store_to_arg(StorageType const & stored) {
        return ::mock_support::convert<ArgType>(stored);
    }
};


/* Tag for value types.
 *
 * These are copyable and will be stored in the call args list by value.
 *
 * @tparam T The type of the return value or parameter.
 * @tparam ST Override the storage type. ST must be convertible to T.
 */
template <
    typename T,
    typename ST = typename ::mock_support::remove_ptr_ref_const<T>::type
>
struct Val : TagBase<T, ST> {};


struct objects_must_be_passed_by_reference_or_pointer;


/* Tag for object types.
 *
 * These are not copyable (or at least don't need to be) and will be stored in the call
 * args list by pointer.
 *
 * @tparam T The type of the return value or parameter.
 */
template <typename T, typename Enable = void>
struct Obj : TagBase<objects_must_be_passed_by_reference_or_pointer> {
};

template <typename T>
struct Obj<T, typename std::enable_if<std::is_pointer<T>::value>::type>
    : TagBase<T, typename std::remove_cv<T>::type>
{};

template <typename T>
struct Obj<T, typename std::enable_if<std::is_reference<T>::value>::type>
    : TagBase<T, typename std::remove_cv<typename std::remove_reference<T>::type>::type *>
{};


/* Tag for void return type.
 *
 * This should be used as the first template argument to MockFun if the function to
 * be mocked returns void.
 */
struct Void {
    using ArgType = void;
    using StorageType = Void;
};


/* A mock (member) function.
 *
 * This is a class template that mocks a (member) function with a given signature.
 * Once an object is created you can set the return value, or specify a function that
 * creates a return value. The mock will track any calls so you can assert that they
 * did or didn't happen.
 *
 * This is intended to partially mirror Python's unittest.mock.Mock so that we can keep
 * the tests similar between Python and C++.
 *
 *
 * Creating mock functions
 *
 * To specify the type of the mocked function, use the template parameters. The first
 * template argument specifies the return type, after that follow the argument types.
 * Each argument needs to be wrapped in the Val<> or Obj<> template.
 *
 * Val<> is used for value types, which must be copyable and moveable. Use this if the
 * type is one that carries data. The base type will be used to record any passed
 * arguments, or for the return_value member.
 *
 * Obj<> is used for objects, e.g. when you're passing a reference to another component.
 * Any passed values will be recorded in a pointer pointing to them, and the
 * return_value member variable will also be a pointer type.
 *
 * For functions returning void, use Void as the return type tag.
 *
 *
 * Examples
 *
 * As an example, if you had a function f with signature
 *
 *     int f(std::string const & s, Communicator & c);
 *
 * then you should mock it using
 *
 *     MockFun<Val<int>, Val<std::string const &>, Obj<Communicator &>> f;
 *
 * f.call_args_list will then be of type
 * std::vector<std::tuple<std::string, Communicator *>> and return_value will be an int.
 *
 *     MockFun<Void, Val<std::string>, Obj<Communicator const *>> f2;
 *
 * mocks a function with signature
 *
 *     void f2(std::string s, Communicator const * s);
 *
 * f2's call_args_list will then be of the same type as that of f, and its return_value
 * will be of a type that cannot be assigned to.
 *
 * Note that we used Val<> on the string argument, since a string is a copyable value
 * and it makes sense to just store it as a string. If we used Obj<> here, then a
 * pointer to the passed string would be stored, which could be problematic if the
 * caller passes a local variable that has gone out of scope by the time we get back to
 * our test function to examine the arguments.
 *
 * The Communicator object isn't copyable, and we know there's only one of it that lives
 * as long as the test is running, so we can use Obj<> for it.
 *
 *
 * Functions with default arguments
 *
 * If the function to be mocked has default arguments, then you'll need to create a
 * derived class with an overload for operator() for the shorter versions:
 *
 * using BaseMockFun = MockFun<Val<int>, Val<std::string const &>, Val<bool>>;
 *
 * struct MockOverloadedFun : BaseMockFun {
 *     int operator()(std::string const & s = "", bool b = true) {
 *         return BaseMockFun::operator()(s, b);
 *     }
 * };
 *
 * Or you can rename the mock and define a separate function with default arguments
 * that forwards to it:
 *
 * MockFun<int, std::string const &, bool> f_mock;
 *
 * int f(std::string const & s = "", bool b = true) {
 *     f_mock(s, b);
 * }
 *
 * If you're mocking a virtual member function override then the first option doesn't
 * work, and the second one needs to be used.
 *
 *
 * Using the mocked function
 *
 * To set a return value for the mocked function f above, use
 *
 *     f.return_value = 7;
 *
 * If the code under test then does
 *
 *     int x = f("test", communicator);
 *
 * x will become 7. Once back in the test, we can check that f was called and how using
 *
 * ASSERT_TRUE(f.called());
 * ASSERT_TRUE(f.called_once());
 * ASSERT_EQ(f.call_arg<0>(), "test");
 * ASSERT_EQ(f.call_arg<1>(), &communicator);
 *
 * To specify a function that should be called when f2 is called, do
 *
 *     f2.side_effect = [](std::string s, Communicator const * s) {
 *         std::cout << "Called with " << s << std::endl;
 *     };
 *
 * Don't forget the semicolon at the end, and don't forget to return a value if the
 * function doesn't return void.
 *
 * @tparam Ret Type returned by the member function to be mocked, wrapped in Val or Obj.
 * @tparam Args... The types of the arguments to be accepted by the mock, also wrapped.
 */
template <typename Ret, typename... Args>
class MockFun {
    public:
        using StorageType = typename ::mock_support::StorageType<Args...>::type;
        using ReturnStorageType = typename std::remove_const<typename Ret::StorageType>::type;

        /* Mock call operator for non-void functions. */
        template <typename R = Ret>
        typename std::enable_if<!std::is_same<Void, R>::value, typename R::ArgType>::type
        operator()(typename Args::ArgType ... args) const {
            call_args_list.push_back(::mock_support::store<Args...>(args...));
            if (side_effect)
                return side_effect(std::forward<decltype(args)>(args)...);
            else {
                if (!return_value.is_set()) {
                    throw std::runtime_error(
                            name + " was called but doesn't have a return_value"
                            " or side_effect set");
                }
                return R::store_to_arg(return_value.get());
            }
        }

        /* Mock call operator for void return type. */
        template <typename R = Ret>
        typename std::enable_if<std::is_same<Void, R>::value>::type
        operator()(typename Args::ArgType ... args) const
        {
            call_args_list.push_back(
                    ::mock_support::store<Args...>(
                        std::forward<decltype(args)>(args)...));
            if (side_effect)
                side_effect(std::forward<decltype(args)>(args)...);
        }

        /* Returns whether the mock was called at least once. */
        bool called() const {
            return !call_args_list.empty();
        }

        /* Returns whether the mock was called exactly once. */
        bool called_once() const {
            return call_args_list.size() == 1u;
        }

        /* Returns whether the last call was done with the given arguments. */
        template <typename... A>
        bool called_with(A... args) const {
            return call_args() == ::mock_support::store<Args...>(args...);
        }

        /* Returns whether there was exactly one call with the given arguments. */
        template <typename... A>
        bool called_once_with(A... args) const {
            return called_once() && called_with(args...);
        }

        /* Returns the arguments with which the mock was called most recently.
         *
         * Getting individual items out of the tuple requires some ugly syntax, so you
         * probably want to use call_arg<I>(j) instead, see below.
         */
        StorageType const & call_args() const {
            if (call_args_list.empty()) {
                throw std::runtime_error(
                        "Tried to get call_args() for " + name + ", but call_args_list"
                        " is empty");
            }
            return call_args_list.back();
        }

        /* Returns the I'th argument of the j'th most recent call.
         *
         * Counts start at 0 as usual, so f.call_arg<0>(1) gets the first argument of
         * the second most recent call.
         */
        template <int I>
        std::tuple_element_t<I, StorageType> const & call_arg(
                std::size_t j = 0u) const
        {
            if (j >= call_args_list.size()) {
                std::ostringstream oss;
                oss << "Requested " << name << ".call_arg<" << I << ">(" << j << ")";
                oss << " but " << name;
                if (call_args_list.empty())
                    oss << " has never been called.";
                else {
                    oss << " has only been called " << call_args_list.size();
                    oss << " times.";
                }
                throw std::runtime_error(oss.str());
            }
            std::size_t i = call_args_list.size() - 1u - j;
            return std::get<I>(call_args_list.at(i));
        }

        /* The value to be returned when the mock is called. */
        ::libmuscle::_MUSCLE_IMPL_NS::Optional<ReturnStorageType> return_value;

        /* A function to be called whose result to return when called. */
        std::function<typename Ret::ArgType(typename Args::ArgType...)> side_effect;

        /* All the arguments with which the function has been called. */
        mutable std::vector<StorageType> call_args_list;

        /* Name of the mocked function, used for error messages.
         *
         * See NAME_MOCK_FUN and NAME_MOCK_MEM_FUN for some helpers.
         * */
        std::string name;
};


/* Set the name of a mock function.
 *
 * Use this to teach a mock what it's called, so that it can give you better error
 * messages. Not required, but very useful.
 *
 * For member functions there's NAME_MOCK_MEM_FUN, which also lets you specify the
 * class name.
 */
#define NAME_MOCK_FUN(FUNC) FUNC.name = #FUNC


/* Set the name of a mock member function.
 *
 * Use this to teach a mock what it's called, so that it can give you better error
 * messages. Not required, but very useful. See MockClass for an example.
 */
#define NAME_MOCK_MEM_FUN(CLS, FUNC) FUNC.name = #CLS "::" #FUNC


/* Tag type for return value constructor. */
struct ReturnValue {};


/* Parent class for mock classes.
 *
 * This adds facilities to a mock class for setting a default object to be cloned when a
 * new object is created.
 *
 * If you have a function under test that creates an object of a mocked class and then
 * calls a member function on it, then you can't set the return value on that object
 * because that would have to happen in between those two actions, and they're inside
 * the function.
 *
 * In Python, you can say MyClass = Mock(), and then MyClass.return_value = Mock(), and
 * now that second mock will be returned when a new MyClass is made. You can then do
 * MyClass.return_value.mem_fun = Mock() and MyClass.return_value.mem_fun.return_value =
 * 10, and now the newly created object will return 10 from its mem_fun().
 *
 * This class has a static return_value member of type T, and is intended to be
 * inherited from using the Curiously Recurring Template Pattern (CRTP):
 *
 * class MockMyClass : public MockClass<MockMyClass> {
 *     public:
 *         MockMyClass(ReturnValue) {
 *             NAME_MOCK_MEM_FUN(MockMyClass, constructor);
 *             NAME_MOCK_MEM_FUN(MockMyClass, fn1);
 *             NAME_MOCK_MEM_FUN(MockMyClass, fn2);
 *         }
 *
 *         MockMyClass() {
 *             init_from_return_value();
 *         }
 *
 *         MockMyClass(int i) {
 *             init_from_return_value();
 *             constructor(i);
 *         }
 *
 *         MockFun<Void> constructor;
 *         MockFun<Val<int>> fn1;
 *         MockFun<Val<std::string>> fn2;
 * };
 *
 * Now, a test can do
 *
 * MockMyClass::return_value.fn1.return_value = 10;
 *
 * and then when the test code does
 *
 * MockMyClass my_class;
 * int x = my_class.fn1();
 *
 * it will receive that 10.
 *
 * The mock class must define a constructor taking a ReturnValue, as shown above. The
 * argument is just a tag to distinguish this from other constructors you may add to
 * mimick the original type. This constructor is used to initialise the ::return_value
 * static member variable. You should use NAME_MOCK_MEM_FUN here for each MockFun<> in
 * the class so that the mock member functions know who they are and can generate
 * helpful error messages. Other initialisation (e.g. setting default return values) is
 * better done in a fixture, so don't add that here.
 *
 * Other constructors can then be added as needed. You'll generally want a default
 * constructor so that an instance of the mock class can easily be made in a fixture or
 * a test, and of course you need to add a constructor mimicking each constructor the
 * real class has. Since you can't have a member variable with the same name as the
 * class, the constructor needs to be an actual constructor. In the example above, we
 * have it forward its arguments to a mock, so that a test can check what it was called
 * with.
 *
 * Each normal constructor (but not the ReturnValue one!) needs to call
 * init_from_return_value() as the first thing it does. This will assign the static
 * ::return_value to the current object, thus ensuring that anything set on that by the
 * user is applied.
 *
 * With the constructors done, you'll probably want to add some MockFun<> member
 * variables that mock functions an the real class. See MockFun<> above.
 *
 * Finally, note that the static return_value is shared by everyone using this mock in
 * this process. If multiple tests are run in a single program, as is usually the case,
 * then the mock needs to be reset between tests to ensure they're independent. See
 * RESET_MOCKS below for this.
 */
template <typename T>
struct MockClass {
    protected:
        /* Initialise this object from the static return_value.
         *
         * To be called in constructors of derived mock classes.
         */
        void init_from_return_value() {
            static_cast<T&>(*this) = return_value;
        }

    public:
        /* Reset return_value.
         *
         * Since return_value is a static variable, there's only one for the entire
         * program, meaning tests share it. If a test modifies the return_value, then
         * this affects all the other tests, and that's bad. To avoid this, call
         * T::reset(); in the fixture constructor.
         */
        struct reset {
            reset() {
                T::return_value = T(ReturnValue());
            }
        };

        /* Return value of T().
         *
         * This is the return value of the *type* T. If a T is created by the test
         * code, then a copy of this value will be returned, assuming that T has been
         * implemented correctly.
         *
         * Currently static and therefore not thread-safe. We could make this
         * thread_local instead, which would allow running tests in parallel, but there
         * are some issues with thread_local on MacOS so we'll need to test carefully.
         * For now this is good enough.
         */
        static T return_value;

        // TODO: we could have a static list of instances and add new ones here
};

template <typename T>
T MockClass<T>::return_value = T(ReturnValue());



/* Return value reset helper.
 *
 * The class return value of a MockClass is a static member, which means that it gets
 * created at start-up of the test program and is destroyed at the end. That means that
 * if multiple tests are run in succession, they share the return_value. This is not
 * good, because it introduces a dependency. Unfortunately, the class itself has static
 * storage duration in a way, and we can't make a new class for every test like we can
 * in Python.
 *
 * So instead, we need to reset the return value in between tests. This can be done in
 * the fixture class constructor, but it's a bit tricky because we want to reset the
 * return value before instantiating the mock. If we did
 *
 * struct fixture {
 *     Mock mock_;
 *
 *     fixture() {
 *         Mock::reset();
 *     }
 * };
 *
 * then mock_ would be created as a copy of whatever the previous test left in
 * Mock::return_value, and only then Mock::return_value would be reset.
 *
 * So instead, Mock::reset is defined as a struct (see MockClass), and we create a
 * variable of that type:
 *
 * struct fixture {
 *     Mock::reset _;
 *     Mock mock_;
 *
 *     fixture() {
 *         // initialise things
 *     }
 * };
 *
 * Since local variables are initialised in the order in which they are declared, the
 * constructor of Mock::reset (which resets the static return value) will be run before
 * mock_ is instantiated.
 *
 * If you're using multiple mocks, then you'll want to reset all of them. Then you'll
 * have to create multiple dummy variables with different names, and it all becomes
 * wordy and unclear. So we have a helper here that lets you write
 *
 * struct fixture {
 *     RESET_MOCKS(Mock1, Mock2, Mock3);
 * };
 *
 * Put that at the top of your fixture class and all should be well.
 */
template <typename... Types>
using reset_mocks_t = std::tuple<typename Types::reset ...>;

#define RESET_MOCKS(...) reset_mocks_t<__VA_ARGS__> _

