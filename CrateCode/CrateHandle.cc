#include <stdexcept>
#include <sstream>
#include <climits>
#include <cassert>
#include <iomanip>
#include <memory>
#include <algorithm>

#include "CrateHandle.hh"
#include "crate_lib.h"

static char ascii_read_buffer[CrateHandle::ASCIIBufferLength];

static const char* human_readable_error(const short ecode)
{
    switch (ecode)
    {
    case CRATE_OK:
        return "CRATE_OK";
    case CRATE_ERROR:
        return "CRATE_ERROR";
    case CRATE_CONNECT_ERROR:
        return "CRATE_CONNECT_ERROR";
    case CRATE_IRQ_ERROR:
        return "CRATE_IRQ_ERROR";
    case CRATE_BIN_ERROR:
        return "CRATE_BIN_ERROR";
    case CRATE_CMD_ERROR:
        return "CRATE_CMD_ERROR";
    case CRATE_ID_ERROR:
        return "CRATE_ID_ERROR";
    case CRATE_MEMORY_ERROR:
        return "CRATE_MEMORY_ERROR";
    case CRATE_PROTOCOL_ERROR:
        return "CRATE_PROTOCOL_ERROR";
    case CRATE_OP_TIMEOUT:
        return "CRATE_OP_TIMEOUT";
    default:
        return "Invalid error code. You probably need to update"
               " and recompile the CAEN CAMAC Crate Lib C++ wrapper.";
    }
}

static void process_ecode(const char* where, const short ecode)
{
    if (ecode != CRATE_OK)
    {
        std::string s = "In ";
        if (where)
            s += where;
        else
            s += "(unknown function)";
        s += ": ";
        s += human_readable_error(ecode);
        throw std::runtime_error(s);
    }
}

template <typename T>
static void validate_parameter(const char* what, const T value,
                               const T minValue, const T maxValue)
{
    if (!(value >= minValue && value <= maxValue))
    {
        std::ostringstream os;
        os << "Invalid value " << value << " of parameter \"" << what << "\": "
           << "should be in [" << minValue << ", " << maxValue << "].";
        throw std::invalid_argument(os.str());
    }
}

#define validate_range(name, min, max) do {\
    validate_parameter(#name, name, min, max);\
} while(0);

CrateHandle::CrateHandle()
    : crateId_(-1), blkSize_(16)
{
    char defaultAddr[] = "192.168.0.98";
    init(defaultAddr);
}

CrateHandle::CrateHandle(const std::string& address)
    : crateId_(-1), blkSize_(16)
{
    std::string addr(address);
    init((char *)(addr.c_str()));
}

CrateHandle::~CrateHandle()
{
    if (crateId_ >= 0)
        CRCLOSE(crateId_);
}

void CrateHandle::init(char* addr)
{
    crateId_ = CROPEN(addr);
    if (crateId_ < 0)
        process_ecode("CrateHandle::init", crateId_);
}

void CrateHandle::CRTOUT(int time_out_in_ms) const
{
    if (time_out_in_ms < 0)
        time_out_in_ms = 0;
    const short status = ::CRTOUT(crateId_, time_out_in_ms);
    process_ecode("CrateHandle::CRTOUT", status);
}

int CrateHandle::getCRTOUT() const
{
    unsigned tmp;
    const short status = ::getCRTOUT(crateId_, &tmp);
    process_ecode("CrateHandle::getCRTOUT", status);
    return tmp;
}

void CrateHandle::CBINR(const bool enable) const
{
    const short s = enable ? 0 : NO_BIN_RESPONSE;
    const short status = ::CBINR(crateId_, s);
    process_ecode("CrateHandle::CBINR", status);
}

int CrateHandle::CSCAN() const
{
    unsigned u = 0;
    const short status = ::CSCAN(crateId_, &u);
    process_ecode("CrateHandle::CBINR", status);
    return u;
}

CrateOpResult CrateHandle::CFSA(const int function, const int slot,
                                const int address, const int data) const
{
    validate_range(function, 0, 27);
    validate_range(slot, 1, 23);
    validate_range(address, 0, 15);
    validate_range(data, 0, 16777215);

    CRATE_OP op;
    op.F = function;
    op.N = slot;
    op.A = address;
    op.Q = 0;
    op.X = 0;
    op.DATA = data;

    const short status = ::CFSA(crateId_, &op);
    process_ecode("CrateHandle::CFSA", status);

    return CrateOpResult(op.Q, op.X, op.DATA);
}

CrateOpResult CrateHandle::CSSA(const int function, const int slot,
                                const int address, const int data) const
{
    validate_range(function, 0, 27);
    validate_range(slot, 1, 23);
    validate_range(address, 0, 15);
    validate_range(data, 0, 65535);

    CRATE_OP op;
    op.F = function;
    op.N = slot;
    op.A = address;
    op.Q = 0;
    op.X = 0;
    op.DATA = data;

    const short status = ::CSSA(crateId_, &op);
    process_ecode("CrateHandle::CSSA", status);

    return CrateOpResult(op.Q, op.X, op.DATA);
}

void CrateHandle::CCCZ() const
{
    const short status = ::CCCZ(crateId_);
    process_ecode("CrateHandle::CCCZ", status);
}

void CrateHandle::CCCC() const
{
    const short status = ::CCCC(crateId_);
    process_ecode("CrateHandle::CCCC", status);
}

void CrateHandle::CCCI(const bool dataway_inhibit)
{
    const char value = dataway_inhibit ? 1 : 0;
    const short status = ::CCCI(crateId_, value);
    process_ecode("CrateHandle::CCCI", status);
}

int CrateHandle::CTCI() const
{
    char res;
    const short status = ::CTCI(crateId_, &res);
    process_ecode("CrateHandle::CTCI", status);
    return res;
}

int CrateHandle::CTLM(const int slot) const
{
    char res;
    if (slot != -1)
        validate_range(slot, 1, 23);
    const short status = ::CTLM(crateId_, slot, &res);
    process_ecode("CrateHandle::CTLM", status);
    return res;
}

void CrateHandle::CCLWT(const int slot) const
{
    if (slot != -1)
        validate_range(slot, 1, 23);
    const short status = ::CCLWT(crateId_, slot);
    process_ecode("CrateHandle::CCLWT", status);
}

void CrateHandle::LACK() const
{
    const short status = ::LACK(crateId_);
    process_ecode("CrateHandle::LACK", status);
}

int CrateHandle::CLMR() const
{
    unsigned u = 0;
    const short status = ::CLMR(crateId_, &u);
    process_ecode("CrateHandle::CLMR", status);
    return u;
}

CrateOpStatus CrateHandle::CTSTAT() const
{
    char Q = 0, X = 0;
    const short status = ::CTSTAT(crateId_, &Q, &X);
    process_ecode("CrateHandle::CTSTAT", status);
    return CrateOpStatus(Q, X);
}

void CrateHandle::BLKBUFFS(const int sz)
{
    validate_range(sz, 1, 256);
    const short status = ::BLKBUFFS(crateId_, sz);
    process_ecode("CrateHandle::BLKBUFFS", status);
    blkSize_ = sz;
}

std::vector<int> CrateHandle::receive_block(
    const int opcode, const int function, const int slot,
    const int address, const int sz, const int timeout_ms) const
{
    validate_range(opcode, OP_BLKSS, OP_BLKFA);
    validate_range(function, 0, 27);
    validate_range(slot, 1, 23);
    validate_range(address, 0, 15);
    validate_range(sz, 0, 65535);
    validate_range(timeout_ms, 0, INT_MAX);
    validate_range((int)blkSize_, 0, sz);

    std::vector<int> data;
    if (sz > 0)
    {
        data.resize(sz);

        BLK_TRANSF_INFO inf;
        inf.opcode = opcode;
        inf.F = function;
        inf.N = slot;
        inf.A = address;
        inf.totsize = sz;
        inf.blksize = blkSize_;
        inf.timeout = timeout_ms;
        inf.ascii_transf = 0;

        const short status = ::BLKTRANSF(crateId_, &inf, (unsigned*)(&data[0]));
        process_ecode("CrateHandle::receive_block", status);
    }
    return data;
}

void CrateHandle::send_block(
    const int opcode, const int function, const int slot, const int address,
    const int timeout_ms, const std::vector<int>& data) const
{
    if (!data.empty())
        sendBlock(opcode, function, slot, address, timeout_ms, &data[0], data.size());
}

void CrateHandle::sendBlock(
    const int opcode, const int function, const int slot, const int address,
    const int timeout_ms, const int* data, const unsigned sz) const
{
    validate_range(opcode, OP_BLKSS, OP_BLKFA);
    validate_range(function, 0, 27);
    validate_range(slot, 1, 23);
    validate_range(address, 0, 15);
    validate_range(sz, 0U, 65535U);
    validate_range(timeout_ms, 0, INT_MAX);

    if (sz > 0)
    {
        assert(data);

        BLK_TRANSF_INFO inf;
        inf.opcode = opcode;
        inf.F = function;
        inf.N = slot;
        inf.A = address;
        inf.totsize = sz;
        inf.blksize = blkSize_;
        inf.timeout = timeout_ms;
        inf.ascii_transf = 0;

        const short status = ::BLKTRANSF(crateId_, &inf, (unsigned*)(data));
        process_ecode("CrateHandle::send_block", status);
    }
}

void CrateHandle::NOSOS(const int nimOutputNumber, const bool b) const
{
    validate_range(nimOutputNumber, 0, 7);
    const char value = b ? 1 : 0;
    const short status = ::NOSOS(crateId_, nimOutputNumber, value);
    process_ecode("CrateHandle::NOSOS", status);
}

void CrateHandle::CMDS(const std::string& cmd) const
{
    std::string cs(cmd);
    cs += '\r';
    const short status = ::CMDS(crateId_, (char*)(cs.c_str()), cs.size());
    process_ecode("CrateHandle::CMDS", status);
}

std::string CrateHandle::CMDR(const int maxResponseSize) const
{
    validate_range(maxResponseSize, 0, INT_MAX);

    char* buf = ascii_read_buffer;
    int buflen = ASCIIBufferLength;

    std::unique_ptr<std::string> cmdbuf;
    if (maxResponseSize > ASCIIBufferLength)
    {
        cmdbuf = std::unique_ptr<std::string>(new std::string(maxResponseSize, 0));
        buf = &(*cmdbuf)[0];
        buflen = maxResponseSize;
    }

    const short status = ::CMDR(crateId_, buf, buflen);
    process_ecode("CrateHandle::CMDR", status);
    return std::string(buf);
}

std::string CrateHandle::CMDSR(const std::string& cmd,
                               const int maxResponseSize) const
{
    validate_range(maxResponseSize, 0, INT_MAX);

    std::string cs(cmd);
    cs += '\r';

    char* buf = ascii_read_buffer;
    int buflen = ASCIIBufferLength;

    std::unique_ptr<std::string> cmdbuf;
    if (maxResponseSize > ASCIIBufferLength)
    {
        cmdbuf = std::unique_ptr<std::string>(new std::string(maxResponseSize, 0));
        buf = &(*cmdbuf)[0];
        buflen = maxResponseSize;
    }

    const short status = ::CMDSR(crateId_, (char*)(cs.c_str()), buf, buflen);
    process_ecode("CrateHandle::CMDSR", status);
    return std::string(buf);
}

CrateOpIRQ CrateHandle::waitForIRQ(const bool ackNow) const
{
    int code, value;
    const short status = ::waitForIRQ(crateId_, ackNow, &code, &value);
    process_ecode("CrateHandle::waitForIRQ", status);
    return CrateOpIRQ(code, value);
}

void CrateHandle::ackIRQ() const
{
    const short status = ::ackIRQ(crateId_);
    process_ecode("CrateHandle::ackIRQ", status);
}

void CrateOpStatus::readable(std::ostream& of) const
{
    of << "Q " << Q_ << " X " << X_;
}

void CrateOpResult::readable(std::ostream& of) const
{
    CrateOpStatus st(Q_, X_);
    st.readable(of);
    of << " D 0x" << std::internal << std::setfill('0')
       << std::hex << std::setw(6) << dat_;
}

void CrateOpIRQ::readable(std::ostream& of) const
{
    switch (code_)
    {
    case LAM_INT:
        of << "LAM_INT";
        break;

    case COMBO_INT:
        of << "COMBO_INT";
        break;

    case DEFAULT_INT:
        of << "DEFAULT_INT";
        break;

    default:
        of << "INVALID_INT";
    }

    of << " 0x" << std::internal << std::setfill('0')
       << std::hex << std::setw(6) << value_;
}
