#include <gtest/gtest.h>

#include <libmuscle/api_guard.hpp>

#include <vector>
#include <set>

using libmuscle::impl::APIGuard;
using libmuscle::impl::APIPhase;

int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

TEST(libmuscle_api_guard, test_no_checkpointing_support) {
    auto guard = APIGuard(false);
    for (int i=0; i<3; ++i) {
        guard.verify_reuse_instance();
        guard.reuse_instance_done(true);
    }

    guard.verify_reuse_instance();
    guard.reuse_instance_done(false);
}

TEST(libmuscle_api_guard, test_final_snapshot_only) {
    auto guard = APIGuard(true);
    for (int i=0; i<4; ++i) {
        guard.verify_reuse_instance();
        guard.reuse_instance_done(true);

        guard.verify_resuming();
        if (i == 0) {
            guard.resuming_done(true);

            guard.verify_load_snapshot();
            guard.load_snapshot_done();
        } else {
            guard.resuming_done(false);
        }

        guard.verify_should_init();
        guard.should_init_done();

        guard.verify_should_save_final_snapshot();
        if (i == 2) {
            guard.should_save_final_snapshot_done(true);

            guard.verify_save_final_snapshot();
            guard.save_final_snapshot_done();
        } else {
            guard.should_save_final_snapshot_done(false);
        }
    }

    guard.verify_reuse_instance();
    guard.reuse_instance_done(false);
}


TEST(libmuscle_api_guard, test_full_checkpointing) {
    auto guard = APIGuard(true);
    for (int i=0; i<4; ++i) {
        guard.verify_reuse_instance();
        guard.reuse_instance_done(true);

        guard.verify_resuming();
        if (i == 0) {
            guard.resuming_done(true);

            guard.verify_load_snapshot();
            guard.load_snapshot_done();
        } else {
            guard.resuming_done(false);
        }

        guard.verify_should_init();
        guard.should_init_done();

        for (int j=0; j<3; ++j) {
            guard.verify_should_save_snapshot();
            if (j != 2) {
                guard.should_save_snapshot_done(true);

                guard.verify_save_snapshot();
                guard.save_snapshot_done();
            } else {
                guard.should_save_snapshot_done(false);
            }
        }

        guard.verify_should_save_final_snapshot();
        if (i == 2) {
            guard.should_save_final_snapshot_done(true);

            guard.verify_save_final_snapshot();
            guard.save_final_snapshot_done();
        } else {
            guard.should_save_final_snapshot_done(false);
        }
    }

    guard.verify_reuse_instance();
    guard.reuse_instance_done(false);
}

static std::vector< std::function<void(APIGuard &)> > api_guard_funs_({
    [](APIGuard & guard){ guard.verify_reuse_instance(); },                 //  0
    [](APIGuard & guard){ guard.reuse_instance_done(true); },               //  1
    [](APIGuard & guard){ guard.verify_resuming(); },                       //  2
    [](APIGuard & guard){ guard.resuming_done(true); },                     //  3
    [](APIGuard & guard){ guard.verify_load_snapshot(); },                  //  4
    [](APIGuard & guard){ guard.load_snapshot_done(); },                    //  5
    [](APIGuard & guard){ guard.verify_should_init(); },                    //  6
    [](APIGuard & guard){ guard.should_init_done(); },                      //  7
    [](APIGuard & guard){ guard.verify_should_save_snapshot(); },           //  8
    [](APIGuard & guard){ guard.should_save_snapshot_done(true); },         //  9
    [](APIGuard & guard){ guard.verify_save_snapshot(); },                  // 10
    [](APIGuard & guard){ guard.save_snapshot_done(); },                    // 11
    [](APIGuard & guard){ guard.verify_should_save_final_snapshot(); },     // 12
    [](APIGuard & guard){ guard.should_save_final_snapshot_done(true); },   // 13
    [](APIGuard & guard){ guard.verify_save_final_snapshot(); }             // 14
});

void run_until_before(APIGuard & guard, int fun) {
    for (int i=0; i<fun; ++i) {
        api_guard_funs_.at(i)(guard);
    }
}

void check_all_raise_except(APIGuard & guard, std::set<int> excluded) {
    for (uint i=0; i<api_guard_funs_.size(); i+=2) {
        // only call the verify functions, which are the even-indexed ones
        if (excluded.find(i) != excluded.end()) {
            // no error expected from the excluded set
            ASSERT_NO_THROW(api_guard_funs_.at(i)(guard));
        } else {
            ASSERT_THROW(api_guard_funs_.at(i)(guard), std::runtime_error);
        }
    }
}

TEST(libmuscle_api_guard, test_missing_resuming){
    auto guard = APIGuard(true);
    run_until_before(guard, 2);  // 2 = verify_resuming
    check_all_raise_except(guard, {2});
}

TEST(libmuscle_api_guard, test_missing_load_snapshot) {
    auto guard = APIGuard(true);
    run_until_before(guard, 4);  // 4 = verify_load_snapshot
    check_all_raise_except(guard, {4});
}

TEST(libmuscle_api_guard, test_missing_should_init) {
    auto guard = APIGuard(true);
    run_until_before(guard, 6);  // 6 = verify_should_init
    check_all_raise_except(guard, {6});
}

TEST(libmuscle_api_guard, test_missing_should_save) {
    auto guard = APIGuard(true);
    run_until_before(guard, 8);  // 8 = verify_should_save_snapshot
    check_all_raise_except(guard, {8, 12});  // 12 = verify_should_save_final_snapshot
}

TEST(libmuscle_api_guard, test_missing_save_snapshot) {
    auto guard = APIGuard(true);
    run_until_before(guard, 10);  // 10 = verify_save_snapshot
    check_all_raise_except(guard, {10});
}

TEST(libmuscle_api_guard, test_missing_should_save_final) {
    auto guard = APIGuard(true);
    run_until_before(guard, 12);  // 12 = verify_should_save_final_snapshot
    check_all_raise_except(guard, {12, 8});  // 8 = verify_should_save_snapshot
}

TEST(libmuscle_api_guard, test_missing_save_final_snapshot) {
    auto guard = APIGuard(true);
    run_until_before(guard, 14);  // 14 = verify_save_final_snapshot
    check_all_raise_except(guard, {14});
}

TEST(libmuscle_api_guard, test_double_should_save) {
    auto guard = APIGuard(true);
    run_until_before(guard, 8);  // 8 = verify_should_save_snapshot
    guard.verify_should_save_snapshot();
    guard.should_save_snapshot_done(true);
    ASSERT_THROW(guard.verify_should_save_snapshot(), std::runtime_error);
}

