import threading
import subprocess
import json
import zmq


def worker_routine(worker_url: str, context: zmq.Context = None):
    """Worker routine"""
    context = context or zmq.Context.instance()

    # Socket to talk to dispatcher
    socket = context.socket(zmq.REP)
    socket.connect(worker_url)

    while True:
        #  Wait for next request from client
        json_file = socket.recv_json()
        json_request = json.loads(json_file)
        print('Processing...')
        print(json_request)
        print()

        command_type = json_request['command_type']
        # Do things according to the type of request and prepare the reply
        match command_type:
            case "os":
                given_os_command = json_request['command_name'] + \
                    " " + ' '.join(json_request['parameters'])
                command_name = json_request['command_name']
                parameters = json_request['parameters']
                parameters.reverse()

                command_output = subprocess.check_output(
                    [command_name] + parameters).decode().strip()

                results = {
                    "given_os_command": given_os_command,
                    "result": command_output,
                }

                reply_json = json.dumps(results)

            case "compute":
                expression = json_request['expression']

                expression_result = str(eval(expression))

                results = {
                    "given_math_expression": expression,
                    "result": expression_result,
                }

                reply_json = json.dumps(results)

        # Send reply back to client
        socket.send_json(reply_json)
        print(reply_json)
        print('Response send.\n')


def main():
    """Server routine"""

    url_worker = "inproc://workers"
    url_client = "tcp://*:5555"

    # Prepare our context and sockets
    context = zmq.Context.instance()

    # Socket to talk to clients
    clients = context.socket(zmq.ROUTER)
    clients.bind(url_client)

    # Socket to talk to workers
    workers = context.socket(zmq.DEALER)
    workers.bind(url_worker)

    # Launch pool of worker threads
    for i in range(5):
        thread = threading.Thread(target=worker_routine, args=(url_worker,))
        thread.daemon = True
        thread.start()

    zmq.proxy(clients, workers)

    # We never get here but clean up anyhow
    clients.close()
    workers.close()
    context.term()


if __name__ == "__main__":
    main()
