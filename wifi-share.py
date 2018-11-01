#!/usr/bin/env python
from __future__ import print_function
import argparse
import subprocess
import sys
import os
from subprocess import Popen, PIPE, STDOUT
from collections import OrderedDict
# import pyqrcode
import qrcode
import qrcode.image.svg
import PIL
from PyInquirer import prompt
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
                                                  Default: [WIFINAME].svg.\
                                                  If argument is not provided the QR code will be displayed\
                                                  on the console.', nargs='?', default = 'no-image')
    parser.add_argument('-s', '--ssid', help = 'Specify the SSID you want the password of.\
                                                Default: the SSID of the network you are currently connected.')
    parser.add_argument('-p', '--password', help = 'Specify a desired password to be used instead of the sotred one.')
    parser.add_argument('-l', '--list', help = 'Display a list of stored Wi-Fi networks to choose from.', action = 'store_true')
    args = parser.parse_args()
    verbose = args.verbose

    wifi_name = args.ssid
    if args.list:
        available_networks = sorted(os.listdir(u'/etc/NetworkManager/system-connections'))
        questions = [
            {
                'type': 'list',
                'name': 'network',
                'message': 'SSID:',
                'choices' : available_networks
            }
        ]
        answer = prompt(questions)
        wifi_name = answer['network']
        log(run('Retrieving the password for ' + green(wifi_name) + ' Wi-Fi'))
    elif args.ssid == None:
        try:
            wifi_name = execute(['iwgetid', '-r'], stdout=PIPE, stdin=PIPE, stderr=STDOUT).rstrip()
        except ProcessError as e:
            log(bad(e))
            print(bad('Error getting Wi-Fi name'))
            print(que('Are you sure you are connected to a Wi-Fi network?'))
            sys.exit(1)
        log(good('You are connected to ' + green(wifi_name) + ' Wi-Fi'))
    else:
        log(run('Retrieving the password for ' + green(wifi_name) + ' Wi-Fi'))

    wifi_password = ''
    if args.password != None:
        wifi_password = args.password
    else:
        try:
            with open( os.path.join('/etc/NetworkManager/system-connections', wifi_name), 'r') as network_file:
                for line in network_file:
                    if 'psk=' in line:
                        wifi_password = line.split('=')[1].rstrip('\r\n')
        except IOError as e:
            log(bad(e))
            print(bad('Error getting Wi-Fi password'))
            if e.errno == 13:
                print(que('Are you root?'))
            elif e.errno == 2 and args.ssid != None:
                print(que('Are you sure SSID is correct?'))
            sys.exit(1)

    if wifi_password != '':
        log(good('The password is ' + green(wifi_password)))
        data = 'WIFI:T:WPA;S:' + escape(wifi_name) + ';P:' + escape(wifi_password) + ';;'
    else:
        log(info('No password needed for this network.'))
        data = 'WIFI:S:' + escape(wifi_name) + ';;;'

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)

    if args.image == 'no-image': # If user did not enter the -i/--image argument
        qr.print_tty()
    else:
        img = qrcode.make(data)
        if args.image == None:  # If user selected the -i/--image argument, but did not give any filename
            img = qrcode.make(data, image_factory=qrcode.image.svg.SvgPathFillImage)
            filename = wifi_name + '.svg'
        else: # If user specified a filename with the -i/--image argument
            if args.image.endswith('.svg'):
                img = qrcode.make(data, image_factory=qrcode.image.svg.SvgPathFillImage)
                filename = args.image
            elif args.image.endswith('.png'):
                filename = args.image
                img = qr.make_image(fill_color="black", back_color="white")
            else:
                img = qrcode.make(data, image_factory=qrcode.image.svg.SvgPathFillImage)
                filename = args.image + '.svg'
        img.save(filename)
        print(good('Qr code drawn in '+filename))


if __name__ == '__main__':
    main()
