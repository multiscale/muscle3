#pragma once

#include <libmuscle/message.hpp>
#include <libmuscle/namespace.hpp>
#include <libmuscle/ports_description.hpp>

#ifdef MUSCLE_ENABLE_MPI
#include <mpi.h>
#endif

#include <ymmsl/ymmsl.hpp>

#include <memory>
#include <string>
#include <vector>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

/** Enumeration of properties that an instance may have.
 *
 * You may combine multiple flags using the bitwise OR operator `|`. For example:
 *
 * \code{cpp}
 *      auto flags = InstanceFlags::DONT_APPLY_OVERLAY | InstanceFlags::USES_CHECKPOINT_API;
 *      Instance instance(argc, argv, flags);
 * \endcode
 */
enum class InstanceFlags : int {
    NONE = 0,

    /**
     * Do not apply the received settings overlay during prereceive of F_INIT
     * messages. If you're going to use Instance.receive_with_settings on
     * your F_INIT ports, you need to set this flag when creating an
     * Instance.
     *
     * If you don't know what that means, do not specify this flag and everything
     * will be fine. If it turns out that you did need to specify the flag, MUSCLE3
     * will tell you about it in an error message and you can add it still.
     */
    DONT_APPLY_OVERLAY = 1,

    /** Indicate that this instance supports checkpointing.
     *
     * You may not use any checkpointing API calls when this flag is not supplied.
     */
    USES_CHECKPOINT_API = 2,

    /** Indicate this instance does not carry state between iterations of the
     * reuse loop. Specifying this flag is equivalent to
     * `ymmsl.KeepsStateForNextUse.NO`.
     *
     * By default, (if neither KEEPS_NO_STATE_FOR_NEXT_USE nor
     * STATE_NOT_REQUIRED_FOR_NEXT_USE are provided), the instance is assumed
     * to keep state between reuses, and to require that state (equivalent to
     * `ymmsl.KeepsStateForNextUse.NECESSARY`).
     */
    KEEPS_NO_STATE_FOR_NEXT_USE = 4,

    /** Indicate this instance carries state between iterations of the
     * reuse loop, however this state is not required for restarting.
     * Specifying this flag is equivalent to `ymmsl.KeepsStateForNextUse.HELPFUL`.
     *
     * By default, (if neither KEEPS_NO_STATE_FOR_NEXT_USE nor
     * STATE_NOT_REQUIRED_FOR_NEXT_USE are provided), the instance is assumed
     * to keep state between reuses, and to require that state (equivalent to
     * `ymmsl.KeepsStateForNextUse.NECESSARY`).
     */
    STATE_NOT_REQUIRED_FOR_NEXT_USE = 8,
};

inline InstanceFlags operator|(InstanceFlags a, InstanceFlags b) {
    return static_cast<InstanceFlags>(static_cast<int>(a) | static_cast<int>(b));
}

inline InstanceFlags operator&(InstanceFlags a, InstanceFlags b) {
    return static_cast<InstanceFlags>(static_cast<int>(a) & static_cast<int>(b));
}

inline bool operator!(InstanceFlags a) {
    return a == InstanceFlags::NONE;
}

/** Represents a component instance in a MUSCLE3 simulation.
 *
 * This class provides a low-level send/receive API for the instance to use.
 */
class Instance {
    public:
        /** Create an Instance.
         *
         * For MPI-based components, creating an Instance is a
         * collective operation, so it must be done in all processes
         * simultaneously, with the same communicator and the same root.
         *
         * @param argc The number of command-line arguments.
         * @param argv Command line arguments.
         * @param communicator MPI communicator containing all processes in
         *      this instance (MPI only).
         * @param root The designated root process (MPI only).
         */
        Instance(
                int argc, char const * const argv[]
#ifdef MUSCLE_ENABLE_MPI
                , MPI_Comm const & communicator = MPI_COMM_WORLD
                , int root = 0
#endif
                );

        /** Create an instance.
         *
         * A PortsDescription can be written like this:
         *
         * PortsDescription ports({
         *     {Operator::F_INIT, {"port1", "port2"}},
         *     {Operator::O_F, {"port3[]"}}
         *     });
         *
         * For MPI-based components, creating an Instance is a
         * collective operation, so it must be done in all processes
         * simultaneously, with the same communicator and the same root.
         *
         * @param argc The number of command-line arguments.
         * @param argv Command line arguments.
         * @param ports A description of the ports that this instance has.
         * @param communicator MPI communicator containing all processes in
         *      this instance (MPI only).
         * @param root The designated root process (MPI only).
         */
        Instance(
                int argc, char const * const argv[],
                PortsDescription const & ports
#ifdef MUSCLE_ENABLE_MPI
                , MPI_Comm const & communicator = MPI_COMM_WORLD
                , int root = 0
#endif
                );

        /** Create an Instance.
         *
         * For MPI-based components, creating an Instance is a
         * collective operation, so it must be done in all processes
         * simultaneously, with the same communicator and the same root.
         *
         * @param argc The number of command-line arguments.
         * @param argv Command line arguments.
         * @param flags InstanceFlags for this instance.
         * @param communicator MPI communicator containing all processes in
         *      this instance (MPI only).
         * @param root The designated root process (MPI only).
         */
        Instance(
                int argc, char const * const argv[],
                InstanceFlags flags
#ifdef MUSCLE_ENABLE_MPI
                , MPI_Comm const & communicator = MPI_COMM_WORLD
                , int root = 0
#endif
                );

        /** Create an instance.
         *
         * A PortsDescription can be written like this:
         *
         * PortsDescription ports({
         *     {Operator::F_INIT, {"port1", "port2"}},
         *     {Operator::O_F, {"port3[]"}}
         *     });
         *
         * For MPI-based components, creating an Instance is a
         * collective operation, so it must be done in all processes
         * simultaneously, with the same communicator and the same root.
         *
         * @param argc The number of command-line arguments.
         * @param argv Command line arguments.
         * @param ports A description of the ports that this instance has.
         * @param flags InstanceFlags for this instance.
         * @param communicator MPI communicator containing all processes in
         *      this instance (MPI only).
         * @param root The designated root process (MPI only).
         */
        Instance(
                int argc, char const * const argv[],
                PortsDescription const & ports,
                InstanceFlags flags
#ifdef MUSCLE_ENABLE_MPI
                , MPI_Comm const & communicator = MPI_COMM_WORLD
                , int root = 0
#endif
                );

        ~Instance();
        Instance(Instance const &);
        Instance(Instance &&);
        Instance & operator=(Instance const &);
        Instance & operator=(Instance &&);

        /** Decide whether to run this instance again.
         *
         * In a multiscale simulation, instances get reused all the time.
         * For example, in a macro-micro simulation, the micromodel does a
         * complete run for every timestep of the macromodel. Rather than
         * starting up a new instance of the micromodel, which could be
         * expensive, we reuse a single instance many times.
         *
         * This may bring other advantages, such as faster convergence
         * when starting from the previous final state, and in some
         * cases may be necessary if micromodel state needs to be
         * preserved from one macro timestep to the next.
         *
         * So in MUSCLE, submodels run in a *reuse loop*, which runs them
         * over and over again until their work is done and they should be
         * shut down. Whether to do another F_INIT, O_I, S, O_F cycle
         * is decided by this method.
         *
         * This method must be called at the beginning of the reuse loop,
         * i.e. before the F_INIT operator, and its return value should
         * decide whether to enter that loop again.
         *
         * MPI-based components must execute the reuse loop in each
         * process in parallel, and call this function at the top of the
         * reuse loop in each process.
         */
        bool reuse_instance();

        /** Logs an error and shuts down the Instance.
         *
         * If you detect that something is wrong (invalid input, invalid
         * settings, simulation diverged, or anything else really), you
         * should call this method before calling exit() or raising
         * an exception that you don't expect to catch.
         *
         * If you do so, the Instance will tell the rest of the simulation
         * that it encountered an error and will shut down. That makes it
         * easier to debug the situation (the message will be logged), and
         * it reduces the chance that other parts of the simulation will
         * sit around waiting forever for a message that this instance was
         * supposed to send.
         *
         * MPI-based components may either call this function in all
         * processes, or only in the root process (as passed to the
         * constructor).
         *
         * @param message An error message describing the problem.
         */
        void error_shutdown(std::string const & message);

        /** List settings by name.
         *
         * This function returns a list of names of the available settings.
         *
         * @return A list of setting names.
         */
        std::vector<std::string> list_settings() const;

        /** Returns the value of a model setting.
         *
         * MPI-based components may call this function at any time
         * within the reuse loop, in any or all processes, simultaneously or
         * not.
         *
         * @param name The name of the setting, without any instance prefix.
         *
         * @return The value of the setting as a generic SettingValue.
         *
         * @throw std::out_of_range if no setting with the given name exists.
         */
        ::ymmsl::SettingValue get_setting(std::string const & name) const;

        /** Returns the value of a model setting.
         *
         * MPI-based components may call this function at any time
         * within the reuse loop, in any or all processes, simultaneously or
         * not.
         *
         * @tparam ValueType The (expected) type of the setting. Needs to
         *      match exactly or an exception will be thrown, this will not
         *      convert e.g. an integer into a string.
         * @param name The name of the setting, without any instance prefix.
         *
         * @return The value of the setting as a ValueType
         *
         * @throw std::out_of_range if no setting with the given name exists.
         * @throw std::bad_cast if the value is not of the specified type.
         */
        template <typename ValueType>
        ValueType get_setting_as(std::string const & name) const;

        /** Returns a description of the ports that this CE has.
         *
         * Note that the result has almost the same format as the port
         * declarations you pass when making an Instance. The only
         * difference is that the port names never have `[]` at the end, even
         * if the port is a vector port.
         *
         * MPI-based components may call this function only in the
         * root process.
         *
         * @return A map, indexed by operator, containing lists of port names.
         *      Operators with no associated ports are not included.
         */
        std::unordered_map<::ymmsl::Operator, std::vector<std::string>>
        list_ports() const;

        /** Returns whether the given port is connected.
         *
         * MPI-based components may call this function only in the
         * root process.
         *
         * @param port The name of the port to inspect.
         * @return true if there is a conduit attached to this port, false if
         *      not.
         */
        bool is_connected(std::string const & port) const;

        /** Returns whether a port is a vector or scalar port.
         *
         * If a port has been declared to be a vector port (i.e. the name
         * passed when creating this Instance had '[]' at the end), then you
         * can pass a 'slot' argument when sending or receiving. It's like the
         * port is a vector of slots on which you can send or receive messages.
         *
         * MPI-based components may call this function only in the
         * root process.
         *
         * This function returns True if the given port is a vector port, and
         * False if it is a scalar port.
         *
         * @param port The port to check this property of.
         */
        bool is_vector_port(std::string const & port) const;

        /** Returns whether the given port is resizable.
         *
         * Scalar ports are never resizable. Whether a vector port is resizable
         * depends on what it is connected to.
         *
         * MPI-based components may call this function only in the
         * root process.
         *
         * @param port Name of the port to inspect.
         *
         * @return: true if the port can be resized, false if not.
         */
        bool is_resizable(std::string const & port) const;

        /** Returns the current length of the port.
         *
         * MPI-based components may call this function only in the
         * root process.
         *
         * @param port The name of the port to measure.
         *
         * @throw std::runtime_error if this is a scalar port.
         */
        int get_port_length(std::string const & port) const;

        /** Resizes the port to the given length.
         *
         * You should check whether the port is resizable using is_resizable()
         * first; whether it is depends on how this component is wired up,
         * so you should check.
         *
         * MPI-based components may call this function only in the
         * root process.
         *
         * @param port Name of the port to resize.
         * @param length The new length.
         *
         * @throw std::runtime_error if the port is not resizable.
         */
        void set_port_length(std::string const & port, int length);

        /** Send a message to the outside world.
         *
         * Sending is non-blocking, a copy of the message will be made and
         * stored until the receiver is ready to receive it.
         *
         * MPI-based components may call this function either in all
         * processes, or only in the root process. In both cases, the message
         * given by the root process will be sent, the others ignored.
         *
         * @param port_name The port on which this message is to be sent.
         * @param message The message to be sent.
         */
        void send(std::string const & port_name, Message const & message);

        /** Send a message to the outside world.
         *
         * Sending is non-blocking, a copy of the message will be made and
         * stored until the receiver is ready to receive it.
         *
         * MPI-based components may call this function either in all
         * processes, or only in the root process. In both cases, the message
         * given by the root process will be sent, the others ignored. You may
         * want to do a gather operation first to collect all the information
         * that is to be sent in the root process.
         *
         * @param port_name The port on which this message is to be sent.
         * @param message The message to be sent.
         * @param slot The slot to send the message on.
         */
        void send(std::string const & port_name, Message const & message,
                int slot);

        /** Receive a message from the outside world.
         *
         * Receiving is a blocking operation. This function will contact the
         * sender, wait for a message to be available, and receive and return
         * it.
         *
         * If the port you are receiving on is not connected, an exception will
         * be thrown.
         *
         * MPI-based components must call this function in all processes
         * simultaneously. The received message will be returned in the root
         * process, all other processes will receive a dummy message. It is
         * therefore up to the model code to scatter or broadcast the received
         * message to the non-root processes, if necessary.
         *
         * @param port_name The endpoint on which a message is to be received.
         *
         * @return The received message. The settings attribute of the received
         *      message will not be set.
         *
         * @throw std::runtime_error if the given port is not connected.
         */
        Message receive(std::string const & port_name);

        /** Receive a message from the outside world.
         *
         * Receiving is a blocking operation. This function will contact the
         * sender, wait for a message to be available, and receive and return
         * it.
         *
         * If the port you are receiving on is not connected, the default value
         * you specified will be returned exactly as you passed it.
         *
         * MPI-based components must call this function in all processes
         * simultaneously. The received message will be returned in the root
         * process, all other processes will receive a dummy message. It is
         * therefore up to the model code to scatter or broadcast the received
         * message to the non-root processes, if necessary.
         *
         * @param port_name The endpoint on which a message is to be received.
         * @param default_msg A default value to return if this port is not
         *      connected.
         *
         * @return The received message. The settings attribute of the received
         *      message will not be set.
         *
         * @throw std::runtime_error if the given port is not connected and no
         *      default value was given.
         */
        Message receive(
                std::string const & port_name, Message const & default_msg);

        /** Receive a message from the outside world.
         *
         * Receiving is a blocking operation. This function will contact the
         * sender, wait for a message to be available, and receive and return
         * it.
         *
         * If the port you are receiving on is not connected, an exception will
         * be thrown.
         *
         * MPI-based components must call this function in all processes
         * simultaneously. The received message will be returned in the root
         * process, all other processes will receive a dummy message. It is
         * therefore up to the model code to scatter or broadcast the received
         * message to the non-root processes, if necessary.
         *
         * @param port_name The endpoint on which a message is to be received.
         * @param slot The slot to receive the message, on, if any.
         *
         * @return The received message. The settings attribute of the received
         *      message will not be set.
         *
         * @throw std::runtime_error if the given port is not connected and no
         *      default value was given.
         */
        Message receive(std::string const & port_name, int slot);

        /** Receive a message from the outside world.
         *
         * Receiving is a blocking operation. This function will contact the
         * sender, wait for a message to be available, and receive and return
         * it.
         *
         * If the port you are receiving on is not connected, the default value
         * you specified will be returned exactly as you passed it. If you
         * didn't specify a default value (e.g. because there is no reasonable
         * default, you really need the outside input) and the port is not
         * connected, you'll get a std::runtime_error thrown.
         *
         * MPI-based components must call this function in all processes
         * simultaneously. The received message will be returned in the root
         * process, all other processes will receive a dummy message. It is
         * therefore up to the model code to scatter or broadcast the received
         * message to the non-root processes, if necessary.
         *
         * @param port_name The endpoint on which a message is to be received.
         * @param slot The slot to receive the message, on, if any.
         * @param default_msg A default value to return if this port is not
         *      connected.
         *
         * @return The received message. The settings attribute of the received
         *      message will not be set.
         *
         * @throw std::runtime_error if the given port is not connected and no
         *      default value was given.
         */
        Message receive(
                std::string const & port_name, int slot,
                Message const & default_msg);

        /** Receive a message with attached settings overlay.
         *
         * This function should not be used in submodels. It is intended for
         * use by special components that are ensemble-aware and have to
         * pass on overlay settings explicitly.
         *
         * Receiving is a blocking operation. This function will contact the
         * sender, wait for a message to be available, and receive and return
         * it.
         *
         * If the port you are receiving on is not connected, an exception will
         * be thrown.
         *
         * MPI-based components must call this function in all processes
         * simultaneously. The received message will be returned in the root
         * process, all other processes will receive a dummy message. It is
         * therefore up to the model code to scatter or broadcast the received
         * message to the non-root processes, if necessary.
         *
         * @param port_name The port on which a message is to be received.
         *
         * @return The received message. The settings attribute of the received
         *      message will contain the received settings.
         *
         * @throw std::runtime_error if the given port is not connected.
         */
        Message receive_with_settings(std::string const & port_name);

        /** Receive a message with attached settings overlay.
         *
         * This function should not be used in submodels. It is intended for
         * use by special components that are ensemble-aware and have to
         * pass on overlay settings explicitly.
         *
         * Receiving is a blocking operation. This function will contact the
         * sender, wait for a message to be available, and receive and return
         * it.
         *
         * If the port you are receiving on is not connected, an exception will
         * be thrown.
         *
         * MPI-based components must call this function in all processes
         * simultaneously. The received message will be returned in the root
         * process, all other processes will receive a dummy message. It is
         * therefore up to the model code to scatter or broadcast the received
         * message to the non-root processes, if necessary.
         *
         * @param port_name The endpoint on which a message is to be received.
         * @param slot The slot to receive the message, on, if any.
         *
         * @return The received message. The settings attribute of the received
         *      message will contain the received settings.
         *
         * @throw std::runtime_error if the given port is not connected.
         */
        Message receive_with_settings(std::string const & port_name, int slot);

        /** Receive a message with attached settings overlay.
         *
         * This function should not be used in submodels. It is intended for
         * use by special components that are ensemble-aware and have to
         * pass on overlay settings explicitly.
         *
         * Receiving is a blocking operation. This function will contact the
         * sender, wait for a message to be available, and receive and return
         * it.
         *
         * If the port you are receiving on is not connected, the default value
         * you specified will be returned exactly as you passed it. If you
         * didn't specify a default value (e.g. because there is no reasonable
         * default, you really need the outside input) and the port is not
         * connected, you'll get a std::runtime_error thrown.
         *
         * MPI-based components must call this function in all processes
         * simultaneously. The received message will be returned in the root
         * process, all other processes will receive a dummy message. It is
         * therefore up to the model code to scatter or broadcast the received
         * message to the non-root processes, if necessary.
         *
         * @param port_name The endpoint on which a message is to be received.
         * @param default_msg A default value to return if this port is not
         *      connected.
         *
         * @return The received message. The settings attribute of the received
         *      message will contain the received settings.
         *
         * @throw std::runtime_error if the given port is not connected and no
         *      default value was given.
         */
        Message receive_with_settings(
                std::string const & port_name, Message const & default_msg);

        /** Receive a message with attached settings overlay.
         *
         * This function should not be used in submodels. It is intended for
         * use by special components that are ensemble-aware and have to
         * pass on overlay settings explicitly.
         *
         * Receiving is a blocking operation. This function will contact the
         * sender, wait for a message to be available, and receive and return
         * it.
         *
         * If the port you are receiving on is not connected, the default value
         * you specified will be returned exactly as you passed it. If you
         * didn't specify a default value (e.g. because there is no reasonable
         * default, you really need the outside input) and the port is not
         * connected, you'll get a std::runtime_error thrown.
         *
         * MPI-based components must call this function in all processes
         * simultaneously. The received message will be returned in the root
         * process, all other processes will receive a dummy message. It is
         * therefore up to the model code to scatter or broadcast the received
         * message to the non-root processes, if necessary.
         *
         * @param port_name The endpoint on which a message is to be received.
         * @param slot The slot to receive the message, on, if any.
         * @param default_msg A default value to return if this port is not
         *      connected.
         *
         * @return The received message. The settings attribute of the received
         *      message will contain the received settings.
         *
         * @throw std::runtime_error if the given port is not connected and no
         *      default value was given.
         */
        Message receive_with_settings(
                std::string const & port_name, int slot,
                Message const & default_msg);

        /** Check if this instance is resuming from a snapshot.
         *
         * Must be used by submodels that implement the checkpointing API. You'll
         * get a RuntimeError if you don't call this method in an iteration of the
         * reuse loop.
         *
         * This method returns True for the first iteration of the reuse loop after
         * resuming from a previously taken snapshot. When resuming from a
         * snapshot, the submodel must load its state from the snapshot returned by
         * Instance::load_snapshot.
         *
         * MPI-based components must call this function in all processes
         * simultaneously.
         *
         * @return true iff the submodel must resume from a snapshot.
         */
        bool resuming();

        /** Check if this instance should initialize.
         *
         * Must be used by submodels that implement the checkpointing API.
         *
         * When resuming from a previous snapshot, instances need not always
         * execute the F_INIT phase of the submodel execution loop. Use this method
         * before attempting to receive data on F_INIT ports.
         *
         * MPI-based components must call this function in all processes
         * simultaneously.
         *
         * @return true if the submodel must execute the F_INIT step.
         * @return false otherwise.
         */
        bool should_init();

        /** Load a snapshot.
         *
         * Must only be called when Instance::resuming returns True.
         *
         * MPI-based components may only call this from the root process. An error
         * is raised when attempting to call this method in any other process. It
         * is therefore up to the model code to scatter or broadcast the snapshot
         * state to the non-root processes, if necessary.
         *
         * @return Message containing the state as saved in a previous run
         *      through Instance::save_snapshot or Instance::save_final_snapshot.
         */
        Message load_snapshot();

        /** Check if a snapshot should be saved after the S Operator of the submodel.
         *
         * This method checks if a snapshot should be saved right now, based on the
         * provided timestamp and elapsed wallclock time.
         *
         * If this method returns true, then the submodel must also save a snapshot
         * through Instance::save_snapshot. A std::runtime_error will be generated if
         * this is not done.
         *
         * See also Instance::should_save_final_snapshot for the variant that must be
         * called at the end of the reuse loop.
         *
         * MPI-based components must call this function in all processes
         * simultaneously.
         *
         * @param timestamp current timestamp of the submodel.
         * @return true iff a snapshot should be taken by the submodel according to the
         *      checkpoint rules provided in the ymmsl configuration.
         */
        bool should_save_snapshot(double timestamp);

        /** Save a snapshot after the S Operator of the submodel.
         *
         * Before saving a snapshot, you should check using
         * Instance::should_save_snapshot if a snapshot should be saved according to
         * the checkpoint rules specified in the ymmsl configuration. You should
         * use the same timestamp in the provided Message object as used to query
         * Instance::should_save_snapshot.
         *
         * MPI-based components may only call this from the root process. An error
         * is raised when attempting to call this method in any other process. It
         * is therefore up to the model code to gather the necessary state from
         * the non-root processes before saving the snapshot.
         *
         * @param message Message object that is saved as snapshot. The message
         *      timestamp attribute should be the same as passed to
         *      Instance::should_save_snapshot. The data attribute can be used to
         *      store the internal state of the submodel.
         */
        void save_snapshot(Message message);

        /** Check if a snapshot should be saved at the end of the reuse loop.
         *
         * This method checks if a snapshot should be saved at the end of the reuse
         * loop. All your communication on O_F ports must be finished before calling
         * this method, otherwise your simulation may deadlock.
         *
         * When this method returns true, the submodel must also save a snapshot
         * through Instance::save_final_snapshot. A std::runtime_error will be
         * generated if this is not done.
         *
         * See also Instance::should_save_snapshot for the variant that may be called
         * inside of a time-integration loop of the submodel.
         *
         * MPI-based components must call this function in all processes
         * simultaneously.
         *
         * \note
         * This method will block until it can determine whether a final
         * snapshot should be taken, because it must determine if this
         * instance is reused.
         *
         * @return true iff a final snapshot should be taken by the submodel according
         *      to the checkpoint rules provided in the ymmsl configuration.
         */
        bool should_save_final_snapshot();

        /** Save a snapshot at the end of the reuse loop.
         *
         * Before saving a snapshot, you should check using
         * Instance::should_save_final_snapshot if a snapshot should be saved
         * according to the checkpoint rules specified in the ymmsl configuration.
         *
         * See also Instance::save_snapshot for the variant that may be called after
         * each S Operator of the submodel.
         *
         * MPI-based components may only call this from the root process. An error
         * is raised when attempting to call this method in any other process. It
         * is therefore up to the model code to gather the necessary state from
         * the non-root processes before saving the snapshot.
         *
         * @param message Message object that is saved as snapshot. The data
         *      attribute can be used to store the internal state of the
         *      submodel.
         */
        void save_final_snapshot(Message message);

    private:
        class Impl;
        std::unique_ptr<Impl> pimpl_;

        Impl const * impl_() const;
        Impl * impl_();

        friend class TestInstance;
};

} }

