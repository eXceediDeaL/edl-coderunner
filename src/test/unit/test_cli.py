from ecr import __main__ as main
from ecr.core import manager
import os
import shutil
from argparse import Namespace


class TestCLI:
    @classmethod
    def setup_class(cls):
        cls.oldCwd = os.getcwd()
        pat = os.path.dirname(__file__)
        while not "src" in os.listdir(pat):
            pat = os.path.dirname(pat)
        pat = os.path.join(pat, "temp")
        if not os.path.isdir(pat):
            os.mkdir(pat)
        assert os.path.isdir(pat)
        cls.path = pat
        cls.mpath = os.path.join(cls.path, "testC")
        if os.path.isdir(cls.mpath):
            shutil.rmtree(cls.mpath)
        os.mkdir(cls.mpath)
        assert os.path.isdir(cls.mpath)
        os.chdir(cls.mpath)
        main.mainInit()
        main.printHead()
        assert main.executeCommand("init") == 0
        assert main.man != None and main.man.state == manager.WorkManagerState.Loaded

    @classmethod
    def teardown_class(cls):
        try:
            shutil.rmtree(cls.mpath)
        except:
            pass
        os.chdir(cls.oldCwd)

    def test_basiccmd(self):
        assert main.executeCommand("pwd") == 0
        assert main.executeCommand("cd .") == 0
        # assert main.executeCommand("--help") == 0
        assert main.executeCommand("init -h") == 0

    def test_newcode(self):
        assert main.executeCommand("new 1.cpp") == 0
        assert os.path.isfile(os.path.join(self.mpath, "1.cpp"))

    def test_execute(self):
        _file = "1.py"
        fpath = os.path.join(self.mpath, _file)
        assert main.executeCommand(f"new {_file}") == 0
        assert os.path.isfile(fpath)
        main.man.currentFile = None
        main.executeCommand(f"run")
        main.executeCommand(f"run {_file}")
        main.executeCommand(f"now {_file}")
        assert main.man.currentFile == _file
        main.man.defaultTimeLimit = 0.5
        main.executeCommand(f"run {_file} -io ff")
        with open(fpath, "w") as f:
            f.write("while True: pass")
        main.executeCommand(f"run {_file} -io ff")

    def test_clean(self):
        main.executeCommand("new 1.cpp")
        main.executeCommand("run 1.cpp")
        assert main.executeCommand("clean") == 0

    def test_clear(self):
        pass

    def test_syscall(self):
        assert main.executeCommand("ls") == 0
        assert main.executeCommand(">ls") == 0
        # assert main.executeCommand("cls") == 0
