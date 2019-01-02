DESTINATION_DIR := /usr/local/bin
CURRENT_DIR := $(realpath ./)
LINK_NAME := wifi-share
PYTHON_INSTALLED := $(shell command -v python 2> /dev/null)
PIP_INSTALLED := $(shell command -v pip 2> /dev/null)
ifdef PYTHON_INSTALLED
	PYV := $(shell python -c "import sys;t='{v[0]}'.format(v=list(sys.version_info[:2]));sys.stdout.write(t)")
	PYTHON := python${PYV}
	PIP := pip${PYV}
endif
GOOD := \033[1;32m[+]\033[1;m

install:
ifndef PYTHON_INSTALLED
	@echo "python not installed, but can be installed with:"
	@echo
	@echo "\tsudo apt install python"
	@echo
	@echo "or using your favorite package manager."
	@echo
	@exit 1
endif
ifndef PIP_INSTALLED
	@echo "pip not installed, but can be installed with:"
	@echo
	@echo "\tsudo apt install python-pip"
	@echo
	@echo "or using your favorite package manager."
	@echo
	@exit 1
endif
	@sudo ${PIP} install -r requirements.txt
	@sudo ln -s -f ${CURRENT_DIR}/wifi-share.py $(DESTINATION_DIR)/${LINK_NAME}
	@echo
	@echo "${GOOD} Wi-Fi Share is setup! Enter '${LINK_NAME} [options]' in a terminal to use it"

uninstall:
	@sudo ${PIP} uninstall -r requirements.txt
	@sudo rm -f $(DESTINATION_DIR)/${LINK_NAME}
	@echo
	@echo "${GOOD} Wi-Fi Share has been removed"
