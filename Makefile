NAME=nc-configure
VERSION=1.0.0
SRC_DIR=$(shell pwd)/src/
PREFIX=/var/lib/netcloud/nc-configure
ARCHITECTURE=all
AFTER_INSTALL=
AFTER_REMOVE=

.PHONY: package
package:
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