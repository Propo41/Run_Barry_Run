import pickle
import socket


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "192.168.0.108"  # the ip of the machine where the server is situated
        self.port = 5555  # any free ports will work. 5555 is a common port in windows
        self.address = (self.server, self.port)
        self.initial_data = self.connect()

    # print("received from server: ", self.initial_data)

    # used only once during creation of this class
    # used to fetch initial values from the server
    def connect(self):
        try:
            self.client.connect(self.address)  # connect the client to the server using the address provided
            print("connected to server")
            # receive whatever msg is sent from server and de-serialize into byte strings
            return pickle.loads(self.client.recv(2048))
        except socket.error as e:
            print("connection couldn't be established from client side: ", e)

    # used more than once to send and receive data continuously
    # sends the given data as a parameter to the server and receives back whatever is sent from it
    def send_and_receive(self, data):
        try:
            # print("sending to server: ", data)
            self.client.send(pickle.dumps(data))  # send data given as a parameter to the server
            received = pickle.loads(self.client.recv(2048))  # receive whatever msg is sent from server and decode
            # print("received from server: ", received)
            return received
        except socket.error as e:
            print(e)

    def fetch_initial_data(self):
        return self.initial_data
