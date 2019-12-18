// This is generated code. If it's broken, then you should
// fix the generation script, not this file.


#include <libmuscle/libmuscle.hpp>
#include <libmuscle/bindings/cmdlineargs.hpp>
#include <stdexcept>


using libmuscle::Data;
using libmuscle::impl::bindings::CmdLineArgs;


extern "C" {

std::intptr_t LIBMUSCLE_Data_create_nil_() {
    Data * result = new Data();
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_Data_create_bool_(int value) {
    Data * result = new Data(value != 0);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_Data_create_string_(char * value, std::size_t value_size) {
    std::string value_s(value, value_size);
    Data * result = new Data(value_s);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_Data_create_char_(char value) {
    Data * result = new Data(value);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_Data_create_int_(int value) {
    Data * result = new Data(value);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_Data_create_int16t_(short int value) {
    Data * result = new Data(value);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_Data_create_int64t_(int64_t value) {
    Data * result = new Data(value);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_Data_create_float_(float value) {
    Data * result = new Data(value);
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_Data_create_double_(double value) {
    Data * result = new Data(value);
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

std::intptr_t LIBMUSCLE_Data_create_dict_() {
    Data * result = new Data(Data::dict());
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_Data_create_list_() {
    Data * result = new Data(Data::list());
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_Data_create_byte_array_(std::size_t size) {
    Data * result = new Data(Data::byte_array(size));
    return reinterpret_cast<std::intptr_t>(result);
}

std::intptr_t LIBMUSCLE_Data_create_nils_(std::size_t size) {
    Data * result = new Data(Data::nils(size));
    return reinterpret_cast<std::intptr_t>(result);
}

void LIBMUSCLE_Data_set_bool_(std::intptr_t self, int value) {
    Data * self_p = reinterpret_cast<Data *>(self);
    *self_p = value != 0;
    return;
}

void LIBMUSCLE_Data_set_string_(std::intptr_t self, char * value, std::size_t value_size) {
    Data * self_p = reinterpret_cast<Data *>(self);
    std::string value_s(value, value_size);
    *self_p = value_s;
    return;
}

void LIBMUSCLE_Data_set_char_(std::intptr_t self, char value) {
    Data * self_p = reinterpret_cast<Data *>(self);
    *self_p = value;
    return;
}

void LIBMUSCLE_Data_set_int16_(std::intptr_t self, short int value) {
    Data * self_p = reinterpret_cast<Data *>(self);
    *self_p = value;
    return;
}

void LIBMUSCLE_Data_set_int_(std::intptr_t self, int value) {
    Data * self_p = reinterpret_cast<Data *>(self);
    *self_p = value;
    return;
}

void LIBMUSCLE_Data_set_int64_(std::intptr_t self, int64_t value) {
    Data * self_p = reinterpret_cast<Data *>(self);
    *self_p = value;
    return;
}

void LIBMUSCLE_Data_set_float_(std::intptr_t self, float value) {
    Data * self_p = reinterpret_cast<Data *>(self);
    *self_p = value;
    return;
}

void LIBMUSCLE_Data_set_double_(std::intptr_t self, double value) {
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

int LIBMUSCLE_Data_is_a_bool_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a<bool>();
    return result ? 1 : 0;
}

int LIBMUSCLE_Data_is_a_string_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a<std::string>();
    return result ? 1 : 0;
}

int LIBMUSCLE_Data_is_a_char_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a<char>();
    return result ? 1 : 0;
}

int LIBMUSCLE_Data_is_a_int_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a<int>();
    return result ? 1 : 0;
}

int LIBMUSCLE_Data_is_a_int16_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a<int16_t>();
    return result ? 1 : 0;
}

int LIBMUSCLE_Data_is_a_int64_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a<int64_t>();
    return result ? 1 : 0;
}

int LIBMUSCLE_Data_is_a_float_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    bool result = self_p->is_a<float>();
    return result ? 1 : 0;
}

int LIBMUSCLE_Data_is_a_double_(std::intptr_t self) {
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

int64_t LIBMUSCLE_Data_size_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    int64_t result = self_p->size();
    return result;
}

int LIBMUSCLE_Data_as_bool_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
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
}

void LIBMUSCLE_Data_as_string_(std::intptr_t self, char ** ret_val, std::size_t * ret_val_size, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
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
}

char LIBMUSCLE_Data_as_char_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
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
}

short int LIBMUSCLE_Data_as_int16_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
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
}

int64_t LIBMUSCLE_Data_as_int64_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
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
}

float LIBMUSCLE_Data_as_float_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
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
}

double LIBMUSCLE_Data_as_double_(std::intptr_t self, int * err_code, char ** err_msg, std::size_t * err_msg_len) {
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


