#pragma once

#include <gtest/gtest.h>

// Note: using POSIX for filesystem calls
// Could be upgraded to std::filesystem when targeting C++17 or later
#include <cstdlib>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <string.h>
#include <unistd.h>
#include <ftw.h>


// callback for nftw() to delete all contents of a folder
int _nftw_rm_callback(
        const char *fpath, const struct stat *sb, int tflag, struct FTW *ftwbuf) {
    if (tflag == FTW_DP) {
        std::cerr << "DEBUG: removing dir " << fpath << std::endl;
        return rmdir(fpath);
    }
    if (tflag == FTW_F) {
        std::cerr << "DEBUG: removing file " << fpath << std::endl;
        return unlink(fpath);
    }
    std::cerr << "DEBUG: unknown file type " << fpath << std::endl;
    return -1;
}

struct TempDirFixture {
    TempDirFixture() {
            char tmpname[] = "/tmp/muscle3_test.XXXXXX";
            if (mkdtemp(tmpname) == nullptr) {
                throw std::runtime_error(strerror(errno));
            }
            temp_dir_ = tmpname;
            std::cerr << "DEBUG: using temp dir " << temp_dir_ << std::endl;
    }

    ~TempDirFixture() {
            // simulate rm -rf `temp_dir_` using a file-tree-walk
            if (nftw(temp_dir_.c_str(), _nftw_rm_callback, 3, FTW_DEPTH) < 0) {
                std::cerr << "ERROR: Could not remove temp dir at " << temp_dir_ << std::endl;
                std::cerr << "ERROR: " << strerror(errno) << std::endl;
            }
    }

    std::string temp_dir_;
};

