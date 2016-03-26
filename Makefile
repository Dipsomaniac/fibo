PROJECT 	?= fibo
VIRTUAL_ENV 	?= env
BUILD_TAG 	?= $(shell cat $(CURDIR)/.version)

all: $(VIRTUAL_ENV)

.PHONY: help
# target: help - Display callable targets
help:
	@egrep "^# target:" [Mm]akefile

.PHONY: clean
# target: clean - Display callable targets
clean:
	@rm -f *.deb *.tar
	@rm -rf build/ dist/ docs/_build *.egg-info
	@find $(CURDIR) -name "*.py[co]" -delete
	@find $(CURDIR) -name "*.orig" -delete
	@find $(CURDIR)/$(MODULE) -name "*.c" -delete
	@find $(CURDIR)/$(MODULE) -name "*.so" -delete
	@find $(CURDIR)/$(MODULE) -name "__pycache__" | xargs rm -rf

# ==============
#  Bump version
# ==============

.PHONY: release
RELEASE ?= minor
# target: release - Bump version
release:
	@$(VIRTUAL_ENV)/bin/pip install bumpversion
	@$(VIRTUAL_ENV)/bin/bumpversion $(RELEASE)
	@git checkout master
	@git merge develop
	@git checkout develop
	@git push origin develop master
	@git push --tags

.PHONY: minor
minor: release

.PHONY: patch
patch:
	make release RELEASE=patch

.PHONY: major
major:
	make release RELEASE=major

.PHONY: version
version:
	@echo Current version: $(shell cat $(CURDIR)/.version)

# ===============
#  Build package
# ===============

.PHONY: docker
docker: clean
	docker build -t $(PROJECT):$(BUILD_TAG) $(CURDIR)
	docker tag $(PROJECT):$(BUILD_TAG) $(PROJECT):latest

RUN = 
.PHONY: docker
docker-run: 
	@docker run --rm -it -p 5000:5000 -v $(CURDIR)/data:/app/data --name $(PROJECT) $(PROJECT) $(RUN)

docker-clean: 
	@docker rm -v $(shell docker ps -a -q -f status=exited) || true
	@docker rmi $(shell docker images -f dangling=true -q) || true

# =============
#  Development
# =============

$(VIRTUAL_ENV): $(CURDIR)/requirements.txt
	@[ -d $(VIRTUAL_ENV) ] || virtualenv --no-site-packages --python=python3 $(VIRTUAL_ENV)
	@$(VIRTUAL_ENV)/bin/pip install -r requirements.txt
	@touch $(VIRTUAL_ENV)

$(VIRTUAL_ENV)/bin/py.test: $(VIRTUAL_ENV) $(CURDIR)/requirements-tests.txt
	@$(VIRTUAL_ENV)/bin/pip install -r requirements-tests.txt
	@touch $(VIRTUAL_ENV)/bin/py.test

.PHONY: test
# target: test - Runs tests
test: $(VIRTUAL_ENV)/bin/py.test
	@$(VIRTUAL_ENV)/bin/py.test -xs tests.py

.PHONY: t
t: test


MANAGER=$(VIRTUAL_ENV)/bin/muffin $(PROJECT)

CMD = --help
manage: $(VIRTUAL_ENV)
	@$(MANAGER) $(CMD)

run: $(VIRTUAL_ENV)
	@$(MANAGER) run --bind=:5000 --reload --timeout=300

shell: $(VIRTUAL_ENV)
	@$(MANAGER) shell --ipython
