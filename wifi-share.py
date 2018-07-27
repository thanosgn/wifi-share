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
    if rc != 0:
        log(out)
        raise ProcessError()
    return out.decode("utf-8")

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
        print(bad('Error getting wifi name'))
        sys.exit(1)

    try:
        wifi_password = execute([['sudo', 'cat', os.path.join('/etc/NetworkManager/system-connections', wifi_name)],
                                ['grep', 'psk='],
                                ['awk', '-F', '=', '{print $2}']],
                                stdout=PIPE, stdin=PIPE, stderr=STDOUT).rstrip()
    except ProcessError as e:
        print(bad('Error getting wifi password'))
        sys.exit(1)

    img = pyqrcode.create('WIFI:T:WPA;S:' + escape(wifi_name) + ';P:' + escape(wifi_password) + ';;')
    print(img.terminal())

if __name__ == '__main__':
    main()
