#pragma once

#ifdef MUSCLE_ENABLE_MPI
#define _MUSCLE_IMPL_NS mpi_impl
#else
#define _MUSCLE_IMPL_NS impl
#endif
