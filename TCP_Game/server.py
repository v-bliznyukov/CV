import socket
import sys
from threading import Thread, Lock
import numpy as np
#environment variables
BUF_SIZE = 2048
IP = "127.0.0.1"
ThreadCount = 0
current_ports = []

#functions that decrements number of active threads
def decrement():
   global ThreadCount
   ThreadCount-= 1
   return
#main function for a thread game
def guessingGame(thread,lock,port):
    attempts = 5
    thread.settimeout(5) # thread waits for a client to connect for 5 seconds
    client, client_address = thread.accept()
    client.send("Welcome to the number guessing game!\nEnter the range:".encode())
    try:
        message = client.recv(BUF_SIZE).decode() #receive the range
        num1, num2 = map(int, message.split()) #get 2 boundaries
        number = np.random.randint(num1, num2+1) # randomly choose one num withing the range
        client.send("Amount of attempts is {}".format(attempts).encode()) # send the initial amount of attempts

        while True:
            attempts -= 1 #each turn decrement the number of attempts
            guessed_num = int(client.recv(BUF_SIZE).decode())
            if guessed_num == number:
                client.send("You win!".encode()) # if client guessed correctly
                break
            elif attempts == 0: #if client guessed incorrectly and there will be no more attempts
                client.send("You lose".encode())
                break
            elif guessed_num >= number: #otherwise, if attempts are still available and guess is incorrect, guide the client and start new attempt
                client.send("Less\nAmount of attempts is {}".format(attempts).encode())

            elif guessed_num <= number:
                client.send("More\nAmount of attempts is {}".format(attempts).encode())
        #close client at the end and decrement the number of threads
        client.close()
        with lock:
            decrement()
    #if client connection is lost do the same (keyboard interrupt is handled by the main thread)
    except Exception:
        client.close()
        with lock:
            decrement()
    #remove the freed port from the list of ports in use
    global current_ports
    current_ports.remove(port)

#scan the arguments from the console
try:
    PORT = sys.argv[1]
    PORT = int(PORT)
    current_ports.append(PORT)
except IndexError:
    print("Usage example: python./server.py <port>")
    sys.exit()

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
try:
    #if any error occurs while binding (occupied port or wrong port) -> throw error and exit
    server.bind((IP, PORT))
    print("Starting the server on {}:{}".format(IP,PORT))
except Exception:
    print("Error while binding to the specified port")
    sys.exit()

server.listen()

try:
    while True:
        print("Waiting for a connection")
        client, address = server.accept()
        #if number of threads is 2
        if ThreadCount == 2:
            client.send("The server is full".encode())
            print("The server is full")
            client.close()
        else:
            print('Client connected')
            while True:
                #choose random port and check if it not already used
                port = np.random.randint(2000, 7000)
                if port in current_ports:
                    continue
                else:
                    current_ports.append(port)
                    break

            new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create new socket
            new_socket.bind(("localhost", port))
            new_socket.listen()
            lock = Lock() #create a lock (this is for safe ThreadCount update)
            with lock:
                ThreadCount += 1
            # create a new thread with daemon parameter (that way if parent thread exits the child threads exit also)
            t = Thread(target=guessingGame, args = (new_socket,lock,port),daemon=True)
            t.start()
            #send the port to a client
            client.send(str(port).encode())
            #close the client connection socket
            client.close()
# in case of keyboard interrupt close server and exit
except KeyboardInterrupt:
    server.close()
    sys.exit()



