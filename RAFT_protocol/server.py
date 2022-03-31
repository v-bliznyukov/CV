import sys
import datetime
import numpy as np
import xmlrpc
import time
import xmlrpc.client
from threading import Thread
from xmlrpc.server import SimpleXMLRPCServer


class RaftServer():
    id = -1
    address = 0
    port = 0
    term_number = 0
    timout = 0
    state = "Follower"
    other_servers = []
    votedFor = None
    currentLeader = -1
    updateTimer = False
    votes = 0
    start = 0
    suspend = 0
    Election = False

    def __init__(self, id, address, port, other_servers):
        self.id = id
        self.address = address
        self.port = port
        self.timeout = np.random.randint(150, 300)
        self.other_servers = other_servers
        self.start = round(time.time() * 1000)
        self.setFollower(self.term_number)

    def isLeader(self):
        return self.state == 'Leader'

    def setTerm(self, term):
        self.term_number = term

    def setVotedFor(self, id):
        self.votedFor = id
        if id != None:
            print("Voted for node", id)

    def setFollower(self, term, vote = None):
        self.state = "Follower"
        self.setTerm(term)
        self.setVotedFor(vote)
        if vote == None:
            self.Election = False
        print("I am a follower. Term:", self.term_number)

    def setCandidate(self):
        self.state = "Candidate"
        self.setTerm(self.term_number + 1)
        print("I am a candidate. Term: ",self.term_number)

    def setLeader(self):
        self.state = "Leader"
        print("I am a leader. Term: ", self.term_number)

    def RequestVote(self, term, candidateId):
        if self.suspend == 0:
            if term < self.term_number:
                return self.term_number, False
            self.start = round(time.time() * 1000)
            self.Election = True
            if term > self.term_number:
                self.currentLeader = candidateId
                self.setFollower(term, candidateId)
            elif (self.votedFor == None):
                self.currentLeader = candidateId
                self.setVotedFor(candidateId)
            else:
                return self.term_number, False
            return self.term_number, True
        return -1, False


    def AppendEntries(self, term, leaderId):
        if self.suspend == 0:
            if term < self.term_number:
                return self.term_number, False
            self.Election = False
            self.start = round(time.time() * 1000)
            if term > self.term_number:
                self.currentLeader = leaderId
                self.setFollower(term)

            elif term == self.term_number:
                self.currentLeader = leaderId

            return self.term_number, True
        return 0, False


    def runLeader(self):
        time.sleep(0.05)
        for server in self.other_servers:
            try:
                with xmlrpc.client.ServerProxy("http://{}:{}/".format(server[1], server[2])) as follower:
                    term, success = follower.AppendEntries(self.term_number, self.id)
                    if term > self.term_number:
                        self.start = round(time.time() * 1000)
                        self.setFollower(term)
                        break
            except ConnectionRefusedError:
                continue

    def runCandidate(self):
        self.votes = 1
        self.setVotedFor(self.id)
        count = 1
        self.Election = True
        electionStart = round(time.time() * 1000)
        for server in other_servers:
            try:
                with xmlrpc.client.ServerProxy("http://{}:{}/".format(server[1], server[2])) as voter:
                    term, answer = voter.RequestVote(self.term_number, id)
                    if term != -1:
                       count += 1
                    if term > self.term_number:
                        self.setFollower(term)
                        self.timeout = np.random.randint(150, 300)
                        self.start = round(time.time() * 1000)
                        break
                    elif answer == True:
                        self.votes+=1
                        break
            except ConnectionRefusedError:
                continue

        if self.state != "Follower":
            print("Votes collected",self.votes, "/" , count)
            if self.votes >= (count + 1) / 2 and (
                    round(time.time() * 1000) - electionStart) <= self.timeout:
                self.setLeader()
            else:
                self.setFollower(self.term_number)
                self.timeout = np.random.randint(150, 300)
                self.start = round(time.time() * 1000)

    def runFollower(self):
        if ( round(time.time() * 1000) - self.start) > self.timeout:
            print("The leader is dead")
            self.setCandidate()

    def getLeader(self):
        if self.suspend == 0:
            print("Command from client: getleader")
            if self.Election:
                if self.votedFor != None:
                    if self.votedFor == self.id:
                        return self.id, "{}:{}".format(self.address, self.port)
                    else:
                        for server in self.other_servers:
                            if int(server[0]) == self.votedFor:
                                return self.votedFor, "{}:{}".format(server[1], server[2])
                else:
                    return "", ""

            elif self.state != "Leader":
                for server in self.other_servers:
                    if int(server[0]) == self.currentLeader:
                     return self.currentLeader, "{}:{}".format(server[1], server[2])
            else:
                return self.id, "{}:{}".format(self.address, self.port)
        else:
            return "", ""
    def Suspend(self, period):
        if self.suspend == 0:
            print("Command from client: suspend", period)
            print("Sleeping for {} seconds".format(period))
            self.suspend = period
        return True

    def run(self):
        if self.state == 'Follower':
            self.runFollower()

        elif self.state == 'Candidate':
            self.runCandidate()

        elif self.state == 'Leader':
            self.runLeader()


other_servers = []
id = int(sys.argv[1])
config = open("config.conf", "r")
for line in config:
    line = line.split()
    if int(line[0]) == id:
        address = line[1]
        port = int(line[2])
        print("Server is started at {}:{}".format(address, port))
    else:
        other_servers.append((line[0], line[1], line[2]))
config.close()

node = RaftServer(id, address, port, other_servers)

server = SimpleXMLRPCServer((address, port), allow_none=True, logRequests=False)
server.register_instance(node)
p = Thread(target=server.serve_forever, daemon=True)
p.start()

try:
    while True:
        if node.suspend != 0:
            time.sleep(node.suspend)
            node.suspend = 0
            node.start = round(time.time() * 1000)
        else:
            node.run()
except KeyboardInterrupt:
    print("Server exits")