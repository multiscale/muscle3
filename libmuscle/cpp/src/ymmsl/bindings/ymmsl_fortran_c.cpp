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

int YMMSL_Settings_equals_(std::intptr_t self, std::intptr_t other) {
    Settings * self_p = reinterpret_cast<Settings *>(self);
    Settings * other_p = reinterpret_cast<Settings *>(other);
    bool result = ((*self_p) == *other_p);
    return result ? 1 : 0;
}

std::size_t YMMSL_Settings_size_(std::intptr_t self) {
    Settings * self_p = reinterpret_cast<Settings *>(self);
    std::size_t result = self_p->size();
    return result;
}

}


