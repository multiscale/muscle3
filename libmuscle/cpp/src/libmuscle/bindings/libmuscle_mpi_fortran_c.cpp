// This is generated code. If it's broken, then you should
// fix the generation script, not this file.


#include <libmuscle/libmuscle.hpp>
#include <libmuscle/bindings/cmdlineargs.hpp>
#include <ymmsl/ymmsl.hpp>
#include <stdexcept>
#include <typeinfo>


using libmuscle::DataConstRef;
using libmuscle::Data;
using libmuscle::PortsDescription;
using libmuscle::Message;
using libmuscle::Instance;
using libmuscle::InstanceFlags;
using libmuscle::mpi_impl::bindings::CmdLineArgs;
using ymmsl::Operator;
using ymmsl::Settings;


extern "C" {

std::intptr_t LIBMUSCLE_MPI_DataConstRef_create_nil_() {
    DataConstRef * result = new DataConstRef();
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_DataConstRef_create_logical_(bool value) {
    DataConstRef * result = new DataConstRef(value);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_DataConstRef_create_character_(char * value, std::size_t value_size) {
    std::string value_s(value, value_size);
    DataConstRef * result = new DataConstRef(value_s);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_DataConstRef_create_int1_(char value) {
    DataConstRef * result = new DataConstRef(value);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_DataConstRef_create_int2_(short int value) {
    DataConstRef * result = new DataConstRef(value);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_DataConstRef_create_int4_(int32_t value) {
    DataConstRef * result = new DataConstRef(value);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_DataConstRef_create_int8_(int64_t value) {
    DataConstRef * result = new DataConstRef(value);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_DataConstRef_create_real4_(float value) {
    DataConstRef * result = new DataConstRef(value);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_DataConstRef_create_real8_(double value) {
    DataConstRef * result = new DataConstRef(value);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_DataConstRef_create_settings_(std::intptr_t value) {
    Settings * value_p = reinterpret_cast<Settings *>(value);
    DataConstRef * result = new DataConstRef(*value_p);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_DataConstRef_create_copy_(std::intptr_t value) {
    DataConstRef * value_p = reinterpret_cast<DataConstRef *>(value);
    DataConstRef * result = new DataConstRef(*value_p);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_DataConstRef_create_grid_logical_a_(bool * data_array, std::size_t * data_array_shape, std::size_t data_array_ndims) {
    std::vector<std::size_t> data_array_shape_v(
            data_array_shape, data_array_shape + data_array_ndims);
    auto data_array_p = const_cast<bool const * const>(data_array);
    DataConstRef * result = new DataConstRef(DataConstRef::grid(data_array_p, data_array_shape_v, {}, libmuscle::StorageOrder::first_adjacent));
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_DataConstRef_create_grid_int4_a_(int32_t * data_array, std::size_t * data_array_shape, std::size_t data_array_ndims) {
    std::vector<std::size_t> data_array_shape_v(
            data_array_shape, data_array_shape + data_array_ndims);
    auto data_array_p = const_cast<int32_t const * const>(data_array);
    DataConstRef * result = new DataConstRef(DataConstRef::grid(data_array_p, data_array_shape_v, {}, libmuscle::StorageOrder::first_adjacent));
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_DataConstRef_create_grid_int8_a_(int64_t * data_array, std::size_t * data_array_shape, std::size_t data_array_ndims) {
    std::vector<std::size_t> data_array_shape_v(
            data_array_shape, data_array_shape + data_array_ndims);
    auto data_array_p = const_cast<int64_t const * const>(data_array);
    DataConstRef * result = new DataConstRef(DataConstRef::grid(data_array_p, data_array_shape_v, {}, libmuscle::StorageOrder::first_adjacent));
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_DataConstRef_create_grid_real4_a_(float * data_array, std::size_t * data_array_shape, std::size_t data_array_ndims) {
    std::vector<std::size_t> data_array_shape_v(
            data_array_shape, data_array_shape + data_array_ndims);
    auto data_array_p = const_cast<float const * const>(data_array);
    DataConstRef * result = new DataConstRef(DataConstRef::grid(data_array_p, data_array_shape_v, {}, libmuscle::StorageOrder::first_adjacent));
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_DataConstRef_create_grid_real8_a_(double * data_array, std::size_t * data_array_shape, std::size_t data_array_ndims) {
    std::vector<std::size_t> data_array_shape_v(
            data_array_shape, data_array_shape + data_array_ndims);
    auto data_array_p = const_cast<double const * const>(data_array);
    DataConstRef * result = new DataConstRef(DataConstRef::grid(data_array_p, data_array_shape_v, {}, libmuscle::StorageOrder::first_adjacent));
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_DataConstRef_create_grid_logical_n_(
        bool * data_array,
        std::size_t * data_array_shape,
        std::size_t data_array_ndims,
        char * index_name_1, std::size_t index_name_1_size,
        char * index_name_2, std::size_t index_name_2_size,
        char * index_name_3, std::size_t index_name_3_size,
        char * index_name_4, std::size_t index_name_4_size,
        char * index_name_5, std::size_t index_name_5_size,
        char * index_name_6, std::size_t index_name_6_size,
        char * index_name_7, std::size_t index_name_7_size
) {
    std::vector<std::size_t> data_array_shape_v(
            data_array_shape, data_array_shape + data_array_ndims);
    auto data_array_p = const_cast<bool const * const>(data_array);

    std::vector<std::string> names_v;
    names_v.emplace_back(index_name_1, index_name_1_size);
    if (data_array_ndims >= 2u)
        names_v.emplace_back(index_name_2, index_name_2_size);
    if (data_array_ndims >= 3u)
        names_v.emplace_back(index_name_3, index_name_3_size);
    if (data_array_ndims >= 4u)
        names_v.emplace_back(index_name_4, index_name_4_size);
    if (data_array_ndims >= 5u)
        names_v.emplace_back(index_name_5, index_name_5_size);
    if (data_array_ndims >= 6u)
        names_v.emplace_back(index_name_6, index_name_6_size);
    if (data_array_ndims >= 7u)
        names_v.emplace_back(index_name_7, index_name_7_size);

    Data * result = new Data(Data::grid(
            data_array_p, data_array_shape_v,
            names_v, libmuscle::StorageOrder::first_adjacent));
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_DataConstRef_create_grid_int4_n_(
        int32_t * data_array,
        std::size_t * data_array_shape,
        std::size_t data_array_ndims,
        char * index_name_1, std::size_t index_name_1_size,
        char * index_name_2, std::size_t index_name_2_size,
        char * index_name_3, std::size_t index_name_3_size,
        char * index_name_4, std::size_t index_name_4_size,
        char * index_name_5, std::size_t index_name_5_size,
        char * index_name_6, std::size_t index_name_6_size,
        char * index_name_7, std::size_t index_name_7_size
) {
    std::vector<std::size_t> data_array_shape_v(
            data_array_shape, data_array_shape + data_array_ndims);
    auto data_array_p = const_cast<int32_t const * const>(data_array);

    std::vector<std::string> names_v;
    names_v.emplace_back(index_name_1, index_name_1_size);
    if (data_array_ndims >= 2u)
        names_v.emplace_back(index_name_2, index_name_2_size);
    if (data_array_ndims >= 3u)
        names_v.emplace_back(index_name_3, index_name_3_size);
    if (data_array_ndims >= 4u)
        names_v.emplace_back(index_name_4, index_name_4_size);
    if (data_array_ndims >= 5u)
        names_v.emplace_back(index_name_5, index_name_5_size);
    if (data_array_ndims >= 6u)
        names_v.emplace_back(index_name_6, index_name_6_size);
    if (data_array_ndims >= 7u)
        names_v.emplace_back(index_name_7, index_name_7_size);

    Data * result = new Data(Data::grid(
            data_array_p, data_array_shape_v,
            names_v, libmuscle::StorageOrder::first_adjacent));
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_DataConstRef_create_grid_int8_n_(
        int64_t * data_array,
        std::size_t * data_array_shape,
        std::size_t data_array_ndims,
        char * index_name_1, std::size_t index_name_1_size,
        char * index_name_2, std::size_t index_name_2_size,
        char * index_name_3, std::size_t index_name_3_size,
        char * index_name_4, std::size_t index_name_4_size,
        char * index_name_5, std::size_t index_name_5_size,
        char * index_name_6, std::size_t index_name_6_size,
        char * index_name_7, std::size_t index_name_7_size
) {
    std::vector<std::size_t> data_array_shape_v(
            data_array_shape, data_array_shape + data_array_ndims);
    auto data_array_p = const_cast<int64_t const * const>(data_array);

    std::vector<std::string> names_v;
    names_v.emplace_back(index_name_1, index_name_1_size);
    if (data_array_ndims >= 2u)
        names_v.emplace_back(index_name_2, index_name_2_size);
    if (data_array_ndims >= 3u)
        names_v.emplace_back(index_name_3, index_name_3_size);
    if (data_array_ndims >= 4u)
        names_v.emplace_back(index_name_4, index_name_4_size);
    if (data_array_ndims >= 5u)
        names_v.emplace_back(index_name_5, index_name_5_size);
    if (data_array_ndims >= 6u)
        names_v.emplace_back(index_name_6, index_name_6_size);
    if (data_array_ndims >= 7u)
        names_v.emplace_back(index_name_7, index_name_7_size);

    Data * result = new Data(Data::grid(
            data_array_p, data_array_shape_v,
            names_v, libmuscle::StorageOrder::first_adjacent));
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_DataConstRef_create_grid_real4_n_(
        float * data_array,
        std::size_t * data_array_shape,
        std::size_t data_array_ndims,
        char * index_name_1, std::size_t index_name_1_size,
        char * index_name_2, std::size_t index_name_2_size,
        char * index_name_3, std::size_t index_name_3_size,
        char * index_name_4, std::size_t index_name_4_size,
        char * index_name_5, std::size_t index_name_5_size,
        char * index_name_6, std::size_t index_name_6_size,
        char * index_name_7, std::size_t index_name_7_size
) {
    std::vector<std::size_t> data_array_shape_v(
            data_array_shape, data_array_shape + data_array_ndims);
    auto data_array_p = const_cast<float const * const>(data_array);

    std::vector<std::string> names_v;
    names_v.emplace_back(index_name_1, index_name_1_size);
    if (data_array_ndims >= 2u)
        names_v.emplace_back(index_name_2, index_name_2_size);
    if (data_array_ndims >= 3u)
        names_v.emplace_back(index_name_3, index_name_3_size);
    if (data_array_ndims >= 4u)
        names_v.emplace_back(index_name_4, index_name_4_size);
    if (data_array_ndims >= 5u)
        names_v.emplace_back(index_name_5, index_name_5_size);
    if (data_array_ndims >= 6u)
        names_v.emplace_back(index_name_6, index_name_6_size);
    if (data_array_ndims >= 7u)
        names_v.emplace_back(index_name_7, index_name_7_size);

    Data * result = new Data(Data::grid(
            data_array_p, data_array_shape_v,
            names_v, libmuscle::StorageOrder::first_adjacent));
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_DataConstRef_create_grid_real8_n_(
        double * data_array,
        std::size_t * data_array_shape,
        std::size_t data_array_ndims,
        char * index_name_1, std::size_t index_name_1_size,
        char * index_name_2, std::size_t index_name_2_size,
        char * index_name_3, std::size_t index_name_3_size,
        char * index_name_4, std::size_t index_name_4_size,
        char * index_name_5, std::size_t index_name_5_size,
        char * index_name_6, std::size_t index_name_6_size,
        char * index_name_7, std::size_t index_name_7_size
) {
    std::vector<std::size_t> data_array_shape_v(
            data_array_shape, data_array_shape + data_array_ndims);
    auto data_array_p = const_cast<double const * const>(data_array);

    std::vector<std::string> names_v;
    names_v.emplace_back(index_name_1, index_name_1_size);
    if (data_array_ndims >= 2u)
        names_v.emplace_back(index_name_2, index_name_2_size);
    if (data_array_ndims >= 3u)
        names_v.emplace_back(index_name_3, index_name_3_size);
    if (data_array_ndims >= 4u)
        names_v.emplace_back(index_name_4, index_name_4_size);
    if (data_array_ndims >= 5u)
        names_v.emplace_back(index_name_5, index_name_5_size);
    if (data_array_ndims >= 6u)
        names_v.emplace_back(index_name_6, index_name_6_size);
    if (data_array_ndims >= 7u)
        names_v.emplace_back(index_name_7, index_name_7_size);

    Data * result = new Data(Data::grid(
            data_array_p, data_array_shape_v,
            names_v, libmuscle::StorageOrder::first_adjacent));
    return reinterpret_cast<std::intptr_t>(result);
}

void LIBMUSCLE_MPI_DataConstRef_free_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    delete self_p;
    return;
}

bool LIBMUSCLE_MPI_DataConstRef_is_a_logical_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_a<bool>();
    return result;
}

bool LIBMUSCLE_MPI_DataConstRef_is_a_character_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_a<std::string>();
    return result;
}

bool LIBMUSCLE_MPI_DataConstRef_is_a_int_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_a<int>();
    return result;
}

bool LIBMUSCLE_MPI_DataConstRef_is_a_int1_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_a<char>();
    return result;
}

bool LIBMUSCLE_MPI_DataConstRef_is_a_int2_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_a<int16_t>();
    return result;
}

bool LIBMUSCLE_MPI_DataConstRef_is_a_int4_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_a<int32_t>();
    return result;
}

bool LIBMUSCLE_MPI_DataConstRef_is_a_int8_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_a<int64_t>();
    return result;
}

bool LIBMUSCLE_MPI_DataConstRef_is_a_real4_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_a<float>();
    return result;
}

bool LIBMUSCLE_MPI_DataConstRef_is_a_real8_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_a<double>();
    return result;
}

bool LIBMUSCLE_MPI_DataConstRef_is_a_dict_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_a_dict();
    return result;
}

bool LIBMUSCLE_MPI_DataConstRef_is_a_list_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_a_list();
    return result;
}

bool LIBMUSCLE_MPI_DataConstRef_is_a_grid_of_logical_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_a_grid_of<bool>();
    return result;
}

bool LIBMUSCLE_MPI_DataConstRef_is_a_grid_of_real4_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_a_grid_of<float>();
    return result;
}

bool LIBMUSCLE_MPI_DataConstRef_is_a_grid_of_real8_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_a_grid_of<double>();
    return result;
}

bool LIBMUSCLE_MPI_DataConstRef_is_a_grid_of_int4_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_a_grid_of<int32_t>();
    return result;
}

bool LIBMUSCLE_MPI_DataConstRef_is_a_grid_of_int8_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_a_grid_of<int64_t>();
    return result;
}

bool LIBMUSCLE_MPI_DataConstRef_is_a_byte_array_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_a_byte_array();
    return result;
}

bool LIBMUSCLE_MPI_DataConstRef_is_nil_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_nil();
    return result;
}

bool LIBMUSCLE_MPI_DataConstRef_is_a_settings_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_a<Settings>();
    return result;
}

std::size_t LIBMUSCLE_MPI_DataConstRef_size_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    std::size_t result = self_p->size();
    return result;
}

bool LIBMUSCLE_MPI_DataConstRef_as_logical_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    try {
        *err_code = 0;
        bool result = self_p->as<bool>();
        return result;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return false;
}

void LIBMUSCLE_MPI_DataConstRef_as_character_(std::intptr_t self, char ** ret_val, std::size_t * ret_val_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    try {
        *err_code = 0;
        static std::string result;
        result = self_p->as<std::string>();
        *ret_val = const_cast<char*>(result.c_str());
        *ret_val_size = result.size();
        return;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

int LIBMUSCLE_MPI_DataConstRef_as_int_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    try {
        *err_code = 0;
        int result = self_p->as<int>();
        return result;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0;
}

char LIBMUSCLE_MPI_DataConstRef_as_int1_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    try {
        *err_code = 0;
        char result = self_p->as<char>();
        return result;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0;
}

short int LIBMUSCLE_MPI_DataConstRef_as_int2_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    try {
        *err_code = 0;
        short int result = self_p->as<int16_t>();
        return result;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0;
}

int32_t LIBMUSCLE_MPI_DataConstRef_as_int4_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    try {
        *err_code = 0;
        int32_t result = self_p->as<int32_t>();
        return result;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0;
}

int64_t LIBMUSCLE_MPI_DataConstRef_as_int8_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    try {
        *err_code = 0;
        int64_t result = self_p->as<int64_t>();
        return result;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0;
}

float LIBMUSCLE_MPI_DataConstRef_as_real4_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    try {
        *err_code = 0;
        float result = self_p->as<float>();
        return result;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0.0;
}

double LIBMUSCLE_MPI_DataConstRef_as_real8_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    try {
        *err_code = 0;
        double result = self_p->as<double>();
        return result;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0.0;
}

std::intptr_t LIBMUSCLE_MPI_DataConstRef_as_settings_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    try {
        *err_code = 0;
        Settings * result = new Settings(self_p->as<Settings>());
        return reinterpret_cast<std::intptr_t>(result);
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0;
}

void LIBMUSCLE_MPI_DataConstRef_as_byte_array_(
        std::intptr_t self,
        char ** data, std::size_t * data_size,
        int * err_code, char ** err_msg, std::size_t * err_msg_len
) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    try {
        *err_code = 0;
        *data = const_cast<char*>(self_p->as_byte_array());
        *data_size = self_p->size();
        return;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg(e.what());
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}
std::intptr_t LIBMUSCLE_MPI_DataConstRef_get_item_by_key_(
        std::intptr_t self,
        char * key, std::size_t key_size,
        int * err_code, char ** err_msg, std::size_t * err_msg_len
) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    std::string key_s(key, key_size);
    try {
        *err_code = 0;
        DataConstRef * result = new DataConstRef((*self_p)[key_s]);
        return reinterpret_cast<std::intptr_t>(result);
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0;
}

std::intptr_t LIBMUSCLE_MPI_DataConstRef_get_item_by_index_(
        std::intptr_t self,
        std::size_t i,
        int * err_code, char ** err_msg, std::size_t * err_msg_len
) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    try {
        *err_code = 0;
        DataConstRef * result = new DataConstRef((*self_p)[i-1u]);
        return reinterpret_cast<std::intptr_t>(result);
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0;
}

std::size_t LIBMUSCLE_MPI_DataConstRef_num_dims_(
        std::intptr_t self,
        int * err_code, char ** err_msg, std::size_t * err_msg_len
) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    try {
        *err_code = 0;
        return self_p->shape().size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0;
}

void LIBMUSCLE_MPI_DataConstRef_shape_(std::intptr_t self, std::size_t ** shp, std::size_t * shp_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    try {
        *err_code = 0;
        static std::vector<std::size_t> result;
        result = self_p->shape();
        *shp = result.data();
        *shp_size = result.size();
        return;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

void LIBMUSCLE_MPI_DataConstRef_elements_logical_(
        std::intptr_t self,
        std::size_t ndims,
        bool ** elements,
        std::size_t * elements_shape,
        int * elements_format,
        int * err_code, char ** err_msg, std::size_t * err_msg_len
) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    try {
        *err_code = 0;
        if (self_p->shape().size() != ndims)
            throw std::runtime_error("Grid does not have a matching number of dimensions.");
        bool const * result = self_p->elements<bool>();
        *elements = const_cast<bool *>(result);

        for (std::size_t i = 0u; i < ndims; ++i)
            elements_shape[i] = self_p->shape()[i];

        *elements_format = (self_p->storage_order() == libmuscle::StorageOrder::last_adjacent);
        return;
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

void LIBMUSCLE_MPI_DataConstRef_elements_int4_(
        std::intptr_t self,
        std::size_t ndims,
        int32_t ** elements,
        std::size_t * elements_shape,
        int * elements_format,
        int * err_code, char ** err_msg, std::size_t * err_msg_len
) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    try {
        *err_code = 0;
        if (self_p->shape().size() != ndims)
            throw std::runtime_error("Grid does not have a matching number of dimensions.");
        int32_t const * result = self_p->elements<int32_t>();
        *elements = const_cast<int32_t *>(result);

        for (std::size_t i = 0u; i < ndims; ++i)
            elements_shape[i] = self_p->shape()[i];

        *elements_format = (self_p->storage_order() == libmuscle::StorageOrder::last_adjacent);
        return;
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

void LIBMUSCLE_MPI_DataConstRef_elements_int8_(
        std::intptr_t self,
        std::size_t ndims,
        int64_t ** elements,
        std::size_t * elements_shape,
        int * elements_format,
        int * err_code, char ** err_msg, std::size_t * err_msg_len
) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    try {
        *err_code = 0;
        if (self_p->shape().size() != ndims)
            throw std::runtime_error("Grid does not have a matching number of dimensions.");
        int64_t const * result = self_p->elements<int64_t>();
        *elements = const_cast<int64_t *>(result);

        for (std::size_t i = 0u; i < ndims; ++i)
            elements_shape[i] = self_p->shape()[i];

        *elements_format = (self_p->storage_order() == libmuscle::StorageOrder::last_adjacent);
        return;
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

void LIBMUSCLE_MPI_DataConstRef_elements_real4_(
        std::intptr_t self,
        std::size_t ndims,
        float ** elements,
        std::size_t * elements_shape,
        int * elements_format,
        int * err_code, char ** err_msg, std::size_t * err_msg_len
) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    try {
        *err_code = 0;
        if (self_p->shape().size() != ndims)
            throw std::runtime_error("Grid does not have a matching number of dimensions.");
        float const * result = self_p->elements<float>();
        *elements = const_cast<float *>(result);

        for (std::size_t i = 0u; i < ndims; ++i)
            elements_shape[i] = self_p->shape()[i];

        *elements_format = (self_p->storage_order() == libmuscle::StorageOrder::last_adjacent);
        return;
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

void LIBMUSCLE_MPI_DataConstRef_elements_real8_(
        std::intptr_t self,
        std::size_t ndims,
        double ** elements,
        std::size_t * elements_shape,
        int * elements_format,
        int * err_code, char ** err_msg, std::size_t * err_msg_len
) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    try {
        *err_code = 0;
        if (self_p->shape().size() != ndims)
            throw std::runtime_error("Grid does not have a matching number of dimensions.");
        double const * result = self_p->elements<double>();
        *elements = const_cast<double *>(result);

        for (std::size_t i = 0u; i < ndims; ++i)
            elements_shape[i] = self_p->shape()[i];

        *elements_format = (self_p->storage_order() == libmuscle::StorageOrder::last_adjacent);
        return;
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

bool LIBMUSCLE_MPI_DataConstRef_has_indexes_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    try {
        *err_code = 0;
        bool result = self_p->has_indexes();
        return result;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return false;
}

void LIBMUSCLE_MPI_DataConstRef_index_(std::intptr_t self, std::size_t i, char ** ret_val, std::size_t * ret_val_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    try {
        *err_code = 0;
        static std::string result;
        result = self_p->indexes().at(i - 1);
        *ret_val = const_cast<char*>(result.c_str());
        *ret_val_size = result.size();
        return;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

std::intptr_t LIBMUSCLE_MPI_Data_create_nil_() {
    Data * result = new Data();
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_Data_create_logical_(bool value) {
    Data * result = new Data(value);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_Data_create_character_(char * value, std::size_t value_size) {
    std::string value_s(value, value_size);
    Data * result = new Data(value_s);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_Data_create_int1_(char value) {
    Data * result = new Data(value);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_Data_create_int2_(short int value) {
    Data * result = new Data(value);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_Data_create_int4_(int32_t value) {
    Data * result = new Data(value);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_Data_create_int8_(int64_t value) {
    Data * result = new Data(value);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_Data_create_real4_(float value) {
    Data * result = new Data(value);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_Data_create_real8_(double value) {
    Data * result = new Data(value);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_Data_create_settings_(std::intptr_t value) {
    Settings * value_p = reinterpret_cast<Settings *>(value);
    Data * result = new Data(*value_p);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_Data_create_copy_(std::intptr_t value) {
    Data * value_p = reinterpret_cast<Data *>(value);
    Data * result = new Data(*value_p);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_Data_create_grid_logical_a_(bool * data_array, std::size_t * data_array_shape, std::size_t data_array_ndims) {
    std::vector<std::size_t> data_array_shape_v(
            data_array_shape, data_array_shape + data_array_ndims);
    auto data_array_p = const_cast<bool const * const>(data_array);
    Data * result = new Data(Data::grid(data_array_p, data_array_shape_v, {}, libmuscle::StorageOrder::first_adjacent));
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_Data_create_grid_int4_a_(int32_t * data_array, std::size_t * data_array_shape, std::size_t data_array_ndims) {
    std::vector<std::size_t> data_array_shape_v(
            data_array_shape, data_array_shape + data_array_ndims);
    auto data_array_p = const_cast<int32_t const * const>(data_array);
    Data * result = new Data(Data::grid(data_array_p, data_array_shape_v, {}, libmuscle::StorageOrder::first_adjacent));
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_Data_create_grid_int8_a_(int64_t * data_array, std::size_t * data_array_shape, std::size_t data_array_ndims) {
    std::vector<std::size_t> data_array_shape_v(
            data_array_shape, data_array_shape + data_array_ndims);
    auto data_array_p = const_cast<int64_t const * const>(data_array);
    Data * result = new Data(Data::grid(data_array_p, data_array_shape_v, {}, libmuscle::StorageOrder::first_adjacent));
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_Data_create_grid_real4_a_(float * data_array, std::size_t * data_array_shape, std::size_t data_array_ndims) {
    std::vector<std::size_t> data_array_shape_v(
            data_array_shape, data_array_shape + data_array_ndims);
    auto data_array_p = const_cast<float const * const>(data_array);
    Data * result = new Data(Data::grid(data_array_p, data_array_shape_v, {}, libmuscle::StorageOrder::first_adjacent));
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_Data_create_grid_real8_a_(double * data_array, std::size_t * data_array_shape, std::size_t data_array_ndims) {
    std::vector<std::size_t> data_array_shape_v(
            data_array_shape, data_array_shape + data_array_ndims);
    auto data_array_p = const_cast<double const * const>(data_array);
    Data * result = new Data(Data::grid(data_array_p, data_array_shape_v, {}, libmuscle::StorageOrder::first_adjacent));
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_Data_create_grid_logical_n_(
        bool * data_array,
        std::size_t * data_array_shape,
        std::size_t data_array_ndims,
        char * index_name_1, std::size_t index_name_1_size,
        char * index_name_2, std::size_t index_name_2_size,
        char * index_name_3, std::size_t index_name_3_size,
        char * index_name_4, std::size_t index_name_4_size,
        char * index_name_5, std::size_t index_name_5_size,
        char * index_name_6, std::size_t index_name_6_size,
        char * index_name_7, std::size_t index_name_7_size
) {
    std::vector<std::size_t> data_array_shape_v(
            data_array_shape, data_array_shape + data_array_ndims);
    auto data_array_p = const_cast<bool const * const>(data_array);

    std::vector<std::string> names_v;
    names_v.emplace_back(index_name_1, index_name_1_size);
    if (data_array_ndims >= 2u)
        names_v.emplace_back(index_name_2, index_name_2_size);
    if (data_array_ndims >= 3u)
        names_v.emplace_back(index_name_3, index_name_3_size);
    if (data_array_ndims >= 4u)
        names_v.emplace_back(index_name_4, index_name_4_size);
    if (data_array_ndims >= 5u)
        names_v.emplace_back(index_name_5, index_name_5_size);
    if (data_array_ndims >= 6u)
        names_v.emplace_back(index_name_6, index_name_6_size);
    if (data_array_ndims >= 7u)
        names_v.emplace_back(index_name_7, index_name_7_size);

    Data * result = new Data(Data::grid(
            data_array_p, data_array_shape_v,
            names_v, libmuscle::StorageOrder::first_adjacent));
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_Data_create_grid_int4_n_(
        int32_t * data_array,
        std::size_t * data_array_shape,
        std::size_t data_array_ndims,
        char * index_name_1, std::size_t index_name_1_size,
        char * index_name_2, std::size_t index_name_2_size,
        char * index_name_3, std::size_t index_name_3_size,
        char * index_name_4, std::size_t index_name_4_size,
        char * index_name_5, std::size_t index_name_5_size,
        char * index_name_6, std::size_t index_name_6_size,
        char * index_name_7, std::size_t index_name_7_size
) {
    std::vector<std::size_t> data_array_shape_v(
            data_array_shape, data_array_shape + data_array_ndims);
    auto data_array_p = const_cast<int32_t const * const>(data_array);

    std::vector<std::string> names_v;
    names_v.emplace_back(index_name_1, index_name_1_size);
    if (data_array_ndims >= 2u)
        names_v.emplace_back(index_name_2, index_name_2_size);
    if (data_array_ndims >= 3u)
        names_v.emplace_back(index_name_3, index_name_3_size);
    if (data_array_ndims >= 4u)
        names_v.emplace_back(index_name_4, index_name_4_size);
    if (data_array_ndims >= 5u)
        names_v.emplace_back(index_name_5, index_name_5_size);
    if (data_array_ndims >= 6u)
        names_v.emplace_back(index_name_6, index_name_6_size);
    if (data_array_ndims >= 7u)
        names_v.emplace_back(index_name_7, index_name_7_size);

    Data * result = new Data(Data::grid(
            data_array_p, data_array_shape_v,
            names_v, libmuscle::StorageOrder::first_adjacent));
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_Data_create_grid_int8_n_(
        int64_t * data_array,
        std::size_t * data_array_shape,
        std::size_t data_array_ndims,
        char * index_name_1, std::size_t index_name_1_size,
        char * index_name_2, std::size_t index_name_2_size,
        char * index_name_3, std::size_t index_name_3_size,
        char * index_name_4, std::size_t index_name_4_size,
        char * index_name_5, std::size_t index_name_5_size,
        char * index_name_6, std::size_t index_name_6_size,
        char * index_name_7, std::size_t index_name_7_size
) {
    std::vector<std::size_t> data_array_shape_v(
            data_array_shape, data_array_shape + data_array_ndims);
    auto data_array_p = const_cast<int64_t const * const>(data_array);

    std::vector<std::string> names_v;
    names_v.emplace_back(index_name_1, index_name_1_size);
    if (data_array_ndims >= 2u)
        names_v.emplace_back(index_name_2, index_name_2_size);
    if (data_array_ndims >= 3u)
        names_v.emplace_back(index_name_3, index_name_3_size);
    if (data_array_ndims >= 4u)
        names_v.emplace_back(index_name_4, index_name_4_size);
    if (data_array_ndims >= 5u)
        names_v.emplace_back(index_name_5, index_name_5_size);
    if (data_array_ndims >= 6u)
        names_v.emplace_back(index_name_6, index_name_6_size);
    if (data_array_ndims >= 7u)
        names_v.emplace_back(index_name_7, index_name_7_size);

    Data * result = new Data(Data::grid(
            data_array_p, data_array_shape_v,
            names_v, libmuscle::StorageOrder::first_adjacent));
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_Data_create_grid_real4_n_(
        float * data_array,
        std::size_t * data_array_shape,
        std::size_t data_array_ndims,
        char * index_name_1, std::size_t index_name_1_size,
        char * index_name_2, std::size_t index_name_2_size,
        char * index_name_3, std::size_t index_name_3_size,
        char * index_name_4, std::size_t index_name_4_size,
        char * index_name_5, std::size_t index_name_5_size,
        char * index_name_6, std::size_t index_name_6_size,
        char * index_name_7, std::size_t index_name_7_size
) {
    std::vector<std::size_t> data_array_shape_v(
            data_array_shape, data_array_shape + data_array_ndims);
    auto data_array_p = const_cast<float const * const>(data_array);

    std::vector<std::string> names_v;
    names_v.emplace_back(index_name_1, index_name_1_size);
    if (data_array_ndims >= 2u)
        names_v.emplace_back(index_name_2, index_name_2_size);
    if (data_array_ndims >= 3u)
        names_v.emplace_back(index_name_3, index_name_3_size);
    if (data_array_ndims >= 4u)
        names_v.emplace_back(index_name_4, index_name_4_size);
    if (data_array_ndims >= 5u)
        names_v.emplace_back(index_name_5, index_name_5_size);
    if (data_array_ndims >= 6u)
        names_v.emplace_back(index_name_6, index_name_6_size);
    if (data_array_ndims >= 7u)
        names_v.emplace_back(index_name_7, index_name_7_size);

    Data * result = new Data(Data::grid(
            data_array_p, data_array_shape_v,
            names_v, libmuscle::StorageOrder::first_adjacent));
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_Data_create_grid_real8_n_(
        double * data_array,
        std::size_t * data_array_shape,
        std::size_t data_array_ndims,
        char * index_name_1, std::size_t index_name_1_size,
        char * index_name_2, std::size_t index_name_2_size,
        char * index_name_3, std::size_t index_name_3_size,
        char * index_name_4, std::size_t index_name_4_size,
        char * index_name_5, std::size_t index_name_5_size,
        char * index_name_6, std::size_t index_name_6_size,
        char * index_name_7, std::size_t index_name_7_size
) {
    std::vector<std::size_t> data_array_shape_v(
            data_array_shape, data_array_shape + data_array_ndims);
    auto data_array_p = const_cast<double const * const>(data_array);

    std::vector<std::string> names_v;
    names_v.emplace_back(index_name_1, index_name_1_size);
    if (data_array_ndims >= 2u)
        names_v.emplace_back(index_name_2, index_name_2_size);
    if (data_array_ndims >= 3u)
        names_v.emplace_back(index_name_3, index_name_3_size);
    if (data_array_ndims >= 4u)
        names_v.emplace_back(index_name_4, index_name_4_size);
    if (data_array_ndims >= 5u)
        names_v.emplace_back(index_name_5, index_name_5_size);
    if (data_array_ndims >= 6u)
        names_v.emplace_back(index_name_6, index_name_6_size);
    if (data_array_ndims >= 7u)
        names_v.emplace_back(index_name_7, index_name_7_size);

    Data * result = new Data(Data::grid(
            data_array_p, data_array_shape_v,
            names_v, libmuscle::StorageOrder::first_adjacent));
    return reinterpret_cast<std::intptr_t>(result);
}

void LIBMUSCLE_MPI_Data_free_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    delete self_p;
    return;
}

bool LIBMUSCLE_MPI_Data_is_a_logical_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a<bool>();
    return result;
}

bool LIBMUSCLE_MPI_Data_is_a_character_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a<std::string>();
    return result;
}

bool LIBMUSCLE_MPI_Data_is_a_int_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a<int>();
    return result;
}

bool LIBMUSCLE_MPI_Data_is_a_int1_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a<char>();
    return result;
}

bool LIBMUSCLE_MPI_Data_is_a_int2_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a<int16_t>();
    return result;
}

bool LIBMUSCLE_MPI_Data_is_a_int4_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a<int32_t>();
    return result;
}

bool LIBMUSCLE_MPI_Data_is_a_int8_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a<int64_t>();
    return result;
}

bool LIBMUSCLE_MPI_Data_is_a_real4_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a<float>();
    return result;
}

bool LIBMUSCLE_MPI_Data_is_a_real8_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a<double>();
    return result;
}

bool LIBMUSCLE_MPI_Data_is_a_dict_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a_dict();
    return result;
}

bool LIBMUSCLE_MPI_Data_is_a_list_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a_list();
    return result;
}

bool LIBMUSCLE_MPI_Data_is_a_grid_of_logical_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a_grid_of<bool>();
    return result;
}

bool LIBMUSCLE_MPI_Data_is_a_grid_of_real4_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a_grid_of<float>();
    return result;
}

bool LIBMUSCLE_MPI_Data_is_a_grid_of_real8_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a_grid_of<double>();
    return result;
}

bool LIBMUSCLE_MPI_Data_is_a_grid_of_int4_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a_grid_of<int32_t>();
    return result;
}

bool LIBMUSCLE_MPI_Data_is_a_grid_of_int8_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a_grid_of<int64_t>();
    return result;
}

bool LIBMUSCLE_MPI_Data_is_a_byte_array_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a_byte_array();
    return result;
}

bool LIBMUSCLE_MPI_Data_is_nil_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_nil();
    return result;
}

bool LIBMUSCLE_MPI_Data_is_a_settings_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a<Settings>();
    return result;
}

std::size_t LIBMUSCLE_MPI_Data_size_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    std::size_t result = self_p->size();
    return result;
}

bool LIBMUSCLE_MPI_Data_as_logical_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        bool result = self_p->as<bool>();
        return result;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return false;
}

void LIBMUSCLE_MPI_Data_as_character_(std::intptr_t self, char ** ret_val, std::size_t * ret_val_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        static std::string result;
        result = self_p->as<std::string>();
        *ret_val = const_cast<char*>(result.c_str());
        *ret_val_size = result.size();
        return;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

int LIBMUSCLE_MPI_Data_as_int_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        int result = self_p->as<int>();
        return result;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0;
}

char LIBMUSCLE_MPI_Data_as_int1_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        char result = self_p->as<char>();
        return result;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0;
}

short int LIBMUSCLE_MPI_Data_as_int2_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        short int result = self_p->as<int16_t>();
        return result;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0;
}

int32_t LIBMUSCLE_MPI_Data_as_int4_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        int32_t result = self_p->as<int32_t>();
        return result;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0;
}

int64_t LIBMUSCLE_MPI_Data_as_int8_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        int64_t result = self_p->as<int64_t>();
        return result;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0;
}

float LIBMUSCLE_MPI_Data_as_real4_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        float result = self_p->as<float>();
        return result;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0.0;
}

double LIBMUSCLE_MPI_Data_as_real8_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        double result = self_p->as<double>();
        return result;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0.0;
}

std::intptr_t LIBMUSCLE_MPI_Data_as_settings_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        Settings * result = new Settings(self_p->as<Settings>());
        return reinterpret_cast<std::intptr_t>(result);
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0;
}

void LIBMUSCLE_MPI_Data_as_byte_array_(
        std::intptr_t self,
        char ** data, std::size_t * data_size,
        int * err_code, char ** err_msg, std::size_t * err_msg_len
) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        *data = self_p->as_byte_array();
        *data_size = self_p->size();
        return;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg(e.what());
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}
std::intptr_t LIBMUSCLE_MPI_Data_get_item_by_key_(
        std::intptr_t self,
        char * key, std::size_t key_size,
        int * err_code, char ** err_msg, std::size_t * err_msg_len
) {
    Data * self_p = reinterpret_cast<Data *>(self);
    std::string key_s(key, key_size);
    try {
        *err_code = 0;
        Data * result = new Data((*self_p)[key_s]);
        return reinterpret_cast<std::intptr_t>(result);
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0;
}

std::intptr_t LIBMUSCLE_MPI_Data_get_item_by_index_(
        std::intptr_t self,
        std::size_t i,
        int * err_code, char ** err_msg, std::size_t * err_msg_len
) {
        Data * self_p = reinterpret_cast<Data *>(self);
        try {
            *err_code = 0;
            Data * result = new Data((*self_p)[i-1u]);
            return reinterpret_cast<std::intptr_t>(result);
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0;
}

std::size_t LIBMUSCLE_MPI_Data_num_dims_(
        std::intptr_t self,
        int * err_code, char ** err_msg, std::size_t * err_msg_len
) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        return self_p->shape().size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0;
}

void LIBMUSCLE_MPI_Data_shape_(std::intptr_t self, std::size_t ** shp, std::size_t * shp_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        static std::vector<std::size_t> result;
        result = self_p->shape();
        *shp = result.data();
        *shp_size = result.size();
        return;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

void LIBMUSCLE_MPI_Data_elements_logical_(
        std::intptr_t self,
        std::size_t ndims,
        bool ** elements,
        std::size_t * elements_shape,
        int * elements_format,
        int * err_code, char ** err_msg, std::size_t * err_msg_len
) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        if (self_p->shape().size() != ndims)
            throw std::runtime_error("Grid does not have a matching number of dimensions.");
        bool const * result = self_p->elements<bool>();
        *elements = const_cast<bool *>(result);

        for (std::size_t i = 0u; i < ndims; ++i)
            elements_shape[i] = self_p->shape()[i];

        *elements_format = (self_p->storage_order() == libmuscle::StorageOrder::last_adjacent);
        return;
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

void LIBMUSCLE_MPI_Data_elements_int4_(
        std::intptr_t self,
        std::size_t ndims,
        int32_t ** elements,
        std::size_t * elements_shape,
        int * elements_format,
        int * err_code, char ** err_msg, std::size_t * err_msg_len
) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        if (self_p->shape().size() != ndims)
            throw std::runtime_error("Grid does not have a matching number of dimensions.");
        int32_t const * result = self_p->elements<int32_t>();
        *elements = const_cast<int32_t *>(result);

        for (std::size_t i = 0u; i < ndims; ++i)
            elements_shape[i] = self_p->shape()[i];

        *elements_format = (self_p->storage_order() == libmuscle::StorageOrder::last_adjacent);
        return;
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

void LIBMUSCLE_MPI_Data_elements_int8_(
        std::intptr_t self,
        std::size_t ndims,
        int64_t ** elements,
        std::size_t * elements_shape,
        int * elements_format,
        int * err_code, char ** err_msg, std::size_t * err_msg_len
) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        if (self_p->shape().size() != ndims)
            throw std::runtime_error("Grid does not have a matching number of dimensions.");
        int64_t const * result = self_p->elements<int64_t>();
        *elements = const_cast<int64_t *>(result);

        for (std::size_t i = 0u; i < ndims; ++i)
            elements_shape[i] = self_p->shape()[i];

        *elements_format = (self_p->storage_order() == libmuscle::StorageOrder::last_adjacent);
        return;
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

void LIBMUSCLE_MPI_Data_elements_real4_(
        std::intptr_t self,
        std::size_t ndims,
        float ** elements,
        std::size_t * elements_shape,
        int * elements_format,
        int * err_code, char ** err_msg, std::size_t * err_msg_len
) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        if (self_p->shape().size() != ndims)
            throw std::runtime_error("Grid does not have a matching number of dimensions.");
        float const * result = self_p->elements<float>();
        *elements = const_cast<float *>(result);

        for (std::size_t i = 0u; i < ndims; ++i)
            elements_shape[i] = self_p->shape()[i];

        *elements_format = (self_p->storage_order() == libmuscle::StorageOrder::last_adjacent);
        return;
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

void LIBMUSCLE_MPI_Data_elements_real8_(
        std::intptr_t self,
        std::size_t ndims,
        double ** elements,
        std::size_t * elements_shape,
        int * elements_format,
        int * err_code, char ** err_msg, std::size_t * err_msg_len
) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        if (self_p->shape().size() != ndims)
            throw std::runtime_error("Grid does not have a matching number of dimensions.");
        double const * result = self_p->elements<double>();
        *elements = const_cast<double *>(result);

        for (std::size_t i = 0u; i < ndims; ++i)
            elements_shape[i] = self_p->shape()[i];

        *elements_format = (self_p->storage_order() == libmuscle::StorageOrder::last_adjacent);
        return;
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

bool LIBMUSCLE_MPI_Data_has_indexes_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        bool result = self_p->has_indexes();
        return result;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return false;
}

void LIBMUSCLE_MPI_Data_index_(std::intptr_t self, std::size_t i, char ** ret_val, std::size_t * ret_val_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        static std::string result;
        result = self_p->indexes().at(i - 1);
        *ret_val = const_cast<char*>(result.c_str());
        *ret_val_size = result.size();
        return;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

std::intptr_t LIBMUSCLE_MPI_Data_create_dict_() {
    Data * result = new Data(Data::dict());
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_Data_create_list_() {
    Data * result = new Data(Data::list());
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_Data_create_nils_(std::size_t size) {
    Data * result = new Data(Data::nils(size));
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_Data_create_byte_array_empty_(std::size_t size) {
    Data * result = new Data(Data::byte_array(size));
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_Data_create_byte_array_from_buf_(
       char * buf, std::size_t buf_size
) {
   Data * result = new Data(Data::byte_array(buf, buf_size));
   return reinterpret_cast<std::intptr_t>(result);
}

void LIBMUSCLE_MPI_Data_set_logical_(std::intptr_t self, bool value) {
    Data * self_p = reinterpret_cast<Data *>(self);
    *self_p = value;
    return;
}

void LIBMUSCLE_MPI_Data_set_character_(std::intptr_t self, char * value, std::size_t value_size) {
    Data * self_p = reinterpret_cast<Data *>(self);
    std::string value_s(value, value_size);
    *self_p = value_s;
    return;
}

void LIBMUSCLE_MPI_Data_set_int1_(std::intptr_t self, char value) {
    Data * self_p = reinterpret_cast<Data *>(self);
    *self_p = value;
    return;
}

void LIBMUSCLE_MPI_Data_set_int2_(std::intptr_t self, short int value) {
    Data * self_p = reinterpret_cast<Data *>(self);
    *self_p = value;
    return;
}

void LIBMUSCLE_MPI_Data_set_int4_(std::intptr_t self, int32_t value) {
    Data * self_p = reinterpret_cast<Data *>(self);
    *self_p = value;
    return;
}

void LIBMUSCLE_MPI_Data_set_int8_(std::intptr_t self, int64_t value) {
    Data * self_p = reinterpret_cast<Data *>(self);
    *self_p = value;
    return;
}

void LIBMUSCLE_MPI_Data_set_real4_(std::intptr_t self, float value) {
    Data * self_p = reinterpret_cast<Data *>(self);
    *self_p = value;
    return;
}

void LIBMUSCLE_MPI_Data_set_real8_(std::intptr_t self, double value) {
    Data * self_p = reinterpret_cast<Data *>(self);
    *self_p = value;
    return;
}

void LIBMUSCLE_MPI_Data_set_data_(std::intptr_t self, std::intptr_t value) {
    Data * self_p = reinterpret_cast<Data *>(self);
    Data * value_p = reinterpret_cast<Data *>(value);
    *self_p = *value_p;
    return;
}

void LIBMUSCLE_MPI_Data_set_nil_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    *self_p = Data();
}

void LIBMUSCLE_MPI_Data_set_item_key_logical_(std::intptr_t self, char * key, std::size_t key_size, bool value, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    std::string key_s(key, key_size);
    try {
        *err_code = 0;
        (*self_p)[key_s] = value;
        return;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

void LIBMUSCLE_MPI_Data_set_item_key_character_(std::intptr_t self, char * key, std::size_t key_size, char * value, std::size_t value_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    std::string key_s(key, key_size);
    std::string value_s(value, value_size);
    try {
        *err_code = 0;
        (*self_p)[key_s] = value_s;
        return;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

void LIBMUSCLE_MPI_Data_set_item_key_int1_(std::intptr_t self, char * key, std::size_t key_size, char value, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    std::string key_s(key, key_size);
    try {
        *err_code = 0;
        (*self_p)[key_s] = value;
        return;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

void LIBMUSCLE_MPI_Data_set_item_key_int2_(std::intptr_t self, char * key, std::size_t key_size, short int value, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    std::string key_s(key, key_size);
    try {
        *err_code = 0;
        (*self_p)[key_s] = value;
        return;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

void LIBMUSCLE_MPI_Data_set_item_key_int4_(std::intptr_t self, char * key, std::size_t key_size, int value, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    std::string key_s(key, key_size);
    try {
        *err_code = 0;
        (*self_p)[key_s] = value;
        return;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

void LIBMUSCLE_MPI_Data_set_item_key_int8_(std::intptr_t self, char * key, std::size_t key_size, int64_t value, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    std::string key_s(key, key_size);
    try {
        *err_code = 0;
        (*self_p)[key_s] = value;
        return;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

void LIBMUSCLE_MPI_Data_set_item_key_real4_(std::intptr_t self, char * key, std::size_t key_size, float value, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    std::string key_s(key, key_size);
    try {
        *err_code = 0;
        (*self_p)[key_s] = value;
        return;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

void LIBMUSCLE_MPI_Data_set_item_key_real8_(std::intptr_t self, char * key, std::size_t key_size, double value, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    std::string key_s(key, key_size);
    try {
        *err_code = 0;
        (*self_p)[key_s] = value;
        return;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

void LIBMUSCLE_MPI_Data_set_item_key_data_(std::intptr_t self, char * key, std::size_t key_size, std::intptr_t value, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    std::string key_s(key, key_size);
    Data * value_p = reinterpret_cast<Data *>(value);
    try {
        *err_code = 0;
        (*self_p)[key_s] = *value_p;
        return;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

void LIBMUSCLE_MPI_Data_set_item_index_logical_(std::intptr_t self, std::size_t i, bool value, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        (*self_p)[i - 1u] = value;
        return;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

void LIBMUSCLE_MPI_Data_set_item_index_character_(std::intptr_t self, std::size_t i, char * value, std::size_t value_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    std::string value_s(value, value_size);
    try {
        *err_code = 0;
        (*self_p)[i - 1u] = value_s;
        return;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

void LIBMUSCLE_MPI_Data_set_item_index_int1_(std::intptr_t self, std::size_t i, char value, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        (*self_p)[i - 1u] = value;
        return;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

void LIBMUSCLE_MPI_Data_set_item_index_int2_(std::intptr_t self, std::size_t i, short int value, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        (*self_p)[i - 1u] = value;
        return;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

void LIBMUSCLE_MPI_Data_set_item_index_int4_(std::intptr_t self, std::size_t i, int value, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        (*self_p)[i - 1u] = value;
        return;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

void LIBMUSCLE_MPI_Data_set_item_index_int8_(std::intptr_t self, std::size_t i, int64_t value, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        (*self_p)[i - 1u] = value;
        return;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

void LIBMUSCLE_MPI_Data_set_item_index_real4_(std::intptr_t self, std::size_t i, float value, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        (*self_p)[i - 1u] = value;
        return;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

void LIBMUSCLE_MPI_Data_set_item_index_real8_(std::intptr_t self, std::size_t i, double value, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        (*self_p)[i - 1u] = value;
        return;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

void LIBMUSCLE_MPI_Data_set_item_index_data_(std::intptr_t self, std::size_t i, std::intptr_t value, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    Data * value_p = reinterpret_cast<Data *>(value);
    try {
        *err_code = 0;
        (*self_p)[i - 1u] = *value_p;
        return;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

void LIBMUSCLE_MPI_Data_key_(
        std::intptr_t self, std::size_t i,
        char ** ret_val, std::size_t * ret_val_size,
        int * err_code,
        char ** err_msg, std::size_t * err_msg_len
) {
    try {
        *err_code = 0;
        Data * self_p = reinterpret_cast<Data *>(self);
        static std::string result;
        result = self_p->key(i - 1);
        *ret_val = const_cast<char*>(result.c_str());
        *ret_val_size = result.size();
        return;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

std::intptr_t LIBMUSCLE_MPI_Data_value_(
        std::intptr_t self, std::size_t i,
        int * err_code,
        char ** err_msg, std::size_t * err_msg_len
) {
    try {
        *err_code = 0;
        Data * self_p = reinterpret_cast<Data *>(self);
        Data * result = new Data(self_p->value(i - 1));
        return reinterpret_cast<std::intptr_t>(result);
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0;
}

std::intptr_t LIBMUSCLE_MPI_PortsDescription_create_() {
    PortsDescription * result = new PortsDescription();
    return reinterpret_cast<std::intptr_t>(result);
}

void LIBMUSCLE_MPI_PortsDescription_free_(std::intptr_t self) {
    PortsDescription * self_p = reinterpret_cast<PortsDescription *>(self);
    delete self_p;
    return;
}

void LIBMUSCLE_MPI_PortsDescription_add_(std::intptr_t self, int op, char * port, std::size_t port_size) {
    PortsDescription * self_p = reinterpret_cast<PortsDescription *>(self);
    Operator op_e = static_cast<Operator>(op);
    std::string port_s(port, port_size);
    (*self_p)[op_e].push_back(port_s);
    return;
}

std::size_t LIBMUSCLE_MPI_PortsDescription_num_ports_(std::intptr_t self, int op) {
    PortsDescription * self_p = reinterpret_cast<PortsDescription *>(self);
    Operator op_e = static_cast<Operator>(op);
    std::size_t result = 0u;
    if (self_p->count(op_e))
        result = (*self_p)[op_e].size();
    return result;
}

void LIBMUSCLE_MPI_PortsDescription_get_(std::intptr_t self, int op, std::size_t i, char ** ret_val, std::size_t * ret_val_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    PortsDescription * self_p = reinterpret_cast<PortsDescription *>(self);
    Operator op_e = static_cast<Operator>(op);
    try {
        *err_code = 0;
        static std::string result;
        result = (*self_p)[op_e].at(i - 1);
        *ret_val = const_cast<char*>(result.c_str());
        *ret_val_size = result.size();
        return;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

std::intptr_t LIBMUSCLE_MPI_Message_create_t_(double timestamp) {
    Message * result = new Message(timestamp);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_Message_create_td_(double timestamp, std::intptr_t data) {
    Data * data_p = reinterpret_cast<Data *>(data);
    Message * result = new Message(timestamp, *data_p);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_Message_create_tnd_(double timestamp, double next_timestamp, std::intptr_t data) {
    Data * data_p = reinterpret_cast<Data *>(data);
    Message * result = new Message(timestamp, next_timestamp, *data_p);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_Message_create_tds_(double timestamp, std::intptr_t data, std::intptr_t settings) {
    Data * data_p = reinterpret_cast<Data *>(data);
    Settings * settings_p = reinterpret_cast<Settings *>(settings);
    Message * result = new Message(timestamp, *data_p, *settings_p);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_MPI_Message_create_tnds_(double timestamp, double next_timestamp, std::intptr_t data, std::intptr_t settings) {
    Data * data_p = reinterpret_cast<Data *>(data);
    Settings * settings_p = reinterpret_cast<Settings *>(settings);
    Message * result = new Message(timestamp, next_timestamp, *data_p, *settings_p);
    return reinterpret_cast<std::intptr_t>(result);
}

void LIBMUSCLE_MPI_Message_free_(std::intptr_t self) {
    Message * self_p = reinterpret_cast<Message *>(self);
    delete self_p;
    return;
}

double LIBMUSCLE_MPI_Message_timestamp_(std::intptr_t self) {
    Message * self_p = reinterpret_cast<Message *>(self);
    double result = self_p->timestamp();
    return result;
}

void LIBMUSCLE_MPI_Message_set_timestamp_(std::intptr_t self, double timestamp) {
    Message * self_p = reinterpret_cast<Message *>(self);
    self_p->set_timestamp(timestamp);
    return;
}

bool LIBMUSCLE_MPI_Message_has_next_timestamp_(std::intptr_t self) {
    Message * self_p = reinterpret_cast<Message *>(self);
    bool result = self_p->has_next_timestamp();
    return result;
}

double LIBMUSCLE_MPI_Message_next_timestamp_(std::intptr_t self) {
    Message * self_p = reinterpret_cast<Message *>(self);
    double result = self_p->next_timestamp();
    return result;
}

void LIBMUSCLE_MPI_Message_set_next_timestamp_(std::intptr_t self, double next_timestamp) {
    Message * self_p = reinterpret_cast<Message *>(self);
    self_p->set_next_timestamp(next_timestamp);
    return;
}

void LIBMUSCLE_MPI_Message_unset_next_timestamp_(std::intptr_t self) {
    Message * self_p = reinterpret_cast<Message *>(self);
    self_p->unset_next_timestamp();
    return;
}

std::intptr_t LIBMUSCLE_MPI_Message_get_data_(std::intptr_t self) {
    Message * self_p = reinterpret_cast<Message *>(self);
    DataConstRef * result = new DataConstRef(self_p->data());
    return reinterpret_cast<std::intptr_t>(result);
}

void LIBMUSCLE_MPI_Message_set_data_d_(std::intptr_t self, std::intptr_t data) {
    Message * self_p = reinterpret_cast<Message *>(self);
    Data * data_p = reinterpret_cast<Data *>(data);
    self_p->set_data(*data_p);
    return;
}

void LIBMUSCLE_MPI_Message_set_data_dcr_(std::intptr_t self, std::intptr_t data) {
    Message * self_p = reinterpret_cast<Message *>(self);
    DataConstRef * data_p = reinterpret_cast<DataConstRef *>(data);
    self_p->set_data(*data_p);
    return;
}

bool LIBMUSCLE_MPI_Message_has_settings_(std::intptr_t self) {
    Message * self_p = reinterpret_cast<Message *>(self);
    bool result = self_p->has_settings();
    return result;
}

std::intptr_t LIBMUSCLE_MPI_Message_get_settings_(std::intptr_t self) {
    Message * self_p = reinterpret_cast<Message *>(self);
    Settings * result = new Settings(self_p->settings());
    return reinterpret_cast<std::intptr_t>(result);
}

void LIBMUSCLE_MPI_Message_set_settings_(std::intptr_t self, std::intptr_t settings) {
    Message * self_p = reinterpret_cast<Message *>(self);
    Settings * settings_p = reinterpret_cast<Settings *>(settings);
    self_p->set_settings(*settings_p);
    return;
}

void LIBMUSCLE_MPI_Message_unset_settings_(std::intptr_t self) {
    Message * self_p = reinterpret_cast<Message *>(self);
    self_p->unset_settings();
    return;
}

std::intptr_t LIBMUSCLE_MPI_Instance_create_(
        std::intptr_t cla,
        std::intptr_t ports,
        int flags,
        int communicator, int root
) {
    CmdLineArgs * cla_p = reinterpret_cast<CmdLineArgs *>(cla);
    InstanceFlags flags_o = static_cast<InstanceFlags>(flags);
    MPI_Comm communicator_m = MPI_Comm_f2c(communicator);
    Instance * result;
    if (ports == 0) {
        result = new Instance(
            cla_p->argc(), cla_p->argv(), flags_o, communicator_m, root);
    } else {
        PortsDescription * ports_p = reinterpret_cast<PortsDescription *>(ports);
        result = new Instance(
            cla_p->argc(), cla_p->argv(), *ports_p, flags_o, communicator_m, root);
    }
    return reinterpret_cast<std::intptr_t>(result);
}

void LIBMUSCLE_MPI_Instance_free_(std::intptr_t self) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    delete self_p;
    return;
}

bool LIBMUSCLE_MPI_Instance_reuse_instance_(std::intptr_t self) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    bool result = self_p->reuse_instance();
    return result;
}

void LIBMUSCLE_MPI_Instance_error_shutdown_(std::intptr_t self, char * message, std::size_t message_size) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    std::string message_s(message, message_size);
    self_p->error_shutdown(message_s);
    return;
}

bool LIBMUSCLE_MPI_Instance_is_setting_a_character_(std::intptr_t self, char * name, std::size_t name_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    std::string name_s(name, name_size);
    try {
        *err_code = 0;
        bool result = self_p->get_setting(name_s).is_a<std::string>();
        return result;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return false;
}

bool LIBMUSCLE_MPI_Instance_is_setting_a_int8_(std::intptr_t self, char * name, std::size_t name_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    std::string name_s(name, name_size);
    try {
        *err_code = 0;
        bool result = self_p->get_setting(name_s).is_a<int64_t>();
        return result;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return false;
}

bool LIBMUSCLE_MPI_Instance_is_setting_a_real8_(std::intptr_t self, char * name, std::size_t name_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    std::string name_s(name, name_size);
    try {
        *err_code = 0;
        bool result = self_p->get_setting(name_s).is_a<double>();
        return result;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return false;
}

bool LIBMUSCLE_MPI_Instance_is_setting_a_logical_(std::intptr_t self, char * name, std::size_t name_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    std::string name_s(name, name_size);
    try {
        *err_code = 0;
        bool result = self_p->get_setting(name_s).is_a<bool>();
        return result;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return false;
}

bool LIBMUSCLE_MPI_Instance_is_setting_a_real8array_(std::intptr_t self, char * name, std::size_t name_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    std::string name_s(name, name_size);
    try {
        *err_code = 0;
        bool result = self_p->get_setting(name_s).is_a<std::vector<double>>();
        return result;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return false;
}

bool LIBMUSCLE_MPI_Instance_is_setting_a_real8array2_(std::intptr_t self, char * name, std::size_t name_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    std::string name_s(name, name_size);
    try {
        *err_code = 0;
        bool result = self_p->get_setting(name_s).is_a<std::vector<std::vector<double>>>();
        return result;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return false;
}

void LIBMUSCLE_MPI_Instance_get_setting_as_character_(std::intptr_t self, char * name, std::size_t name_size, char ** ret_val, std::size_t * ret_val_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    std::string name_s(name, name_size);
    try {
        *err_code = 0;
        static std::string result;
        result = self_p->get_setting_as<std::string>(name_s);
        *ret_val = const_cast<char*>(result.c_str());
        *ret_val_size = result.size();
        return;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

int64_t LIBMUSCLE_MPI_Instance_get_setting_as_int8_(std::intptr_t self, char * name, std::size_t name_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    std::string name_s(name, name_size);
    try {
        *err_code = 0;
        int64_t result = self_p->get_setting_as<int64_t>(name_s);
        return result;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0;
}

double LIBMUSCLE_MPI_Instance_get_setting_as_real8_(std::intptr_t self, char * name, std::size_t name_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    std::string name_s(name, name_size);
    try {
        *err_code = 0;
        double result = self_p->get_setting_as<double>(name_s);
        return result;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0.0;
}

bool LIBMUSCLE_MPI_Instance_get_setting_as_logical_(std::intptr_t self, char * name, std::size_t name_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    std::string name_s(name, name_size);
    try {
        *err_code = 0;
        bool result = self_p->get_setting_as<bool>(name_s);
        return result;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return false;
}

void LIBMUSCLE_MPI_Instance_get_setting_as_real8array_(std::intptr_t self, char * name, std::size_t name_size, double ** value, std::size_t * value_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    std::string name_s(name, name_size);
    try {
        *err_code = 0;
        static std::vector<double> result;
        result = self_p->get_setting_as<std::vector<double>>(name_s);
        *value = result.data();
        *value_size = result.size();
        return;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

void LIBMUSCLE_MPI_Instance_get_setting_as_real8array2_(std::intptr_t self, char * name, std::size_t name_size, double ** value, std::size_t * value_shape, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    std::string name_s(name, name_size);
    try {
        *err_code = 0;
        std::vector<std::vector<double>> result = self_p->get_setting_as<std::vector<std::vector<double>>>(name_s);
        std::size_t max_len = 0u;
        for (auto const & v : result)
            max_len = std::max(max_len, v.size());

        static std::vector<double> ret;
        ret.resize(result.size() * max_len);
        for (std::size_t i = 0; i < result.size(); ++i)
            for (std::size_t j = 0; j < result[i].size(); ++j)
                ret[j * result.size() + i] = result[i][j];

        *value = ret.data();
        value_shape[0] = result.size();
        value_shape[1] = max_len;
        return;
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
}

void LIBMUSCLE_MPI_Instance_list_settings_(std::intptr_t self, char ** value, std::size_t * value_shape) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    std::vector<std::string> result = self_p->list_settings();
    std::size_t max_len = 0u;
    for (auto const & v : result)
        max_len = std::max(max_len, v.size());

    static std::string ret;
    ret.resize(result.size() * max_len, ' ');
    for (std::size_t i = 0; i < result.size(); ++i)
        for (std::size_t j = 0; j < result[i].size(); ++j)
            ret[j * result.size() + i] = result[i][j];

    *value = const_cast<char*>(ret.c_str());
    value_shape[0] = result.size();
    value_shape[1] = max_len;
    return;
}

std::intptr_t LIBMUSCLE_MPI_Instance_list_ports_(std::intptr_t self) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    PortsDescription * result = new PortsDescription(self_p->list_ports());
    return reinterpret_cast<std::intptr_t>(result);
}

bool LIBMUSCLE_MPI_Instance_is_connected_(std::intptr_t self, char * port, std::size_t port_size) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    std::string port_s(port, port_size);
    bool result = self_p->is_connected(port_s);
    return result;
}

bool LIBMUSCLE_MPI_Instance_is_vector_port_(std::intptr_t self, char * port, std::size_t port_size) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    std::string port_s(port, port_size);
    bool result = self_p->is_vector_port(port_s);
    return result;
}

bool LIBMUSCLE_MPI_Instance_is_resizable_(std::intptr_t self, char * port, std::size_t port_size) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    std::string port_s(port, port_size);
    bool result = self_p->is_resizable(port_s);
    return result;
}

int LIBMUSCLE_MPI_Instance_get_port_length_(std::intptr_t self, char * port, std::size_t port_size) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    std::string port_s(port, port_size);
    int result = self_p->get_port_length(port_s);
    return result;
}

void LIBMUSCLE_MPI_Instance_set_port_length_(std::intptr_t self, char * port, std::size_t port_size, int length) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    std::string port_s(port, port_size);
    self_p->set_port_length(port_s, length);
    return;
}

void LIBMUSCLE_MPI_Instance_send_pm_(std::intptr_t self, char * port_name, std::size_t port_name_size, std::intptr_t message) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    std::string port_name_s(port_name, port_name_size);
    Message * message_p = reinterpret_cast<Message *>(message);
    self_p->send(port_name_s, *message_p);
    return;
}

void LIBMUSCLE_MPI_Instance_send_pms_(std::intptr_t self, char * port_name, std::size_t port_name_size, std::intptr_t message, int slot) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    std::string port_name_s(port_name, port_name_size);
    Message * message_p = reinterpret_cast<Message *>(message);
    self_p->send(port_name_s, *message_p, slot);
    return;
}

std::intptr_t LIBMUSCLE_MPI_Instance_receive_p_(std::intptr_t self, char * port_name, std::size_t port_name_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    std::string port_name_s(port_name, port_name_size);
    try {
        *err_code = 0;
        Message * result = new Message(self_p->receive(port_name_s));
        return reinterpret_cast<std::intptr_t>(result);
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0;
}

std::intptr_t LIBMUSCLE_MPI_Instance_receive_pd_(std::intptr_t self, char * port_name, std::size_t port_name_size, std::intptr_t default_msg, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    std::string port_name_s(port_name, port_name_size);
    Message * default_msg_p = reinterpret_cast<Message *>(default_msg);
    try {
        *err_code = 0;
        Message * result = new Message(self_p->receive(port_name_s, *default_msg_p));
        return reinterpret_cast<std::intptr_t>(result);
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0;
}

std::intptr_t LIBMUSCLE_MPI_Instance_receive_ps_(std::intptr_t self, char * port_name, std::size_t port_name_size, int slot, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    std::string port_name_s(port_name, port_name_size);
    try {
        *err_code = 0;
        Message * result = new Message(self_p->receive(port_name_s, slot));
        return reinterpret_cast<std::intptr_t>(result);
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0;
}

std::intptr_t LIBMUSCLE_MPI_Instance_receive_psd_(std::intptr_t self, char * port_name, std::size_t port_name_size, int slot, std::intptr_t default_message, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    std::string port_name_s(port_name, port_name_size);
    Message * default_message_p = reinterpret_cast<Message *>(default_message);
    try {
        *err_code = 0;
        Message * result = new Message(self_p->receive(port_name_s, slot, *default_message_p));
        return reinterpret_cast<std::intptr_t>(result);
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0;
}

std::intptr_t LIBMUSCLE_MPI_Instance_receive_with_settings_p_(std::intptr_t self, char * port_name, std::size_t port_name_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    std::string port_name_s(port_name, port_name_size);
    try {
        *err_code = 0;
        Message * result = new Message(self_p->receive_with_settings(port_name_s));
        return reinterpret_cast<std::intptr_t>(result);
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0;
}

std::intptr_t LIBMUSCLE_MPI_Instance_receive_with_settings_pd_(std::intptr_t self, char * port_name, std::size_t port_name_size, std::intptr_t default_msg, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    std::string port_name_s(port_name, port_name_size);
    Message * default_msg_p = reinterpret_cast<Message *>(default_msg);
    try {
        *err_code = 0;
        Message * result = new Message(self_p->receive_with_settings(port_name_s, *default_msg_p));
        return reinterpret_cast<std::intptr_t>(result);
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0;
}

std::intptr_t LIBMUSCLE_MPI_Instance_receive_with_settings_ps_(std::intptr_t self, char * port_name, std::size_t port_name_size, int slot, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    std::string port_name_s(port_name, port_name_size);
    try {
        *err_code = 0;
        Message * result = new Message(self_p->receive_with_settings(port_name_s, slot));
        return reinterpret_cast<std::intptr_t>(result);
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0;
}

std::intptr_t LIBMUSCLE_MPI_Instance_receive_with_settings_psd_(std::intptr_t self, char * port_name, std::size_t port_name_size, int slot, std::intptr_t default_msg, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    std::string port_name_s(port_name, port_name_size);
    Message * default_msg_p = reinterpret_cast<Message *>(default_msg);
    try {
        *err_code = 0;
        Message * result = new Message(self_p->receive_with_settings(port_name_s, slot, *default_msg_p));
        return reinterpret_cast<std::intptr_t>(result);
    }
    catch (std::domain_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::out_of_range const & e) {
        *err_code = 2;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::logic_error const & e) {
        *err_code = 3;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::runtime_error const & e) {
        *err_code = 4;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::bad_cast const & e) {
        *err_code = 5;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    return 0;
}

bool LIBMUSCLE_MPI_Instance_resuming_(std::intptr_t self) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    bool result = self_p->resuming();
    return result;
}

bool LIBMUSCLE_MPI_Instance_should_init_(std::intptr_t self) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    bool result = self_p->should_init();
    return result;
}

std::intptr_t LIBMUSCLE_MPI_Instance_load_snapshot_(std::intptr_t self) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    Message * result = new Message(self_p->load_snapshot());
    return reinterpret_cast<std::intptr_t>(result);
}

bool LIBMUSCLE_MPI_Instance_should_save_snapshot_(std::intptr_t self, double timestamp) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    bool result = self_p->should_save_snapshot(timestamp);
    return result;
}

void LIBMUSCLE_MPI_Instance_save_snapshot_(std::intptr_t self, std::intptr_t message) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    Message * message_p = reinterpret_cast<Message *>(message);
    self_p->save_snapshot(*message_p);
    return;
}

bool LIBMUSCLE_MPI_Instance_should_save_final_snapshot_(std::intptr_t self) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    bool result = self_p->should_save_final_snapshot();
    return result;
}

void LIBMUSCLE_MPI_Instance_save_final_snapshot_(std::intptr_t self, std::intptr_t message) {
    Instance * self_p = reinterpret_cast<Instance *>(self);
    Message * message_p = reinterpret_cast<Message *>(message);
    self_p->save_final_snapshot(*message_p);
    return;
}

std::intptr_t LIBMUSCLE_MPI_IMPL_BINDINGS_CmdLineArgs_create_(int count) {
    CmdLineArgs * result = new CmdLineArgs(count);
    return reinterpret_cast<std::intptr_t>(result);
}

void LIBMUSCLE_MPI_IMPL_BINDINGS_CmdLineArgs_free_(std::intptr_t self) {
    CmdLineArgs * self_p = reinterpret_cast<CmdLineArgs *>(self);
    delete self_p;
    return;
}

void LIBMUSCLE_MPI_IMPL_BINDINGS_CmdLineArgs_set_arg_(std::intptr_t self, int i, char * arg, std::size_t arg_size) {
    CmdLineArgs * self_p = reinterpret_cast<CmdLineArgs *>(self);
    std::string arg_s(arg, arg_size);
    self_p->set_arg(i, arg_s);
    return;
}

}


