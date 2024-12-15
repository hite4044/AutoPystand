import wx
import sys
import subprocess
from os import makedirs, walk
from os.path import isdir, normpath, expandvars, join as path_join, abspath
from guis.proj_settings import ProjectSettings
from guis.widget import *


class PackagesShower(wx.Panel):
    def __init__(self, parent: wx.Panel = None):
        super().__init__(parent)
        self.executable = None

        self.sizer = wx.BoxSizer(wx.VERTICAL, self)
        self.refresh_btn = wx.Button(self, label="刷新")
        self.sizer.Add(self.refresh_btn, proportion=0, flag=wx.ALIGN_CENTER)
        self.SetSizer(self.sizer)

        self.refresh_btn.Bind(wx.EVT_BUTTON, self.refresh_packages)

    def update_data(self, executable: str):
        self.executable = executable
        self.refresh_btn.Enable()

    def refresh_packages(self):
        if self.executable is None:
            return
        self.refresh_btn.Disable()

    def get_packages_thread(self):
        # 读取pip输出
        command = f"{self.executable} -m pip list"
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        raw_stdout, raw_stderr = process.communicate()
        if process.returncode != 0:
            wx.MessageBox(raw_stderr.decode(), "错误", wx.OK | wx.ICON_ERROR)
            return

        # 处理pip输出
        stdout = raw_stdout.decode()
        start_read = False
        packages: list[tuple[str, str]] = []
        for line in stdout.splitlines():
            if set(list(line)) == {" ", "-"}:
                start_read = True
                continue
            if start_read:
                packages.append(tuple(line.split()))
        wx.CallAfter(self.on_packages_read_over, packages)

    def on_packages_read_over(self, packages: list[tuple[str, str]]):
        pass


class LibraryManager(wx.Panel):
    def __init__(self, parent: wx.Panel = None):
        super().__init__(parent)

        self.sizer = wx.StaticBoxSizer(wx.VERTICAL, self, label="库管理器")
        self.SetSizer(self.sizer)


class MainWindow(wx.Frame):
    """看什么看，一个主窗口而已"""

    def __init__(self, parent: wx.Frame = None):
        super().__init__(parent, title="Main Window", size=(800, 600))
        self.SetFont(ft(12))

        ###Global###
        self.project_dir = None  # 项目文件夹

        ###UI###
        self.notebook = wx.Notebook(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.project_configure = ProjectSettings(self.notebook)
        self.notebook.AddPage(self.project_configure, "项目配置")
        self.sizer.Add(self.notebook, proportion=1, flag=wx.EXPAND)
        self.SetSizer(self.sizer)


if __name__ == "__main__":
    app = wx.App()
    frame = MainWindow()
    frame.Show()
    app.MainLoop()
