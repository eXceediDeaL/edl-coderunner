from ecr.core.manager import getConfigPath, getExecutorPath, getFileExt, getFileInputPath, getFileOutputPath, getMainPath, getTemplatePath
import os


class TestPath:
    @classmethod
    def setup_class(cls):
        cls.unixPath = "~/work"
        cls.winPath = r"C:\work"

    def _test_end(self, end, func):
        assert func(self.unixPath).endswith(end)
        assert func(self.winPath).endswith(end)

    def test_config(self):
        self._test_end("config.json", getConfigPath)

    def test_executor(self):
        self._test_end("executor.json", getExecutorPath)

    def test_templates(self):
        self._test_end("templates", getTemplatePath)

    def test_fileinput(self):
        self._test_end("input.data", getFileInputPath)

    def test_fileoutput(self):
        self._test_end("output.data", getFileOutputPath)
    
    def test_fileext(self):
        assert getFileExt("~/dir/a.c") == "c"
        assert getFileExt("~/dir/a.java") == "java"
        assert getFileExt(r"C:\a.java") == "java"
        assert getFileExt(r"D:\p.pas") == "pas"
