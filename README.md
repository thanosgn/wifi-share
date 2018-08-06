# wifi-share

<p align="center">
  <img src="https://thanosgn.github.io/assets/qr-wifi.svg" height="30%" width="30%">
</p>

Instantly share your WIFI connection using a QR code.
Scan it with your phone and connect automatically.

## Instalation
```
git clone https://github.com/thanosgn/wifi-share.git
cd wifi-share
pip install -r requirements.txt
```

## Usage (default)
```
python wifi-share.py
```
## Options
All the below arguments are optional.
The default behavior is to generate a QR code on the terminal for the network you are currently connected.
However, there are many options available if you want something besides the default scenario.
```
usage: wifi-share.py [-h] [-v] [-i [IMAGE]] [-s SSID] [-l]

Wi-Fi Share

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Enable verbose output.
  -i [IMAGE], --image [IMAGE]
                        Specify a filename for the generated QR code image.
                        (.png or .svg). Default: [WIFINAME].svg. If argument
                        is not provided the QR code will be displayed on the
                        console.
  -s SSID, --ssid SSID  Specify the SSID you want the password of. Default:
                        the SSID of the network you are currently connected.
  -l, --list            Display a list of stored Wi-Fi networks to choose
                        from.
                        ```

