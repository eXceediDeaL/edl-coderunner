.PHONY : build clean prepare upload uptest redoc install uninstall

PY = python
SHELL = powershell.exe
override RARG += --dir ../temp/debug

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
	cd src ; $(PY) -m test --html=./docs/dev/reports/test/index.html --self-contained-html
	# pytest --html=./docs/dev/reports/test/index.html --self-contained-html

cover : 
	cd src ; coverage run --source=ecr -m test quiet
	cd src ; coverage report
	cd src ; coverage html -d ../docs/dev/reports/coverage/

redoc : test cover

upload : build
	twine upload ./dist/*

# When use this, remove classifiers in setup.py and rebuild
uptest : build
	twine upload --repository-url https://test.pypi.org/legacy/ ./dist/*

prepare : 
	$(PY) -m pip install -r requirements.txt

clean : 
	-rm -r ./.pytest_cache/*
	-rm -r ./temp/*
	-rm -r ./dist/*
	-rm -r ./build/*
	-rm -r ./src/*.egg-info
	-rm ./src/*.coverage