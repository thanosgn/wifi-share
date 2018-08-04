from __future__ import print_function
import argparse
import subprocess
import sys
import os
from subprocess import Popen, PIPE, STDOUT
from collections import OrderedDict
import pyqrcode
from huepy import *

verbose = True

def log(message):
    if verbose:
        print(message, file=sys.stderr)

class ProcessError(Exception):
    def __init__(self, message=''):
        self.message = message
    def __str__(self):
        return self.message

# Execute provided command(s).
# In case of multiple commands, pipe them.
def execute(commands, stdout, stdin, stderr):
    input = stdin
    if not any(isinstance(el, list) for el in commands): # if we have only one command
        commands = [commands]
    for command in commands:
        log(run('Running: ' + ' '.join(command)))
        process = Popen(command, stdout = stdout, stdin = input, stderr = stderr)
        input = process.stdout
    out, err = process.communicate();
    rc = process.returncode
    if out != None:
        out = out.decode("utf-8").rstrip()
    if rc != 0:
        if err != None:
            err = err.decode("utf-8").rstrip()
            raise ProcessError(err)
        else:
            raise ProcessError(out)
    return out

def escape(input_string):
    translations = OrderedDict([('\\' , '\\\\'),
    (':' , '\\:'),
    (';' , '\\;'),
    (',' , '\\,'),
    ('"' , '\\"')])
    escaped = input_string
    for k,v in translations.items():
        escaped = escaped.replace(k, v)
    return escaped

def main():
    global verbose
    parser = argparse.ArgumentParser(description='Wi-Fi Share')
    parser.add_argument('-v', '--verbose', help = 'Enable verbose output.', action = 'store_true')
    args = parser.parse_args()
    verbose = args.verbose

    try:
        wifi_name = execute(['iwgetid', '-r'], stdout=PIPE, stdin=PIPE, stderr=STDOUT).rstrip()
    except ProcessError as e:
        log(bad(e))
        print(bad('Error getting Wi-Fi name'))
        print(que('Are you sure you are connected to a WiFi network?'))
        sys.exit(1)

    log(good('You are connected to ' + green(wifi_name) + ' Wi-Fi'))

    try:
        with open( os.path.join('/etc/NetworkManager/system-connections', wifi_name), 'r') as network_file:
            for line in network_file:
                if 'psk=' in line:
                    wifi_password = line.split('=')[1].rstrip('\r\n')
    except IOError as e:
        log(bad(e))
        print(bad('Error getting Wi-Fi password'))
        print(que('Are you root?'))
        sys.exit(1)

    if wifi_password != '':
        log(good('The  password is ' + green(wifi_password)))
        img = pyqrcode.create('WIFI:T:WPA;S:' + escape(wifi_name) + ';P:' + escape(wifi_password) + ';;')
    else:
        log(info('No password needed for this network.'))
        img = pyqrcode.create('WIFI:S:' + escape(wifi_name) + ';;;')

    print(img.terminal())

if __name__ == '__main__':
    main()
