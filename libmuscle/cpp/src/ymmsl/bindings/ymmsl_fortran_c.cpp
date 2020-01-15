// This is generated code. If it's broken, then you should
// fix the generation script, not this file.


#include <ymmsl/ymmsl.hpp>
#include <stdexcept>


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

}


