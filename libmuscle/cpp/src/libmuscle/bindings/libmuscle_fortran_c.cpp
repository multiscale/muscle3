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

std::intptr_t LIBMUSCLE_Data_create_int_(int value) {
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

void LIBMUSCLE_Data_free_(std::intptr_t self) {
    Data * self_p = reinterpret_cast<Data *>(self);
    delete self_p;
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


