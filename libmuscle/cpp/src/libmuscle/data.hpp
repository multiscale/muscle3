#pragma once

#include <memory>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#include <msgpack.hpp>

#include <ymmsl/settings.hpp>


namespace libmuscle {

class Data;

namespace mcp {
    // forward-declare this so it can be a friend
    Data unpack_data(
            std::shared_ptr<msgpack::zone> const & zone,
            char const * begin, std::size_t length);
}


/** A const reference to some kind of data.
 *
 * This defines a read-only API for variable data objects, which is what
 * MUSCLE 3 sends and receives.
 *
 * As a user, you should be creating Data objects, not DataConstRef objects.
 * Data objects have the same interface as DataConstRef objects, but have
 * additional member functions for modification.
 *
 * This class models a const reference. You can create it and access the
 * referenced data, but you cannot assign to this because that would change
 * the referenced data, and this is a const reference.
 *
 * With respect to memory management, this is like a shared_ptr, in that it
 * will automatically manage referenced memory, even if you copy the object.
 */
class DataConstRef {
    public:
        /** Create a Data object representing nil.
         *
         * Nil is a special "no data" value, like nullptr or None in Python.
         */
        DataConstRef();

        /** Create a DataConstRef object representing a boolean value.
         *
         * @param value The value to represent.
         */
        DataConstRef(bool value);

        /** Create a DataConstRef object representing a string value.
         *
         * @param value The value to represent, a null-terminated C string.
         */
        DataConstRef(char const * const value);

        /** Create a DataConstRef object representing a string value.
         *
         * @param value The value to represent.
         */
        DataConstRef(std::string const & value);

        /** Create a DataConstRef object representing an integer value.
         *
         * @param value The value to represent.
         */
        DataConstRef(int value);

        /** Create a DataConstRef object representing an integer value.
         *
         * @param value The value to represent.
         */
        DataConstRef(long int value);

        /** Create a DataConstRef object representing an integer value.
         *
         * @param value The value to represent.
         */
        DataConstRef(long long int value);

        /** Create a DataConstRef object representing an unsigned integer value.
         *
         * @param value The value to represent.
         */
        DataConstRef(unsigned int value);

        /** Create a DataConstRef object representing an unsigned integer value.
         *
         * @param value The value to represent.
         */
        DataConstRef(unsigned long int value);

        /** Create a DataConstRef object representing an unsigned integer value.
         *
         * @param value The value to represent.
         */
        DataConstRef(unsigned long long int value);

        /** Create a DataConstRef object representing a 32-bit floating point value.
         *
         * @param value The value to represent.
         */
        DataConstRef(float value);

        /** Create a DataConstRef object representing a 64-bit floating point value.
         *
         * @param value The value to represent.
         */
        DataConstRef(double value);

        /** Create a DataConstRef object from a ParameterValue's value.
         *
         * Note that this will decode to whichever type is stored in the
         * ParameterValue, not to a ParameterValue object.
         *
         * @param value The value to represent.
         */
        DataConstRef(::ymmsl::ParameterValue const & value);

        /** Create a DataConstRef object representing a Settings object.
         *
         * @param value The value to represent.
         */
        DataConstRef(::ymmsl::Settings const & settings);

        /** Copy-construct a DataConstRef object.
         */
        DataConstRef(DataConstRef const &) = default;

        /** Move-construct a DataConstRef object.
         */
        DataConstRef(DataConstRef &&) = default;

        /** Assignment is forbidden, this models a const reference.
         */
        DataConstRef & operator=(DataConstRef const &) = delete;

        /** Assignment is forbidden, this models a const reference.
         */
        DataConstRef & operator=(DataConstRef &&) = delete;

        /** Determine the type of the referenced data.
         *
         * This works for the following types:
         *
         * - bool
         * - std::string
         * - char (checks for integer, not for string!)
         * - short int
         * - int
         * - long int
         * - long long int
         * - unsigned char
         * - unsigned short int
         * - unsigned int
         * - unsigned long int
         * - unsigned long long int
         * - float
         * - double
         * - ymmsl::ParameterValue
         * - ymmsl::Settings
         *
         * For checking nil, list and dict, see is_nil(), is_list() and
         * is_dict().
         *
         * @tparam T The type to check.
         */
        template <typename T>
        bool is_a() const;

        /** Return whether this references a nil value.
         *
         * @return True iff this references a nil value.
         */
        bool is_nil() const;

        /** Return whether this references a dict value.
         *
         * If so, operator[key] can be used to obtain values.
         *
         * @return True iff this references a dict.
         */
        bool is_a_dict() const;

        /** Return whether this references a list value.
         *
         * If so, operator[index] can be used to obtain values.
         *
         * @return True iff this references a list.
         */
        bool is_a_list() const;

        /** Return whether this references a byte array.
         *
         * If so, as_byte_array() can be used to obtain values, and size()
         * to get the number of bytes in the array.
         *
         * @return True iff this references a byte array.
         */
        bool is_a_byte_array() const;

        /** Returns the size of a list, dict or byte array.
         *
         * @return The number of items in a referenced list or dict value, or
         *         the number of bytes in a byte array.
         */
        std::size_t size() const;

        /** Access a referenced scalar value.
         *
         * Use is_a* first to check whether the type is what you expect. If
         * the type mismatches, an exception will be thrown.
         *
         * The following types can be used:
         *
         * - bool
         * - std::string
         * - char (accesses as integer, not as string!)
         * - short int
         * - int
         * - long int
         * - long long int
         * - unsigned char
         * - unsigned short int
         * - unsigned int
         * - unsigned long int
         * - unsigned long long int
         * - float
         * - double
         * - ymmsl::ParameterValue
         * - ymmsl::Settings
         *
         * @tparam T The type to access, as above.
         * @return The referenced value, as the given type.
         * @throws std::runtime_error if the type does not match.
         */
        template <typename T>
        T as() const;

        /** Access a byte array.
         *
         * Use is_a_byte_array() to check whether this object represents a byte
         * array.
         *
         * The returned buffer will remain valid and accessible at least until
         * this ConstDataRef goes out of scope.
         *
         * @return A pointer to a the first byte of a consecutive buffer.
         * @throws std::runtime_error if this is not a byte array.
         */
        char const * as_byte_array() const;

        /** Access an item in a dictionary by key.
         *
         * Use only if is_dict() returns true.
         *
         * @param key The key whose value to retrieve.
         * @throws std::runtime_error if the object is not a map.
         * @throws std::domain_error if the key does not exist.
         */
        DataConstRef operator[](std::string const & key) const;

        /** Access a key in a dictionary by index.
         *
         * Use only if is_dict() returns true.
         *
         * Indices match those of value(), so value(i) will give you the value
         * corresponding to key(i).
         *
         * @param i The index of the key to retrieve.
         * @throws std::runtime_error if the object is not a map.
         * @throws std::domain_error if the index is out of bounds.
         * @see size()
         */
        DataConstRef key(std::size_t i) const;

        /** Access a value in a dictionary by index.
         *
         * Use only if is_dict() returns true.
         *
         * Indices match those of key(), so value(i) will give you the value
         * corresponding to key(i).
         *
         * @param i The index of the value to retrieve.
         * @throws std::runtime_error if the object is not a map.
         * @throws std::domain_error if the index is out of bounds.
         * @see size()
         */
        DataConstRef value(std::size_t i) const;

        /** Access an item in a list.
         *
         * Use only if is_list() returns true.
         *
         * Indexes are zero-based, use size() to find the valid range.
         *
         * @param index The index at which to retrieve a value.
         * @throws std::runtime_error if the object is not a list.
         * @throws std::domain_error if the index is out of range.
         */
        DataConstRef operator[](std::size_t index) const;

    protected:
        using Zones_ = std::shared_ptr<std::vector<std::shared_ptr<msgpack::zone>>>;
        Zones_ mp_zones_;
        msgpack::object * mp_obj_;

        // create DCR pointing to the given object and sharing the given zone
        DataConstRef(
                msgpack::object * data,
                std::shared_ptr<msgpack::zone> const & zone);

        // create DCR pointing to the given object and sharing the given zones
        DataConstRef(
                msgpack::object * data,
                Zones_ const & zones);

        // create DCR sharing the given zone
        DataConstRef(std::shared_ptr<msgpack::zone> const & zone);

        // allocate an object on this object's zone
        template <typename T>
        T * zone_alloc_(uint32_t size = 1u);

        std::vector<double> as_vec_double_() const;

        friend struct msgpack::adaptor::object_with_zone<DataConstRef>;
        friend struct msgpack::adaptor::pack<DataConstRef>;

        // see comment at Data::init_dict_'s implementation
        friend class Data;
        friend bool ::libmuscle::is_close_port(DataConstRef const &);
};


/** A data object.
 *
 * This represents a data object, which is what MUSCLE 3 sends and receives.
 *
 * Data objects refer to a simple value of a basic type, or refer to a
 * dictionary or list. They model a reference, so if you copy a Data object to
 * a new Data object, you'll have two Data objects referring to the same data
 * item. If you assign to a Data object, you modify the referred-to item,
 * which will be visible also via any existing copies of the Data object.
 *
 * With respect to memory management, this is like a shared_ptr, in that it
 * will automatically manage any referenced memory, and only remove any actual
 * items once all Data objects referring to them have been destructed.
 *
 * Note that this publicly derives from DataConstRef, so see that class for the
 * constructors and read-only member functions; they work on Data as well.
 *
 * See the C++ tutorial for examples of how to use this.
 */
class Data : public DataConstRef {
    public:
        // create from scalar type
        using DataConstRef::DataConstRef;

        /** Create a Data containing an empty dictionary.
         *
         * @returns A Data containing an empty dictionary.
         */
        static Data dict();
        template <typename... Args>

        /** Create a Data containing a dictionary with the given keys and values.
         *
         * An even number of arguments must be given. The even arguments must be
         * strings, and are the keys, while the odd arguments are the values.
         * These are Data objects, so you can pass those, or a value of any type
         * representable by Data.
         *
         * Example:
         *
         * auto mydict = Data::dict(
         *     "id", "element1",
         *     "stress", 12.3,
         *     "strain", 1.23);
         *
         * @returns A Data containing a dictionary with the given keys and
         *          values.
         */
        static Data dict(Args const &... args);

        /** Create a Data containing an empty list.
         *
         * @returns A Data containing an empty list.
         */
        static Data list();

        /** Create a Data containing a list of the given size.
         *
         * The items in the list will be initialised to the nil value.
         *
         * @param size The size of the new list.
         * @return A Data containing a list of nil values of length size.
         */
        static Data nils(std::size_t size);

        /** Create a Data containing a list of the given items.
         *
         * Each argument must be either a Data object, or an object of a type
         * representable by a Data object.
         */
        template <typename... Args>
        static Data list(Args const &... args);

        /** Create a Data referencing a byte array.
         *
         * The buffer passed will not be copied! This creates a Data object
         * that refers to your buffer, and you need to make sure that that
         * buffer exists for as long as the Data object (and/or any copies of
         * it) is used.
         *
         * @param buffer A pointer to the beginning of the buffer.
         * @param size The size of the buffer.
         */
        static Data byte_array(char const * buffer, uint32_t size);

        /** Copy-assign the given value to this Data object.
         *
         * If the argument is a basic type, then the value will be copied. If
         * it is a list or a dict, then this Data object will refer to the same
         * list or dict as the argument.
         *
         * @param rhs The object to copy from.
         */
        Data & operator=(Data const & rhs);

        /** Access a dictionary value by key.
         *
         * Returns a Data object referring to the value for the given key.
         * Assign to that object to modify a value, as in
         *
         * mydict["stress"] = 12.4;
         *
         * If no key with the given name exists, a new entry is added to the
         * dictionary with the given key and a nil value, and a reference to
         * it is then returned. This way new key/value pairs can be added to a
         * dictionary.
         *
         * @param key The key to search for.
         * @return A writable reference to the requested value.
         * @throws std::runtime_error if the object is not a dictionary.
         */
        Data operator[](std::string const & key);

        /** Access a list entry by index.
         *
         * Returns a Data object referring to the value at the given index.
         * Assign to that object to modify a value, as in
         *
         * mylist[3] = 12.4;
         * mylist[4] = "MUSCLE 3";
         *
         * @param index The index to refer to.
         * @return A writable reference to the requested value.
         * @throws std::runtime_error if the object is not a list.
         * @throws std::out_of_range if the index is beyond the end of the list.
         */
        Data operator[](std::size_t index);

    private:
        void init_dict_(uint32_t size);

        template <typename... Args>
        void init_dict_(
                uint32_t offset,
                std::string const & key, DataConstRef const & value,
                Args const &...args);

        template <typename... Args>
        void init_dict_(
                uint32_t offset,
                std::string const & key, Data const & value,
                Args const &...args);

        template <typename Arg, typename... Args>
        void init_dict_(
                uint32_t offset,
                std::string const & key, Arg const & value,
                Args const &...args);

        void init_list_(uint32_t size);

        template <typename... Args>
        void init_list_(
                uint32_t offset, DataConstRef const & value,
                Args const &...args);

        template <typename... Args>
        void init_list_(
                uint32_t offset, Data const & value,
                Args const &...args);

        template <typename Arg, typename... Args>
        void init_list_(
                uint32_t offset, Arg const & value,
                Args const &...args);

        friend struct msgpack::adaptor::pack<Data>;
        friend struct msgpack::adaptor::object_with_zone<Data>;
        friend Data libmuscle::mcp::unpack_data(
                std::shared_ptr<msgpack::zone> const & zone,
                char const * begin, std::size_t length);
};

}   // namespace libmuscle

#include <libmuscle/data.tpp>

