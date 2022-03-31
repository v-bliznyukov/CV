from socket import socket, AF_INET, SOCK_DGRAM

DEST_IP_ADDR = "127.0.0.1"
DEST_PORT = 7780
PORT = 7779
BUF_SIZE = 100

s = socket(AF_INET,SOCK_DGRAM)

s.bind(("localhost", PORT))

try:
   while True:
        message = input("Input the expression:")

        if (message.lower() == 'quit'):
            print("User has quit")
            break

        s.sendto(message.encode(), (DEST_IP_ADDR,DEST_PORT))

        data, addr = s.recvfrom(BUF_SIZE)
        print(data.decode())

except KeyboardInterrupt:
    print()
    print("User has quit")

s.close()

