import random
from threading import Thread
from xmlrpc.server import SimpleXMLRPCServer
# set seed = 0
random.seed(0)

class Registry(Thread):
    # registry has a node dict and a number of bits for each nodes to encode
    node_id_dict = {}
    m = 0
    # initialize registry server and register the functions
    def __init__(self,m):
        super().__init__()
        self.registry = SimpleXMLRPCServer(('127.0.0.1', 8007), logRequests=False)
        self.registry.register_function(self.register)
        self.registry.register_function(self.deregister)
        self.registry.register_function(self.get_chord_info)
        self.registry.register_function(self.populate_finger_table)
        self.m = m

    def register(self,port):
        try:
            #if dict is full
            if len(self.node_id_dict) >= 2**(self.m):
                return (-1, "No available node can be assigned for {}".format(port))
            while True:
                # choose random id
                id = random.randint(0, 2**self.m-1)
                # if it is not in set of dict keys -> return the id, save the node record
                if str(id) not in self.node_id_dict.keys():
                    self.node_id_dict[str(id)] = port
                    break
            return (id, len(self.node_id_dict))
        # if any exception occured return its string to the calling node
        except Exception as e:
            return (-1, str(e))

    def deregister(self, id):
        try:
            # if node id is still in the chord
            if str(id) in self.node_id_dict.keys():
                self.node_id_dict.pop(str(id), None)
                return (True, len(self.node_id_dict))
            else:
                return(False, "No such node id")
        except Exception as e:
            return (False, str(e))

    def get_chord_info(self):
        return self.node_id_dict
    # successor function
    def successor(self,List,n):
        L = sorted(List)
        for item in L:
            if item >= n:
                return item
        return L[0]

    def predecessor(self, List,n):
        L = sorted(List)
        for item in reversed(L):
            if item < n:
                return item
        return L[-1]

    def populate_finger_table(self, id):
        try:
            if str(id) not in self.node_id_dict.keys():
                return (False,"Node id does not exist")
            # transform set of dict key to integers list
            keys_list = [int(x) for x in list(self.node_id_dict.keys())]
            # exclude the calling node
            keys_list.remove(id)
            finger_table = {}
            # if the list contains at least one node
            if len(keys_list) != 0:
                # populate finger table
                for i in range(self.m):
                    value = id + 2**i
                    # call successor function on mod(value, 2**m)
                    successor_id = self.successor(keys_list, value%(2**self.m))
                    # to avoid duplicates add only new nodes current node can communicate with
                    if str(successor_id) not in finger_table.keys():
                        finger_table[str(successor_id)] = self.node_id_dict[str(successor_id)]

                pred_id = self.predecessor(keys_list, id)
                pred_port = self.node_id_dict[str(pred_id)]
                return finger_table, (pred_id, pred_port)
            else:
                return (False, 'No nodes to communicate to')
        except Exception as e:
            # if any exception occured, send it to the node
            print(str(e))
            return (False, str(e))

    def run(self):
        self.registry.serve_forever()


