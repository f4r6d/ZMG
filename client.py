import sys
import zmq

# Checking user input to see if the filename has been entered
try:
    file_name = sys.argv[1]
except Exception:
    print("Please enter the file name in the command line; like this: python3 client.py request.json")

# opening json file
try:
    with open(file_name) as json_file:
        json_request = json_file.read()
except Exception:
    print('Can\'t open file or error in json file')


context = zmq.Context()

#  Socket to talk to server
print("Connecting server…")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

#  Send json request.
socket.send_json(json_request)

#  Get the reply.
message = socket.recv_json()
print(message)
