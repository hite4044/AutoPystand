from typing import Any, Callable
import wx
import ctypes
from random import randbytes
from threading import Thread

user32 = ctypes.windll.user32
MAX_SIZE = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

__font_cache: dict[float, wx.Font] = {}


def ft(size: float):
    if size not in __font_cache:
        font: wx.Font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetPointSize(int(size))
        __font_cache[size] = font
    return __font_cache[size]


def start_return(func, *args, **kwargs):
    def wrapper():
        return func(*args, **kwargs)

    t = Thread(target=wrapper)
    t.start()
    return t


def rand_hex(length: int = 8):
    return randbytes(length).hex()


apEVT_VENV_CREATE_OVER = wx.NewEventType()
EVT_VENV_CREATE_OVER = wx.PyEventBinder(apEVT_VENV_CREATE_OVER, 1)


class VenvCreateOverEvent(wx.PyCommandEvent):  # 1 定义事件
    def __init__(self, evtType, id):
        wx.PyCommandEvent.__init__(self, evtType, id)
        self.venv_path = ""

    def GetVenvPath(self):
        return self.venv_path

    def SetVenvPath(self, path: str):
        self.venv_path = path


class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, callback: Callable[[int, int, list[str]], bool]):
        super().__init__()
        self.callback = callback

    def OnDropFiles(self, x, y, filenames) -> bool:
        ret = self.callback(x, y, filenames)
        if ret is not None:
            return ret
        return True


class CenteredStaticText(wx.StaticText):
    """使得绘制的文字始终保持在控件中央"""

    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        label=wx.EmptyString,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=0,
        name=wx.StaticTextNameStr,
        x_center=True,
        y_center=True,
    ):
        super().__init__(parent, id, label, pos, size, style, name)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.x_center = x_center
        self.y_center = y_center

    def OnPaint(self, event: wx.PaintEvent):
        dc = wx.PaintDC(self)
        label = self.GetLabel()
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        dc.SetFont(self.GetFont())
        Tsize = dc.GetTextExtent(label)
        size = self.GetSize()

        dc.DrawText(
            label,
            ((size[0] - Tsize[0]) // 2) * int(self.x_center),
            ((size[1] - Tsize[1]) // 2) * int(self.y_center),
        )

    def Enable(self, enable=True):
        print("fsdsds")
        return super().Enable(enable)


class LabelTextCtrl(wx.TextCtrl):
    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        value=wx.EmptyString,
        label=wx.EmptyString,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=0,
        validator=wx.DefaultValidator,
        name=wx.TextCtrlNameStr,
    ):
        self.real_parent = wx.Panel(parent)
        super().__init__(self.real_parent, id, value, pos, size, style, validator, name)
        self.label = CenteredStaticText(self.real_parent, label=label, x_center=False)
        self.label.SetMinSize((-1, MAX_SIZE[1]))
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.label, proportion=0, flag=wx.RIGHT, border=5)
        self.sizer.Add(self, proportion=1, flag=wx.EXPAND)
        self.real_parent.SetSizer(self.sizer)

    def GetParent(self):
        return self.real_parent.GetParent()

    def SetMaxSize(self, size):
        return self.real_parent.SetMaxSize(size)

    def SetMinSize(self, size):
        return self.real_parent.SetMinSize(size)


class DataWidget:
    def check(self) -> str | None:
        """返回为None时表示输入合法, 为字符串时为错误信息"""
        return None

    def get_data(self) -> Any:
        return None
