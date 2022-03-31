import socket
import time
from multiprocessing import Process

#--Initial server setup--#

Clients = 0
BUF_SIZE = 2048
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(('localhost', 8091))

sessions = {} # dictionary to store current sessions

#--Function to release the data allocated--#
def delete(client_address):
    # --Wait for 1 second and release data in the dictionary--#
    time.sleep(1)
    print("Closing created files for {}".format(client_address))
    sessions[client_address][4].close()
    print("Releasing data for {}".format(client_address))
    sessions.pop(client_address,None)
    print(sessions)

#--Function of to serve one particular message and client--#

def threaded_client(data, client_address):
    duplicate = False
    message = data
    receive_time = time.time() # record packet receive time
    message_type, content = message.split("|".encode(), maxsplit=1) # extract needed info
    message_type = message_type.decode()

    #--Start message processing--#

    if message_type == "s":
        seqno, extension, size = content.split("|".encode(), maxsplit=2)
        seqno = int(seqno.decode())

        #--If session is not already in dictionary, then this is the very 1st message--#

        if not(client_address in sessions.keys()):
            extension = extension.decode()
            size = int(size.decode())
            new_message = "a|{}|{}".format(seqno + 1, BUF_SIZE).encode()
            global Clients
            Clients += 1
            filename = 'server{}{}'.format(Clients,extension)

            #---Adding to dictionary---#
            sessions[client_address] = [seqno + 1, receive_time, size, extension, open(filename, "wb")]

        else:
            #--otherwise, set dublicate flag to true for the current packet--#
            size = int(size.decode())
            duplicate = True
            print('this is a dublicate')

    elif message_type == "d":
        seqno, image_chunk = content.split("|".encode(), maxsplit=1)
        seqno = int(seqno.decode())
        #--If sequence number is less than expected, then it is a duplicate packet--#
        if not(client_address in sessions.keys()):
            return
        if not(seqno <= sessions[client_address][0] - 1):
            new_message = "a|{}".format(seqno + 1).encode()

            # ---Updating dictionary---#
            sessions[client_address][2] -= len(image_chunk)
            sessions[client_address][4].write(image_chunk)
            sessions[client_address][0] = seqno + 1
            sessions[client_address][1] = receive_time

        else:
            # --otherwise, set duplicate flag to true for the current packet--#
            duplicate = True

    #--If packet was not a duplicate, send an ACK message--#
    if not duplicate:
        server.sendto(new_message, client_address)

    # --If expected size is 0, then transmission is finished for this client--#
    if sessions[client_address][2] == 0 and not(duplicate):
        print("File from {} has been received".format(client_address))
        #--Wait for 1 second and release data in the dictionary--#
        time.sleep(1)
        print("Closing created files for {}".format(client_address))
        sessions[client_address][4].close()
        print("Releasing data for {}".format(client_address))
        sessions.pop(client_address, None)
        #p = Process(target=delete, args=(client_address,))
        #p.start()
        return

#--Main loop--#
try:
    while True:
        #--Every 0.05 seconds we check all connections to be within 3 sec interval between 2 received packets--#
        #--remember set of available keys--#
        keys = list(sessions)
        #--check if the last message was received >3 sec ago--#
        for key in keys:
            current_time = time.time()
            if current_time - sessions[key][1] >= 3:
                sessions.pop(key, None)
                print("Releasing data for client on address")
        try:
            #--Wait for a new message--#
            server.settimeout(0.05)
            data, client_address = server.recvfrom(BUF_SIZE)
            #-process the message--#
            threaded_client(data,client_address)
        except socket.timeout:
            continue
except KeyboardInterrupt:
    print("Server was interrupted")

server.close()
