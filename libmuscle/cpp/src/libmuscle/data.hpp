#pragma once

#include <cstddef>
#include <memory>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#include <msgpack.hpp>

#include <ymmsl/ymmsl.hpp>


namespace libmuscle { namespace impl {

enum class StorageOrder {
    first_adjacent,
    last_adjacent
};

class DataConstRef;

class Data;

bool is_close_port(DataConstRef const &);

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

        /** Create a DataConstRef object containing a grid object.
         *
         * This creates a DataConstRef that represents a grid or array of a
         * given element type.
         *
         * Supported types are ``std::int32_t``, ``std::int64_t``, ``float``,
         * ``double`` and ``bool``. Note that unless you have exotic hardware,
         * ``int``, ``long`` and ``long long`` will be aliased as either
         * ``int32_t`` or ``int64_t``, and will therefore work as well. Unsigned
         * integer types are not supported.
         *
         * Besides a type, arrays have a shape. This is a list of sizes, one for
         * each dimension of the array.
         *
         * They also have a storage order, which specifies in which order the
         * elements are arranged in memory. StorageOrder::first_adjacent means
         * that array items who only differ by one in their first index are
         * adjacent in memory, while StorageOrder::last_adjacent means that
         * array items which only differ by one in their last index are adjacent
         * in memory. Last adjacent is the standard in C and C++, and is also
         * known as column-major, while first adjacent is the standard in
         * Fortran, and is also known as row-major.
         *
         * The data argument should be a pointer to a contiguous array of
         * elements of the given type.
         *
         * Finally, the optional index_names argument may be used to specify the
         * names of the indices. For a Cartesian grid, these may be ``x`` and
         * ``y``, while for for example a polar grid you may have ``rho`` and
         * ``phi``. These names are optional, but help to make it easier to
         * interpret the data, and so adding them is very much recommended.
         *
         * @tparam Element The type of the elements.
         * @param data Pointer to the array data.
         * @param shape The shape of the array.
         * @param indexes Names of the array's indexes.
         * @param storage_order The storage order of the array data.
         */
        template <typename Element>
        static DataConstRef grid(
                Element const * const data,
                std::vector<std::size_t> const & shape,
                std::vector<std::string> const & indexes = {},
                StorageOrder storage_order = StorageOrder::last_adjacent);

        /** Create a DataConstRef object from a SettingValue's value.
         *
         * Note that this will decode to whichever type is stored in the
         * SettingValue, not to a SettingValue object.
         *
         * @param value The value to represent.
         */
        DataConstRef(::ymmsl::SettingValue const & value);

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

        /** Reseat the reference.
         *
         * This makes this DataConstRef object refer to the object referred to
         * by the argument.
         *
         * @param target The object to refer to.
         */
        void reseat(DataConstRef const & target);

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
         * - ymmsl::SettingValue
         * - ymmsl::Settings
         *
         * For checking nil, list and dict, see is_nil(), is_a_list() and
         * is_a_dict().
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

        /** Return whether this references a grid of the given element type.
         *
         * Supported element types are ``std::int32_t``, ``std::int64_t``,
         * ``float``, ``double``, and ``bool``. Unless you're on some exotic
         * machine, ``int``, ``long``, and ``long long`` are aliases for
         * ``int32_t`` or ``int64_t``, and so will also work. Unsigned types are
         * not supported.
         *
         * @tparam Element The type of the elements of the array.
         */
        template <typename Element>
        bool is_a_grid_of() const;

        /** Return whether this references a byte array.
         *
         * If so, as_byte_array() can be used to obtain values, and size()
         * to get the number of bytes in the array.
         *
         * @return True iff this references a byte array.
         */
        bool is_a_byte_array() const;

        /** Returns the size of a list, dict, grid or byte array.
         *
         * @return The number of items in a referenced list or dict value, the
         *         number of elements in a grid, or the number of bytes in a
         *         byte array.
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
         * - ymmsl::SettingValue
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
         * array. Use size() to get the size.
         *
         * The returned buffer will remain valid and accessible at least until
         * this DataConstRef goes out of scope.
         *
         * @return A pointer to a the first byte of a consecutive buffer.
         * @throws std::runtime_error if this is not a byte array.
         */
        char const * as_byte_array() const;

        /** Access an item in a dictionary by key.
         *
         * Use only if is_a_dict() returns true.
         *
         * @param key The key whose value to retrieve.
         * @throws std::runtime_error if the object is not a map.
         * @throws std::domain_error if the key does not exist.
         */
        DataConstRef operator[](std::string const & key) const;

        /** Access a key in a dictionary by index.
         *
         * Use only if is_a_dict() returns true.
         *
         * Indices match those of value(), so value(i) will give you the value
         * corresponding to key(i).
         *
         * @param i The index of the key to retrieve.
         * @throws std::runtime_error if the object is not a map.
         * @throws std::domain_error if the index is out of bounds.
         * @see size()
         */
        std::string key(std::size_t i) const;

        /** Access a value in a dictionary by index.
         *
         * Use only if is_a_dict() returns true.
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
         * Use only if is_a_list() returns true.
         *
         * Indexes are zero-based, use size() to find the valid range.
         *
         * @param index The index at which to retrieve a value.
         * @throws std::runtime_error if the object is not a list.
         * @throws std::domain_error if the index is out of range.
         */
        DataConstRef operator[](std::size_t index) const;

        /** Get the shape of a grid.
         *
         * Use only if is_a_grid_of() returns true.
         *
         * The shape of an array is a list of sizes of the array, one for each
         * of its dimensions.
         *
         * @return The shape of the contained grid.
         * @throws std::runtime_error if the object is not a grid.
         */
        std::vector<std::size_t> shape() const;

        /** Get the storage order of the grid.
         *
         * Use only if is_a_grid_of() returns true.
         *
         * The storage order is either StorageOrder::first_adjacent or
         * StorageOrder::last_adjacent. StorageOrder::first_adjacent means that
         * array items who only differ by one in their first index are adjacent
         * in memory, while StorageOrder::last_adjacent means that array items
         * which only differ by one in their last index are adjacent in memory.
         * Last adjacent is the standard in C and C++, and is also known as
         * column-major, while first adjacent is the standard in Fortran, and is
         * also known as row-major.
         *
         * @return The storage order of the grid.
         * @throws std::runtime_error if the object is not a grid.
         */
        StorageOrder storage_order() const;

        /** Return whether a grid has index names.
         *
         * Use only if is_a_grid_of() returns true.
         *
         * This function determines whether the grid has named indexes. If so,
         * you can access them through indexes().
         *
         * @return True iff the grid has named indexes.
         * @throw std::runtime_Error if the object is not a grid.
         */
        bool has_indexes() const;

        /** Get the index names of the grid.
         *
         * Use only if is_a_grid_of() returns true and has_indexes()
         * returns true.
         *
         * The optional index names returned by this function specify which
         * index refers to what. For a 2D Cartesian grid, these may be ``'x'``
         * and ``'y'`` for example, or for a polar grid, ``'phi'`` and
         * ``'rho'``. They're intended to help annotate and use the data, and
         * may be absent if the sender of a message did not include them.
         *
         * @return The indexes.
         * @throw std::runtime_error if the object is not a grid.
         */
        std::vector<std::string> indexes() const;

        /** Get the elements (data values) of a grid.
         *
         * Use only if is_a_grid_of<Element>() returns true.
         *
         * This returns a pointer to the specified type which points to a block
         * of memory containing the grid's element values. They are contiguous
         * in memory in the order specified by storage_order().
         *
         * The returned pointer is valid at least as long as this object exists.
         *
         * @tparam Element The type of the data stored in the grid.
         * @return A pointer to the data, as specified above.
         * @throws std::runtime_error if the object is not a grid of this type.
         */
        template <typename Element>
        Element const * elements() const;

    protected:
        using Zones_ = std::shared_ptr<std::vector<std::shared_ptr<msgpack::zone>>>;
        Zones_ mp_zones_;
        msgpack::object * mp_obj_;

        // cache for extracted complex object, e.g. Settings, Grid
        mutable std::shared_ptr<DataConstRef> obj_cache_;

        // create DCR pointing to the given object and sharing the given zone
        DataConstRef(
                msgpack::object * data,
                std::shared_ptr<msgpack::zone> const & zone);

        // create DCR pointing to the given object and sharing the given zones
        DataConstRef(
                msgpack::object * data,
                Zones_ const & zones);

        // create DCR sharing the given zone
        explicit DataConstRef(std::shared_ptr<msgpack::zone> const & zone);

        // create DCR with given data packed as ext type
        DataConstRef(char ext_type_id, DataConstRef const & data);

        // allocate an object on this object's zone
        template <typename T>
        T * zone_alloc_(uint32_t size = 1u);

        std::vector<double> as_vec_double_() const;

        friend struct msgpack::adaptor::object_with_zone<DataConstRef>;
        friend struct msgpack::adaptor::pack<DataConstRef>;

        // see comment at Data::init_dict_'s implementation
        friend class Data;
        friend bool ::libmuscle::impl::is_close_port(DataConstRef const &);

        bool is_a_grid_() const;

        DataConstRef grid_dict_() const;

        template <typename Element>
        DataConstRef grid_data_(Element const * const data, std::size_t num_elems) const;
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

        /** Create a Data object containing a grid object.
         *
         * This creates a DataConstRef that represents a grid or array of a
         * given element type.
         *
         * Supported types are ``std::int32_t``, ``std::int64_t``, ``float``,
         * ``double`` and ``bool``. Note that unless you have exotic hardware,
         * ``int``, ``long`` and ``long long`` will be aliased as either
         * ``int32_t`` or ``int64_t``, and will therefore work as well. Unsigned
         * integer types are not supported.
         *
         * Besides a type, arrays have a shape. This is a list of sizes, one for
         * each dimension of the array.
         *
         * They also have a storage order, which specifies in which order the
         * elements are arranged in memory. StorageOrder::first_adjacent means
         * that array items who only differ by one in their first index are
         * adjacent in memory, while StorageOrder::last_adjacent means that
         * array items which only differ by one in their last index are adjacent
         * in memory. Last adjacent is the standard in C and C++, and is also
         * known as column-major, while first adjacent is the standard in
         * Fortran, and is also known as row-major.
         *
         * The data argument should be a pointer to a contiguous array of
         * elements of the given type.
         *
         * Finally, the optional index_names argument may be used to specify the
         * names of the indices. For a Cartesian grid, these may be ``x`` and
         * ``y``, while for for example a polar grid you may have ``rho`` and
         * ``phi``. These names are optional, but help to make it easier to
         * interpret the data, and so adding them is very much recommended.
         *
         * @tparam Element The type of the elements.
         * @param data Pointer to the array data.
         * @param shape The shape of the array.
         * @param indexes Names of the array's indexes.
         * @param storage_order The storage order of the array data.
         */
        template <typename Element>
        static Data grid(
                Element const * const data,
                std::vector<std::size_t> const & shape,
                std::vector<std::string> const & indexes = {},
                StorageOrder storage_order = StorageOrder::last_adjacent);

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
         * \code{.cpp}
         * auto mydict = Data::dict(
         *     "id", "element1",
         *     "stress", 12.3,
         *     "strain", 1.23);
         * \endcode
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

        /** Create a byte array of a given size.
         *
         * The buffer will be owned by this Data object. Use as_byte_array() to
         * get a pointer to put data into it.
         */
        static Data byte_array(uint32_t size);

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
         * \code{.cpp}
         * mydict["stress"] = 12.4;
         * \endcode
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

        /** Access a value in a dictionary by index.
         *
         * Use only if is_a_dict() returns true.
         *
         * Indices match those of key(), so value(i) will give you the value
         * corresponding to key(i).
         *
         * @param i The index of the value to retrieve.
         * @throws std::runtime_error if the object is not a map.
         * @throws std::domain_error if the index is out of bounds.
         * @see size()
         */
        Data value(std::size_t i) const;

        /** Access a list entry by index.
         *
         * Returns a Data object referring to the value at the given index.
         * Assign to that object to modify a value, as in
         *
         * \code{.cpp}
         * mylist[3] = 12.4;
         * mylist[4] = "MUSCLE 3";
         * \endcode
         *
         * @param index The index to refer to.
         * @return A writable reference to the requested value.
         * @throws std::runtime_error if the object is not a list.
         * @throws std::out_of_range if the index is beyond the end of the list.
         */
        Data operator[](std::size_t index);

        /** Access a byte array.
         *
         * Use is_a_byte_array() to check whether this object represents a byte
         * array. Use size() to get the size in bytes.
         *
         * The returned buffer will remain valid and accessible at least until
         * this Data goes out of scope.
         *
         * @return A pointer to a the first byte of a consecutive buffer.
         * @throws std::runtime_error if this is not a byte array.
         */
        char * as_byte_array();

    private:
        // this requires packing, so needs to be non-template
        void set_dict_item_(
                uint32_t offset,
                std::string const & key, DataConstRef const & value);

        void set_dict_item_(
                uint32_t offset,
                std::string const & key, Data const & value);

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
        friend Data libmuscle::impl::mcp::unpack_data(
                std::shared_ptr<msgpack::zone> const & zone,
                char const * begin, std::size_t length);
};

} }   // namespace libmuscle::impl

#include <libmuscle/data.tpp>

