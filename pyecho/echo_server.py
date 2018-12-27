import select
import socket
import sys
from lib import click

try:
    import thread
except ImportError:
    import _thread as thread

def on_new_client(clientsocket,client_address):
    try:
        click.echo("Connection from {} established".format(client_address[0]))
        clientsocket.send('Send "quit" to close the connection\nClient: '.encode())
        while True:
            data = clientsocket.recv(1024)
            if data.decode().lower().rstrip() == 'quit':
                click.echo('Request to close connection received from {}, closing now'.format(client_address[0]))
                response="Received quit signal, goodbye!\n"
                clientsocket.send(response.encode())
                break
            elif data:
                click.echo("{}: {}".format(client_address[0], data.decode().rstrip() ))
                response="Server: {}\nClient: ".format(data.decode().rstrip())
                clientsocket.send(response.encode())
            else:
                click.echo("No data from {}, closing connection".format(client_address[0]))
                break   

    finally:
        # Clean up the connection
        clientsocket.close()


@click.command()
@click.option('--host', '-h', default='0.0.0.0', help="Host address to bind to")
@click.option('--port', '-p', multiple=True, help="Port to bind to. May be passed multiple times")
def setup(host, port):
    servers = []
    
    for p in port:
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        server_address = (host, int(p))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        click.echo('starting up on {} port {}'.format(*server_address))
        sock.bind(server_address)
        sock.listen(1)
        
        servers.append(sock)

    while True:
	# Wait for a connection
        click.echo('waiting for a connections')
        readable,_,_ = select.select(servers, [], [])
        ready_server = readable[0]
        while True:
            connection, client_address = sock.accept()
            thread.start_new_thread(on_new_client,(connection,client_address))

    sock.close()


if __name__ == '__main__':
    setup() 
