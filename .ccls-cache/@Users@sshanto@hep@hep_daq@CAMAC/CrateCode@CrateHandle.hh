#ifndef CRATEHANDLE_HH_
#define CRATEHANDLE_HH_

#include <string>
#include <vector>
#include <iostream>


class CrateOpStatus
{
public:
    inline CrateOpStatus(const int iQ, const int iX)
        : Q_(iQ), X_(iX) {}

    inline int Q() const {return Q_;}
    inline int X() const {return X_;}

    void readable(std::ostream& of) const;

private:
    int Q_;
    int X_;
};


class CrateOpResult
{
public:
    inline CrateOpResult(const int iQ, const int iX, const int idata)
        : Q_(iQ), X_(iX), dat_(idata) {}

    inline int Q() const {return Q_;}
    inline int X() const {return X_;}
    inline int datum() const {return dat_;}

    void readable(std::ostream& of) const;

private:
    int Q_;
    int X_;
    int dat_;
};


class CrateOpIRQ
{
public:
    inline CrateOpIRQ(const int c, const int v)
        : code_(c), value_(v) {}

    // Possible values of "code" are
    // IRQ_TIMED_OUT, LAM_INT, COMBO_INT, and DEFAULT_INT
    inline int code() const {return code_;}
    inline int value() const {return value_;}

    void readable(std::ostream& of) const;

private:
    int code_;
    int value_;
};


class CrateHandle
{
public:
    enum {
        ASCIIBufferLength = 2048
    };

    CrateHandle();
    explicit CrateHandle(const std::string& address);

    ~CrateHandle();

    inline short getCrateId() const {return crateId_;}

    // Set operation timeout (in ms). Negative and 0 values
    // correspond to no timeout (the program will wait until
    // operation completes).
    void CRTOUT(int time_out_in_ms) const;

    // Get current operation timeout (in ms)
    int getCRTOUT() const;

    // Enable/disable the response acknowledge when a binary command is sent.
    // Disabling response improves the performance, but it is not a reliable
    // way to send commands.
    void CBINR(bool enable_binary_command_acknowledgements) const;

    // Crate scan. Return a mask with a bit set to 1 for every filled slot.
    int CSCAN() const;

    // 24-bit camac operation
    CrateOpResult CFSA(int function, int slot, int address, int data) const;

    // 16-bit camac operation
    CrateOpResult CSSA(int function, int slot, int address, int data) const;

    // Dataway init
    void CCCZ() const;

    // Crate clear
    void CCCC() const;

    // Changes Dataway Inhibit to a specified value
    void CCCI(bool dataway_inhibit);

    // Performs a CAMAC Test Inhibit operation
    int CTCI() const;

    // Test LAM on specified slot. If slot = -1, the function checks for
    // a LAM on any slot.
    int CTLM(int slot) const;

    // Waits for LAM on specified slot; if slot = -1, wait for LAM on any slot
    void CCLWT(int slot) const;

    // LAM acknowledge
    void LACK() const;

    // Return current LAM register, a 24-bit mask with 1 for each slot
    int CLMR() const;

    // Returns Q and X values from the last access on the bus
    CrateOpStatus CTSTAT() const;

    // Set the block transfer buffer size (the numbers of data
    // words transferred in a single TCP/IP transaction).
    // The argument should satisfy 1 <= sz <= 256.
    void BLKBUFFS(int sz);

    // Get the block transfer buffer size
    inline int getBLKBUFFS() const {return blkSize_;}

    // Perform block transfer operation (send data to crate)
    void send_block(int opcode, int function, int slot, int address,
                    int timeout_ms, const std::vector<int>& data) const;

    // Similar block transfer function which is easier to wrap
    void sendBlock(int opcode, int function, int slot,
                   int address, int timeout_ms,
                   const int* in, unsigned dataLen) const;

    // Perform block transfer operation (receive data from crate)
    std::vector<int> receive_block(int opcode, int function, int slot,
                                   int address, int size, int timeout_ms) const;

    // Performs a single NIM out operation
    void NOSOS(int nimOutputNumber, bool value) const;

    // Send a generic ASCII command
    void CMDS(const std::string& cmd) const;

    // Receive output produced by a generic ASCII command
    std::string CMDR(int maxResponseSize = ASCIIBufferLength) const;

    // Send an ASCII command and then receive output
    std::string CMDSR(const std::string& cmd,
                      int maxResponseSize = ASCIIBufferLength) const;

    // Wait for "IRQ" event (data on the "IRQ" socket). This operation
    // can time out if "CRTOUT" was called previously. The CrateOpIRQ
    // code will be set appropriately.
    CrateOpIRQ waitForIRQ(bool acknowledgeImmediately = false) const;

    // Acknowledge "IRQ" event
    void ackIRQ() const;

private:
    void init(char* addr);

    short crateId_;
    short blkSize_;
};

#endif // CRATEHANDLE_HH_
