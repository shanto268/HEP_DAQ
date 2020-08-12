#ifdef WIN32

////////////////////////////////////////////
// WINDOWS
#include <windows.h> 
#include <stdio.h> 
#include <stdlib.h>
#include <io.h> 
#include <fcntl.h>
#include <sys/types.h>
#include  <sys/stat.h>

////////////////////////////////////////////

#else

////////////////////////////////////////////
// LINUX
#include <pthread.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <errno.h>
#include <string.h>
#include <sys/wait.h>
#include <sys/stat.h>
#include <arpa/inet.h>

#define SOCKET int
#define SOCKADDR_IN struct sockaddr_in

////////////////////////////////////////////
#endif

////////////////////////////////////////////
//	DEFINES
////////////////////////////////////////////
#define MAJOR_VER 1
#define MINOR_VER 0

#define MAX_PARAM		10
#define MAX_LEN_PARAM	32
#define MAX_LEN_VALUE	64

#define HELP			0
#define FILE_NAME		1
#define IP_ADDR			2
#define RUN				3
#define STOP			4	
#define STORE			5
#define ROB				6
#define GET_SCRIPT		7
#define GET_ERR			8
#define GET_LOG			9


#define SOCK_PORT			2000
#define CRATE_OK			0
#define ERROR_CRATE			-1
#define ERROR_CONNECTION	-2
#define ERROR_SEND			-3
////////////////////////////////////////////
//	STRUCTURES
////////////////////////////////////////////
typedef struct {

	char par[MAX_LEN_PARAM];
	char rem[128];
	char ret[128];
	short getvalue;
	char cmd[MAX_LEN_PARAM];
	char value[MAX_LEN_VALUE];

} OPTIONS;


////////////////////////////////////////////
//	FUNCTIONS
////////////////////////////////////////////
void	DisplayHelp();
int		GetParameter(int argc, char* argv[]);
int		GetParamIdx(char *param);
int		Crate_Receive(char *buffer,short size);
void	Crate_Connect();
void	CloseConnection();
int		SendText(char *cmd,char *value,char *ipaddr);
int		SendScript(char *cmd,char *value,char *ipaddr);
int		_sendtext(char *function,char *result,short size,short receive);
int		GetScript(char *cmd,char *value,char *ipaddr);
