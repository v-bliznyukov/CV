import os
import sys
import xmlrpc.client

# handle incorrect start command just in case
try:

    DEST_IP_ADDR = sys.argv[1]
    DEST_PORT = int(sys.argv[2])

except IndexError:
    print("Usage example: python./client.py <address> <port>")
    sys.exit()

except ValueError:
    print("PORT should be an integer")
    sys.exit()

try:
    with xmlrpc.client.ServerProxy("http://{}:{}/".format(DEST_IP_ADDR,DEST_PORT)) as server:
        while True:
            try:
                print("\nEnter the command:")
                command = input()
                command_elements = command.split()
                length = len(command_elements)

                #---Quit command---#
                if command == "quit":
                    print("Client is stopping")
                    sys.exit()

                #---Send command---#
                elif length == 2 and command_elements[0] == "send":
                    command, filename = command.split()

                    if not os.path.isfile(filename):
                        print("Not completed")
                        print("No such file")
                    else:
                        file = open(filename, "rb")
                        data = xmlrpc.client.Binary(file.read())
                        result = server.send(filename, data)
                        if result:
                            print("Completed")
                        else:
                            print("Not completed")
                            print("File already exists")

                #---List command---#
                elif command_elements[0] == "list" and length == 1:
                    files = server.get_list()
                    for item in files:
                        print(item)
                    print("Completed")

                #---Delete command---#
                elif command_elements[0] == "delete" and length == 2:
                    command, filename = command.split()
                    result = server.delete(filename)
                    if result:
                        print("Completed")
                    else:
                        print("Not completed")
                        print("No such file")


                #---Get command---#
                elif command_elements[0] == "get" and 3 >= length >= 2:
                    # if there are 3 arguments
                    if length == 3:
                        command, filename, newfilename = command.split()
                        if os.path.isfile(newfilename):
                            print("Not completed")
                            print("File already exists")
                        else:
                             file = server.get(filename)
                             if file == False:
                                 print("Not completed")
                                 print("No such file")
                             else:
                                 with open(newfilename, "wb") as newfile:
                                     newfile.write(file.data)
                                 print("Completed")
                    else:
                        # if there are 2 arguments
                        command, filename = command.split()
                        if os.path.isfile(filename):
                            print("Not completed")
                            print("File already exists")
                        else:
                            file = server.get(filename)
                            if file == False:
                                print("Not completed")
                                print("No such file")
                            else:
                                with open(filename, "wb") as newfile:
                                    newfile.write(file.data)
                                    print("Completed")

                #---Calc command---#
                elif command_elements[0] == "calc" and length >= 2:
                    command, expression = command.split(maxsplit=1)
                    result = server.calc(expression)
                    if result[0]:
                        print(result[1])
                        print("Completed")
                    else:
                        print("Not completed")
                        print(result[1])

                else:
                    print("Not completed")
                    print("Wrong command")
            # print error from server side
            except xmlrpc.client.Fault as err:
                print("Not completed")
                print("Fault string: %s" % err.faultString)

except KeyboardInterrupt:
    print("Client is stopping")
    sys.exit()

except Exception as error:
    print(str(error))
    print("Client is stopping")
    sys.exit()




