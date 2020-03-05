import pickle
import socket
from _thread import *

from Player import Player
from util import get_spawn_location


class Server:
    def __init__(self):
        self.server = "192.168.0.108"
        self.port = 5555
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.s.bind((self.server, self.port))
        except socket.error as e:
            str(e)
        self.s.listen(2)  # listen from maximum 2 clients
        print("waiting for connection")
        pos = get_spawn_location()
        self.players = [Player(pos[0][0], pos[0][1], 1), Player(pos[1][0], pos[1][1], 2)]  # setting up the x,y
        # co-ordinates of the players
        self.current_player = 0
        self.run()

    def threaded_client(self, conn, current_player):
        conn.send(pickle.dumps(self.players[current_player]))  # send initial positions to client
        while True:
            try:
                data = pickle.loads(conn.recv(2048))  # receive data from client
                self.players[current_player] = data  # replace data
                if not data:
                    print("disconnected")  # if no data is received, then disconnect and close the port
                    break
                else:  # if data is received, then do what ever you want with it
                    if current_player == 1:
                        reply = self.players[0]
                    else:
                        reply = self.players[1]
                    # print("received from client: ", data)
                    # print("sending to client: ", reply)
                conn.sendall(pickle.dumps(reply))  # send data to clients connected
            except socket.error as e:
                print("connection couldn't be established: ", e)
                break
        print("lost connection")
        conn.close()

    def run(self):
        while True:
            conn, address = self.s.accept()  # wait for a connection to establish, and accept it
            print("connected to: ", address)
            start_new_thread(self.threaded_client, (conn, self.current_player))
            # send current player to Game. If current player = 0 show initial screen. If current player
            self.players[self.current_player].is_connected = True
            self.current_player += 1


server = Server()
