DESTINATION_DIR := /usr/local/bin
CURRENT_DIR := $(realpath ./)
LINK_NAME := wifi-share
PYV := $(shell python -c "import sys;t='{v[0]}'.format(v=list(sys.version_info[:2]));sys.stdout.write(t)")
PYTHON := python${PYV}
PIP := pip${PYV}
GOOD := \033[1;32m[+]\033[1;m

install:
	@sudo ${PIP} install -r requirements.txt
	@sudo ln -s -f ${CURRENT_DIR}/wifi-share.py $(DESTINATION_DIR)/${LINK_NAME}
	@echo
	@echo "${GOOD} Wi-Fi Share is setup! Enter '${LINK_NAME} [options]' in a terminal to use it"

uninstall:
	@sudo ${PIP} uninstall -r requirements.txt
	@sudo rm -f $(DESTINATION_DIR)/${LINK_NAME}
	@echo 
	@echo "${GOOD} Wi-Fi Share has been removed"
