program test_fortran_api
      use libmuscle

      implicit none

      type(LIBMUSCLE_Data) :: d1

      print *, ''
      print *, '[==========] Fortran API test'

      d1 = LIBMUSCLE_Data_create()
      call LIBMUSCLE_Data_free(d1)

      print *, '[==========] Fortran API test'
      print *, '[  PASSED  ] Fortran API test'
      print *, ''

end program test_fortran_api

