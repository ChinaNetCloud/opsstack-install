NAME=nc-configure
VERSION=$(BUILD_NAME)
SRC_DIR=$(shell pwd)
PREFIX=/var/lib/netcloud/nc-configure
ARCHITECTURE=all
BEFORE_INSTALL=--before-install $(SRC_DIR)/before_install.sh
AFTER_INSTALL=--after-install $(SRC_DIR)/after_install.sh
AFTER_REMOVE=--after-remove $(SRC_DIR)/after_remove.sh
AGGREGATE_PATH=/repo-aggregate

.PHONY: package
package:
	msgfmt -o src/locale/en_US/LC_MESSAGES/nc-configure.mo src/locale/en_US/LC_MESSAGES/nc-configure.po
	msgfmt -o src/locale/zh_CN/LC_MESSAGES/nc-configure.mo src/locale/zh_CN/LC_MESSAGES/nc-configure.po
	fpm -C $(SRC_DIR)/src/ \
		-s dir -t rpm \
		-n $(NAME) \
		-v $(VERSION) \
		--prefix $(PREFIX) \
		-a $(ARCHITECTURE) \
		$(AFTER_INSTALL) \
		$(AFTER_REMOVE) \
		--template-scripts \
		--deb-no-default-config-files \
		--force

deploy:
	mv $(SRC_DIR)/*.rpm $(AGGREGATE_PATH)/

clean:
	rm -rf $(SRC_DIR)/*.rpm $(SRC_DIR)/*.deb