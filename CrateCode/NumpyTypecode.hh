#ifndef TTUDAQ_NUMPYTYPECODE_HH_
#define TTUDAQ_NUMPYTYPECODE_HH_

#include <complex>
#include <numpy/arrayobject.h>

namespace ttudaq {
    namespace NumpyConvert
    {
        enum {
            NONE = 0,
            BOOL,
            COMPLEX
        };
    }

    template<typename T>
    struct NumpyTypecode
    {
        typedef T c_type;
        enum {code = NPY_NOTYPE};
        enum {conversion = NumpyConvert::NONE};
    };

    template<>
    struct NumpyTypecode<bool>
    {
        typedef unsigned char c_type;
        enum {code = NPY_BOOL};
        enum {conversion = NumpyConvert::BOOL};
    };

    template<>
    struct NumpyTypecode<signed char>
    {
        typedef signed char c_type;
        enum {code = NPY_BYTE};
        enum {conversion = NumpyConvert::NONE};
    };

    template<>
    struct NumpyTypecode<unsigned char>
    {
        typedef unsigned char c_type;
        enum {code = NPY_UBYTE};
        enum {conversion = NumpyConvert::NONE};
    };

    template<>
    struct NumpyTypecode<short>
    {
        typedef short c_type;
        enum {code = NPY_SHORT};
        enum {conversion = NumpyConvert::NONE};
    };

    template<>
    struct NumpyTypecode<unsigned short>
    {
        typedef unsigned short c_type;
        enum {code = NPY_USHORT};
        enum {conversion = NumpyConvert::NONE};
    };

    template<>
    struct NumpyTypecode<int>
    {
        typedef int c_type;
        enum {code = NPY_INT};
        enum {conversion = NumpyConvert::NONE};
    };

    template<>
    struct NumpyTypecode<unsigned int>
    {
        typedef unsigned int c_type;
        enum {code = NPY_UINT};
        enum {conversion = NumpyConvert::NONE};
    };

    template<>
    struct NumpyTypecode<long>
    {
        typedef long c_type;
        enum {code = NPY_LONG};
        enum {conversion = NumpyConvert::NONE};
    };

    template<>
    struct NumpyTypecode<unsigned long>
    {
        typedef unsigned long c_type;
        enum {code = NPY_ULONG};
        enum {conversion = NumpyConvert::NONE};
    };

    template<>
    struct NumpyTypecode<long long>
    {
        typedef long long c_type;
        enum {code = NPY_LONGLONG};
        enum {conversion = NumpyConvert::NONE};
    };

    template<>
    struct NumpyTypecode<unsigned long long>
    {
        typedef unsigned long long c_type;
        enum {code = NPY_ULONGLONG};
        enum {conversion = NumpyConvert::NONE};
    };

    template<>
    struct NumpyTypecode<float>
    {
        typedef float c_type;
        enum {code = NPY_FLOAT};
        enum {conversion = NumpyConvert::NONE};
    };

    template<>
    struct NumpyTypecode<double>
    {
        typedef double c_type;
        enum {code = NPY_DOUBLE};
        enum {conversion = NumpyConvert::NONE};
    };

    template<>
    struct NumpyTypecode<long double>
    {
        typedef long double c_type;
        enum {code = NPY_LONGDOUBLE};
        enum {conversion = NumpyConvert::NONE};
    };

    template<>
    struct NumpyTypecode<std::complex<float> >
    {
        typedef npy_cfloat c_type;
        enum {code = NPY_CFLOAT};
        enum {conversion = NumpyConvert::COMPLEX};
    };

    template<>
    struct NumpyTypecode<std::complex<double> >
    {
        typedef npy_cdouble c_type;
        enum {code = NPY_CDOUBLE};
        enum {conversion = NumpyConvert::COMPLEX};
    };

    template<>
    struct NumpyTypecode<std::complex<long double> >
    {
        typedef npy_clongdouble c_type;
        enum {code = NPY_CLONGDOUBLE};
        enum {conversion = NumpyConvert::COMPLEX};
    };
}

#endif // TTUDAQ_NUMPYTYPECODE_HH_
