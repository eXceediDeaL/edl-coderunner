.PHONY : build clean prepare upload uptest

PY = python
SHELL = powershell.exe
override RARG += --wdir ../temp/debug

build : 
	$(PY) setup.py sdist bdist_wheel

install : 
	$(PY) setup.py install

uninstall : 
	$(PY) -m pip uninstall edl-cr -y

run : 
	-cd temp ; mkdir debug
	cd src ; $(PY) -m ecr $(RARG)

test : 
	pytest --html=./docs/dev/reports/test/index.html --self-contained-html

cover : 
	cd src ; coverage run --source=ecr -m test
	cd src ; coverage report
	cd src ; coverage html -d ../docs/dev/reports/coverage/

upload : 
	twine upload ./dist/*

# When use this, remove classifiers in setup.py and rebuild
uptest : 
	twine upload --repository-url https://test.pypi.org/legacy/ ./dist/*

prepare : 
	$(PY) -m pip install --user --upgrade pytest
	$(PY) -m pip install --user --upgrade coverage
	$(PY) -m pip install --user --upgrade setuptools wheel
	$(PY) -m pip install --user --upgrade twine
	$(PY) -m pip install --user --upgrade pytest-html


clean : 
	-rm -r ./.pytest_cache/*
	-rm -r ./temp/*
	-rm -r ./dist/*
	-rm -r ./build/*
	-rm -r ./src/*.egg-info
	-rm ./src/*.coverage