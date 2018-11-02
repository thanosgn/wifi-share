<p align="center">
  <img src="https://github.com/thanosgn/wifi-share/blob/master/logos/LOGOTYPE_H.svg" height="50%" width="50%">
</p>

Instantly share your WIFI connection using a QR code.
Scan it with your phone and connect automatically.

## Installation (using make)
```
git clone https://github.com/thanosgn/wifi-share.git
cd wifi-share
make install
```
You can uninstall at any time using `make uninstall`.
If you don't have `make` you can always use `pip install -r requirements.txt` to install the necessary requirements.

## Usage (default)
```
wifi-share
```
## Example
<p align="center">
  <img src="https://thanosgn.github.io/assets/wifi-share-example.png">
</p>

## Options
All the below arguments are optional.
The default behavior is to generate a QR code on the terminal for the network you are currently connected.
However, there are many options available if you want something besides the default scenario.
```
usage: wifi-share [-h] [-v] [-i [IMAGE]] [-s SSID] [-p PASSWORD] [-l]

Wi-Fi Share

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Enable verbose output.
  -i [IMAGE], --image [IMAGE]
                        Specify a filename for the generated QR code image.
                        (.png or .svg). Default: [WIFINAME].svg. If -i/--image
                        argument is not provided the QR code will be displayed
                        on the console.
  -s SSID, --ssid SSID  Specify the SSID you want the password of. Default:
                        the SSID of the network you are currently connected.
  -p PASSWORD, --password PASSWORD
                        Specify a desired password to be used instead of the
                        stored one.
  -l, --list            Display a list of stored Wi-Fi networks to choose
                        from.
```
