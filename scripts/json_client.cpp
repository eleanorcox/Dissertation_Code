#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <iostream>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

void error(const char *msg) {
	perror(msg);
	exit(0);
}

int main(int argc, char *argv[]) {
	int sockfd, portno, n;
	struct sockaddr_in serv_addr;
	struct hostent *server;

	char buffer[512];
	if (argc < 3) {
		fprintf(stderr,"usage %s hostname port\n", argv[0]);
		exit(0);
	}

  portno = atoi(argv[2]);
  sockfd = socket(AF_INET, SOCK_STREAM, 0);
  if (sockfd < 0)
    error("ERROR opening socket");

	server = gethostbyname(argv[1]);
  if (server == NULL) {
    fprintf(stderr,"ERROR, no such host\n");
    exit(0);
  }

	bzero((char *) &serv_addr, sizeof(serv_addr));
  serv_addr.sin_family = AF_INET;
  bcopy((char *)server->h_addr,
       (char *)&serv_addr.sin_addr.s_addr,
       server->h_length);
  serv_addr.sin_port = htons(portno);
  if (connect(sockfd,(struct sockaddr *) &serv_addr,sizeof(serv_addr)) < 0)
    error("ERROR connecting");

	json j;
	j["test"] = {0,1,2};

  // j["data"] = {0.00293035,
  //               0.00160099,
  //               0.000359102,
  //               -0.000851335,
  //               -0.00175064,
  //               -0.00161139,
  //               0,
  //               0.00108983,
  //               0.00115877,
  //               0.00118993,
  //               0.00155764,
  //               0.00201586,
  //               1.85658,
  //               1.67926,
  //               1.44182,
  //               1.14568,
  //               0.799541,
  //               0.413394,
  //               0,
  //               -0.422727,
  //               -0.839049,
  //               -1.23074,
  //               -1.58498,
  //               -1.88441,
  //               -0.00155115,
  //               -0.0012941,
  //               -0.000899192,
  //               -0.000394523,
  //               9.75928e-05,
  //               0.000273061,
  //               -1.13378e-16,
  //               -0.000368698,
  //               -0.000531688,
  //               -0.000592779,
  //               -0.000647052,
  //               -0.000634936,
  //               -2.37307,
  //               -2.86179,
  //               -3.34781,
  //               -3.8011,
  //               -4.1801,
  //               -4.43111,
  //               -4.47354,
  //               -4.43117,
  //               -4.18053,
  //               -3.8024,
  //               -3.3507,
  //               -2.86672,
  //               -0.118667,
  //               -0.117794,
  //               -0.117658,
  //               -0.118112,
  //               -0.11898,
  //               -0.120241,
  //               -0.121848,
  //               -0.123632,
  //               -0.125552,
  //               -0.127602,
  //               -0.129827,
  //               -0.132216,
  //               -1.7727,
  //               -1.77374,
  //               -1.7742,
  //               -1.77425,
  //               -1.77404,
  //               -1.77353,
  //               -1.77276,
  //               -1.77184,
  //               -1.77099,
  //               -1.76992,
  //               -1.76859,
  //               -1.7671,
  //               -1.3792,
  //               -1.37898,
  //               -1.37856,
  //               -1.37804,
  //               -1.37736,
  //               -1.37668,
  //               -1.37585,
  //               -1.37495,
  //               -1.37408,
  //               -1.37305,
  //               -1.37197,
  //               -1.3709,
  //               -0.278949,
  //               -0.278509,
  //               -0.278475,
  //               -0.278167,
  //               -0.278041,
  //               -0.278022,
  //               -0.278122,
  //               -0.278149,
  //               -0.27786,
  //               -0.278099,
  //               -0.278063,
  //               -0.278318,
  //               -0.131919,
  //               -0.132078,
  //               -0.132208,
  //               -0.132185,
  //               -0.132142,
  //               -0.132063,
  //               -0.132104,
  //               -0.132178,
  //               -0.132063,
  //               -0.132168,
  //               -0.132356,
  //               -0.132426,
  //               -0.0435566,
  //               -0.0435566,
  //               -0.043548,
  //               -0.0435823,
  //               -0.0435823,
  //               -0.0435737,
  //               -0.0436508,
  //               -0.043685,
  //               -0.0437278,
  //               -0.0436679,
  //               -0.0436936,
  //               -0.0434453,
  //               0,
  //               -1.02801,
  //               0,
  //               0,
  //               -1.02801e-10,
  //               0,
  //               -0.0934805,
  //               -0.914939,
  //               -0.00786061,
  //               -0.129297,
  //               -0.523707,
  //               -0.151812,
  //               -0.0890103,
  //               -0.142404,
  //               0.0479095,
  //               -0.113049,
  //               -0.0635174,
  //               -0.0518847,
  //               0,
  //               -1.02801e-10,
  //               0,
  //               0.0973179,
  //               -0.923752,
  //               -0.00655393,
  //               0.129723,
  //               -0.517339,
  //               -0.160719,
  //               0.0874852,
  //               -0.137418,
  //               0.0459194,
  //               0.112369,
  //               -0.0609057,
  //               -0.0582083,
  //               0,
  //               -1.02801e-10,
  //               0,
  //               0.00207026,
  //               -1.10991,
  //               -0.0499593,
  //               0.00496358,
  //               -1.23119,
  //               -0.132165,
  //               4.96358e-13,
  //               -1.23119e-10,
  //               -1.32165e-11,
  //               0.00276774,
  //               -1.32756,
  //               -0.151,
  //               0.000973394,
  //               -1.397,
  //               -0.172313,
  //               4.96358e-13,
  //               -1.23119e-10,
  //               -1.32165e-11,
  //               -0.158332,
  //               -1.33105,
  //               -0.0762412,
  //               -0.271931,
  //               -1.0514,
  //               -0.00803194,
  //               -0.250914,
  //               -0.940313,
  //               -0.128344,
  //               -2.50914e-11,
  //               -9.40313e-11,
  //               -1.28344e-11,
  //               -2.48696e-11,
  //               -9.20503e-11,
  //               -1.54771e-11,
  //               -2.50914e-11,
  //               -9.40313e-11,
  //               -1.28344e-11,
  //               4.96358e-13,
  //               -1.23119e-10,
  //               -1.32165e-11,
  //               0.151741,
  //               -1.33713,
  //               -0.0773709,
  //               0.272051,
  //               -1.04718,
  //               -0.00599731,
  //               0.251192,
  //               -0.93748,
  //               -0.126375,
  //               2.51192e-11,
  //               -9.3748e-11,
  //               -1.26375e-11,
  //               2.49045e-11,
  //               -9.20705e-11,
  //               -1.49808e-11,
  //               2.51192e-11,
  //               -9.3748e-11,
  //               -1.26375e-11,
  //               0.000458362,
  //               0.000300444,
  //               -0.125226,
  //               4.58362e-14,
  //               3.00444e-14,
  //               -1.25226e-11,
  //               0.000553433,
  //               0.000315471,
  //               -0.125987,
  //               -0.00244587,
  //               4.20691e-05,
  //               -0.133671,
  //               -0.00423466,
  //               -0.00105285,
  //               -0.138311,
  //               -0.00480097,
  //               -0.000731918,
  //               -0.139024,
  //               4.58362e-14,
  //               3.00444e-14,
  //               -1.25226e-11,
  //               0.000278359,
  //               0.000303439,
  //               -0.125972,
  //               0.00224651,
  //               0.000443326,
  //               -0.132056,
  //               0.00362542,
  //               4.0178e-05,
  //               -0.135271,
  //               0.00429988,
  //               0.000172631,
  //               -0.136596,
  //               4.58362e-14,
  //               3.00444e-14,
  //               -1.25226e-11,
  //               0.00040309,
  //               0.000293825,
  //               -0.123104,
  //               0.000420824,
  //               0.000312964,
  //               -0.122281,
  //               4.20824e-14,
  //               3.12964e-14,
  //               -1.22281e-11,
  //               0.000470065,
  //               0.000317621,
  //               -0.121166,
  //               0.00051698,
  //               0.000319937,
  //               -0.1196,
  //               4.20824e-14,
  //               3.12964e-14,
  //               -1.22281e-11,
  //               0.000956774,
  //               0.000320326,
  //               -0.121339,
  //               0.00188946,
  //               0.000300019,
  //               -0.124028,
  //               0.00117311,
  //               0.000727357,
  //               -0.125149,
  //               1.17311e-13,
  //               7.27357e-14,
  //               -1.25149e-11,
  //               1.03958e-13,
  //               8.26368e-14,
  //               -1.2505e-11,
  //               1.17311e-13,
  //               7.27357e-14,
  //               -1.25149e-11,
  //               4.20824e-14,
  //               3.12964e-14,
  //               -1.22281e-11,
  //               0.000292168,
  //               0.000590083,
  //               -0.121545,
  //               -0.000717911,
  //               0.00102557,
  //               -0.125456,
  //               -0.00071135,
  //               0.00098144,
  //               -0.126531,
  //               -7.1135e-14,
  //               9.8144e-14,
  //               -1.26531e-11,
  //               -7.1027e-14,
  //               9.71026e-14,
  //               -1.26391e-11,
  //               -7.1135e-14,
  //               9.8144e-14,
  //               -1.26531e-11,
  //               0.0263981,
  //               0.0304921,
  //               0.0335853,
  //               0.0355465,
  //               0.0373688,
  //               0.0387414,
  //               0.0387493,
  //               0.0381652,
  //               0.0373086,
  //               0.0361115,
  //               0.0346209,
  //               0.0334258,
  //               -0.00463098,
  //               -0.0024453,
  //               -0.000915095,
  //               -0.000414441,
  //               0.00103876,
  //               0.00257107,
  //               0.0025887,
  //               0.00229163,
  //               0.00147622,
  //               0.000275559,
  //               -0.000747972,
  //               -0.00108786,
  //               0.0281892,
  //               0.0324783,
  //               0.0360791,
  //               0.0393708,
  //               0.0429899,
  //               0.0464179,
  //               0.0482337,
  //               0.0485565,
  //               0.0480889,
  //               0.0475573,
  //               0.0478124,
  //               0.0487801};

	j["data"] = {0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0,
							  0};


	std::string b;
	b = j.dump();

  n = write(sockfd,b.c_str(),4000);
  if (n < 0)
		error("ERROR writing to socket");

  bzero(buffer,512);
  n = read(sockfd,buffer,511);
  if (n < 0)
		error("ERROR reading from socket");
  printf("%s\n",buffer);

  close(sockfd);
  return 0;
}