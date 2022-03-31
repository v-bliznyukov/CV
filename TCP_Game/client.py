import sys
from socket import socket, AF_INET, SOCK_STREAM, timeout

BUF_SIZE = 2048
try:
    # read the arquments from the console
    DEST_IP_ADDR = sys.argv[1]
    DEST_PORT = int(sys.argv[2])
    # is any of the arguments are missing
except IndexError:
    print("Usage example: python./client.py <address> <port>")
    sys.exit()

try:
    # create a socket
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((DEST_IP_ADDR, DEST_PORT))
    # wait for a new port
    message = s.recv(BUF_SIZE)
    if message.decode() == "The server is full":
        print("The server is full")
        sys.exit()

    NEW_PORT = int(message.decode())
    # create new socket
    socket = socket(AF_INET, SOCK_STREAM)
    socket.connect((DEST_IP_ADDR, NEW_PORT))
    print(socket.recv(BUF_SIZE).decode())
    while True:
        try:
            # this is the code that ensures that the range is inputted correctly
            client_range = input()
            if len(client_range.split()) == 2:
                num1 = int(client_range.split()[0])
                num2 = int(client_range.split()[1])
                if num1 < num2:
                    socket.send(client_range.encode())
                    break
                else:
                    print("Enter the range:")
            else:
                print("Enter the range:")
        except ValueError:
            print("Enter the range:")

    while True:
        #wait for answer; if buffer is empty -> throw connection reset exception
        answer = socket.recv(BUF_SIZE).decode()
        if answer == '':
            raise ConnectionResetError
        print(answer)
        if (answer == "You lose" or answer == "You win!"):
            break
        client_message = input()
        socket.send(client_message.encode())


except KeyboardInterrupt:
    sys.exit()
# if conncetion is lost
except (ConnectionResetError, BrokenPipeError):
    print("Connection is lost")
    sys.exit()

# if socket.connect was unsuccessful
except ConnectionRefusedError:
    print("Server is unavailable")
    sys.exit()




