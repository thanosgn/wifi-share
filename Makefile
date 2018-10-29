DESTINATION_DIR := /usr/local/bin
CURRENT_DIR := $(realpath ./)
LINK_NAME := wifi-share

install:
	@sudo ln -s -f ${CURRENT_DIR}/wifi-share.py $(DESTINATION_DIR)/${LINK_NAME}
	@echo "Wi-Fi Share is setup! Enter '${LINK_NAME} [options]' in a terminal to use it"

uninstall:
	@sudo rm -f $(DESTINATION_DIR)/${LINK_NAME}
	@echo "Wi-Fi Share has been removed"
