int sock;

/**This block is needed only if using WinSocket (Windows) to initialize the socket*/

printf("\nInitialising Winsock...\n\n"); 
WSADATA wsa;

if (WSAStartup(MAKEWORD(2,2),&wsa) != 0){
        printf("Failed. Error Code : %d",WSAGetLastError());
return 1; 
}

/** End of WinSocket initializing*/
if( (sock = socket(AF_INET, SOCK_STREAM , 0)) == INVALID_SOCKET ){
    printf("Could not create socket");
    return -1; }

/*Initialize address of device
* IP address needs to be adapted, depending on local network and Ethernet
settings of the device*/

struct sockaddr_in server;
server.sin_addr.s_addr = inet_addr("192.168.100.115"); 
server.sin_family = AF_INET;
server.sin_port = htons( 5000 );
    //Connect to remote server
if (connect(sock , (struct sockaddr *)&server , sizeof(server)) < 0){ printf("connect error");
return -1;
}