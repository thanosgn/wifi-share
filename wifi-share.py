from __future__ import print_function
import argparse
import subprocess
import sys
import os
from subprocess import Popen, PIPE, STDOUT
from collections import OrderedDict
import pyqrcode
import png
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
    parser.add_argument('-i', '--image', help = 'Specify a filename for the generated QR code image. (.png or .svg).\
                                                  Default [WIFINAME].svg.\
                                                  If argument is not provided the QR code will be displayed\
                                                  on the console.', nargs='?', default = 'no-image')
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

    wifi_password = ''
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

    if args.image == 'no-image': # If user did not enter the -i/--image argument
        print(img.terminal())
    else:
        if args.image == None:  # If user selected the -i/--image argument, but did not give any filename
            filename = wifi_name + '.svg'
        else: # If user specified a filename with the -i/--image argument
            if args.image.endswith('.svg'):
                filename = args.image
                img.svg(filename, scale = 4, background = 'white')
            elif args.image.endswith('.png'):
                filename = args.image
                img.png(filename, scale = 4)
            else:
                filename = args.image + '.svg'
                img.svg(filename, scale = 4, background = 'white')
        print(good('Qr code drawn in '+filename))


if __name__ == '__main__':
    main()
