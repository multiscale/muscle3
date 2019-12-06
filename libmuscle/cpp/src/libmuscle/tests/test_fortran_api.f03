program test_fortran_api
      use libmuscle

      implicit none

      integer, parameter :: long_int = selected_int_kind(18)
      type(LIBMUSCLE_Data) :: d1

      print *, ''
      print *, '[==========] Fortran API test'

      d1 = LIBMUSCLE_Data_create()
      call LIBMUSCLE_Data_free(d1)

      d1 = LIBMUSCLE_Data_create(.true.)
      call LIBMUSCLE_Data_free(d1)

      d1 = LIBMUSCLE_Data_create('Testing')
      call LIBMUSCLE_Data_free(d1)

      d1 = LIBMUSCLE_Data_create(13)
      call LIBMUSCLE_Data_free(d1)

      d1 = LIBMUSCLE_Data_create(131313131313131313_long_int)
      call LIBMUSCLE_Data_free(d1)

      d1 = LIBMUSCLE_Data_create(42.0)
      call LIBMUSCLE_Data_free(d1)

      d1 = LIBMUSCLE_Data_create(42.0d0)
      call LIBMUSCLE_Data_free(d1)

      print *, '[==========] Fortran API test'
      print *, '[  PASSED  ] Fortran API test'
      print *, ''

end program test_fortran_api

