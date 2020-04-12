ROOT_DIR = $(CURDIR)
BUILD_DIR = $(ROOT_DIR)/build
DIST_DIR = $(ROOT_DIR)/dist
SRC_DIR = $(ROOT_DIR)/liqueur
PKGINFO_DIR = $(ROOT_DIR)/liqueur.egg-info
CHANGELOG_FILE = $(ROOT_DIR)/CHANGELOG.md
VERSION_FILE = $(ROOT_DIR)/.version
PACKAGE_FILE = $(ROOT_DIR)/.package
TEST_FILE = $(ROOT_DIR)/.test


$(VERSION_FILE):
	@cat $(SRC_DIR)/__init__.py | grep "__version__" | \
		sed 's/"//g' | awk -F " = " '{print $$2}' > $(VERSION_FILE)

# Print the current version
version: $(VERSION_FILE)
	@echo `cat $(VERSION_FILE)`

# Produce the files which prepare to upload/release
gen_package: $(VERSION_FILE) $(VERSION_FILE)
	@py setup.py sdist
	@py setup.py bdist_wheel

$(PACKAGE_FILE): gen_package
	@touch $(PACKAGE_FILE)

package: $(VERSION_FILE) $(PACKAGE_FILE)

upload_testpypi: $(PACKAGE_FILE)
	@twine upload --repository testpypi \
		$(DIST_DIR)/liqueur-`cat $(VERSION_FILE)`-py3-none-any.whl \
		$(DIST_DIR)/liqueur-`cat $(VERSION_FILE)`.tar.gz


$(TEST_FILE): upload_testpypi
	@pip install -i https://test.pypi.org/simple/ liqueur
	@touch $(TEST_FILE)

#
test_publish: $(TEST_FILE)

# Offical release
publish: $(VERSION_FILE) $(PACKAGE_FILE) test_publish
	@twine upload \
		$(DIST_DIR)/liqueur-`cat $(VERSION_FILE)`-py3-none-any.whl \
		$(DIST_DIR)/liqueur-`cat $(VERSION_FILE)`.tar.gz

# Clean all files which generate by makefile
clean:
	@rm -rf $(BUILD_DIR) $(DIST_DIR) $(PKGINFO_DIR)
	@rm -f $(VERSION_FILE) $(PACKAGE_FILE) $(TEST_FILE)

# Change log generation
changelog: $(VERSION_FILE)
	@git checkout $(CHANGELOG_FILE)
	@cp $(CHANGELOG_FILE) $(CHANGELOG_FILE).org
	@echo -e '# Changelog\n' > $(CHANGELOG_FILE)
	@echo -e '## '`cat $(VERSION_FILE)`'\n' >> $(CHANGELOG_FILE)
	@echo -e '### Feature {#feat_'`cat $(VERSION_FILE) | sed 's/\./_/g'`}'\n' >> \
		$(CHANGELOG_FILE)
	@git log origin/master..HEAD --no-merges --pretty=format:'* %s' | grep 'feat' >> \
		$(CHANGELOG_FILE)
	@echo -e '\n### Bug fixes {#fix_'`cat $(VERSION_FILE) | sed 's/\./_/g'`}'\n' >> \
		$(CHANGELOG_FILE)
	@git log origin/master..HEAD --no-merges --pretty=format:'* %s' | grep 'fix' >> \
		$(CHANGELOG_FILE)
	@sed -e '1d' $(CHANGELOG_FILE).org >> $(CHANGELOG_FILE)
	@rm $(CHANGELOG_FILE).org

# Install this library
install:
	@py setup.py install

.PHONY: version test_publish publish clean changelog install
