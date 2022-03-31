import socket
import os
import time


client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Creating a new client socket

DEST_IP_ADDR = "127.0.0.1"
DEST_PORT = 8091
BUF_SIZE = 2048 # client's buf-size
SERVER_BUF_SIZE = 0 # server's buf-size (updated with the first ACK message)
first_message = True # flag to check if the message sent is the first one
seqno = 0 # sequence number for a packet

class FileIsEmpty(Exception): #custom exception that terminates file transmission
    pass

#---Function that creates a data packet---#

def createMessage(picture, seqno):

  seqno_size = len(("d" + "|"+ str(seqno) + "|").encode()) # get byte-size of a 'header'
  image_chunk = SERVER_BUF_SIZE - seqno_size # compute available space for image for the next chunk
  data_bytes = picture.read(image_chunk)
  if not data_bytes: # if no data to read, raise exception
      raise FileIsEmpty
  return ("d" + "|"+ str(seqno) + "|").encode() + data_bytes


try:
    #--Name a file to transfer--#
    filename = 'innopolis.jpg'
    name, extension = filename.split('.')
    file = open(filename, 'rb')
    file_size = os.path.getsize(filename)

    while True:
        #--First message has the following structure--#
        if first_message:
            sent_message = "s|{}|.{}|{}".format(seqno, extension, file_size).encode()
        else:
            sent_message = createMessage(file, seqno)
        #--Send a message--#

        client.sendto(sent_message,(DEST_IP_ADDR,DEST_PORT))

        #--Wait for a reply--#
        i = 0
        while True:
            try:
                client.settimeout(0.5)
                message, addr = client.recvfrom(BUF_SIZE)

                #--In case of successful ACK unpack the package--#
                if first_message:
                    message_type, content = message.split("|".encode(), maxsplit=1)
                    seqno_server, buffsize = content.split("|".encode(), maxsplit=1)
                    seqno = int(seqno_server.decode())
                    SERVER_BUF_SIZE = int(buffsize.decode())
                    first_message = False
                    break
                else:
                    message_type, seqno_server = message.split("|".encode(), maxsplit=1)
                    seqno = int(seqno_server)
                    break

            #--If ACK is not received, retransmitt (5 trials)--#
            except socket.timeout:
                i += 1
                if (i == 6):
                    print("Server is down")
                    raise KeyboardInterrupt #in case of 5 unsuccessful interrupt exit client
                else:
                    print('Trying to reconnect')
                    client.sendto(sent_message,(DEST_IP_ADDR,DEST_PORT))

except KeyboardInterrupt:
    print("Exiting client")

except FileIsEmpty:
    print("File has been transferred")

#--Close files and client--#

print("Closing files")
file.close()
print("Closing client")
client.close()