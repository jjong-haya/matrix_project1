import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from typing import List, Optional
from app.matrix_ops import inverse_by_adjugate, gauss_jordan_inverse, matrices_equal
from app.styles import build_styles

class MatrixConsoleApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("이산수학 Project 1")
        self.geometry("1000x780")
        self.configure(bg="white")

        styles = build_styles(self)
        self.det_font: tkfont.Font = styles["det_font"]
        self.gj_font:  tkfont.Font = styles["gj_font"]
        self.cur_font: tkfont.Font = styles["cur_font"]
        entry_style = styles["entry_style"]

        # 상태
        self.state = "await_n"  # await_n | await_row | edit_ready
        self.n: Optional[int] = None
        self.rows: List[List[float]] = []          # 현재 입력/편집 중 행렬 데이터
        self.cur_labels: Optional[List[List[tk.Label]]] = None  # 현재 입력 표 셀 레퍼런스

        # 결과표 하이라이트용
        self.default_cell_bg = "white"
        self.det_labels: Optional[List[List[tk.Label]]] = None
        self.gj_labels: Optional[List[List[tk.Label]]] = None

        # 상단 입력 바
        top = ttk.Frame(self, padding=10, style="TFrame")
        top.pack(fill="x")
        self.prompt = tk.StringVar(value="정방행렬 크기 n을 입력: ")
        ttk.Label(top, textvariable=self.prompt, font=("Segoe UI", 11, "bold"), style="TLabel").pack(side="left")
        self.entry = ttk.Entry(top, width=60, style=entry_style)
        self.entry.pack(side="left", padx=6)
        self.entry.bind("<Return>", self.on_enter)
        self.entry.focus()

        self.msg = tk.StringVar(value="예) n=3, 각 행은 공백으로 3개의 수를 입력. (엔터로 제출) • 셀 클릭으로 값 직접 수정 가능")
        ttk.Label(self, textvariable=self.msg, foreground="#666", style="TLabel").pack(fill="x", padx=12)

        # 본문 2열 레이아웃
        body = ttk.Frame(self, padding=10, style="TFrame")
        body.pack(fill="both", expand=True)
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=2)

        # 좌: 현재 입력 행렬
        self.cur_section = ttk.LabelFrame(body, text="현재 입력 행렬", style="Cur.TLabelframe")
        self.cur_section.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.cur_container = tk.Frame(self.cur_section, bg="white")
        self.cur_container.pack(fill="both", expand=True, pady=6, padx=6)

        # 우: 결과들
        right = ttk.Frame(body, style="TFrame")
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        self.det_section = ttk.LabelFrame(right, text="행렬식 결과", style="Det.TLabelframe")
        self.det_section.grid(row=0, column=0, sticky="nsew", pady=(0, 8))
        self.det_container = tk.Frame(self.det_section, bg="white")
        self.det_container.pack(fill="both", expand=True, pady=4, padx=4)

        self.gj_section = ttk.LabelFrame(right, text="소거법 결과", style="GJ.TLabelframe")
        self.gj_section.grid(row=1, column=0, sticky="nsew")
        self.gj_container = tk.Frame(self.gj_section, bg="white")
        self.gj_container.pack(fill="both", expand=True, pady=4, padx=4)

        # 하단 비교
        ttk.Separator(self, orient="horizontal", style="TSeparator").pack(fill="x", pady=4)
        bottom = ttk.Frame(self, padding=(10, 0, 10, 10), style="TFrame")
        bottom.pack(fill="x")
        self.compare_lbl = ttk.Label(
            bottom,
            text="비교 결과: (입력 완료 후 표시됩니다.)",
            font=("Segoe UI", 11, "bold"),
            anchor="center",
            style="TLabel"
        )
        self.compare_lbl.pack(fill="x")

    # ================= 입력 처리 =================
    def on_enter(self, event=None):
        text = self.entry.get().strip()
        self.entry.delete(0, tk.END)

        if self.state == "await_n":
            # n 파싱/검증
            try:
                n = int(text)
                if n <= 0:
                    raise ValueError
            except Exception:
                self.msg.set("n은 양의 정수로 입력하세요. 예: 3")
                return
            self.n = n
            self.rows = []
            self.state = "await_row"
            self.prompt.set("1행 : ")
            self.msg.set(f"{n}×{n} 행렬 입력을 시작합니다. 각 행에 {n}개의 수(공백 구분)를 입력하고 엔터. (셀 클릭으로 편집 가능)")
            self.clear_results()
            self.render_current_matrix_empty(n)
            return

        if self.state == "await_row":
            assert self.n is not None
            parts = text.split()
            if len(parts) != self.n:
                self.msg.set(f"{len(self.rows)+1}행에는 {self.n}개의 수를 공백으로 입력하세요.")
                return
            try:
                row = [float(x) for x in parts]
            except Exception:
                self.msg.set("숫자만 입력하세요.")
                return

            self.rows.append(row)
            self.render_current_matrix_progress(self.n, self.rows)

            if len(self.rows) < self.n:
                self.prompt.set(f"{len(self.rows)+1}행 : ")
                self.msg.set(f"{len(self.rows)}행 입력 완료. 다음 행을 입력하세요. (셀 클릭으로 방금 값도 수정 가능)")
            else:
                # 입력 완료 → 계산
                self.prompt.set("입력 완료. 다시 시작하려면 n을 입력: ")
                self.state = "edit_ready"   # 이후 셀 클릭 수정 가능 상태 유지
                self.msg.set("계산 중...")
                self.compute_and_show(self.rows)
                self.msg.set("완료. 셀 클릭으로 값을 수정하면 결과가 다시 계산됩니다. 새로 시작하려면 상단에 n을 입력하세요.")

        elif self.state == "edit_ready":
            # edit_ready에서 엔터 입력은 새 n으로 간주
            try:
                n = int(text)
                if n <= 0:
                    raise ValueError
            except Exception:
                self.msg.set("새로 시작하려면 n(양의 정수)을 입력하세요. 예: 3")
                return
            # 새 입력 시작
            self.n = n
            self.rows = []
            self.state = "await_row"
            self.prompt.set("1행 : ")
            self.msg.set(f"{n}×{n} 행렬 입력을 시작합니다. 각 행에 {n}개의 수(공백 구분)를 입력하고 엔터. (셀 클릭으로 편집 가능)")
            self.clear_results()
            self.render_current_matrix_empty(n)

    # ================= 현재 입력 표 렌더 =================
    def _clear_container(self, parent: tk.Frame):
        for w in parent.winfo_children():
            w.destroy()

    def render_current_matrix_empty(self, n: int):
        self._clear_container(self.cur_container)
        grid = tk.Frame(self.cur_container, bg="white")
        grid.pack(fill="both", expand=True)
        labels: List[List[tk.Label]] = [[None]*n for _ in range(n)]  # type: ignore

        for i in range(n):
            for j in range(n):
                lbl = tk.Label(
                    grid, text=" ", bd=1, relief="solid",
                    padx=10, pady=6, bg="white", anchor="center",
                    font=self.cur_font
                )
                lbl.grid(row=i, column=j, sticky="nsew")
                # 빈칸 클릭 편집은 의미 없으니 입력 진행 중에는 무시
                lbl.bind("<Button-1>", lambda e, r=i, c=j: self._maybe_edit_cell(r, c))
                labels[i][j] = lbl

        for j in range(n):
            grid.grid_columnconfigure(j, weight=1, uniform="curcol")
        for i in range(n):
            grid.grid_rowconfigure(i, weight=1, uniform="currow")

        self.cur_labels = labels
        self.cur_container.bind("<Configure>", lambda e, r=n: self._auto_font_resize(self.cur_container, r, self.cur_font))

    def render_current_matrix_progress(self, n: int, rows: List[List[float]]):
        self._clear_container(self.cur_container)
        grid = tk.Frame(self.cur_container, bg="white")
        grid.pack(fill="both", expand=True)
        labels: List[List[tk.Label]] = [[None]*n for _ in range(n)]  # type: ignore
        entered = len(rows)

        for i in range(n):
            for j in range(n):
                text = f"{rows[i][j]:.6g}" if i < entered else " "
                lbl = tk.Label(
                    grid, text=text, bd=1, relief="solid",
                    padx=10, pady=6, bg="white", anchor="center",
                    font=self.cur_font
                )
                lbl.grid(row=i, column=j, sticky="nsew")
                lbl.bind("<Button-1>", lambda e, r=i, c=j: self._maybe_edit_cell(r, c))
                labels[i][j] = lbl

        for j in range(n):
            grid.grid_columnconfigure(j, weight=1, uniform="curcol")
        for i in range(n):
            grid.grid_rowconfigure(i, weight=1, uniform="currow")

        self.cur_labels = labels
        self.cur_container.bind("<Configure>", lambda e, r=n: self._auto_font_resize(self.cur_container, r, self.cur_font))

    # ================= 셀 클릭 편집 =================
    def _maybe_edit_cell(self, r: int, c: int):
        """표의 (r,c)를 클릭했을 때 편집 가능한지 확인하고, 가능하면 에디터를 연다."""
        if self.n is None or self.cur_labels is None:
            return
        # 아직 해당 행이 입력되지 않았으면 편집 불가
        if r >= len(self.rows):
            return
        self._open_cell_editor(r, c)

    def _open_cell_editor(self, r: int, c: int):
        """작은 팝업으로 (r,c) 값만 편집"""
        cur_val = self.rows[r][c]
        top = tk.Toplevel(self)
        top.title(f"값 편집: ({r+1},{c+1})")
        top.transient(self)
        top.grab_set()
        top.resizable(False, False)
        # 위치를 현재 셀 근처로
        try:
            cell = self.cur_labels[r][c]
            x = cell.winfo_rootx()
            y = cell.winfo_rooty()
            top.geometry(f"+{x}+{y}")
        except Exception:
            pass

        tk.Label(top, text=f"({r+1},{c+1}) 값:", anchor="w").pack(padx=12, pady=(12,4), fill="x")
        var = tk.StringVar(value=str(cur_val))
        ent = ttk.Entry(top)
        ent.pack(padx=12, fill="x")
        ent.insert(0, str(cur_val))
        ent.select_range(0, tk.END)
        ent.focus()

        btns = tk.Frame(top, bg="white")
        btns.pack(padx=12, pady=12, fill="x")
        def on_ok():
            txt = ent.get().strip()
            try:
                val = float(txt)
            except Exception:
                # 간단히 입력창 테두리로 오류 표시
                ent.configure(style="")
                ent.configure(foreground="red")
                return
            # 업데이트
            self.rows[r][c] = val
            # 표 갱신
            self.render_current_matrix_progress(self.n, self.rows)
            # 결과 재계산: 모든 행이 존재할 때만
            if len(self.rows) == self.n:
                self.compute_and_show(self.rows)
                self.state = "edit_ready"
                self.prompt.set("입력 완료. 다시 시작하려면 n을 입력: ")
                self.msg.set("값이 수정되어 결과를 재계산했습니다. 또 수정하려면 셀을 클릭하세요.")
            top.destroy()

        def on_cancel():
            top.destroy()

        ok = ttk.Button(btns, text="확인", command=on_ok)
        ok.pack(side="left")
        ttk.Button(btns, text="취소", command=on_cancel).pack(side="left", padx=8)
        top.bind("<Return>", lambda e: on_ok())
        top.bind("<Escape>", lambda e: on_cancel())

    # ================= 결과/메시지 렌더 =================
    def _auto_font_resize(self, container: tk.Frame, rows: int, font_obj: tkfont.Font):
        if rows <= 0:
            return
        h = container.winfo_height() or container.winfo_reqheight()
        raw_size = h / (rows * 1.8)
        size = max(12, min(32, int(raw_size)))
        try:
            font_obj.configure(size=size)
        except:
            pass

    def render_matrix(self, parent: tk.Frame, M: List[List[float]], grid_name: str):
        self._clear_container(parent)
        grid = tk.Frame(parent, bg="white")
        grid.pack(fill="both", expand=True)
        rows, cols = len(M), len(M[0])
        labels: List[List[tk.Label]] = [[None]*cols for _ in range(rows)]
        f = self.det_font if grid_name == "det" else self.gj_font
        for i in range(rows):
            for j in range(cols):
                cell = tk.Label(
                    grid, text=f"{M[i][j]:.6g}", bd=1, relief="solid",
                    padx=8, pady=4, anchor="center",
                    bg=self.default_cell_bg, font=f
                )
                cell.grid(row=i, column=j, sticky="nsew")
                cell.bind("<Enter>", lambda e, g=grid_name, r=i, c=j: self.on_cell_enter(g, r, c))
                cell.bind("<Leave>", lambda e, g=grid_name, r=i, c=j: self.on_cell_leave(g, r, c))
                labels[i][j] = cell
        for j in range(cols):
            grid.grid_columnconfigure(j, weight=1, uniform=f"{grid_name}_col")
        for i in range(rows):
            grid.grid_rowconfigure(i, weight=1, uniform=f"{grid_name}_row")
        if grid_name == "det":
            self.det_labels = labels
        else:
            self.gj_labels = labels
        parent.bind(
            "<Configure>",
            lambda e, r=rows, fo=f: self._auto_font_resize(parent, r, fo)
        )

    def show_center_message(self, parent: tk.Frame, text: str, grid_name: str):
        self._clear_container(parent)
        lbl = tk.Label(parent, text=text, bg="white", fg="red", font=("Segoe UI", 18, "bold"))
        lbl.pack(fill="both", expand=True)
        if grid_name == "det":
            self.det_labels = None
        else:
            self.gj_labels = None

    def clear_results(self):
        self._clear_container(self.det_container)
        self._clear_container(self.gj_container)
        self.compare_lbl.config(text="비교 결과: (입력 완료 후 표시됩니다.)", foreground="black")

    # ================= 계산/비교 =================
    def compute_and_show(self, A: List[List[float]]):
        inv_det = None
        try:
            inv_det = inverse_by_adjugate(A)
            self.render_matrix(self.det_container, inv_det, grid_name="det")
        except:
            self.show_center_message(self.det_container, "역행렬이 존재하지 않습니다.", "det")
            inv_det = None

        inv_gj = None
        try:
            inv_gj = gauss_jordan_inverse(A)
            self.render_matrix(self.gj_container, inv_gj, grid_name="gj")
        except:
            self.show_center_message(self.gj_container, "역행렬이 존재하지 않습니다.", "gj")
            inv_gj = None

        if inv_det is not None and inv_gj is not None:
            same = matrices_equal(inv_det, inv_gj, tol=1e-6)
            if same:
                self.compare_lbl.config(text="비교 결과: 두 결과가 동일합니다 (허용오차 1e-6).", foreground="green")
            else:
                self.compare_lbl.config(text="비교 결과: 두 결과가 다릅니다.", foreground="red")
        elif inv_det is None and inv_gj is None:
            self.compare_lbl.config(text="비교 결과: 두 방법 모두 역행렬이 존재하지 않습니다.", foreground="red")
        elif inv_det is None:
            self.compare_lbl.config(text="비교 결과: 행렬식 실패, 소거법 성공.", foreground="orange")
        else:
            self.compare_lbl.config(text="비교 결과: 소거법 실패, 행렬식 성공.", foreground="orange")

        # edit_ready 상태 유지: 이후 셀 클릭 수정 → 즉시 재계산 가능
        if self.n is not None and len(self.rows) == self.n:
            self.state = "edit_ready"

    # ================= 결과표 하이라이트 =================
    def _set_bg(self, lbl: Optional[tk.Label], color: Optional[str]):
        if lbl is None:
            return
        lbl.configure(bg=(color if color else self.default_cell_bg))

    def on_cell_enter(self, grid_name: str, r: int, c: int):
        if grid_name == "det":
            a = self.det_labels[r][c] if self.det_labels else None
            b = self.gj_labels[r][c] if (self.gj_labels and r < len(self.gj_labels) and c < len(self.gj_labels[0])) else None
        else:
            a = self.gj_labels[r][c] if self.gj_labels else None
            b = self.det_labels[r][c] if (self.det_labels and r < len(self.det_labels) and c < len(self.det_labels[0])) else None
        self._set_bg(a, "#fff4b2")
        self._set_bg(b, "#c8f7c5")

    def on_cell_leave(self, grid_name: str, r: int, c: int):
        if grid_name == "det":
            a = self.det_labels[r][c] if self.det_labels else None
            b = self.gj_labels[r][c] if (self.gj_labels and r < len(self.gj_labels) and c < len(self.gj_labels[0])) else None
        else:
            a = self.gj_labels[r][c] if self.gj_labels else None
            b = self.det_labels[r][c] if (self.det_labels and r < len(self.det_labels[0])) else None
        self._set_bg(a, None)
        self._set_bg(b, None)
