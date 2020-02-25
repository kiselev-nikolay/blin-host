import threading
import socket
import sys
import traceback
import paramiko

from blines import named_blin


HOST_KEY = paramiko.RSAKey(filename='keys/private.key')
PORT = 22


def handle_cmd(cmd, chan):
    """Branching statements to handle and prepare a response for a command"""
    response = ""
    command = cmd.split(' ')
    if command[0] == "rm":
        if "/" in command:
            response = "BLIN> " + named_blin("rmrf")
        else:
            response = ''
    elif command[0] == "cd":
        response = ""
    elif command[0] == "ls":
        response = "Pipfile\r\nblines.py\r\nkeys\r\ntest.py\r\nPipfile.lock\r\ncountdown.html\r\nmain.py\r\ntodo.md\r\n__pycache__\r\nindex.html\r\nssh.py"
    elif command[0] == "visudo" or "/etc/sudoers" in command:
        response = "BLIN> " + named_blin("visudo")
    elif command[0] == "sudo":
        response = "BLIN> " + named_blin("sudo")
    elif command[0] == "uname":
        if "-a" in command:
            response = "Linux centos-s-1vcpu-1gb-fra1-01 4.18.0-147.5.1.el8_1.x86_64 #1 SMP Wed Feb 19 02:01:39 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux"
            response += "\r\n"
            response += "BLIN> " + named_blin("uname")
        else:
            response = "Linux"
    elif command[0] == "systemctl":
        response = "BLIN> " + named_blin("powermanager")
    elif command[0] == "reboot":
        response = "BLIN> " + named_blin("powermanager")
    elif command[0] == "shutdown":
        response = "BLIN> " + named_blin("powermanager")
    else:
        response = "sh: command not found: " + command[0]
    if response:
        chan.send(response + "\r\n")


class FakeSshServer(paramiko.ServerInterface):
    """Settings for paramiko server interface"""
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        # Accept all passwords as valid by default
        if username == "root" and len(password) > 4:
            return paramiko.AUTH_SUCCESSFUL
        else:
            return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return 'password'

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True


def handle_connection(client, addr):
    """Handle a new ssh connection"""
    print("\n\nConnection from: " + addr[0] + "\n")
    print('Got a connection!')
    try:
        transport = paramiko.Transport(client)
        transport.add_server_key(HOST_KEY)
        # Change banner to appear legit on nmap (or other network) scans
        transport.local_version = "SSH-2.0-OpenSSH_7.6p1 Ubuntu-4ubuntu0.3"
        server = FakeSshServer()
        try:
            transport.start_server(server=server)
        except paramiko.SSHException:
            print('*** SSH negotiation failed.')
            raise Exception("SSH negotiation failed")
        # wait for auth
        chan = transport.accept(20)
        if chan is None:
            print('*** No channel.')
            raise Exception("No channel")

        server.event.wait(10)
        if not server.event.is_set():
            print('*** Client never asked for a shell.')
            raise Exception("No shell request")

        try:
            # chan.send("\r\n\r\n")
            run = True
            while run:
                chan.send("[root@blin.host ~]$ ")
                command = ""
                while not command.endswith("\r"):
                    transport = chan.recv(1024)
                    if transport == b'\x04':
                        run = False
                        chan.close()
                        break
                    elif transport == b'\x7f':
                        if command:
                            command = command[:-1]
                            chan.send(b"\b \b")
                    elif transport == b'\t':
                        pass
                    elif transport == b'\x1b[A':
                        for _ in command:
                            chan.send(b"\b \b")
                        command = ""
                    else:
                        # Echo input to psuedo-simulate a basic terminal
                        chan.send(transport)
                        command += transport.decode("utf-8")

                chan.send("\r\n")
                command = command.rstrip()
                if "exit" in command:
                    run = False
                else:
                    handle_cmd(command, chan)

        except Exception as err:
            print('!!! Exception: {}: {}'.format(err.__class__, err))
            traceback.print_exc()
            try:
                transport.close()
            except Exception:
                pass

        chan.close()

    except Exception as err:
        print('!!! Exception: {}: {}'.format(err.__class__, err))
        traceback.print_exc()
        try:
            transport.close()
        except Exception:
            pass


def start_server():
    """Init and run the ssh server"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', PORT))
    except Exception as err:
        print('*** Bind failed: {}'.format(err))
        traceback.print_exc()
        sys.exit(1)

    threads = []
    while True:
        try:
            sock.listen(100)
            print('Listening for connection ...')
            client, addr = sock.accept()
        except Exception as err:
            print('*** Listen/accept failed: {}'.format(err))
            traceback.print_exc()
        new_thread = threading.Thread(target=handle_connection, args=(client, addr))
        new_thread.start()
        threads.append(new_thread)

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    start_server()
