#ifndef TTUDAQ_VECTORTONUMPY_HH_
#define TTUDAQ_VECTORTONUMPY_HH_

#include <vector>
#include <sstream>
#include <stdexcept>
#include <cassert>

#include "NumpyTypecode.hh"

namespace ttudaq {
    template <typename NPType, typename T>
    PyObject* vectorToNumpyConvert(const std::vector<T>& vec)
    {
        const int typenum = NumpyTypecode<NPType>::code;
        if (typenum == NPY_NOTYPE)
        {
            std::ostringstream os;
            os << "In ttudaq::vectorToNumpyConvert: "
               << "invalid type of target numpy array";
            throw std::invalid_argument(os.str());
        }

        const int conversion = NumpyTypecode<NPType>::conversion;
        if (conversion != NumpyConvert::NONE)
        {
            std::ostringstream os;
            os << "In ttudaq::vectorToNumpyConvert: "
               << "this kind of element conversion is not supported";
            throw std::invalid_argument(os.str());
        }

        const npy_intp len = vec.size();
        npy_intp sh[1];
        sh[0] = len;
        PyObject* array = PyArray_SimpleNew(1, sh, typenum);
        if (array && len > 0)
        {
            PyArrayObject* a = reinterpret_cast<PyArrayObject*>(array);
            NPType* to = (NPType*)(PyArray_DATA(a));
            const T* from = &vec[0];
            for (npy_intp i=0; i<len; ++i)
                *to++ = *from++;
        }
        return array;
    }

    template <typename T>
    PyObject* vectorToNumpy(const std::vector<T>& vec)
    {
        return vectorToNumpyConvert<T, T>(vec);
    }

    PyObject* intBufferToNumpy(const int* buf, int buflen)
    {
        if (buflen < 0)
            buflen = 0;
        if (buflen > 0)
            assert(buf);
        npy_intp sh[1];
        sh[0] = buflen;
        PyObject* array = PyArray_SimpleNew(1, sh, NPY_INT);
        if (array && buflen > 0)
        {
            PyArrayObject* a = reinterpret_cast<PyArrayObject*>(array);
            int* to = (int*)(PyArray_DATA(a));
            for (int i=0; i<buflen; ++i)
                *to++ = *buf++;
        }
        return array;
    }

    PyObject* ushortBufferToNumpy(const unsigned short* buf, int buflen)
    {
        if (buflen < 0)
            buflen = 0;
        if (buflen > 0)
            assert(buf);
        npy_intp sh[1];
        sh[0] = buflen;
        PyObject* array = PyArray_SimpleNew(1, sh, NPY_USHORT);
        if (array && buflen > 0)
        {
            PyArrayObject* a = reinterpret_cast<PyArrayObject*>(array);
            unsigned short* to = (unsigned short*)(PyArray_DATA(a));
            for (int i=0; i<buflen; ++i)
                *to++ = *buf++;
        }
        return array;
    }
}

#endif // TTUDAQ_VECTORTONUMPY_HH_
