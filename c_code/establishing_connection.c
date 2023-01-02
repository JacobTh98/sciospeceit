int sock;
char *cmd, *readBuffer;
/**This block is needed only if using WinSocket (Windows) to initialize the socket*/
printf("\nInitialising Winsock...\n\n");
WSADATA wsa;

if (WSAStartup(MAKEWORD(2,2),&wsa) != 0){ printf("Failed. Error Code : %d",WSAGetLastError()); return 1;
}
/** End of WinSocket initializing*/
if( (sock = socket(AF_INET, SOCK_STREAM , 0)) == INVALID_SOCKET ){ printf("Could not create socket");
return -1;
}
/*Initialize address of Device
* IP address needs to be adapted, depending on local network and Ethernet settings in Device*/
struct sockaddr_in server;
server.sin_addr.s_addr = inet_addr("192.168.100.115");
server.sin_family = AF_INET;
server.sin_port = htons( 5000 );
//Connect to remote server
if (connect(sock , (struct sockaddr *)&server , sizeof(server)) < 0){ printf("connect error");
return -1;
}
/* ************************* *
* Reading DeviceID *
* ************************* */
int numberOfBytes = 3;
printf("Reading DeviceId\n");
cmd = (char*)malloc(sizeof(byte)*numberOfBytes); cmd[0] = 0xD1; cmd[1] = 0x00; cmd[2] = 0xD1; if( send(sock , cmd , numberOfBytes , 0) < 0) { printf("Could not send cmd.");
return -1; } free(cmd);
readBuffer = (char*)malloc(sizeof(byte)*19); recv(sock , readBuffer , 19 , 0);
printf("DeviceID: ");
int i;
for(i=0; i<19;i++){
printf("%.2X ", (byte)readBuffer[i]); }