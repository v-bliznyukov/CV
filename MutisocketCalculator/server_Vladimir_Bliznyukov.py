from socket import socket, AF_INET, SOCK_DGRAM, timeout
import time

IP_ADDR = "127.0.0.1"
PORT = 7780
BUF_SIZE=100

class InvalidParametersException(Exception):
    pass

def parseToNum(n):
   try:
       num = float(n)
       if (num == int(num)):
           return int(num)
       else:
           return num

   except ValueError:
       return "NaN"


def calculator(data):

    elements = data.split()
    if len(elements) != 3 :
        raise InvalidParametersException

    sign = elements[0]
    left_operand  = parseToNum(elements[1])
    right_operand  = parseToNum(elements[2])

    if (left_operand == "NaN" or right_operand == "NaN" or sign not in ["+", "=","*","-", "/", "<", ">", ">=", "<="]):
        raise InvalidParametersException
    elif sign == "+":
        return left_operand + right_operand 
    
    elif sign == "-":
        return left_operand  - right_operand 
    
    elif sign == "*":

        return left_operand  * right_operand 
    
    elif sign == "/":
        if right_operand  == 0:
            return "You cannot divide by 0"
        else:
            return left_operand  / right_operand 
    
    elif sign == "<":
        return left_operand  < right_operand 
    
    elif sign == ">":
        return left_operand  > right_operand 
    
    elif sign == ">=":
        return left_operand  >= right_operand 

    elif sign == "<=":
        return left_operand  <= right_operand 


with socket(AF_INET,SOCK_DGRAM) as s:
     s.bind((IP_ADDR, PORT))
     print("Server started at: {}".format(time.time()))
     try:
         while True:
            try:
                print('Waiting for a new message')
                data, addr = s.recvfrom(BUF_SIZE)
                print("Client at {}: {}".format(addr, data.decode()))
                answer = calculator(data.decode())
                answer = str(answer)
                s.sendto(answer.encode(), addr)

            except InvalidParametersException:
                s.sendto("Invalid parameters".encode(), addr)

     except KeyboardInterrupt:
        print()
        print("KeyboardInterrupt")




