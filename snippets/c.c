//TODO
int Socket;
Socket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
connect(Socket, (struct sockaddr *)&SockAddr, sizeof(SockAddr); 
char sreq[MAXSIZE]; char recresp[MAXSIZE]; //MAXSIZE is 4096
snprintf(sreq, MAXSIZE,
         "POST %s HTTP/1.1\r\n"
         "Host: %s\r\n"
         "Content-Type: application/json\r\n"
         "Content-Length:%d\r\n\r\n" 
          "%s",page, host, strlen(postJson), postJson);

int bWrit; 
bWrit= write(Socket, sreq, strlen(sreq));
printf("bWrit is %d\n", bWrit); 

do {
   bRead = recv(Socket, recresp, MAXSIZE, 0);

   printf(" Now the read bytes are %d\n", bRead);  //this is 7(error)
   printf("Response before conversion:\n%s\n",*recresp); //empty

   if (bRead< 0)
     putMsg("ERROR reading response from socket\n");
     break;
   if (bRead== 0)
     putMsg("Nothing received");
     break;
  } while (bRead != 0);
