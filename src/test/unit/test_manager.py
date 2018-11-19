from ecr.core import manager
import os
import shutil


class TestManager:
    @classmethod
    def setup_class(cls):
        pat = os.path.dirname(__file__)
        while not "src" in os.listdir(pat):
            pat = os.path.dirname(pat)
        pat = os.path.join(pat, "temp")
        if not os.path.isdir(pat):
            os.mkdir(pat)
        assert os.path.isdir(pat)
        cls.path = pat
        cls.mpath = os.path.join(cls.path, "testM")
        if os.path.isdir(cls.mpath):
            shutil.rmtree(cls.mpath)
        os.mkdir(cls.mpath)
        assert os.path.isdir(cls.mpath)
    
    @classmethod
    def teardown_class(cls):
        shutil.rmtree(cls.mpath)

    def test_init(self):
        manager.initialize(self.mpath)
        epath = manager.getMainPath(self.mpath)
        assert manager.hasInitialized(self.mpath)
        assert os.path.isdir(epath)
        assert os.path.isdir(manager.getTemplatePath(self.mpath))
        assert os.path.isfile(manager.getExecutorPath(self.mpath))
        assert os.path.isfile(manager.getConfigPath(self.mpath))
        assert os.path.isfile(manager.getFileInputPath(self.mpath))
        assert os.path.isfile(manager.getFileOutputPath(self.mpath))

    def test_load(self):
        if not manager.hasInitialized(self.mpath):
            self.test_init()
        self.man = manager.load(self.mpath)
        assert self.man.workingDirectory == self.mpath
        assert self.man.state == manager.WorkManagerState.Loaded

    def test_newcode(self):
        if not manager.hasInitialized(self.mpath):
            self.test_init()
        self.man = manager.load(self.mpath)
        self.man.newCode("1.cpp")
        assert os.path.isfile(os.path.join(self.mpath, "1.cpp"))
        self.man.newCode("2.c")
        assert os.path.isfile(os.path.join(self.mpath, "2.c"))
        self.man.newCode("1.cpp")
        assert os.path.isfile(os.path.join(self.mpath, "1.cpp"))
        self.man.newCode("3.txt")
        assert os.path.isfile(os.path.join(self.mpath, "3.txt"))
        
    
    def test_execute(self):
        if not manager.hasInitialized(self.mpath):
            self.test_init()
        self.man = manager.load(self.mpath)
        _file = "1.py"
        fpath = os.path.join(self.mpath, _file)
        self.man.newCode(_file)
        assert os.path.isfile(fpath)
        self.man.execute(file=_file)
        self.man.currentFile = _file
        self.man.defaultTimeLimit = 0.5
        self.man.execute()
        self.man.execute(io="ss")
        self.man.execute(io="ff")
        self.man.execute(io="fs")
        self.man.execute(io="sf")
        with open(fpath, "w") as f:
            f.write("while True: pass")
        self.man.execute()
    
    def test_clean(self):
        if not manager.hasInitialized(self.mpath):
            self.test_init()
        self.man = manager.load(self.mpath)
        self.man.newCode("1.cpp")
        self.man.execute(file="1.cpp")
        self.man.clean()

    def test_clear(self):
        assert manager.hasInitialized(self.mpath)
        manager.clear(self.mpath)
        assert not manager.hasInitialized(self.mpath)
