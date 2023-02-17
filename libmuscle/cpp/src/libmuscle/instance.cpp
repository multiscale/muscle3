#include <libmuscle/instance.hpp>

#include <libmuscle/api_guard.hpp>
#include <libmuscle/communicator.hpp>
#include <libmuscle/data.hpp>
#include <libmuscle/mcp/data_pack.hpp>
#include <libmuscle/logger.hpp>
#include <libmuscle/mmp_client.hpp>
#include <libmuscle/peer_manager.hpp>
#include <libmuscle/profiler.hpp>
#include <libmuscle/profiling.hpp>
#include <libmuscle/settings_manager.hpp>
#include <libmuscle/snapshot_manager.hpp>
#include <libmuscle/checkpoint_triggers.hpp>

#include <ymmsl/ymmsl.hpp>

#include <cstdint>
#include <cstdlib>
#include <stdexcept>
#include <utility>

#ifdef MUSCLE_ENABLE_MPI
#include <libmuscle/mpi_tcp_barrier.hpp>
#endif


using ymmsl::Operator;
using ymmsl::Reference;
using ymmsl::Settings;

using libmuscle::impl::LogLevel;
using libmuscle::impl::ProfileEvent;
using libmuscle::impl::ProfileEventType;


namespace {

/* Converts a user-input string to a log level.
 *
 * The input is case-insensitive.
 */
LogLevel string_to_level(std::string const & log_level_str) {
    // convert to upper case (ASCII/UTF-8 only, which is fine here)
    std::string log_level(log_level_str);
    for (char & c : log_level)
        if (('a' <= c) && (c <= 'z')) c += ('A' - 'a');

    // convert to LogLevel
    LogLevel level;
    if (log_level == "DISABLE") level = LogLevel::DISABLE;
    else if (log_level == "CRITICAL") level = LogLevel::CRITICAL;
    else if (log_level == "ERROR") level = LogLevel::ERROR;
    else if (log_level == "WARNING") level = LogLevel::WARNING;
    else if (log_level == "INFO") level = LogLevel::INFO;
    else if (log_level == "DEBUG") level = LogLevel::DEBUG;
    else if (log_level == "LOCAL") level = LogLevel::LOCAL;
    else {
        throw std::runtime_error("Invalid log level " + log_level_str);
    }
    return level;
}

}


namespace libmuscle { namespace impl {

class Instance::Impl {
    public:
        Impl(
                int argc, char const * const argv[],
                PortsDescription const & ports,
                InstanceFlags flags
#ifdef MUSCLE_ENABLE_MPI
                , MPI_Comm const & communicator
                , int root
#endif
                );
        ~Impl();

        bool reuse_instance();
        void error_shutdown(std::string const & message);
        ::ymmsl::SettingValue get_setting(std::string const & name) const;
        template <typename ValueType>
        ValueType get_setting_as(std::string const & name) const;
        std::unordered_map<::ymmsl::Operator, std::vector<std::string>>
        list_ports() const;
        bool is_connected(std::string const & port) const;
        bool is_vector_port(std::string const & port) const;
        bool is_resizable(std::string const & port) const;
        int get_port_length(std::string const & port) const;
        void set_port_length(std::string const & port, int length);
        void send(std::string const & port_name, Message const & message);
        void send(std::string const & port_name, Message const & message,
                int slot);
        Message receive_message(
                std::string const & port_name,
                Optional<int> slot,
                Optional<Message> default_msg,
                bool with_settings);
        bool resuming();
        bool should_init();
        Message load_snapshot();
        bool should_save_snapshot(double timestamp);
        void save_snapshot(Message message);
        bool should_save_final_snapshot();
        void save_final_snapshot(Message message);

    private:
        ::ymmsl::Reference instance_name_;
        std::unique_ptr<MMPClient> manager_;
        std::unique_ptr<Logger> logger_;
        std::unique_ptr<APIGuard> api_guard_;
        std::unique_ptr<Profiler> profiler_;
        std::unique_ptr<Communicator> communicator_;
#ifdef MUSCLE_ENABLE_MPI
        int mpi_root_;
        MPI_Comm mpi_comm_;
        MPITcpBarrier mpi_barrier_;
#endif
        PortsDescription declared_ports_;
        SettingsManager settings_manager_;
        std::unique_ptr<SnapshotManager> snapshot_manager_;
        std::unique_ptr<TriggerManager> trigger_manager_;
        Optional<bool> first_run_;
        Optional<bool> do_reuse_;
        bool do_resume_;
        bool do_init_;
        std::unordered_map<::ymmsl::Reference, Message> f_init_cache_;
        bool is_shut_down_;
        InstanceFlags flags_;

        void register_();
        void connect_();
        void deregister_();
        void setup_checkpointing_();

        ::ymmsl::Reference make_full_name_(int argc, char const * const argv[]) const;
        std::string extract_manager_location_(int argc, char const * const argv[]) const;
        ::ymmsl::Reference name_() const;
        std::vector<int> index_() const;
        std::vector<::ymmsl::Port> list_declared_ports_() const;
        void check_port_(std::string const & port_name);
        bool receive_settings_();
        bool have_f_init_connections_();
        bool pre_receive_();
        void pre_receive_(std::string const & port_name, Optional<int> slot);
        void pre_receive_f_init_();
        Optional<double> f_init_max_timestamp_();
        bool decide_reuse_instance_();
        void save_snapshot_(
                Optional<Message> message, bool final,
                Optional<double> f_init_max_timestamp);
        void set_local_log_level_();
        void set_remote_log_level_();
        void apply_overlay_(Message const & message);
        void check_compatibility_(
                std::string const & port_name,
                Optional<::ymmsl::Settings> const & overlay);
        void close_outgoing_ports_();
        void drain_incoming_port_(std::string const & port_name);
        void drain_incoming_vector_port_(std::string const & port_name);
        void close_incoming_ports_();
        void close_ports_();
        void shutdown_();

        friend class TestInstance;
};

Instance::Impl::Impl(
        int argc, char const * const argv[],
        PortsDescription const & ports,
        InstanceFlags flags
#ifdef MUSCLE_ENABLE_MPI
        , MPI_Comm const & communicator
        , int root
#endif
        )
    : instance_name_(make_full_name_(argc, argv))
#ifdef MUSCLE_ENABLE_MPI
    , mpi_root_(root)
    , mpi_barrier_(communicator, root)
#endif
    , declared_ports_(ports)
    , settings_manager_()
    , first_run_()
    , do_reuse_()
    , do_resume_(false)
    , do_init_(false)
    , f_init_cache_()
    , is_shut_down_(false)
    , flags_(flags)
{
    api_guard_.reset(new APIGuard(!!(flags_ & InstanceFlags::USES_CHECKPOINT_API)));
#ifdef MUSCLE_ENABLE_MPI
    MPI_Comm_dup(communicator, &mpi_comm_);
    if (mpi_barrier_.is_root()) {
#endif
        manager_.reset(
                new MMPClient(instance_name_, extract_manager_location_(argc, argv)));

        std::string instance_id = static_cast<std::string>(instance_name_);
        std::string default_logfile = "muscle_" + instance_id + ".log";
        std::string log_file = extract_log_file_location(argc, argv, default_logfile);
        logger_.reset(new Logger(instance_id, log_file, *manager_));
        profiler_.reset(new Profiler(*manager_));

        communicator_.reset(
                new Communicator(name_(), index_(), ports, *logger_, *profiler_));
        snapshot_manager_.reset(new SnapshotManager(
                instance_name_, *manager_, *communicator_, *logger_));
        trigger_manager_.reset(new TriggerManager());

        register_();
        connect_();
        // Note: setup_checkpointing_() needs to have the ports initialized
        // so it comes after connect_()
        setup_checkpointing_();
        set_local_log_level_();
        set_remote_log_level_();
#ifdef MUSCLE_ENABLE_MPI
        auto sbase_data = Data(settings_manager_.base);
        msgpack::sbuffer sbuf;
        msgpack::pack(sbuf, sbase_data);
        int size = sbuf.size();
        MPI_Bcast(&size, 1, MPI_INT, mpi_root_, mpi_comm_);
        MPI_Bcast(sbuf.data(), size, MPI_CHAR, mpi_root_, mpi_comm_);
    }
    else {
        int size;
        MPI_Bcast(&size, 1, MPI_INT, mpi_root_, mpi_comm_);
        std::vector<char> buf(size);
        MPI_Bcast(&buf[0], size, MPI_CHAR, mpi_root_, mpi_comm_);
        auto zone = std::make_shared<msgpack::zone>();
        DataConstRef sbase_data = mcp::unpack_data(zone, &buf[0], size);
        settings_manager_.base = sbase_data.as<Settings>();
    }
#endif
}

Instance::Impl::~Impl() {
    // This communicates if we did not shut down cleanly, and therefore risks
    // an exception and a crash. Since we're already going down abnormally,
    // trying to not hurt the rest of the simulation seems worth it.
    shutdown_();
}

bool Instance::Impl::reuse_instance() {
    api_guard_->verify_reuse_instance();

    bool do_reuse;
    if (do_reuse_.is_set()) {
        // thank you, should_save_final_snapshot, for running this already
        do_reuse = do_reuse_.get();
        do_reuse_ = {};
    } else {
        do_reuse = decide_reuse_instance_();
    }

    // now first_run_, do_resume_ and do_init_ are also set correctly
#ifdef MUSCLE_ENABLE_MPI
    if (mpi_barrier_.is_root()) {
#endif
        bool do_implicit_checkpoint = (
                !first_run_.get() &&
                !(InstanceFlags::USES_CHECKPOINT_API & flags_) &&
                (!!(InstanceFlags::STATE_NOT_REQUIRED_FOR_NEXT_USE & flags_) or
                 !!(InstanceFlags::KEEPS_NO_STATE_FOR_NEXT_USE & flags_)));

        if (do_implicit_checkpoint) {
            if (trigger_manager_->should_save_final_snapshot(
                    do_reuse, f_init_max_timestamp_()))
                save_snapshot_({}, true, f_init_max_timestamp_());
        }

#ifdef MUSCLE_ENABLE_MPI
    }
#endif

    if (!do_reuse)
        shutdown_();

    api_guard_->reuse_instance_done(do_reuse);
    return do_reuse;
}

void Instance::Impl::error_shutdown(std::string const & message) {
#ifdef MUSCLE_ENABLE_MPI
    if (mpi_barrier_.is_root()) {
#endif
        logger_->critical("Exiting with error: ", message);
        shutdown_();
#ifdef MUSCLE_ENABLE_MPI
    }
#endif
}

::ymmsl::SettingValue Instance::Impl::get_setting(std::string const & name) const {
    return settings_manager_.get_setting(instance_name_, name);
}

/* This is a template, but it's only ever instantiated in this file,
 * namely below in the public version that calls this. So it doesn't need
 * to be in a .tpp file.
 */
template <typename ValueType>
ValueType Instance::Impl::get_setting_as(std::string const & name) const {
    return settings_manager_.get_setting(instance_name_, name).as<ValueType>();
}

std::unordered_map<::ymmsl::Operator, std::vector<std::string>>
Instance::Impl::list_ports() const {
#ifdef MUSCLE_ENABLE_MPI
    if (mpi_barrier_.is_root()) {
#endif
        return communicator_->list_ports();
#ifdef MUSCLE_ENABLE_MPI
    }
    else
        throw std::runtime_error("list_ports can only be called from the MPI root process");
#endif
}

bool Instance::Impl::is_connected(std::string const & port) const {
#ifdef MUSCLE_ENABLE_MPI
    if (mpi_barrier_.is_root()) {
#endif
    return communicator_->get_port(port).is_connected();
#ifdef MUSCLE_ENABLE_MPI
    }
    else
        throw std::runtime_error("is_connected can only be called from the MPI root process");
#endif
}

bool Instance::Impl::is_vector_port(std::string const & port) const {
#ifdef MUSCLE_ENABLE_MPI
    if (mpi_barrier_.is_root()) {
#endif
    return communicator_->get_port(port).is_vector();
#ifdef MUSCLE_ENABLE_MPI
    }
    else
        throw std::runtime_error("is_vector_port can only be called from the MPI root process");
#endif
}

bool Instance::Impl::is_resizable(std::string const & port) const {
#ifdef MUSCLE_ENABLE_MPI
    if (mpi_barrier_.is_root()) {
#endif
    return communicator_->get_port(port).is_resizable();
#ifdef MUSCLE_ENABLE_MPI
    }
    else
        throw std::runtime_error("is_resizable can only be called from the MPI root process");
#endif
}

int Instance::Impl::get_port_length(std::string const & port) const {
#ifdef MUSCLE_ENABLE_MPI
    if (mpi_barrier_.is_root()) {
#endif
    return communicator_->get_port(port).get_length();
#ifdef MUSCLE_ENABLE_MPI
    }
    else
        throw std::runtime_error("get_port_length can only be called from the MPI root process");
#endif
}

void Instance::Impl::set_port_length(std::string const & port, int length) {
#ifdef MUSCLE_ENABLE_MPI
    if (mpi_barrier_.is_root()) {
#endif
    return communicator_->get_port(port).set_length(length);
#ifdef MUSCLE_ENABLE_MPI
    }
    else
        throw std::runtime_error("set_port_length can only be called from the MPI root process");
#endif
}

void Instance::Impl::send(std::string const & port_name, Message const & message) {
#ifdef MUSCLE_ENABLE_MPI
    if (mpi_barrier_.is_root()) {
#endif
        check_port_(port_name);
        if (!message.has_settings()) {
            Message msg(message);
            msg.set_settings(settings_manager_.overlay);
            communicator_->send_message(port_name, msg);
        }
        else
            communicator_->send_message(port_name, message);
#ifdef MUSCLE_ENABLE_MPI
    }
#endif
}

void Instance::Impl::send(
        std::string const & port_name, Message const & message, int slot)
{
#ifdef MUSCLE_ENABLE_MPI
    if (mpi_barrier_.is_root()) {
#endif
        check_port_(port_name);
        if (!message.has_settings()) {
            Message msg(message);
            msg.set_settings(settings_manager_.overlay);
            communicator_->send_message(port_name, msg, slot);
        }
        else
            communicator_->send_message(port_name, message, slot);
#ifdef MUSCLE_ENABLE_MPI
    }
#endif
}

/* Register this instance with the manager.
 */
void Instance::Impl::register_() {
    ProfileEvent register_event(ProfileEventType::register_, ProfileTimestamp());
    auto locations = communicator_->get_locations();
    auto port_list = list_declared_ports_();
    manager_->register_instance(locations, port_list);
    profiler_->record_event(std::move(register_event));
    logger_->info("Registered with the manager");
}

/* Connect this instance to the given peers / conduits.
 */
void Instance::Impl::connect_() {
    ProfileEvent connect_event(ProfileEventType::connect, ProfileTimestamp());
    auto peer_info = manager_->request_peers();
    communicator_->connect(std::get<0>(peer_info), std::get<1>(peer_info), std::get<2>(peer_info));
    settings_manager_.base = manager_->get_settings();
    profiler_->record_event(std::move(connect_event));
    logger_->info("Received peer locations and base settings");
}

/* Deregister this instance from the manager.
 */
void Instance::Impl::deregister_() {
    ProfileEvent deregister_event(ProfileEventType::deregister, ProfileTimestamp());
    manager_->deregister_instance();
    profiler_->record_event(std::move(deregister_event));
    // This is the last thing we'll profile, so flush messages
    profiler_->shutdown();
    logger_->info("Deregistered from the manager");
}

void Instance::Impl::setup_checkpointing_() {
    auto checkpoint_info = manager_->get_checkpoint_info();

    auto elapsed_time = std::get<0>(checkpoint_info);
    auto checkpoints = std::get<1>(checkpoint_info);
    trigger_manager_->set_checkpoint_info(elapsed_time, checkpoints);

    auto checkpoint_support_mask = (
            InstanceFlags::USES_CHECKPOINT_API |
            InstanceFlags::KEEPS_NO_STATE_FOR_NEXT_USE |
            InstanceFlags::STATE_NOT_REQUIRED_FOR_NEXT_USE);
    if (trigger_manager_->has_checkpoints() && !(flags_ & checkpoint_support_mask)) {
        std::string msg(
                "The workflow has requested checkpoints, but this instance"
                " does not support checkpointing. Please consult the"
                " MUSCLE3 checkpointing documentation how to add"
                " checkpointing support.");
        logger_->critical(msg);
        shutdown_();
        throw std::runtime_error(msg);
    }

    auto resume_snapshot = std::get<2>(checkpoint_info);
    auto snapshot_dir = std::get<3>(checkpoint_info);
    auto saved_at = snapshot_manager_->prepare_resume(resume_snapshot, snapshot_dir);
    // resume settings overlay
    settings_manager_.overlay = snapshot_manager_->resume_overlay();

    if (saved_at.is_set())
        trigger_manager_->update_checkpoints(saved_at.get());
}

Message Instance::Impl::receive_message(
                std::string const & port_name,
                Optional<int> slot,
                Optional<Message> default_msg,
                bool with_settings)
{
    Message result(-1.0, Data());
#ifdef MUSCLE_ENABLE_MPI
    if (mpi_barrier_.is_root()) {
#endif
        check_port_(port_name);

        Reference port_ref(port_name);
        auto const & port = communicator_->get_port(port_name);
        if (port.oper == Operator::F_INIT) {
            if (slot.is_set())
                port_ref += slot.get();

            if (f_init_cache_.count(port_ref) == 1) {
                result = f_init_cache_.at(port_ref);
                f_init_cache_.erase(port_ref);

                if (with_settings && !result.has_settings()) {
                    std::string msg(
                            "If you use receive_with_settings() on an F_INIT"
                            " port, then you have to set the flag"
                            " 'InstanceFlags::DONT_APPLY_OVERLAY' when constructing"
                            " the Instance, otherwise the settings will"
                            " already have been applied by MUSCLE.");
                    logger_->critical(msg);
                    shutdown_();
                    throw std::logic_error(msg);
                }
            }
            else {
                if (port.is_connected()) {
                    std::ostringstream oss;
                    oss << "Tried to receive twice on the same port '";
                    oss << port_ref << "' in a single F_INIT, that's not possible.";
                    oss << " Did you forget to call reuse_instance() in your reuse";
                    oss << " loop?";
                    logger_->critical(oss.str());
                    shutdown_();
                    throw std::logic_error(oss.str());
                }
                else {
                    if (default_msg.is_set())
                        result = default_msg.get();
                    else {
                        std::ostringstream oss;
                        oss << "Tried to receive on port '" << port_ref << "', which";
                        oss << " is not connected, and no default value was given.";
                        oss << " Please connect this port!";
                        logger_->critical(oss.str());
                        shutdown_();
                        throw std::logic_error(oss.str());
                    }
                }
            }
        }
        else {
            result = communicator_->receive_message(port_name, slot, default_msg);
            if (port.is_connected() && !port.is_open(slot)) {
                std::ostringstream oss;
                oss << "Port '" << port_ref << "' is closed, but we're trying to";
                oss << " receive on it. Did the peer crash?";
                logger_->critical(oss.str());
                shutdown_();
                throw std::runtime_error(oss.str());
            }
            if (port.is_connected() && !with_settings)
                check_compatibility_(port_name, result.settings());
            if (!with_settings)
                result.unset_settings();
        }
#ifdef MUSCLE_ENABLE_MPI
        mpi_barrier_.signal();
    }
    else
        mpi_barrier_.wait();
#endif
    return result;
}

bool Instance::Impl::resuming() {
    api_guard_->verify_resuming();
    api_guard_->resuming_done(do_resume_);
    return do_resume_;
}

bool Instance::Impl::should_init() {
    api_guard_->verify_should_init();
    api_guard_->should_init_done();
    return do_init_;
}

Message Instance::Impl::load_snapshot() {
    api_guard_->verify_load_snapshot();
    auto result = snapshot_manager_->load_snapshot();
    api_guard_->load_snapshot_done();
    return result;
}

bool Instance::Impl::should_save_snapshot(double timestamp) {
    api_guard_->verify_should_save_snapshot();
    auto result = trigger_manager_->should_save_snapshot(timestamp);
    api_guard_->should_save_snapshot_done(result);
    return result;
}

void Instance::Impl::save_snapshot(Message message) {
    api_guard_->verify_save_snapshot();
    save_snapshot_(message, false, {});
    api_guard_->save_snapshot_done();
}

bool Instance::Impl::should_save_final_snapshot() {
    api_guard_->verify_should_save_final_snapshot();

    do_reuse_ = decide_reuse_instance_();
    auto result = trigger_manager_->should_save_final_snapshot(
            do_reuse_.get(), f_init_max_timestamp_());

    api_guard_->should_save_final_snapshot_done(result);
    return result;
}

void Instance::Impl::save_final_snapshot(Message message) {
    api_guard_->verify_save_final_snapshot();
    save_snapshot_(message, true, f_init_max_timestamp_());
    api_guard_->save_final_snapshot_done();
}

/* Returns instance name.
 *
 * This takes the argument to the --muscle-instance= command-line option and
 * returns it as a Reference.
 */
Reference Instance::Impl::make_full_name_(int argc, char const * const argv[]) const {
    std::string prefix_tag("--muscle-instance=");
    for (int i = 1; i < argc; ++i) {
        if (strncmp(argv[i], prefix_tag.c_str(), prefix_tag.size()) == 0) {
            std::string prefix_str(argv[i] + prefix_tag.size());
            return Reference(prefix_str);
        }
    }
    char * prefix_str = getenv("MUSCLE_INSTANCE");
    if (prefix_str != nullptr)
        return Reference(prefix_str);
    throw std::runtime_error("A --muscle-instance command line argument or"
            " MUSCLE_INSTANCE environment variable is required to"
            " identify this instance. Please add one.");
}

/* Gets the manager network location from the command line.
 *
 * We use a --muscle-manager=<host:port> argument to tell the MUSCLE library
 * how to connect to the manager. This function will extract this argument
 * from the command line arguments, if it is present.
 *
 * If not, it will check the MUSCLE_MANAGER environment variable, and if that
 * is not set, fall back to the default.
 */
std::string Instance::Impl::extract_manager_location_(
        int argc, char const * const argv[]) const
{
    std::string prefix_tag("--muscle-manager=");
    for (int i = 1; i < argc; ++i)
        if (strncmp(argv[i], prefix_tag.c_str(), prefix_tag.size()) == 0)
            return std::string(argv[i] + prefix_tag.size());

    char * prefix = getenv("MUSCLE_MANAGER");
    if (prefix != nullptr)
        return std::string(prefix);

    return "tcp:localhost:9000";
}

/* Returns the component name of this instance, i.e. without the index.
 */
Reference Instance::Impl::name_() const {
    auto it = instance_name_.cbegin();
    while (it != instance_name_.cend() && it->is_identifier())
        ++it;

    return Reference(instance_name_.cbegin(), it);
}

/* Returns the index of this instance, i.e. without the component.
 */
std::vector<int> Instance::Impl::index_() const {
    std::vector<int> result;
    auto it = instance_name_.cbegin();
    while (it != instance_name_.cend() && it->is_identifier())
        ++it;

    while (it != instance_name_.cend() && it->is_index()) {
        result.push_back(it->index());
        ++it;
    }
    return result;
}

/* Returns a list of declared ports for this instance.
 *
 * This returns a list of ymmsl::Port objects, which have only the name and
 * operator, not libmuscle::Port, which has more.
 */
std::vector<::ymmsl::Port> Instance::Impl::list_declared_ports_() const {
    std::vector<::ymmsl::Port> result;
    for (auto const & oper_ports : declared_ports_) {
        for (auto const & fullname : oper_ports.second) {
            std::string portname(fullname);
            if (fullname.size() > 2 && fullname.substr(fullname.size() - 2) == "[]")
                portname = fullname.substr(0, fullname.size() - 2);
            result.push_back(::ymmsl::Port(portname, oper_ports.first));
        }
    }
    return result;
}

/* Checks that the given port exists, error-exits if not.
 *
 * @param port_name The name of the port to check.
 */
void Instance::Impl::check_port_(std::string const & port_name) {
    if (!communicator_->port_exists(port_name)) {
        std::ostringstream oss;
        oss << "Port '" << port_name << "' does not exist on '";
        oss << instance_name_ << "'. Please check the name and the list of";
        oss << " ports you gave for this component.";
        logger_->critical(oss.str());
        shutdown_();
        throw std::logic_error(oss.str());
    }
}

/* Receives settings on muscle_settings_in.
 *
 * @return false iff the port is connected and ClosePort was received.
 */
bool Instance::Impl::receive_settings_() {
    Message default_message(0.0, Settings(), Settings());
    auto msg = communicator_->receive_message("muscle_settings_in", {}, default_message);
    if (is_close_port(msg.data()))
        return false;

    if (!msg.data().is_a<Settings>()) {
        std::ostringstream oss;
        oss << "'" << instance_name_ << "' received a message on";
        oss << " muscle_settings_in that is not a Settings. It seems that the";
        oss << " simulation is miswired or the sending instance is broken.";
        logger_->critical(oss.str());
        shutdown_();
        throw std::logic_error(oss.str());
    }

    Settings settings(msg.settings());
    for (auto const & key_val : msg.data().as<Settings>())
        settings[key_val.first] = key_val.second;
    settings_manager_.overlay = settings;
    return true;
}

/** Checks whether we have connected F_INIT ports.
 *
 * This includes muscle_settings_in, and any user-defined ports.
 */
bool Instance::Impl::have_f_init_connections_() {
    auto ports = communicator_->list_ports();
    if (ports.count(Operator::F_INIT) != 0)
        for (auto const & port : ports.at(Operator::F_INIT))
            if (communicator_->get_port(port).is_connected())
                return true;
    return communicator_->settings_in_connected();
}

/** Pre-receives on all ports.
 *
 * This includes muscle_settings_in and all user-defined ports.
 *
 * @return true iff no ClosePort messages were received.
 */
bool Instance::Impl::pre_receive_() {
    bool all_ports_open = receive_settings_();
    pre_receive_f_init_();
    for (auto const & ref_msg : f_init_cache_)
        if (is_close_port(ref_msg.second.data()))
                all_ports_open = false;
    return all_ports_open;
}

/* Pre-receive on the given port and slot, if any.
 */
void Instance::Impl::pre_receive_(
        std::string const & port_name, Optional<int> slot) {
    Reference port_ref(port_name);
    if (slot.is_set())
        port_ref += slot.get();

    Message msg = communicator_->receive_message(port_name, slot);
    bool apply_overlay = !(flags_ & InstanceFlags::DONT_APPLY_OVERLAY);
    if (apply_overlay) {
        apply_overlay_(msg);
        check_compatibility_(port_name, msg.settings());
        msg.unset_settings();
    }
    f_init_cache_.emplace(port_ref, msg);
}

/* Receives on all ports connected to F_INIT.
 *
 * This receives all incoming messages on F_INIT and stores them in
 * f_init_cache_.
 */
void Instance::Impl::pre_receive_f_init_() {
    f_init_cache_.clear();
    auto ports = communicator_->list_ports();
    if (ports.count(Operator::F_INIT) == 1) {
        for (auto const & port_name : ports.at(Operator::F_INIT)) {
            logger_->debug("Pre-receiving on port ", port_name);
            auto const & port = communicator_->get_port(port_name);
            if (!port.is_connected())
                continue;
            if (!port.is_vector())
                pre_receive_(port_name, {});
            else {
                pre_receive_(port_name, 0);
                // The above receives the length, if needed, so now we can get
                // the rest.
                for (int slot = 1; slot < port.get_length(); ++slot)
                    pre_receive_(port_name, slot);
            }
        }
    }
}

/** Return max timestamp of pre-received F_INIT messages
 */
Optional<double> Instance::Impl::f_init_max_timestamp_() {
    Optional<double> result;
    for (auto const & ref_msg : f_init_cache_) {
        auto timestamp = ref_msg.second.timestamp();
        if (!result.is_set() || result.get() < timestamp)
            result = timestamp;
    }
    return result;
}

/** Decide whether and how to reuse the instance.
 *
 * This sets self._first_run, self._do_resume and self._do_init, and
 * returns whether to reuse one more time. This is the real top of
 * the reuse loop, and it gets called by reuse_instance and
 * should_save_final_snapshot.
 */
bool Instance::Impl::decide_reuse_instance_() {
    if (!first_run_.is_set())
        first_run_ = true;
    else
        first_run_ = false;

    bool do_reuse;

#ifdef MUSCLE_ENABLE_MPI
    if (mpi_barrier_.is_root()) {
#endif
        bool f_init_connected = have_f_init_connections_();
        if (first_run_.get() && snapshot_manager_->resuming_from_intermediate()) {
            // resume from intermediate
            do_resume_ = true;
            do_init_ = false;
            do_reuse = true;
        } else if (first_run_.get() && snapshot_manager_->resuming_from_final()) {
            // resume from final
            if (f_init_connected) {
                bool got_f_init_messages = pre_receive_();
                do_resume_ = true;
                do_init_ = true;
                do_reuse = got_f_init_messages;
            } else {
                do_resume_ = false;
                do_init_ = false;
                do_reuse = false;
            }
        } else {
            // fresh start or resuming from implicit snapshot
            do_resume_ = false;

            if (!f_init_connected) {
                // simple straight single run without resuming
                do_init_ = first_run_.get();
                do_reuse = first_run_.get();
            } else {
                // not resuming and f_init connected, run while we get messages
                bool got_f_init_messages = pre_receive_();
                do_init_ = got_f_init_messages;
                do_reuse = got_f_init_messages;
            }
        }

#ifdef MUSCLE_ENABLE_MPI
        mpi_barrier_.signal();
        int do_reuse_mpi[3] = {do_reuse, do_resume_, do_init_};
        MPI_Bcast(do_reuse_mpi, 3, MPI_INT, mpi_root_, mpi_comm_);
    } else {
        mpi_barrier_.wait();
        int do_reuse_mpi[3];
        MPI_Bcast(do_reuse_mpi, 3, MPI_INT, mpi_root_, mpi_comm_);
        do_reuse = do_reuse_mpi[0];
        do_resume_ = do_reuse_mpi[1];
        do_init_ = do_reuse_mpi[2];
    }
#endif

#ifdef MUSCLE_ENABLE_MPI
    if (mpi_barrier_.is_root()) {
        auto soverlay_data = Data(settings_manager_.overlay);
        msgpack::sbuffer sbuf;
        msgpack::pack(sbuf, soverlay_data);
        int size = sbuf.size();
        MPI_Bcast(&size, 1, MPI_INT, mpi_root_, mpi_comm_);
        MPI_Bcast(sbuf.data(), size, MPI_CHAR, mpi_root_, mpi_comm_);
    }
    else {
        int size;
        MPI_Bcast(&size, 1, MPI_INT, mpi_root_, mpi_comm_);
        std::vector<char> buf(size);
        MPI_Bcast(&buf[0], size, MPI_CHAR, mpi_root_, mpi_comm_);
        auto zone = std::make_shared<msgpack::zone>();
        DataConstRef soverlay_data = mcp::unpack_data(zone, &buf[0], size);
        settings_manager_.overlay = soverlay_data.as<Settings>();
    }
#endif

    return do_reuse;
}

/** Save a snapshot to disk and notify manager.
 *
 * @param message The data to save.
 * @param final Whether this is a final snapshot or an intermediate one.
 * @param f_init_max_timestamp Timestamp for final snapshots.
 */
void Instance::Impl::save_snapshot_(
        Optional<Message> message, bool final,
        Optional<double> f_init_max_timestamp) {
    auto triggers = trigger_manager_->get_triggers();
    auto walltime = trigger_manager_->elapsed_walltime();
    auto timestamp = snapshot_manager_->save_snapshot(
            message, final, triggers, walltime,
            f_init_max_timestamp, settings_manager_.overlay);
    trigger_manager_->update_checkpoints(timestamp);
}

/* Sets the level a log message must have to be printed locally.
 *
 * It gets this from the muscle_local_log_level setting.
 */
void Instance::Impl::set_local_log_level_() {
    try {
        std::string log_level_str = settings_manager_.get_setting(
               instance_name_, "muscle_local_log_level").as<std::string>();

        LogLevel level = string_to_level(log_level_str);
        logger_->set_local_level(level);
    }
    catch (std::runtime_error const & e) {
        logger_->error(e.what() + std::string(" in muscle_local_log_level"));
    }
    catch (std::out_of_range const &) {
        // muscle_local_log_level not set, do nothing and keep the default
    }
}

/* Sets the level a log message must have to be sent to the manager.
 *
 * It gets this from the muscle_remote_log_level setting.
 */
void Instance::Impl::set_remote_log_level_() {
    try {
        std::string log_level_str = settings_manager_.get_setting(
               instance_name_, "muscle_remote_log_level").as<std::string>();

        LogLevel level = string_to_level(log_level_str);
        logger_->set_remote_level(level);
    }
    catch (std::runtime_error const & e) {
        logger_->error(e.what() + std::string(" in muscle_remote_log_level"));
    }
    catch (std::out_of_range const &) {
        // muscle_remote_log_level not set, do nothing and keep the default
    }
}

/* Sets local overlay if we don't already have one.
 *
 * @param message The message to apply the overlay from.
 */
void Instance::Impl::apply_overlay_(Message const & message) {
    if (settings_manager_.overlay.empty())
        if (message.has_settings())
            settings_manager_.overlay = message.settings();
}

/* Checks whether a received overlay matches the current one.
 *
 * @param port_name Name of the port on which the overlay was received.
 * @param overlay The received overlay.
 */
void Instance::Impl::check_compatibility_(
        std::string const & port_name,
        Optional<Settings> const & overlay)
{
    if (!overlay.is_set())
        return;
    if (settings_manager_.overlay != overlay.get()) {
        std::ostringstream oss;
        oss << "Unexpectedly received data from a parallel universe on port";
        oss << " '" << port_name << "'. My settings are '";
        oss << settings_manager_.overlay << "' and I received from a";
        oss << " universe with '" << overlay << "'.";
        logger_->critical(oss.str());
        shutdown_();
        throw std::logic_error(oss.str());
    }
}


/* Closes outgoing ports.
 *
 * This sends a close port message on all slots of all outgoing ports.
 */
void Instance::Impl::close_outgoing_ports_() {
    for (auto const & oper_ports : communicator_->list_ports()) {
        if (allows_sending(oper_ports.first)) {
            for (auto const & port_name : oper_ports.second) {
                auto const & port = communicator_->get_port(port_name);
                if (port.is_vector()) {
                    for (int slot = 0; slot < port.get_length(); ++slot)
                        communicator_->close_port(port_name, slot);
                }
                else
                    communicator_->close_port(port_name);
            }
        }
    }
}

/* Receives messages until a ClosePort is received.
 *
 * Receives at least once.
 *
 * @param port_name Port to drain.
 */
void Instance::Impl::drain_incoming_port_(std::string const & port_name) {
    auto const & port = communicator_->get_port(port_name);
    while (port.is_open())
        communicator_->receive_message(port_name);
}

/* Receives messages until a ClosePort is received.
 *
 * Works with (resizable) vector ports.
 *
 * @param port_name Port to drain.
 */
void Instance::Impl::drain_incoming_vector_port_(std::string const & port_name) {
    auto const & port = communicator_->get_port(port_name);

    bool all_closed = true;
    for (int slot = 0; slot < port.get_length(); ++slot)
        if (port.is_open(slot))
            all_closed = false;

    while (!all_closed) {
        all_closed = true;
        for (int slot = 0; slot < port.get_length(); ++slot) {
            if (port.is_open(slot))
                communicator_->receive_message(port_name, slot);
            if (port.is_open(slot))
                all_closed = false;
        }
    }
}

/* Closes incoming ports.
 *
 * This receives on all incoming ports until a ClosePort is received on them,
 * signaling that there will be no more messages, and allowing the sending
 * instance to shut down cleanly.
 */
void Instance::Impl::close_incoming_ports_() {
    for (auto const & oper_ports : communicator_->list_ports()) {
        if (allows_receiving(oper_ports.first)) {
            for (auto const & port_name : oper_ports.second) {
                auto const & port = communicator_->get_port(port_name);
                if (!port.is_connected())
                    continue;
                if (port.is_vector())
                    drain_incoming_vector_port_(port_name);
                else
                    drain_incoming_port_(port_name);
            }
        }
    }
}

/* Closes all ports.
 *
 * This sends a close port message on all slots of all outgoing ports, then
 * receives one on all incoming ports.
 */
void Instance::Impl::close_ports_() {
    close_outgoing_ports_();
    close_incoming_ports_();
}

/* Shuts down communication with the outside world and deregisters.
 */
void Instance::Impl::shutdown_() {
    if (!is_shut_down_) {
#ifdef MUSCLE_ENABLE_MPI
        if (mpi_barrier_.is_root()) {
#endif
            close_ports_();
            communicator_->shutdown();
            deregister_();
            manager_->close();
#ifdef MUSCLE_ENABLE_MPI
        }
        mpi_barrier_.shutdown();
        MPI_Comm_free(&mpi_comm_);
#endif
        is_shut_down_ = true;
    }
}


/* Below is the implementation of the public interface.
 *
 * These just forward to the hidden implementations above.
 */

#ifdef MUSCLE_ENABLE_MPI
#define MPI_ARGS_DECL , MPI_Comm const & communicator, int root
#define MPI_ARGS_CALL , communicator, root
#else
#define MPI_ARGS_DECL
#define MPI_ARGS_CALL
#endif

Instance::Instance(
        int argc, char const * const argv[]
        MPI_ARGS_DECL)
    : pimpl_(new Impl(argc, argv, {}, InstanceFlags::NONE MPI_ARGS_CALL))
{}

Instance::Instance(
        int argc, char const * const argv[],
        PortsDescription const & ports
        MPI_ARGS_DECL)
    : pimpl_(new Impl(argc, argv, ports, InstanceFlags::NONE MPI_ARGS_CALL))
{}

Instance::Instance(
        int argc, char const * const argv[],
        InstanceFlags flags
        MPI_ARGS_DECL)
    : pimpl_(new Impl(argc, argv, {}, flags MPI_ARGS_CALL))
{}

Instance::Instance(
        int argc, char const * const argv[],
        PortsDescription const & ports,
        InstanceFlags flags
        MPI_ARGS_DECL)
    : pimpl_(new Impl(argc, argv, ports, flags MPI_ARGS_CALL))
{}

Instance::~Instance() = default;

bool Instance::reuse_instance() {
    return impl_()->reuse_instance();
}

void Instance::error_shutdown(std::string const & message) {
    impl_()->error_shutdown(message);
}

::ymmsl::SettingValue Instance::get_setting(std::string const & name) const {
    return impl_()->get_setting(name);
}

/* This is instantiated explicitly, it's the only way to do this with a
 * pImpl. Fortunately, we don't allow arbitrary types for settings, so it
 * works this way.
 */
template <typename ValueType>
ValueType Instance::get_setting_as(std::string const & name) const {
    return impl_()->get_setting_as<ValueType>(name);
}

/** This keeps Doxygen from getting confused.
 * \cond
 */
template std::string Instance::get_setting_as<std::string>(std::string const & name) const;
template int64_t Instance::get_setting_as<int64_t>(std::string const & name) const;
template double Instance::get_setting_as<double>(std::string const & name) const;
template bool Instance::get_setting_as<bool>(std::string const & name) const;
template std::vector<double> Instance::get_setting_as<std::vector<double>>(
        std::string const & name) const;
template std::vector<std::vector<double>> Instance::get_setting_as<std::vector<std::vector<double>>>(
        std::string const & name) const;
/** \endcond
 */

std::unordered_map<::ymmsl::Operator, std::vector<std::string>>
Instance::list_ports() const {
    return impl_()->list_ports();
}

bool Instance::is_connected(std::string const & port) const {
    return impl_()->is_connected(port);
}

bool Instance::is_vector_port(std::string const & port) const {
    return impl_()->is_vector_port(port);
}

bool Instance::is_resizable(std::string const & port) const {
    return impl_()->is_resizable(port);
}

int Instance::get_port_length(std::string const & port) const {
    return impl_()->get_port_length(port);
}

void Instance::set_port_length(std::string const & port, int length) {
    impl_()->set_port_length(port, length);
}

void Instance::send(std::string const & port_name, Message const & message) {
    impl_()->send(port_name, message);
}

void Instance::send(
        std::string const & port_name, Message const & message, int slot)
{
    impl_()->send(port_name, message, slot);
}

Message Instance::receive(std::string const & port_name) {
    return impl_()->receive_message(port_name, {}, {}, false);
}

Message Instance::receive(
        std::string const & port_name,
        int slot)
{
    return impl_()->receive_message(port_name, slot, {}, false);
}

Message Instance::receive(
        std::string const & port_name, Message const & default_msg)
{
    return impl_()->receive_message(port_name, {}, default_msg, false);
}

Message Instance::receive(
        std::string const & port_name,
        int slot,
        Message const & default_msg)
{
    return impl_()->receive_message(port_name, slot, default_msg, false);
}

Message Instance::receive_with_settings(std::string const & port_name) {
    return impl_()->receive_message(port_name, {}, {}, true);
}

Message Instance::receive_with_settings(
        std::string const & port_name,
        int slot)
{
    return impl_()->receive_message(port_name, slot, {}, true);
}

Message Instance::receive_with_settings(
        std::string const & port_name, Message const & default_msg)
{
    return impl_()->receive_message(port_name, {}, default_msg, true);
}


Message Instance::receive_with_settings(
        std::string const & port_name,
        int slot,
        Message const & default_msg)
{
    return impl_()->receive_message(port_name, slot, default_msg, true);
}

bool Instance::resuming() {
    return impl_()->resuming();
}

bool Instance::should_init() {
    return impl_()->should_init();
}

Message Instance::load_snapshot() {
    return impl_()->load_snapshot();
}

bool Instance::should_save_snapshot(double timestamp) {
    return impl_()->should_save_snapshot(timestamp);
}

void Instance::save_snapshot(Message message) {
    impl_()->save_snapshot(message);
}

bool Instance::should_save_final_snapshot() {
    return impl_()->should_save_final_snapshot();
}

void Instance::save_final_snapshot(Message message) {
    impl_()->save_final_snapshot(message);
}

Instance::Impl const * Instance::impl_() const {
    return pimpl_.get();
}

Instance::Impl * Instance::impl_() {
    return pimpl_.get();
}

} }

