import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

def build_styles(root: tk.Tk):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except:
        pass

    # 전역: ttk 기본 위젯 배경을 모두 흰색으로
    style.configure("TFrame", background="white")
    style.configure("TLabel", background="white")
    style.configure("TSeparator", background="white")
    style.configure("TLabelframe", background="white")
    style.configure("TLabelframe.Label", background="white")

    # 섹션 타이틀(라벨프레임 제목) 폰트
    style.configure("Cur.TLabelframe.Label", font=("Segoe UI", 14, "bold"))
    style.configure("Det.TLabelframe.Label", font=("Segoe UI", 14, "bold"))
    style.configure("GJ.TLabelframe.Label",  font=("Segoe UI", 14, "bold"))

    # 라벨프레임 컨테이너(배경 흰색)
    style.configure("Cur.TLabelframe", background="white")
    style.configure("Det.TLabelframe", background="white")
    style.configure("GJ.TLabelframe",  background="white")

    # 흰색 입력창 스타일(Entry)
    style.configure("White.TEntry", fieldbackground="white", foreground="black", background="white")
    style.map("White.TEntry", fieldbackground=[("disabled", "white"), ("readonly", "white")])

    # 표(셀) 폰트: 볼드 + 크게
    det_font = tkfont.Font(family="Segoe UI", size=14, weight="bold")
    gj_font  = tkfont.Font(family="Segoe UI", size=14, weight="bold")
    cur_font = tkfont.Font(family="Segoe UI", size=14, weight="bold")

    return {
        "det_font": det_font,
        "gj_font": gj_font,
        "cur_font": cur_font,
        "entry_style": "White.TEntry",
    }
