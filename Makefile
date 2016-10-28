NAME=opsstack-install
VERSION=$(BUILD_DISPLAY_NAME)
SRC_DIR=$(shell pwd)
PREFIX=/var/lib/opsstack/install
ARCHITECTURE=all
AFTER_INSTALL=--after-install $(SRC_DIR)/after_install.sh
BEFORE_REMOVE=--before-remove $(SRC_DIR)/before_remove.sh
REQUIRES=-d opsstack-common -d opsstack-configure
AGGREGATE_PATH=/repo-aggregate

.PHONY: package
package:
	find . -type f -name ".gitkeep" -exec rm -rf {} +
	msgfmt -o src/locale/en_US/LC_MESSAGES/translations.mo src/locale/en_US/LC_MESSAGES/translations.po
	msgfmt -o src/locale/zh_CN/LC_MESSAGES/translations.mo src/locale/zh_CN/LC_MESSAGES/translations.po
	fpm -C $(SRC_DIR)/src/ \
		-s dir -t rpm \
		-n $(NAME) \
		-v $(VERSION) \
		--prefix $(PREFIX) \
		-a $(ARCHITECTURE) \
		$(AFTER_INSTALL) \
		$(BEFORE_REMOVE) \
		--template-scripts \
		$(REQUIRES) \
		--force
	fpm -C $(SRC_DIR)/src/ \
		-s dir -t deb \
		-n $(NAME) \
		-v $(VERSION) \
		--prefix $(PREFIX) \
		-a $(ARCHITECTURE) \
		$(AFTER_INSTALL) \
		$(BEFORE_REMOVE) \
		--template-scripts \
		$(REQUIRES) \
		--iteration "1.ubuntu" \
		--force

deploy:
	mv $(SRC_DIR)/*.rpm $(AGGREGATE_PATH)/ || true
	mv $(SRC_DIR)/*.deb $(AGGREGATE_PATH)/ || true

clean:
	rm -rf $(SRC_DIR)/*.rpm $(SRC_DIR)/*.deb || true
