// This is generated code. If it's broken, then you should
// fix the generation script, not this file.


#include <ymmsl/ymmsl.hpp>
#include <cstring>
#include <stdexcept>
#include <typeinfo>


using ymmsl::Operator;
using ymmsl::Settings;


extern "C" {

std::intptr_t YMMSL_Settings_create_() {
    Settings * result = new Settings();
    return reinterpret_cast<std::intptr_t>(result);
}

void YMMSL_Settings_free_(std::intptr_t self) {
    Settings * self_p = reinterpret_cast<Settings *>(self);
    delete self_p;
    return;
}

bool YMMSL_Settings_equals_(std::intptr_t self, std::intptr_t other) {
    Settings * self_p = reinterpret_cast<Settings *>(self);
    Settings * other_p = reinterpret_cast<Settings *>(other);
    bool result = ((*self_p) == *other_p);
    return result;
}

std::size_t YMMSL_Settings_size_(std::intptr_t self) {
    Settings * self_p = reinterpret_cast<Settings *>(self);
    std::size_t result = self_p->size();
    return result;
}

bool YMMSL_Settings_empty_(std::intptr_t self) {
    Settings * self_p = reinterpret_cast<Settings *>(self);
    bool result = self_p->empty();
    return result;
}

bool YMMSL_Settings_is_a_character_(std::intptr_t self, char * key, std::size_t key_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Settings * self_p = reinterpret_cast<Settings *>(self);
    std::string key_s(key, key_size);
    try {
        *err_code = 0;
        bool result = self_p->at(key_s).is_a<std::string>();
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

bool YMMSL_Settings_is_a_int4_(std::intptr_t self, char * key, std::size_t key_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Settings * self_p = reinterpret_cast<Settings *>(self);
    std::string key_s(key, key_size);
    try {
        *err_code = 0;
        bool result = self_p->at(key_s).is_a<int32_t>();
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

bool YMMSL_Settings_is_a_int8_(std::intptr_t self, char * key, std::size_t key_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Settings * self_p = reinterpret_cast<Settings *>(self);
    std::string key_s(key, key_size);
    try {
        *err_code = 0;
        bool result = self_p->at(key_s).is_a<int64_t>();
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

bool YMMSL_Settings_is_a_real8_(std::intptr_t self, char * key, std::size_t key_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Settings * self_p = reinterpret_cast<Settings *>(self);
    std::string key_s(key, key_size);
    try {
        *err_code = 0;
        bool result = self_p->at(key_s).is_a<double>();
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

bool YMMSL_Settings_is_a_logical_(std::intptr_t self, char * key, std::size_t key_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Settings * self_p = reinterpret_cast<Settings *>(self);
    std::string key_s(key, key_size);
    try {
        *err_code = 0;
        bool result = self_p->at(key_s).is_a<bool>();
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

bool YMMSL_Settings_is_a_real8array_(std::intptr_t self, char * key, std::size_t key_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Settings * self_p = reinterpret_cast<Settings *>(self);
    std::string key_s(key, key_size);
    try {
        *err_code = 0;
        bool result = self_p->at(key_s).is_a<std::vector<double>>();
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

bool YMMSL_Settings_is_a_real8array2_(std::intptr_t self, char * key, std::size_t key_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Settings * self_p = reinterpret_cast<Settings *>(self);
    std::string key_s(key, key_size);
    try {
        *err_code = 0;
        bool result = self_p->at(key_s).is_a<std::vector<std::vector<double>>>();
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

void YMMSL_Settings_set_character_(std::intptr_t self, char * key, std::size_t key_size, char * value, std::size_t value_size) {
    Settings * self_p = reinterpret_cast<Settings *>(self);
    std::string key_s(key, key_size);
    std::string value_s(value, value_size);
    (*self_p)[key_s] = value_s;
    return;
}

void YMMSL_Settings_set_int4_(std::intptr_t self, char * key, std::size_t key_size, int32_t value) {
    Settings * self_p = reinterpret_cast<Settings *>(self);
    std::string key_s(key, key_size);
    (*self_p)[key_s] = value;
    return;
}

void YMMSL_Settings_set_int8_(std::intptr_t self, char * key, std::size_t key_size, int64_t value) {
    Settings * self_p = reinterpret_cast<Settings *>(self);
    std::string key_s(key, key_size);
    (*self_p)[key_s] = value;
    return;
}

void YMMSL_Settings_set_real8_(std::intptr_t self, char * key, std::size_t key_size, double value) {
    Settings * self_p = reinterpret_cast<Settings *>(self);
    std::string key_s(key, key_size);
    (*self_p)[key_s] = value;
    return;
}

void YMMSL_Settings_set_logical_(std::intptr_t self, char * key, std::size_t key_size, bool value) {
    Settings * self_p = reinterpret_cast<Settings *>(self);
    std::string key_s(key, key_size);
    (*self_p)[key_s] = value;
    return;
}

void YMMSL_Settings_set_real8array_(std::intptr_t self, char * key, std::size_t key_size, double * value, std::size_t value_size) {
    Settings * self_p = reinterpret_cast<Settings *>(self);
    std::string key_s(key, key_size);
    std::vector<double> value_v(value, value + value_size);
    (*self_p)[key_s] = value_v;
    return;
}

void YMMSL_Settings_set_real8array2_(std::intptr_t self, char * key, std::size_t key_size, double * value, std::size_t * value_shape) {
    Settings * self_p = reinterpret_cast<Settings *>(self);
    std::string key_s(key, key_size);
    std::vector<std::vector<double>> value_v(
            value_shape[0], std::vector<double>(value_shape[1]));
    for (std::size_t i = 0; i < value_shape[0]; ++i)
        for (std::size_t j = 0; j < value_shape[1]; ++j)
            value_v[i][j] = value[j * value_shape[0] + i];
    (*self_p)[key_s] = value_v;
    return;
}

void YMMSL_Settings_get_as_character_(std::intptr_t self, char * key, std::size_t key_size, char ** ret_val, std::size_t * ret_val_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Settings * self_p = reinterpret_cast<Settings *>(self);
    std::string key_s(key, key_size);
    try {
        *err_code = 0;
        static std::string result;
        result = self_p->at(key_s).as<std::string>();
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

int32_t YMMSL_Settings_get_as_int4_(std::intptr_t self, char * key, std::size_t key_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Settings * self_p = reinterpret_cast<Settings *>(self);
    std::string key_s(key, key_size);
    try {
        *err_code = 0;
        int32_t result = self_p->at(key_s).as<int32_t>();
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

int64_t YMMSL_Settings_get_as_int8_(std::intptr_t self, char * key, std::size_t key_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Settings * self_p = reinterpret_cast<Settings *>(self);
    std::string key_s(key, key_size);
    try {
        *err_code = 0;
        int64_t result = self_p->at(key_s).as<int64_t>();
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

double YMMSL_Settings_get_as_real8_(std::intptr_t self, char * key, std::size_t key_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Settings * self_p = reinterpret_cast<Settings *>(self);
    std::string key_s(key, key_size);
    try {
        *err_code = 0;
        double result = self_p->at(key_s).as<double>();
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

bool YMMSL_Settings_get_as_logical_(std::intptr_t self, char * key, std::size_t key_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Settings * self_p = reinterpret_cast<Settings *>(self);
    std::string key_s(key, key_size);
    try {
        *err_code = 0;
        bool result = self_p->at(key_s).as<bool>();
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

void YMMSL_Settings_get_as_real8array_(std::intptr_t self, char * key, std::size_t key_size, double ** value, std::size_t * value_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Settings * self_p = reinterpret_cast<Settings *>(self);
    std::string key_s(key, key_size);
    try {
        *err_code = 0;
        static std::vector<double> result;
        result = self_p->at(key_s).as<std::vector<double>>();
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

void YMMSL_Settings_get_as_real8array2_(std::intptr_t self, char * key, std::size_t key_size, double ** value, std::size_t * value_shape, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
    Settings * self_p = reinterpret_cast<Settings *>(self);
    std::string key_s(key, key_size);
    try {
        *err_code = 0;
        std::vector<std::vector<double>> result = self_p->at(key_s).as<std::vector<std::vector<double>>>();
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

bool YMMSL_Settings_contains_(std::intptr_t self, char * key, std::size_t key_size) {
    Settings * self_p = reinterpret_cast<Settings *>(self);
    std::string key_s(key, key_size);
    bool result = self_p->contains(key_s);
    return result;
}

std::size_t YMMSL_Settings_erase_(std::intptr_t self, char * key, std::size_t key_size) {
    Settings * self_p = reinterpret_cast<Settings *>(self);
    std::string key_s(key, key_size);
    std::size_t result = self_p->erase(key_s);
    return result;
}

void YMMSL_Settings_clear_(std::intptr_t self) {
    Settings * self_p = reinterpret_cast<Settings *>(self);
    self_p->clear();
    return;
}

void YMMSL_Settings_key_(
        std::intptr_t self, std::size_t i,
        char ** ret_val, std::size_t * ret_val_size,
        int * err_code,
        char ** err_msg, std::size_t * err_msg_len
) {
    Settings * self_p = reinterpret_cast<Settings *>(self);
    if (i == 0 || i > self_p->size()) {
       *err_code = 2;
       *err_msg = const_cast<char*>("Key index out of range.");
       *err_msg_len = strlen(*err_msg);
       return;
    }
    *err_code = 0;
    static std::string result;
    result = std::string(std::next(self_p->begin(), i-1)->first);
    *ret_val = const_cast<char*>(result.c_str());
    *ret_val_size = result.size();
    return;
}

}


