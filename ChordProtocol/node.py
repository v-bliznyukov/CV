from threading import Thread
import xmlrpc.client
from time import sleep
from xmlrpc.server import SimpleXMLRPCServer
import zlib

class Node(Thread):
    # intial values for node object
    id = 0
    port = -1
    finger_table = {}
    predecessor = None
    successor = None
    m = 0
    not_quitted = True
    filenames = []
    nodes_communicate = []

    def __init__(self,port,m):
        # create a thread
        super().__init__()
        self.port = port
        self.m = m
        with xmlrpc.client.ServerProxy("http://127.0.0.1:8007/") as registry:
            result = registry.register(self.port)
        # if registration is successful, then initialize server, id, port and register functions
        if result[0] != -1:
            self.id = result[0]
            self.node = SimpleXMLRPCServer(('127.0.0.1', self.port), logRequests=False)
            self.node.register_function(self.get_finger_table)
            self.node.register_function(self.quit)
            self.node.register_function(self.notify_s)
            self.node.register_function(self.notify_p)
            self.node.register_function(self.savefile)
            self.node.register_function(self.getfile)
        else:
            #otherwise, init node (server) to none, and print out the error message
            self.node = None
            print(result[1])

    def lookup(self, target_id):
        if self.at_range(self.predecessor[0], self.id, target_id):
           return self.id
        if self.at_range(self.id, self.successor, target_id):
           return self.successor
        for i in range(len(self.nodes_communicate)-1):
           if self.at_range(self.nodes_communicate[i], self.nodes_communicate[i+1], target_id):
               return self.nodes_communicate[i]
        return self.nodes_communicate[-1]

    def at_range(self, A, B, target):
        if B > A:
            if B >= target and target > A:
                return True
        elif B < A:
            if A < target or target <= B:
                return True
        return False

    def notify_s(self, files, predecessor):
        self.filenames += files
        self.predecessor = predecessor
        return True

    def notify_p(self, successor):
        self.successor = successor
        return True

    def savefile(self,filename):
        hash_value = zlib.adler32(filename.encode())
        target_id = hash_value % 2**self.m
        lookup_id = self.lookup(target_id)
        if self.not_quitted == False:
            return (False, "Node with port {} isn’t part of the network".format(self.port))
        if lookup_id != self.id:
            print("node {} passed {} to node {}".format(self.id, filename, lookup_id))
            port = self.finger_table[str(lookup_id)]
            with xmlrpc.client.ServerProxy("http://127.0.0.1:{}/".format(port)) as node:
                return node.savefile(filename)
        else:
            if filename in self.filenames:
                return (False, "{} already exists in node {}".format(filename,self.id))
            else:
                self.filenames.append(filename)
                return (True, "{} is saved in node {}".format(filename, self.id))

    def getfile(self,filename):
        hash_value = zlib.adler32(filename.encode())
        target_id = hash_value % 2 ** self.m
        lookup_id = self.lookup(target_id)
        if self.not_quitted == False:
            return (False, "Node with port {} isn’t part of the network".format(self.port))
        if lookup_id != self.id:
            print("node {} passed request to node {}".format(self.id, lookup_id))
            port = self.finger_table[str(lookup_id)]
            with xmlrpc.client.ServerProxy("http://127.0.0.1:{}/".format(port)) as node:
                return node.getfile(filename)
        else:
            if filename in self.filenames:
                return (True, "node {} has {}".format(self.id, filename))
            else:
                return (False, "node {} doesn't have {}".format(self.id, filename))

    def get_finger_table(self):
        return self.finger_table

    def quit(self):
        with xmlrpc.client.ServerProxy("http://127.0.0.1:8007/") as registry:
            result = registry.deregister(self.id)
            if result[0] == True:
                self.not_quitted = False
                if result[1] != 0:
                    successor_port = self.finger_table[str(self.successor)]
                    predecessor_port = self.predecessor[1]
                    successor_node = xmlrpc.client.ServerProxy("http://127.0.0.1:{}/".format(successor_port))
                    successor_node.notify_s(self.filenames, self.predecessor)
                    predecessor_node = xmlrpc.client.ServerProxy("http://127.0.0.1:{}/".format(predecessor_port))
                    predecessor_node.notify_p(self.successor)
                return(True, "Node {} with port {} was successfully removed".format(self.id, self.port))
            else:
                return (False, "Node {} with port {} isn’t part of the network".format(self.id, self.port))

    def ft_updator(self):
        while self.not_quitted:
            sleep(1)
            try:
                with xmlrpc.client.ServerProxy("http://127.0.0.1:8007/") as registry:
                    self.finger_table, self.predecessor = registry.populate_finger_table(self.id)
                    if self.finger_table != False:
                        self.nodes_communicate = []
                        for key in self.finger_table.keys():
                            self.nodes_communicate.append(int(key))
                        self.successor = self.nodes_communicate[0]
                    else:
                        self.nodes_communicate.append(self.id)
                        self.successor = self.id
                        self.predecessor = (self.id, self.port)
            except OSError:
                continue
    def run(self):
        thread = Thread(target=self.ft_updator, daemon=True)
        thread.start()
        try:
            self.node.serve_forever()
        except OSError:
            self.node.serve_forever()


