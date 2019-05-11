#!/usr/bin/env python
from __future__ import print_function
import argparse
import subprocess
import sys
import os
from subprocess import Popen, PIPE, STDOUT
from collections import OrderedDict
import qrcode
import qrcode.image.svg
import PIL
from PyInquirer import prompt
from huepy import *
import platform

verbose = True

ascii_art='''
 __          ___        ______ _      _____ _
 \ \        / (_)      |  ____(_)    / ____| |
  \ \  /\  / / _ ______| |__   _    | (___ | |__   __ _ _ __ ___
   \ \/  \/ / | |______|  __| | |    \___ \| '_ \ / _` | '__/ _ \\
    \  /\  /  | |      | |    | |    ____) | | | | (_| | | |  __/
     \/  \/   |_|      |_|    |_|   |_____/|_| |_|\__,_|_|  \___|
'''

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

def fix_ownership(path): # Change the owner of the file to SUDO_UID
    uid = os.environ.get('SUDO_UID')
    gid = os.environ.get('SUDO_GID')
    if uid is not None:
        os.chown(path, int(uid), int(gid))

def create_QR_string(ssid = None, security = 'WPA', password = None):
    if ssid != None:
        if password != None:
            return 'WIFI:T:WPA;S:' + escape(ssid) + ';P:' + escape(password) + ';;'
        else:
             return 'WIFI:S:' + escape(ssid) + ';;;'
    return ''

def create_QR_object(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    return qr

def main():
    global verbose
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=ascii_art)
    parser.add_argument('-v', '--verbose', help = 'Enable verbose output.', action = 'store_true')
    parser.add_argument('-i', '--image', help = 'Specify a filename for the generated QR code image. (.png or .svg).\
                                                  Default: [WIFINAME].svg.\
                                                  If -i/--image argument is not provided the QR code will be displayed\
                                                  on the console.', nargs='?', default = 'no-image')
    parser.add_argument('-s', '--ssid', help = 'Specify the SSID you want the password of.\
                                                Default: the SSID of the network you are currently connected.')
    parser.add_argument('-p', '--password', help = 'Specify a desired password to be used instead of the stored one.')
    parser.add_argument('-l', '--list', help = 'Display a list of stored Wi-Fi networks (SSIDs) to choose from.', action = 'store_true')
    args = parser.parse_args()
    verbose = args.verbose
    wifi_name = args.ssid

    system = platform.system()

    if args.list:
        available_networks = []
        if system == 'Windows':
            try:
                output = execute(['netsh', 'wlan', 'show', 'profiles'], stdout=PIPE, stdin=PIPE, stderr=STDOUT).rstrip()
                for line in output.splitlines():
                    if line.startswith('    All User Profile'):
                       available_networks.append(line.split(':')[1].lstrip())
                if available_networks == []:
                    raise ProcessError
            except ProcessError as e:
                log(bad(e))
                print(bad('Error getting Wi-Fi connections'))
                sys.exit(1)
        elif system == 'Darwin':
            try:
                output = execute([['defaults', 'read', '/Library/Preferences/SystemConfiguration/com.apple.airport.preferences'],\
                ['grep', 'SSIDString']], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
                for line in output.splitlines():
                    if line.startswith('            SSIDString ='):
                        available_networks.append(line.split('=')[1].lstrip()[:-1].replace('"', ''))
                if available_networks == []:
                    raise ProcessError
            except ProcessError as e:
                log(bad(e))
                print(bad('Error getting Wi-Fi connections'))
                sys.exit(1)
        else:
            try:
                output = execute([['nmcli', 'connection', 'show', '--order', 'type:name'],\
                ['grep', '-w', 'wifi'],\
                ['awk', 'NR > 1 {print $1}']], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
                available_networks = output.splitlines()
                if available_networks == []:
                    raise ProcessError
            except ProcessError as e:
                log(bad(e))
                print(bad('Error getting Wi-Fi connections'))
                sys.exit(1)
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
            if system == 'Windows':
                output = execute(['netsh', 'wlan', 'show', 'interfaces'], stdout=PIPE, stdin=PIPE, stderr=STDOUT).rstrip()
                for line in output.splitlines():
                    if line.startswith('    SSID'):
                       wifi_name = line.split(':')[1].lstrip()
                if wifi_name == None:
                    raise ProcessError
            elif system == 'Darwin':
                output = execute(['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-I'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
                for line in output.splitlines():
                    if line.startswith('           SSID'):
                       wifi_name = line.split(':')[1].lstrip()
                if wifi_name == None:
                    raise ProcessError
            else:
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
            if system == 'Windows':
                output = execute(['netsh', 'wlan', 'show', 'profile', wifi_name, 'key=clear'], stdout=PIPE, stdin=PIPE, stderr=STDOUT).rstrip()
                for line in output.splitlines():
                    if line.startswith('    Key Content'):
                       wifi_password = line.split(':')[1].lstrip()
            elif system == 'Darwin':
                wifi_password = execute(['security', 'find-generic-password', '-wga', wifi_name], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
            else:
                wifi_password = execute([['nmcli', 'connection', 'show', 'id', wifi_name, '--show-secrets'],\
                ['grep', '802-11-wireless-security.psk:'],\
                ['awk', '{print $2}']], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
            if wifi_password == None:
                raise ProcessError
        except (ProcessError, IOError) as e:
            log(bad(e))
            print(bad('Error getting Wi-Fi password'))
            if e.__class__ == IOError:
                if e.errno == 13:
                    print(que('Are you root?'))
                elif e.errno == 2 and args.ssid != None:
                    print(que('Are you sure SSID is correct?'))
            sys.exit(1)

    if wifi_password != '':
        log(good('The password is ' + green(wifi_password)))
        data = create_QR_string(ssid = wifi_name, password = wifi_password)
    else:
        log(info('No password needed for this network.'))
        data = create_QR_string(ssid = wifi_name)

    qr = create_QR_object(data)

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
        if system == 'Linux':
            fix_ownership(filename)
        print(good('Qr code drawn in '+filename))


if __name__ == '__main__':
    main()
