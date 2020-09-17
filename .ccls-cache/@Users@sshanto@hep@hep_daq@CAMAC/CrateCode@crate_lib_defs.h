#ifndef CRATE_LIB_DEFS_H
#define CRATE_LIB_DEFS_H

#define MAX_CRATE                       128
#define MAX_PAR				16

#define CMD_PORT			2000
#define BIN_PORT			2001
#define IRQ_PORT			2002

////////////////////////////////////////////
//	Return Codes
////////////////////////////////////////////

#define CRATE_OK		          0
#define CRATE_ERROR		        (-1)
#define CRATE_CONNECT_ERROR		(-2)
#define CRATE_IRQ_ERROR			(-3)
#define CRATE_BIN_ERROR			(-4)
#define CRATE_CMD_ERROR			(-5)
#define CRATE_ID_ERROR			(-6)
#define CRATE_MEMORY_ERROR		(-7)
#define CRATE_PROTOCOL_ERROR		(-8)
#define CRATE_OP_TIMEOUT		(-9)

////////////////////////////////////////////
//	BLK_TRANSF Opcode Defines
////////////////////////////////////////////

#define OP_BLKSS			0x0
#define OP_BLKFS			0x1
#define OP_BLKSR			0x2
#define OP_BLKFR			0x3
#define OP_BLKSA			0x4
#define OP_BLKFA			0x5

////////////////////////////////////////////
//	IRQ Type Defines
////////////////////////////////////////////

#define LAM_INT				0x1
#define COMBO_INT			0x2
#define DEFAULT_INT			0x3

////////////////////////////////////////////
//	Defines for BIN Protocol
////////////////////////////////////////////

#define STX				0x2
#define ETX				0x4
#define STUFF				0x10
#define CMD_ERROR			0xCE
#define PAR_ERROR			0xCF

#define BIN_CFSA_CMD			0x20
#define BIN_CSSA_CMD			0x21
#define BIN_CCCZ_CMD			0x22
#define BIN_CCCC_CMD			0x23
#define BIN_CCCI_CMD			0x24
#define BIN_CTCI_CMD			0x25
#define BIN_CTLM_CMD			0x26
#define BIN_CCLWT_CMD			0x27
#define BIN_LACK_CMD			0x28
#define BIN_CTSTAT_CMD			0x29
#define BIN_CLMR_CMD			0x2A
#define BIN_CSCAN_CMD			0x2B

#define BIN_NIM_SETOUTS_CMD		0x30

#define NO_BIN_RESPONSE			0xA0

#endif /* CRATE_LIB_DEFS_H */
