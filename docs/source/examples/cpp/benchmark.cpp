#include "libmuscle/libmuscle.hpp"
#include "ymmsl/ymmsl.hpp"

#include <cstdint>
#include <iostream>
#include <set>
#include <string>
#include <unistd.h>


using libmuscle::Data;
using libmuscle::Instance;
using libmuscle::Message;
using ymmsl::Operator;

using std::set;
using std::string;


// Sleep for a time period in seconds
void sleep(double time) {
    usleep(static_cast<int64_t>(time * 1e6));
}


// Not optimal, but easily good enough
int64_t powi(int64_t base, int64_t power) {
    int64_t result = 1ll;
    for (int64_t i = 0ll; i < power; ++i)
        result *= base;
    return result;
}


void driver(int argc, char **argv) {
    Instance instance(argc, argv, {
            {Operator::O_I, {"out"}},
            {Operator::S, {"in"}}});

    // Message size is base_size * scale_base**scale, with scale in
    // the range [0..num_scales).
    int64_t base_size = instance.get_setting_as<int64_t>("base_size");
    int64_t scale_base = instance.get_setting_as<int64_t>("scale_base");
    int64_t num_scales = instance.get_setting_as<int64_t>("num_scales");
    int64_t num_repeats = instance.get_setting_as<int64_t>("num_repeats");

    // in seconds
    double pre_send_delay = instance.get_setting_as<double>("pre_send_delay");
    double pre_recv_delay = instance.get_setting_as<double>("pre_recv_delay");

    std::vector<char> buffer(base_size * powi(scale_base, num_scales - 1));

    while (instance.reuse_instance()) {
        // wait a bit to make sure mirror is running
        sleep(0.2);

        for (int64_t scale = 0; scale < num_scales; ++scale) {
            int64_t size = base_size * powi(scale_base, scale);
            if (size > 10ll * powi(1024, 3))
                throw std::runtime_error("Messages > 10GB are not supported");

            for (int64_t i = 0; i < num_repeats; ++i) {
                sleep(pre_send_delay);
                instance.send("out", Message(
                            0.0, Data::byte_array(buffer.data(), size)));
                sleep(pre_recv_delay);
                auto msg = instance.receive("in");
            }
        }
    }
}


void mirror(int argc, char **argv) {
    Instance instance(argc, argv, {
            {Operator::O_I, {"out"}},
            {Operator::S, {"in"}}});

    int64_t num_scales = instance.get_setting_as<int64_t>("num_scales");
    int64_t num_repeats = instance.get_setting_as<int64_t>("num_repeats");

    // in seconds
    double pre_send_delay = instance.get_setting_as<double>("pre_send_delay");
    double pre_recv_delay = instance.get_setting_as<double>("pre_recv_delay");

    while (instance.reuse_instance()) {
        for (int64_t scale = 0; scale < num_scales; ++scale) {
            for (int64_t i = 0; i < num_repeats; ++i) {
                sleep(pre_recv_delay);
                auto msg = instance.receive("in");

                sleep(pre_send_delay);
                instance.send("out", msg);
            }
        }
    }
}


int main(int argc, char * argv[]) {
    if (argc < 2 || !set<string>{"driver", "mirror"}.count(argv[1]))
        throw std::runtime_error(
                "Please specify 'driver' or 'mirror' in the first argument");

    if (argv[1] == string("driver"))
        driver(argc, argv);
    else
        mirror(argc, argv);
}

