// This is generated code. If it's broken, then you should
// fix the generation script, not this file.


#include <libmuscle/libmuscle.hpp>
#include <libmuscle/bindings/cmdlineargs.hpp>
#include <ymmsl/ymmsl.hpp>
#include <stdexcept>


using libmuscle::DataConstRef;
using libmuscle::Data;
using libmuscle::Message;
using libmuscle::impl::bindings::CmdLineArgs;
using ymmsl::Settings;


extern "C" {

std::intptr_t LIBMUSCLE_DataConstRef_create_nil_() {
    DataConstRef * result = new DataConstRef();
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_DataConstRef_create_logical_(int value) {
    DataConstRef * result = new DataConstRef(value != 0);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_DataConstRef_create_character_(char * value, std::size_t value_size) {
    std::string value_s(value, value_size);
    DataConstRef * result = new DataConstRef(value_s);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_DataConstRef_create_int1_(char value) {
    DataConstRef * result = new DataConstRef(value);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_DataConstRef_create_int2_(short int value) {
    DataConstRef * result = new DataConstRef(value);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_DataConstRef_create_int4_(int32_t value) {
    DataConstRef * result = new DataConstRef(value);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_DataConstRef_create_int8_(int64_t value) {
    DataConstRef * result = new DataConstRef(value);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_DataConstRef_create_real4_(float value) {
    DataConstRef * result = new DataConstRef(value);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_DataConstRef_create_real8_(double value) {
    DataConstRef * result = new DataConstRef(value);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_DataConstRef_create_settings_(std::intptr_t value) {
    Settings * value_p = reinterpret_cast<Settings *>(value);
    DataConstRef * result = new DataConstRef(*value_p);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_DataConstRef_create_copy_(std::intptr_t value) {
    DataConstRef * value_p = reinterpret_cast<DataConstRef *>(value);
    DataConstRef * result = new DataConstRef(*value_p);
    return reinterpret_cast<std::intptr_t>(result);
}

void LIBMUSCLE_DataConstRef_free_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    delete self_p;
    return;
}

int LIBMUSCLE_DataConstRef_is_a_logical_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_a<bool>();
    return result ? 1 : 0;
}

int LIBMUSCLE_DataConstRef_is_a_character_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_a<std::string>();
    return result ? 1 : 0;
}

int LIBMUSCLE_DataConstRef_is_a_int_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_a<int>();
    return result ? 1 : 0;
}

int LIBMUSCLE_DataConstRef_is_a_int1_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_a<char>();
    return result ? 1 : 0;
}

int LIBMUSCLE_DataConstRef_is_a_int2_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_a<int16_t>();
    return result ? 1 : 0;
}

int LIBMUSCLE_DataConstRef_is_a_int4_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_a<int32_t>();
    return result ? 1 : 0;
}

int LIBMUSCLE_DataConstRef_is_a_int8_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_a<int64_t>();
    return result ? 1 : 0;
}

int LIBMUSCLE_DataConstRef_is_a_real4_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_a<float>();
    return result ? 1 : 0;
}

int LIBMUSCLE_DataConstRef_is_a_real8_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_a<double>();
    return result ? 1 : 0;
}

int LIBMUSCLE_DataConstRef_is_a_dict_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_a_dict();
    return result ? 1 : 0;
}

int LIBMUSCLE_DataConstRef_is_a_list_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_a_list();
    return result ? 1 : 0;
}

int LIBMUSCLE_DataConstRef_is_a_byte_array_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_a_byte_array();
    return result ? 1 : 0;
}

int LIBMUSCLE_DataConstRef_is_nil_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_nil();
    return result ? 1 : 0;
}

int LIBMUSCLE_DataConstRef_is_a_settings_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    bool result = self_p->is_a<Settings>();
    return result ? 1 : 0;
}

std::size_t LIBMUSCLE_DataConstRef_size_(std::intptr_t self) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    std::size_t result = self_p->size();
    return result;
}

int LIBMUSCLE_DataConstRef_as_logical_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    try {
        *err_code = 0;
        bool result = self_p->as<bool>();
        return result ? 1 : 0;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

void LIBMUSCLE_DataConstRef_as_character_(std::intptr_t self, char ** ret_val, std::size_t * ret_val_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    try {
        *err_code = 0;
        static std::string result;
        result = self_p->as<std::string>();
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
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

int LIBMUSCLE_DataConstRef_as_int_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    try {
        *err_code = 0;
        int result = self_p->as<int>();
        return result;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

char LIBMUSCLE_DataConstRef_as_int1_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    try {
        *err_code = 0;
        char result = self_p->as<char>();
        return result;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

short int LIBMUSCLE_DataConstRef_as_int2_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    try {
        *err_code = 0;
        short int result = self_p->as<int16_t>();
        return result;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

int32_t LIBMUSCLE_DataConstRef_as_int4_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    try {
        *err_code = 0;
        int32_t result = self_p->as<int32_t>();
        return result;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

int64_t LIBMUSCLE_DataConstRef_as_int8_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    try {
        *err_code = 0;
        int64_t result = self_p->as<int64_t>();
        return result;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

float LIBMUSCLE_DataConstRef_as_real4_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    try {
        *err_code = 0;
        float result = self_p->as<float>();
        return result;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

double LIBMUSCLE_DataConstRef_as_real8_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    try {
        *err_code = 0;
        double result = self_p->as<double>();
        return result;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

std::intptr_t LIBMUSCLE_DataConstRef_as_settings_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    DataConstRef * self_p = reinterpret_cast<DataConstRef *>(self);
    try {
        *err_code = 0;
        Settings * result = new Settings(self_p->as<Settings>());
        return reinterpret_cast<std::intptr_t>(result);
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

void LIBMUSCLE_DataConstRef_as_byte_array_(
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
std::intptr_t LIBMUSCLE_DataConstRef_get_item_by_key_(
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
}

std::intptr_t LIBMUSCLE_DataConstRef_get_item_by_index_(
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
}

std::intptr_t LIBMUSCLE_Data_create_nil_() {
    Data * result = new Data();
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_Data_create_logical_(int value) {
    Data * result = new Data(value != 0);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_Data_create_character_(char * value, std::size_t value_size) {
    std::string value_s(value, value_size);
    Data * result = new Data(value_s);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_Data_create_int1_(char value) {
    Data * result = new Data(value);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_Data_create_int2_(short int value) {
    Data * result = new Data(value);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_Data_create_int4_(int32_t value) {
    Data * result = new Data(value);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_Data_create_int8_(int64_t value) {
    Data * result = new Data(value);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_Data_create_real4_(float value) {
    Data * result = new Data(value);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_Data_create_real8_(double value) {
    Data * result = new Data(value);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_Data_create_settings_(std::intptr_t value) {
    Settings * value_p = reinterpret_cast<Settings *>(value);
    Data * result = new Data(*value_p);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_Data_create_copy_(std::intptr_t value) {
    Data * value_p = reinterpret_cast<Data *>(value);
    Data * result = new Data(*value_p);
    return reinterpret_cast<std::intptr_t>(result);
}

void LIBMUSCLE_Data_free_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    delete self_p;
    return;
}

int LIBMUSCLE_Data_is_a_logical_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a<bool>();
    return result ? 1 : 0;
}

int LIBMUSCLE_Data_is_a_character_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a<std::string>();
    return result ? 1 : 0;
}

int LIBMUSCLE_Data_is_a_int_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a<int>();
    return result ? 1 : 0;
}

int LIBMUSCLE_Data_is_a_int1_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a<char>();
    return result ? 1 : 0;
}

int LIBMUSCLE_Data_is_a_int2_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a<int16_t>();
    return result ? 1 : 0;
}

int LIBMUSCLE_Data_is_a_int4_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a<int32_t>();
    return result ? 1 : 0;
}

int LIBMUSCLE_Data_is_a_int8_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a<int64_t>();
    return result ? 1 : 0;
}

int LIBMUSCLE_Data_is_a_real4_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a<float>();
    return result ? 1 : 0;
}

int LIBMUSCLE_Data_is_a_real8_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a<double>();
    return result ? 1 : 0;
}

int LIBMUSCLE_Data_is_a_dict_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a_dict();
    return result ? 1 : 0;
}

int LIBMUSCLE_Data_is_a_list_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a_list();
    return result ? 1 : 0;
}

int LIBMUSCLE_Data_is_a_byte_array_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a_byte_array();
    return result ? 1 : 0;
}

int LIBMUSCLE_Data_is_nil_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_nil();
    return result ? 1 : 0;
}

int LIBMUSCLE_Data_is_a_settings_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a<Settings>();
    return result ? 1 : 0;
}

std::size_t LIBMUSCLE_Data_size_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    std::size_t result = self_p->size();
    return result;
}

int LIBMUSCLE_Data_as_logical_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        bool result = self_p->as<bool>();
        return result ? 1 : 0;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

void LIBMUSCLE_Data_as_character_(std::intptr_t self, char ** ret_val, std::size_t * ret_val_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        static std::string result;
        result = self_p->as<std::string>();
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
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

int LIBMUSCLE_Data_as_int_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        int result = self_p->as<int>();
        return result;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

char LIBMUSCLE_Data_as_int1_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        char result = self_p->as<char>();
        return result;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

short int LIBMUSCLE_Data_as_int2_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        short int result = self_p->as<int16_t>();
        return result;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

int32_t LIBMUSCLE_Data_as_int4_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        int32_t result = self_p->as<int32_t>();
        return result;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

int64_t LIBMUSCLE_Data_as_int8_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        int64_t result = self_p->as<int64_t>();
        return result;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

float LIBMUSCLE_Data_as_real4_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        float result = self_p->as<float>();
        return result;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

double LIBMUSCLE_Data_as_real8_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        double result = self_p->as<double>();
        return result;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

std::intptr_t LIBMUSCLE_Data_as_settings_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        Settings * result = new Settings(self_p->as<Settings>());
        return reinterpret_cast<std::intptr_t>(result);
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

void LIBMUSCLE_Data_as_byte_array_(
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
std::intptr_t LIBMUSCLE_Data_get_item_by_key_(
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
}

std::intptr_t LIBMUSCLE_Data_get_item_by_index_(
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
}

std::intptr_t LIBMUSCLE_Data_create_dict_() {
    Data * result = new Data(Data::dict());
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_Data_create_list_() {
    Data * result = new Data(Data::list());
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_Data_create_nils_(std::size_t size) {
    Data * result = new Data(Data::nils(size));
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_Data_create_byte_array_empty_(std::size_t size) {
    Data * result = new Data(Data::byte_array(size));
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_Data_create_byte_array_from_buf_(
       char * buf, std::size_t buf_size
) {
   Data * result = new Data(Data::byte_array(buf, buf_size));
   return reinterpret_cast<std::intptr_t>(result);
}

void LIBMUSCLE_Data_set_logical_(std::intptr_t self, int value) {
    Data * self_p = reinterpret_cast<Data *>(self);
    *self_p = value != 0;
    return;
}

void LIBMUSCLE_Data_set_character_(std::intptr_t self, char * value, std::size_t value_size) {
    Data * self_p = reinterpret_cast<Data *>(self);
    std::string value_s(value, value_size);
    *self_p = value_s;
    return;
}

void LIBMUSCLE_Data_set_int1_(std::intptr_t self, char value) {
    Data * self_p = reinterpret_cast<Data *>(self);
    *self_p = value;
    return;
}

void LIBMUSCLE_Data_set_int2_(std::intptr_t self, short int value) {
    Data * self_p = reinterpret_cast<Data *>(self);
    *self_p = value;
    return;
}

void LIBMUSCLE_Data_set_int4_(std::intptr_t self, int32_t value) {
    Data * self_p = reinterpret_cast<Data *>(self);
    *self_p = value;
    return;
}

void LIBMUSCLE_Data_set_int8_(std::intptr_t self, int64_t value) {
    Data * self_p = reinterpret_cast<Data *>(self);
    *self_p = value;
    return;
}

void LIBMUSCLE_Data_set_real4_(std::intptr_t self, float value) {
    Data * self_p = reinterpret_cast<Data *>(self);
    *self_p = value;
    return;
}

void LIBMUSCLE_Data_set_real8_(std::intptr_t self, double value) {
    Data * self_p = reinterpret_cast<Data *>(self);
    *self_p = value;
    return;
}

void LIBMUSCLE_Data_set_data_(std::intptr_t self, std::intptr_t value) {
    Data * self_p = reinterpret_cast<Data *>(self);
    Data * value_p = reinterpret_cast<Data *>(value);
    *self_p = *value_p;
    return;
}

void LIBMUSCLE_Data_set_nil_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    *self_p = Data();
}

void LIBMUSCLE_Data_set_item_key_logical_(std::intptr_t self, char * key, std::size_t key_size, int value, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    std::string key_s(key, key_size);
    try {
        *err_code = 0;
        (*self_p)[key_s] = value != 0;
        return;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

void LIBMUSCLE_Data_set_item_key_character_(std::intptr_t self, char * key, std::size_t key_size, char * value, std::size_t value_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    std::string key_s(key, key_size);
    std::string value_s(value, value_size);
    try {
        *err_code = 0;
        (*self_p)[key_s] = value_s;
        return;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

void LIBMUSCLE_Data_set_item_key_int1_(std::intptr_t self, char * key, std::size_t key_size, char value, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    std::string key_s(key, key_size);
    try {
        *err_code = 0;
        (*self_p)[key_s] = value;
        return;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

void LIBMUSCLE_Data_set_item_key_int2_(std::intptr_t self, char * key, std::size_t key_size, short int value, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    std::string key_s(key, key_size);
    try {
        *err_code = 0;
        (*self_p)[key_s] = value;
        return;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

void LIBMUSCLE_Data_set_item_key_int4_(std::intptr_t self, char * key, std::size_t key_size, int value, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    std::string key_s(key, key_size);
    try {
        *err_code = 0;
        (*self_p)[key_s] = value;
        return;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

void LIBMUSCLE_Data_set_item_key_int8_(std::intptr_t self, char * key, std::size_t key_size, int64_t value, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    std::string key_s(key, key_size);
    try {
        *err_code = 0;
        (*self_p)[key_s] = value;
        return;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

void LIBMUSCLE_Data_set_item_key_real4_(std::intptr_t self, char * key, std::size_t key_size, float value, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    std::string key_s(key, key_size);
    try {
        *err_code = 0;
        (*self_p)[key_s] = value;
        return;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

void LIBMUSCLE_Data_set_item_key_real8_(std::intptr_t self, char * key, std::size_t key_size, double value, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    std::string key_s(key, key_size);
    try {
        *err_code = 0;
        (*self_p)[key_s] = value;
        return;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

void LIBMUSCLE_Data_set_item_key_data_(std::intptr_t self, char * key, std::size_t key_size, std::intptr_t value, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    std::string key_s(key, key_size);
    Data * value_p = reinterpret_cast<Data *>(value);
    try {
        *err_code = 0;
        (*self_p)[key_s] = *value_p;
        return;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

void LIBMUSCLE_Data_set_item_index_logical_(std::intptr_t self, std::size_t i, int value, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        (*self_p)[i - 1u] = value != 0;
        return;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

void LIBMUSCLE_Data_set_item_index_character_(std::intptr_t self, std::size_t i, char * value, std::size_t value_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    std::string value_s(value, value_size);
    try {
        *err_code = 0;
        (*self_p)[i - 1u] = value_s;
        return;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

void LIBMUSCLE_Data_set_item_index_int1_(std::intptr_t self, std::size_t i, char value, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        (*self_p)[i - 1u] = value;
        return;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

void LIBMUSCLE_Data_set_item_index_int2_(std::intptr_t self, std::size_t i, short int value, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        (*self_p)[i - 1u] = value;
        return;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

void LIBMUSCLE_Data_set_item_index_int4_(std::intptr_t self, std::size_t i, int value, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        (*self_p)[i - 1u] = value;
        return;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

void LIBMUSCLE_Data_set_item_index_int8_(std::intptr_t self, std::size_t i, int64_t value, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        (*self_p)[i - 1u] = value;
        return;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

void LIBMUSCLE_Data_set_item_index_real4_(std::intptr_t self, std::size_t i, float value, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        (*self_p)[i - 1u] = value;
        return;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

void LIBMUSCLE_Data_set_item_index_real8_(std::intptr_t self, std::size_t i, double value, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    try {
        *err_code = 0;
        (*self_p)[i - 1u] = value;
        return;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

void LIBMUSCLE_Data_set_item_index_data_(std::intptr_t self, std::size_t i, std::intptr_t value, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Data * self_p = reinterpret_cast<Data *>(self);
    Data * value_p = reinterpret_cast<Data *>(value);
    try {
        *err_code = 0;
        (*self_p)[i - 1u] = *value_p;
        return;
    }
    catch (std::runtime_error const & e) {
        *err_code = 1;
        static std::string msg;
        msg = e.what();
        *err_msg = const_cast<char*>(msg.data());
        *err_msg_len = msg.size();
    }
    catch (std::domain_error const & e) {
        *err_code = 2;
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
    catch (std::logic_error const & e) {
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

void LIBMUSCLE_Data_key_(
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

std::intptr_t LIBMUSCLE_Data_value_(
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
}

std::intptr_t LIBMUSCLE_Message_create_td_(double timestamp, std::intptr_t data) {
    Data * data_p = reinterpret_cast<Data *>(data);
    Message * result = new Message(timestamp, *data_p);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_Message_create_tnd_(double timestamp, double next_timestamp, std::intptr_t data) {
    Data * data_p = reinterpret_cast<Data *>(data);
    Message * result = new Message(timestamp, next_timestamp, *data_p);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_Message_create_tds_(double timestamp, std::intptr_t data, std::intptr_t settings) {
    Data * data_p = reinterpret_cast<Data *>(data);
    Settings * settings_p = reinterpret_cast<Settings *>(settings);
    Message * result = new Message(timestamp, *data_p, *settings_p);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_Message_create_tnds_(double timestamp, double next_timestamp, std::intptr_t data, std::intptr_t settings) {
    Data * data_p = reinterpret_cast<Data *>(data);
    Settings * settings_p = reinterpret_cast<Settings *>(settings);
    Message * result = new Message(timestamp, next_timestamp, *data_p, *settings_p);
    return reinterpret_cast<std::intptr_t>(result);
}

void LIBMUSCLE_Message_free_(std::intptr_t self) {
    Message * self_p = reinterpret_cast<Message *>(self);
    delete self_p;
    return;
}

double LIBMUSCLE_Message_timestamp_(std::intptr_t self) {
    Message * self_p = reinterpret_cast<Message *>(self);
    double result = self_p->timestamp();
    return result;
}

void LIBMUSCLE_Message_set_timestamp_(std::intptr_t self, double timestamp) {
    Message * self_p = reinterpret_cast<Message *>(self);
    self_p->set_timestamp(timestamp);
    return;
}

int LIBMUSCLE_Message_has_next_timestamp_(std::intptr_t self) {
    Message * self_p = reinterpret_cast<Message *>(self);
    bool result = self_p->has_next_timestamp();
    return result ? 1 : 0;
}

double LIBMUSCLE_Message_next_timestamp_(std::intptr_t self) {
    Message * self_p = reinterpret_cast<Message *>(self);
    double result = self_p->next_timestamp();
    return result;
}

void LIBMUSCLE_Message_set_next_timestamp_(std::intptr_t self, double next_timestamp) {
    Message * self_p = reinterpret_cast<Message *>(self);
    self_p->set_next_timestamp(next_timestamp);
    return;
}

void LIBMUSCLE_Message_unset_next_timestamp_(std::intptr_t self) {
    Message * self_p = reinterpret_cast<Message *>(self);
    self_p->unset_next_timestamp();
    return;
}

std::intptr_t LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_create_(int count) {
    CmdLineArgs * result = new CmdLineArgs(count);
    return reinterpret_cast<std::intptr_t>(result);
}

void LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_free_(std::intptr_t self) {
    CmdLineArgs * self_p = reinterpret_cast<CmdLineArgs *>(self);
    delete self_p;
    return;
}

void LIBMUSCLE_IMPL_BINDINGS_CmdLineArgs_set_arg_(std::intptr_t self, int i, char * arg, std::size_t arg_size) {
    CmdLineArgs * self_p = reinterpret_cast<CmdLineArgs *>(self);
    std::string arg_s(arg, arg_size);
    self_p->set_arg(i, arg_s);
    return;
}

}


