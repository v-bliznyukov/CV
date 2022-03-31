import zlib

from registry import Registry
from node import Node
import sys
import xmlrpc.client

try:
    # parameters
    m = int(sys.argv[1])
    first_port = int(sys.argv[2])
    last_port = int(sys.argv[3])

    # check for correct input just in case
    if first_port > last_port:
        print("first_port must be less or equal to than last_port")
        sys.exit()
except IndexError:
    print("Usage example: main.py #_of_bits first_port last_port")
    sys.exit()
except ValueError:
    print("Values must be an integer")
    sys.exit()


counter = 0
list_of_ports = []

# creating registry
thread_registry = Registry(m)
thread_registry.setDaemon(True)
thread_registry.start()


# creating nodes as many as possible (num. of ports might be higher than 2**m)
for i in range(first_port, last_port + 1):
    thread_node = Node(i,m)
    thread_node.setDaemon(True)
    if thread_node.node != None:
        list_of_ports.append(i)
        counter += 1
        thread_node.start()


print("Registry and {} nodes are created.".format(counter))

try:
  while True:
     try:
      # wait for a command, is command is incorrect -> ask again
      print("\nEnter the command:")
      command = input()
      command_elements = command.split()
      length = len(command_elements)

      if command == '':
          continue

      #---quit command---#
      if command_elements[0] == "quit" and length == 2:
         port = int(command_elements[1])
         # here and below the programme checks if the port is within [first_port; last_port] boundaries
         if port in list_of_ports:
             node = xmlrpc.client.ServerProxy("http://127.0.0.1:{}/".format(port))
             result = node.quit()
             print("[{},{}]".format(str(result[0]),result[1]))
         else:
             print("[False, Node with port {} isn’t part of the network]".format(port))

      #---get_finger_table command---#
      elif command_elements[0] == "get_finger_table" and length == 2:
          port = int(command_elements[1])
          if port in list_of_ports:
              node = xmlrpc.client.ServerProxy("http://127.0.0.1:{}/".format(port))
              finger_table = node.get_finger_table()
              print(finger_table)
          else:
              print("[False, Node with port {} isn’t available]".format(port))

      #---get_chord_info command---#
      elif command == "get_chord_info":
         # connecting to registry
         registry = xmlrpc.client.ServerProxy("http://127.0.0.1:8007/")
         chord_info = registry.get_chord_info()
         print(chord_info)

      elif command_elements[0] == "save" and length == 3:
          port = int(command_elements[1])
          if port in list_of_ports:
            node = xmlrpc.client.ServerProxy("http://127.0.0.1:{}/".format(port))
            filename = command_elements[2]
            hash_value = zlib.adler32(filename.encode())
            target_id = hash_value % 2 ** m
            print("{} has identifier {}".format(filename, target_id))
            result = node.savefile(filename)
            print("[{},{}]".format(str(result[0]), result[1]))
          else:
              print("[False, Node with port {} isn’t available]".format(port))

      elif command_elements[0] == "get" and length == 3:
          port = int(command_elements[1])
          if port in list_of_ports:
              node = xmlrpc.client.ServerProxy("http://127.0.0.1:{}/".format(port))
              filename = command_elements[2]
              hash_value = zlib.adler32(filename.encode())
              target_id = hash_value % 2 ** m
              print("{} has identifier {}".format(filename, target_id))
              result = node.getfile(filename)
              print("[{},{}]".format(str(result[0]), result[1]))
          else:
              print("[False, Node with port {} isn’t available]".format(port))

     #print the possible error on registry/node side
     except xmlrpc.client.Fault as err:
        print("Fault string: %s" % err.faultString)
     except ValueError:
        print("All ports should be intergers!")

#exit on keyboard interrupt
except KeyboardInterrupt:
 print("Keyboard Interrupt")
 sys.exit()
#or other exception created by main
except Exception as error:
 print(str(error))
 sys.exit()




