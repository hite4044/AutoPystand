import wx
import sys
import subprocess
from os import makedirs, walk
from os.path import isdir, normpath, expandvars, join as path_join, abspath, isfile
from guis.widget import *


class ProjectSettings(wx.Panel):
    def __init__(self, parent: wx.Panel = None):
        super().__init__(parent)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.dir_choose_tab = DirChooseTab(self)
        self.executable_inputter = ExecutableInputter(self)
        self.pro_enter_inputter = ProjEnterInputter(self)
        self.sizer.Add(self.dir_choose_tab, flag=wx.EXPAND | wx.RIGHT | wx.LEFT, border=5)
        self.sizer.Add(self.executable_inputter, flag=wx.EXPAND | wx.RIGHT | wx.LEFT, border=5)
        self.sizer.Add(self.pro_enter_inputter, flag=wx.EXPAND | wx.RIGHT | wx.LEFT, border=5)
        self.SetSizer(self.sizer)

    def check(self):
        checks: dict[str, DataWidget] = {
            "文件夹配置": self.dir_choose_tab,
            "Python解释器": self.executable_inputter,
            "项目入口": self.pro_enter_inputter,
        }
        for name, widget in checks.items():
            assert isinstance(widget, DataWidget)
            if not widget.check():
                return name

    def get_data(self):
        return {
            "project_dir": self.dir_choose_tab.get_data(),
            "executable": self.executable_inputter.get_data(),
            "enter": self.pro_enter_inputter.get_data(),
        }


class DirChooseTab(wx.Panel, DataWidget):
    """选择项目文件夹的标签页"""

    def __init__(self, parent: wx.Panel = None):
        super().__init__(parent)

        self.sizer = wx.StaticBoxSizer(wx.VERTICAL, self, label="项目文件夹")

        self.input_panel = wx.Panel(self)
        self.input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.input_choose_btn = wx.Button(self.input_panel, label="打开")
        self.proj_dir = LabelTextCtrl(self.input_panel, label="项目文件夹:")
        self.proj_dir.SetMaxSize((MAX_SIZE[0], 31))
        self.input_choose_btn.SetMaxSize((MAX_SIZE[0], 31))
        self.input_sizer.Add(self.proj_dir.real_parent, proportion=1, flag=wx.EXPAND)
        self.input_sizer.AddSpacer(5)
        self.input_sizer.Add(self.input_choose_btn, proportion=0)
        self.input_sizer.SetMinSize((MAX_SIZE[0], 31))
        self.input_panel.SetSizer(self.input_sizer)
        self.sizer.Add(self.input_panel, flag=wx.EXPAND)
        self.sizer.AddSpacer(5)

        self.output_panel = wx.Panel(self)
        self.output_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.output_choose_btn = wx.Button(self.output_panel, label="打开")
        self.output_dir = LabelTextCtrl(self.output_panel, label="输出文件夹:")
        self.output_dir.SetMaxSize((MAX_SIZE[0], 31))
        self.output_choose_btn.SetMaxSize((MAX_SIZE[0], 31))
        self.output_sizer.Add(self.output_dir.real_parent, proportion=1, flag=wx.EXPAND)
        self.output_sizer.AddSpacer(5)
        self.output_sizer.Add(self.output_choose_btn, proportion=0)
        self.output_sizer.SetMinSize((MAX_SIZE[0], 31))
        self.output_panel.SetSizer(self.output_sizer)
        self.sizer.Add(self.output_panel, flag=wx.EXPAND)
        self.sizer.AddSpacer(5)

        self.SetSizer(self.sizer)

        self.input_choose_btn.Bind(wx.EVT_BUTTON, self.open_file_chooser)
        self.output_choose_btn.Bind(wx.EVT_BUTTON, self.open_file_chooser)
        self.input_panel.SetDropTarget(MyFileDropTarget(self.input_drop_cbk))
        self.output_panel.SetDropTarget(MyFileDropTarget(self.output_drop_cbk))

    def open_file_chooser(self, event: wx.Event):
        with wx.DirDialog(
            self, "选择项目文件夹", style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST
        ) as dirDialog:
            if dirDialog.ShowModal() == wx.ID_OK:
                path = dirDialog.GetPath()
                if event.GetEventObject() == self.input_choose_btn:
                    self.proj_dir.SetValue(path)
                    self.output_dir.SetValue(path_join(path, "output"))
                else:
                    self.output_dir.SetValue(path)

    def input_drop_cbk(self, x, y, filenames):
        self.proj_dir.SetValue(filenames[0])
        self.output_dir.SetValue(path_join(filenames[0], "output"))

    def output_drop_cbk(self, x, y, filenames):
        self.output_dir.SetValue(filenames[0])

    def get_data(self) -> tuple[str, str]:
        return abspath(self.proj_dir.GetValue()), abspath(self.output_dir.GetValue())

    def check(self) -> str:
        dp = self.proj_dir.GetValue()
        if not dp:
            return "请选择项目文件夹"
        dp = abspath(dp)
        if not isdir(dp):
            return "文件夹不存在"
        self.proj_dir.SetValue(dp)
        makedirs(self.output_dir.GetValue(), exist_ok=True)
        return None


class VenvCreator(wx.Button):
    def __init__(self, parent: wx.Window = None):
        super().__init__(parent, label="创建虚拟环境", size=(170, 29))
        self.Bind(wx.EVT_BUTTON, self.create_venv)

    def create_venv(self, _):
        self.Disable()
        self.SetLabel("创建中...")
        start_return(self.venv_create_thread, r"D:\Python310\python.exe")

    def venv_create_thread(self, executable: str = None):
        try:
            venv_dir = self.venv_create(executable)
            wx.CallAfter(self.on_create_over, venv_dir)
        except Exception as e:
            wx.MessageBox(str(e), "错误", wx.OK | wx.ICON_ERROR)
        finally:
            self.Enable()

    def venv_create(self, executable: str = None) -> str:
        temp_dir = expandvars("%TEMP%")
        venv_dir = path_join(temp_dir, f"auto_pystand_venv_{rand_hex()}")
        command = f"{executable} -m venv {venv_dir}"
        subprocess.run(command, shell=True)
        return venv_dir

    def on_create_over(self, venv_dir: str):
        self.Enable()
        self.SetLabel("创建虚拟环境(已完成)")
        event = VenvCreateOverEvent(apEVT_VENV_CREATE_OVER, self.GetId())
        event.SetVenvPath(venv_dir)
        self.ProcessEvent(event)


class ExecutableInputter(wx.Panel, DataWidget):
    """处理输入Python解释器路径"""

    def __init__(self, parent: wx.Panel = None):
        super().__init__(parent)

        self.sizer = wx.StaticBoxSizer(wx.VERTICAL, self, label="Python解释器")
        self.btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.text_ctrl = wx.TextCtrl(self, value=str(sys.executable))
        self.choose_file_btn = wx.Button(self, label="选择文件")
        self.create_venv_btn = VenvCreator(self)
        self.sizer.Add(self.text_ctrl, proportion=1, flag=wx.EXPAND)
        self.btn_sizer.Add(self.choose_file_btn, proportion=0)
        self.btn_sizer.AddSpacer(5)
        self.btn_sizer.Add(self.create_venv_btn, proportion=0)
        self.sizer.AddSpacer(5)
        self.sizer.Add(self.btn_sizer, proportion=0)
        self.sizer.AddSpacer(5)
        self.SetSizer(self.sizer)

        self.text_ctrl.SetDropTarget(MyFileDropTarget(self.OnDropFiles))
        self.create_venv_btn.Bind(EVT_VENV_CREATE_OVER, self.OnVenvCreateOver)

    def OnVenvCreateOver(self, event: VenvCreateOverEvent):
        self.text_ctrl.SetValue(path_join(event.GetVenvPath(), "Scripts", "python.exe"))

    def Enable(self, enable: bool):
        super().Enable(enable)
        if enable:
            self.text_ctrl.SetWindowStyleFlag(wx.TE_READONLY)
            self.choose_file_btn.Enable()
        else:
            self.text_ctrl.SetWindowStyleFlag(0)
            self.choose_file_btn.Disable()

    def OnDropFiles(self, x, y, filenames):
        self.text_ctrl.SetValue(filenames[0])

    def check(self) -> str | None:
        if not self.text_ctrl.GetValue():
            return "请选择Python解释器"
        fp: str = abspath(self.text_ctrl.GetValue())
        if not isfile(fp):
            return "文件不存在"
        if not fp.endswith(".exe"):
            return "文件不是Python解释器"
        self.text_ctrl.SetValue(fp)
        return None

    def get_data(self) -> str:
        return abspath(self.text_ctrl.GetValue())


class ProjEnterInputter(wx.Panel, DataWidget):
    """处理输入项目路径"""

    def __init__(self, parent: ProjectSettings = None):
        super().__init__(parent)
        self.parent = parent
        self.activate_dir = None

        self.sizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label="项目入口")
        self.label = wx.StaticText(self, label="入口文件: ")
        self.enter_path = wx.ComboBox(self, style=wx.CB_DROPDOWN, choices=["114514"])
        self.sizer.Add(self.label, proportion=0, flag=wx.ALIGN_CENTER)
        self.sizer.Add(self.enter_path, proportion=1, flag=wx.EXPAND)
        self.SetSizer(self.sizer)

        self.enter_path.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        self.enter_path.Bind(wx.EVT_KILL_FOCUS, self.on_lost_focus)

    def on_focus(self, event: wx.FocusEvent):
        proj_dir = abspath(normpath(self.parent.dir_choose_tab.proj_dir.GetValue()))
        if not isdir(proj_dir):
            wx.MessageBox("项目目录不存在", "错误", wx.OK | wx.ICON_ERROR)
            return
        self.parent.dir_choose_tab.proj_dir.SetValue(proj_dir)
        self.parent.dir_choose_tab.input_panel.Enable(False)
        self.parent.dir_choose_tab.input_panel.Refresh()
        self.activate_dir = proj_dir
        walk_obj = walk(proj_dir)
        _, _, files = next(walk_obj)
        record_value = self.enter_path.GetValue()
        self.enter_path.SetItems(files)
        self.enter_path.SetValue(record_value)
        event.Skip()

    def on_lost_focus(self, event: wx.FocusEvent):
        self.parent.dir_choose_tab.input_panel.Enable(True)
        self.parent.dir_choose_tab.input_panel.Refresh()
        event.Skip()

    def check(self) -> str | None:
        real_fp = path_join(self.activate_dir, self.enter_path.GetValue())
        if isfile(real_fp):
            return None
        else:
            return "项目入口文件不存在"

    def get_data(self) -> str:
        real_fp = path_join(self.activate_dir, self.enter_path.GetValue())
        return real_fp
