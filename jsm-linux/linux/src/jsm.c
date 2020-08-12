#include "jsm.h"

////////////////////////////////////////////
//	VARIABLES
////////////////////////////////////////////
OPTIONS options[] = {
	{"-h"	,"help"							,"",1,"",""},
	{"-u"	,"upload script"				,"Script file uploaded.",1,"lua_setfile",""},
	{"-ip"	,"Jenet IP address"	            ,"",1,"",""},
	{"-run"	,"run script"					,"Script running.",0,"lua_setrun","1"},
	{"-stop","stop script"					,"Script stopped.",0,"lua_setrun","0"},
	{"-s"	,"store script"					,"Script stored.",0,"lua_store",""},
	{"-rob"	,"set Run-on-Boot flag"			,"Run-on-Boot flag written.",1,"ee_setrob",""},
	{"-d"	,"download script"				,"Script file downloaded.",1,"lua_getfile",""},
	{"-e"	,"download error file"			,"Error file uploaded.",1,"lua_geterr",""},
	{"-l"	,"download log file"			,"Log file uploaded.",1,"lua_getlog",""},
};

char param[MAX_PARAM][MAX_LEN_PARAM];
int connection_ok = 0;
int error_code = 0;
SOCKET	sock;
////////////////////////////////////////////
//	main
////////////////////////////////////////////
int main(int argc, char* argv[])
{
	int i=0,nParameter,idx,x;

#ifdef WIN32
	WSADATA WSAData;
	if (WSAStartup (MAKEWORD(1,1), &WSAData) != 0) {
		perror("Error init library!\n");
		return 0;
	}

#endif

//	printf("\r\nJenet Script Manager %d.%d - %s\r\n\r\n", MAJOR_VER, MINOR_VER, __DATE__);

	if (argc == 1) {
		printf("bad parameter number\r\ntype jsm -h for help.\r\n\r\n");
	}
	else {
		nParameter = GetParameter(argc,argv);
		if (nParameter == -1) {
			exit(0);
		}
		else {
			for (i = 0; i < nParameter; i++) {
				idx = GetParamIdx(param[i]);
				if (idx != IP_ADDR) {
					if (idx == FILE_NAME) 
						x = SendScript(options[FILE_NAME].cmd, options[FILE_NAME].value, options[IP_ADDR].value);
					else if ((idx == GET_SCRIPT) ||	(idx == GET_ERR) ||	(idx == GET_LOG))
						x = GetScript(options[idx].cmd, options[idx].value, options[IP_ADDR].value);
					else
						x = SendText(options[idx].cmd, options[idx].value, options[IP_ADDR].value);
					
					if(x != -1)	{
						if (((idx == GET_SCRIPT) ||	(idx == GET_ERR) ||	(idx == GET_LOG)) && 
							(strcmp(options[idx].value,"stdout")==0))
							;	
						else
							printf("%s\r\n",options[idx].ret);
					}
				}
			}
		}
	}

	CloseConnection();

	return 0;
}

////////////////////////////////////////////
//	GetParameter
////////////////////////////////////////////
int GetParameter(int argc, char* argv[])
{
	int i,idx,npar = 0;
	for(i=1;i<argc;i++) {

		idx = GetParamIdx(argv[i]);
		if(idx == -1) {

			printf("bad parameter: %s\r\n",argv[i]);
			npar = -1;
			break;
		}
		else {

			if((idx == HELP) && (i == 1)) {

				DisplayHelp();
				npar = -1;
				break;
			}
			else {

				strncpy(param[npar],argv[i],MAX_LEN_PARAM-1);
				param[npar][MAX_LEN_PARAM-1] = '\0';
				if(options[idx].getvalue == 1) {

					if((i+1) <= (argc-1)) {

						if(argv[i+1][0]== '-') {

							printf("no option for %s\r\n",argv[i]);
							npar = -1;
							break;
						}
						else {

							strncpy(options[idx].value,argv[i+1],MAX_LEN_PARAM-1);
							options[idx].value[MAX_LEN_PARAM-1] = '\0';
							i++;
						}
					}
					else {

						printf("no option for %s\r\n",argv[i]);
						npar = -1;
						break;
					}
				}
				npar++;
			}
		}
	}

	return npar;
}

////////////////////////////////////////////
//	GetParamIdx
////////////////////////////////////////////
int GetParamIdx(char *param)
{
	int i, retcode = -1;
	short nParam = sizeof(options)/sizeof(OPTIONS);
	for(i=0;i< nParam;i++) {

#ifdef WIN32

		if(strcmp(_strlwr(param),options[i].par) == 0) break;
#else
		if(strcasecmp(param,options[i].par) == 0) break;
#endif

	}

	if(i < nParam) retcode = i;

	return retcode;
}

////////////////////////////////////////////
//	DisplayHelp
////////////////////////////////////////////
void DisplayHelp()
{
	int i;
	short nParam = sizeof(options)/sizeof(OPTIONS);
	printf("\r\nJenet Script Manager %d.%d - %s\r\n\r\n", MAJOR_VER, MINOR_VER, __DATE__);
	for(i=0;i< nParam;i++) {
		printf("%s\t%s\r\n",options[i].par,options[i].rem);
	}
}


////////////////////////////////////////////
//	SendScript
////////////////////////////////////////////
int SendScript(char *cmd,char *value,char *ipaddr)
{
	int retcode = -1;
	struct stat stat_s;
	int attempt = 0;
	char tmpcmd[256];
    int cont = 0,rp;
	int char_to_write;
	FILE *fh;

	int x,h;
	char buffer[256];
	
	h = open(value,O_RDONLY);
	if(h != -1) {

		fstat(h,&stat_s);
		close(h);

		sprintf(tmpcmd,"%s %lu\r\n",cmd,stat_s.st_size);
		x = _sendtext(tmpcmd,buffer,256,0);
		if(x != 0) printf("error sending command script. code = %d",x);
		else {

#ifdef WIN32
			Sleep(1);
#else
			sleep(1);
#endif
			fh =fopen(value,"rb");
			while ((cont < 4) && (attempt < 50)) {

				rp = recv(sock, tmpcmd, 4, 0);
				if (rp > 0) cont += rp;
				else { 
					attempt++;
#ifdef WIN32
					Sleep(1);
#else
					sleep(1);
#endif
				}
			}

			char_to_write = stat_s.st_size;
			while (char_to_write > 0){

				if (char_to_write >= 256)	x = fread(tmpcmd,sizeof(char),256,fh);
				else						x = fread(tmpcmd,sizeof(char),char_to_write,fh);

				send(sock, tmpcmd, x,0);		
				char_to_write -= x;
			}
			fclose(fh);

			retcode = 0;
			CloseConnection();
		}
	}
	else printf("no script file %s\r\n",value);
	
	return retcode;
}

////////////////////////////////////////////
//	SendText
////////////////////////////////////////////
int SendText(char *cmd,char *value,char *ipaddr)
{
	char buffer[256];
	char result[256];
	char retcode = -1;
	int x;
	sprintf(buffer,"%s %s\r\n",cmd,value);
	x = _sendtext(buffer,result,256,1);
	
	if(x != 0) printf("operation error. code = %d",x);
	else retcode = atoi(result);

	return retcode;	
}

////////////////////////////////////////////
//	CloseConnection
////////////////////////////////////////////
void CloseConnection()
{

	connection_ok = 0;
    shutdown(sock, 2);

#ifdef WIN32
	closesocket(sock);
#else
	close(sock);
#endif
}

////////////////////////////////////////////
//	Crate_Receive
////////////////////////////////////////////
int Crate_Receive(char *buffer,short size)
{
	short retcode = ERROR_CRATE;
	char rxbuffer[2];
	int  res, done = 0;
    char *pdest;


    memset(rxbuffer,0,strlen(rxbuffer));
    memset(buffer,0,size);
    while (done == 0) {

        res = recv(sock, rxbuffer, 1, 0);
        if (res > 0) {

	        rxbuffer[1] = '\0';
            strcat(buffer, rxbuffer);
            if (rxbuffer[0] == '\n' ) {
		        done		= 1;
		        error_code	= CRATE_OK;
		        retcode		= CRATE_OK;
            }
        }
        else {

            shutdown(sock, 2);

#ifdef WIN32
			closesocket(sock);
#else
			close(sock);
#endif

			sock		    = -1;
			connection_ok	= 0;
			error_code	    = ERROR_CONNECTION;
			done = 1;
        }
    }
    return retcode;                   
}


////////////////////////////////////////////
//	_sendtext
////////////////////////////////////////////
int _sendtext(char *function,char *result,short size,short receive)
{
	int retcode = -1;

	if(connection_ok != 1) {

		Crate_Connect();
		if(connection_ok != 1) 
			return retcode;
	}

    if(send(sock,function,strlen(function),0) != strlen(function)){

		connection_ok	= 0;
		error_code	    = ERROR_SEND;
	}
    else {
        
		if (receive) 
			retcode = Crate_Receive(result,size);
		else 
			retcode = 0;
    }

	return retcode;
}

////////////////////////////////////////////
//	Crate_Connect
////////////////////////////////////////////
void Crate_Connect()
{
	struct sockaddr_in pin;
	int addr;

	connection_ok		= 0;
	error_code	        = ERROR_CONNECTION;

	if ((sock= socket(AF_INET, SOCK_STREAM, 0)) != 0) {
#ifdef WIN32
		pin.sin_addr.S_un.S_addr	= inet_addr(options[IP_ADDR].value);
#else 
		addr = inet_addr(options[IP_ADDR].value);
		memcpy ((char *) &(pin.sin_addr), (char *)&addr, sizeof(int));
#endif
		pin.sin_family	= AF_INET;
		pin.sin_port	= htons(SOCK_PORT);
    
		if (connect (sock, (void *) &pin, sizeof (pin)) == -1) {

            shutdown(sock, 2);

#ifdef WIN32
			closesocket(sock);
#else
			close(sock);
#endif
			sock = -1;
		}
		else {
			connection_ok	= 1;
			error_code	    = CRATE_OK;
		}
	}
}

////////////////////////////////////////////
//	GetScript
////////////////////////////////////////////
int GetScript(char *cmd, char *value, char *ipaddr)
{
	int retcode = -1;
	int attempt = 0;
	char tmpcmd[256];
    int cont = 0,rp;
	int char_to_read;
	FILE *fh;

	int x;
	char buffer[256];
	
	if (strcmp(value,"stdout")==0)
		fh = stdout;
	else
		fh = fopen(value,"w");
	
	if (fh == NULL) {
		printf("Unable to create script file %s\r\n", value);
		return -1;
	}

	memset(buffer,'\0',255);
	sprintf(tmpcmd,"%s\r\n", cmd);
	x = _sendtext(tmpcmd, buffer, 256, 1);
	if (x != 0) 
		printf("error sending command script. code = %d",x);
	else {
		char_to_read = atoi(buffer);
		sprintf(tmpcmd,"OK\r\n");
		x = _sendtext(tmpcmd, buffer, 256, 0);
		
		if (char_to_read == 0) {
			printf("Requested file is empty.\r\n");
			return -1;
		}

#ifdef WIN32
		Sleep(1);
#else
		sleep(1);
#endif
		
		while ((cont < char_to_read) && (attempt < 50)) {
			rp = recv(sock, tmpcmd, 255, 0);
			if (rp > 0) {
				fwrite(tmpcmd,sizeof(char),rp,fh);
				cont += rp;
			}
			else {	
				attempt++;	
#ifdef WIN32
				Sleep(1);
#else
				sleep(1);
#endif
			}
		}
		if (attempt == 50) { 
			printf("Error downloading script.\r\n");
			retcode = -1;
		}
		fclose(fh);
		
		retcode = 0;
		CloseConnection();
	}
	
	return retcode;
}
