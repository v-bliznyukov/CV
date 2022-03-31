import sys
import os
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer

list_of_files = []

def send_file(filename, data):
    # check if a file exists
    if os.path.isfile("server/{}".format(filename)):
        print("{} not saved".format(filename))
        return False
    else:
        # if no file at server side
        with open("server/{}".format(filename), "wb") as new_file:
            new_file.write(data.data)
            list_of_files.append(filename)
            print("{} saved".format(filename))
            return True

def list_files():
    return list_of_files


def delete_file(filename):
    # if no such filename
    if not os.path.isfile("server/{}".format(filename)):
        print("{} not deleted".format(filename))
        return False

    else:
        # remove file with specific filename
        os.remove("server/{}".format(filename))
        # remove from list of filenames
        list_of_files.remove(filename)
        print("{} deleted".format(filename))
        return True

def get_file(filename):
    # if no such file
    if not os.path.isfile("server/{}".format(filename)):
        print("No such file: {}".format(filename))
        return False
    else:
        # send file to client
        with open("server/{}".format(filename), "rb") as file:
            data = xmlrpc.client.Binary(file.read())
            print("File send: {}".format(filename))
        return data

def parseToNum(n):
   try:
       num = float(n)
       if (num == int(num)):
           return int(num)
       else:
           return num

   except ValueError:
       return "NaN"

def calculate(expression):
    elements = expression.split()
    if len(elements) != 3:
        print("{} -- not done".format(expression))
        return (False, "Wrong expression")

    sign = elements[0]
    left_operand = parseToNum(elements[1])
    right_operand = parseToNum(elements[2])

    if (left_operand == "NaN" or right_operand == "NaN" or sign not in ["+", "=", "*", "-", "/", "<", ">", ">=", "<="]):
        print("{} -- not done".format(expression))
        return (False, "Wrong expression")

    elif sign == "+":
        return (True, left_operand + right_operand)

    elif sign == "-":
        print("{} -- done".format(expression))
        return (True, left_operand - right_operand)

    elif sign == "*":
        print("{} -- done".format(expression))
        return (True, left_operand * right_operand)

    elif sign == "/":
        if right_operand == 0:
            print("{} -- not done".format(expression))
            return (False, "Division by zero")
        else:
            print("{} -- done".format(expression))
            return (True, left_operand / right_operand)

    elif sign == "<":
        print("{} -- done".format(expression))
        return (True, left_operand < right_operand)

    elif sign == ">":
        print("{} -- done".format(expression))
        return (True, left_operand > right_operand)

    elif sign == ">=":
        print("{} -- done".format(expression))
        return (True, left_operand >= right_operand)

    elif sign == "<=":
        print("{} -- done".format(expression))
        return (True, left_operand <= right_operand)

# handle incorrect start command just in case
try:
    IP_ADDR = sys.argv[1]
    PORT = int(sys.argv[2])

except IndexError:
    print("Usage example: python./server.py <address> <port>")
    sys.exit()

except ValueError:
    print("PORT should be an integer")
    sys.exit()

# creating a directory to store server files (if it is already exists -> pass)
try:
    os.mkdir("server/")
except OSError:
    pass

folder = os.fsencode("server/")
# just in case server folder in non-empty add filenames to the list
for file in os.listdir(folder):
    filename = os.fsdecode(file)
    list_of_files.append(filename)

try:
    with SimpleXMLRPCServer((IP_ADDR, PORT), logRequests=False) as server:
        server.register_function(send_file, 'send')
        server.register_function(delete_file, 'delete')
        server.register_function(get_file, 'get')
        server.register_function(calculate, 'calc')
        server.register_function(list_files, 'get_list')
        server.serve_forever()


except KeyboardInterrupt:
    print("Server is stopping")
    sys.exit()

