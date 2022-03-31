import sys
import xmlrpc.client

print("The client starts")

server_address = 0
server_port = 0

try:
    while True:
        try:
            command = input()
            command_elements = command.split()
            length = len(command_elements)

            if command_elements[0] == 'connect' and length == 3:
                server_address = command_elements[1]
                server_port = int(command_elements[2])
            elif command_elements[0] == 'getleader' and length == 1:
                if not server_address == server_port == 0:
                    with xmlrpc.client.ServerProxy("http://{}:{}/".format(server_address,server_port)) as server:
                        leader_id, leader_address = server.getLeader()
                        print(leader_id,' ',leader_address)
                else:
                    print("Should connect first")
            elif command_elements[0] == 'suspend' and length == 2:
                if not server_address == server_port == 0:
                    period = int(command_elements[1])
                    with xmlrpc.client.ServerProxy("http://{}:{}/".format(server_address,server_port)) as server:
                        server.Suspend(period)
                else:
                    print("Should connect first")
            elif command_elements[0] == 'quit' and length == 1:
                break
            else:
                print("Couldn't parse command")
        except IndexError:
            continue
        except ValueError:
            print("port and period should be integers")
            continue
        except ConnectionRefusedError:
            print("The server {}:{} is unavailable.".format(server_address, server_port))
            continue
except KeyboardInterrupt:
    print('The client ends')
    sys.exit()
