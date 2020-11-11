%include stddecls.i

%{
#include <sstream>

#include "CrateHandle.hh"
#include "vectorToNumpy.hh"

#define LOCAL_BUFFER_SIZE_16 8256
#define LOCAL_BUFFER_SIZE_24 512
%}

%feature("python:slot", "tp_str", functype="reprfunc") CrateOpStatus::as_string;

%extend CrateOpStatus {
    std::string as_string() const
    {
        std::ostringstream os;
        $self->readable(os);
        return os.str();
    }
}

%feature("python:slot", "tp_str", functype="reprfunc") CrateOpResult::as_string;

%extend CrateOpResult {
    std::string as_string() const
    {
        std::ostringstream os;
        $self->readable(os);
        return os.str();
    }
}

%feature("python:slot", "tp_str", functype="reprfunc") CrateOpIRQ::as_string;

%extend CrateOpIRQ {
    std::string as_string() const
    {
        std::ostringstream os;
        $self->readable(os);
        return os.str();
    }
}

%ignore CrateHandle::send_block;
%ignore CrateHandle::receive_block;

%extend CrateHandle {
    PyObject* receiveBlock(int opcode, int function, int slot,
                           int address, int size, int timeout_ms) const
    {
        return ttudaq::vectorToNumpy($self->receive_block(
                  opcode, function, slot, address, size, timeout_ms));
    }

    /*start of method*/
    PyObject* read24ScanScaler(int function, int slot, int address, int size) const
    {
        int buffer[LOCAL_BUFFER_SIZE_24];

        if (size < 0 || size > LOCAL_BUFFER_SIZE_24)
        {
            std::ostringstream os;
            if (size < 0)
                os << "In read24ScanScaler: scan length can not be negative";
            else
                os << "In read24ScanScaler: scan length " << size
                   << " exceeds the local buffer size";
            throw std::runtime_error(os.str());
        }

        if (size)
        {
            const CrateOpResult r0 = $self->CFSA(function, slot, address, 0);
            if (r0.Q() == 1)
            {
                for (int i=0; i<size; ++i)
                    buffer[i] = -1;
            }
            else
            {
                assert(r0.Q() == 0);
                buffer[0] = r0.datum();
                for (int i=1; i<size; ++i)
                {
                    const CrateOpResult r = $self->CFSA(function, slot, address+i, 0);
                    if (r.Q() != 0)  /*Might need to change to 1*/
                    {
                        std::ostringstream os;
                        os << "In read24ScanScaler: got Q != 1 for slot " << slot
                           << " and subaddress " << address+i;
                        throw std::runtime_error(os.str());
                    }
                    buffer[i] = r.datum();
                }
            }
        }
        return ttudaq::intBufferToNumpy(buffer, size);
    }
    /*end of method*/


    /*start of method*/
    PyObject* read24Scan(int function, int slot, int address, int size) const
    {
        int buffer[LOCAL_BUFFER_SIZE_24];

        if (size < 0 || size > LOCAL_BUFFER_SIZE_24)
        {
            std::ostringstream os;
            if (size < 0)
                os << "In read24Scan: scan length can not be negative";
            else
                os << "In read24Scan: scan length " << size
                   << " exceeds the local buffer size";
            throw std::runtime_error(os.str());
        }

        if (size)
        {
            const CrateOpResult r0 = $self->CFSA(function, slot, address, 0);
            if (r0.Q() == 0)
            {
                for (int i=0; i<size; ++i)
                    buffer[i] = -1;
            }
            else
            {
                assert(r0.Q() == 1);
                buffer[0] = r0.datum();
                for (int i=1; i<size; ++i)
                {
                    const CrateOpResult r = $self->CFSA(function, slot, address+i, 0);
                    if (r.Q() != 1)
                    {
                        std::ostringstream os;
                        os << "In read24Scan: got Q != 1 for slot " << slot
                           << " and subaddress " << address+i;
                        throw std::runtime_error(os.str());
                    }
                    buffer[i] = r.datum();
                }
            }
        }
        return ttudaq::intBufferToNumpy(buffer, size);
    }
    /*end of method*/

    PyObject* read24UntilQ0(int function, int slot, int address) const
    {
        int buffer[LOCAL_BUFFER_SIZE_24];

        int nread = 0;
        while (1)
        {
            const CrateOpResult r = $self->CFSA(function, slot, address, 0);
            if (r.Q() != 1)
            {
                assert(r.Q() == 0);
                break;
            }
            if (nread >= LOCAL_BUFFER_SIZE_24)
                throw std::runtime_error("In read24UntilQ0: readout exceeds "
                                         "the local buffer size");
            buffer[nread++] = r.datum();
        }
        return ttudaq::intBufferToNumpy(buffer, nread);
    }

    PyObject* read16UntilQ0Q0(int function, int slot, int address) const
    {
        unsigned short buffer[LOCAL_BUFFER_SIZE_16];

        // Read until the read command returns Q = 0 twice in a row
        int nread = 0;
        bool lastQis0 = false;
        while (1)
        {
            const CrateOpResult r = $self->CSSA(function, slot, address, 0);
            if (r.Q() == 1)
            {
                if (nread >= LOCAL_BUFFER_SIZE_16)
                    throw std::runtime_error("In read16UntilQ0Q0: readout exceeds "
                                             "the local buffer size");
                buffer[nread++] = r.datum() & 0xffff;
                lastQis0 = false;
            }
            else
            {
                assert(r.Q() == 0);
                if (lastQis0)
                    break;
                lastQis0 = true;
            }
        }
        return ttudaq::ushortBufferToNumpy(buffer, nread);
    }
}

%apply (int* IN_ARRAY1, int DIM1) {
    (const int* in, unsigned dataLen)
};

%include "CrateHandle.hh"

%clear (const int* in, unsigned dataLen);
