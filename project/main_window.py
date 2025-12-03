import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np, cv2
from PIL import Image, ImageTk
from engine.collage_generator import CollageGenerator

# 메인 UI 클래스
class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("디지털 콜라주 생성기")
        self.root.geometry("1280x720")

        self.image_paths = []
        self.generator = CollageGenerator()

        self._create_menu()
        self._create_layout()

    def _create_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="이미지 불러오기", command=self._open_files)
        file_menu.add_command(label="초기화", command=self._clear_selection)
        file_menu.add_separator()
        file_menu.add_command(label="프로젝트 저장(결과 PNG)", command=self._save_result)
        file_menu.add_separator()
        file_menu.add_command(label="종료", command=self.root.destroy)
        menubar.add_cascade(label="파일", menu=file_menu)

        run_menu = tk.Menu(menubar, tearoff=0)
        run_menu.add_command(label="콜라주 생성", command=self._generate_collage)
        menubar.add_cascade(label="실행", menu=run_menu)

        self.root.config(menu=menubar)

    def _create_layout(self):
        # 왼쪽 패널
        left = tk.Frame(self.root, width=260, bg="lightgray")
        left.pack(side="left", fill="y")

        # 메인 이미지
        self._create_label(left, "메인 이미지 (첫 번째)", bold=True)
        self.main_image_label = tk.Label(left, text="선택된 이미지 없음", bg="white", 
                                         fg="gray", width=36, height=2, relief="solid", borderwidth=1)
        self.main_image_label.pack(padx=10, pady=6)

        # 배경 조각 이미지
        self._create_label(left, "배경 조각 이미지", bold=True, top_padding=10)
        self.listbox = tk.Listbox(left, width=36, height=15)
        self.listbox.pack(padx=10, pady=6)

        # 옵션
        self._create_label(left, "옵션", bold=True, top_padding=6)
        opt = tk.Frame(left, bg="lightgray")
        opt.pack(padx=10, pady=4)

        # 조각 개수
        tk.Label(opt, text="조각 개수:", bg="lightgray", width=10, anchor="w").grid(row=0, column=0, pady=2)
        self.pieces_var = tk.IntVar(value=100)
        tk.Entry(opt, textvariable=self.pieces_var, width=8).grid(row=0, column=1, padx=5)

        # 캔버스 W
        tk.Label(opt, text="캔버스 W:", bg="lightgray", width=10, anchor="w").grid(row=1, column=0, pady=2)
        self.canvas_w = tk.IntVar(value=800)
        tk.Entry(opt, textvariable=self.canvas_w, width=8).grid(row=1, column=1, padx=5)

        # 캔버스 H
        tk.Label(opt, text="캔버스 H:", bg="lightgray", width=10, anchor="w").grid(row=2, column=0, pady=2)
        self.canvas_h = tk.IntVar(value=600)
        tk.Entry(opt, textvariable=self.canvas_h, width=8).grid(row=2, column=1, padx=5)

        # 버튼들
        btn_frame = tk.Frame(left, bg="lightgray")
        btn_frame.pack(padx=10, pady=10)
        tk.Button(btn_frame, text="이미지 불러오기", command=self._open_files, width=15).pack(side="left", padx=(0,5))
        tk.Button(btn_frame, text="콜라주 생성", command=self._generate_collage, width=15).pack(side="left")

        # 미리보기 영역
        self.preview_frame = tk.Frame(self.root, bg="white")
        self.preview_frame.pack(side="right", fill="both", expand=True)
        self.info_label = tk.Label(self.preview_frame, text="이미지를 불러오고 '콜라주 생성'을 누르세요.", 
                                   font=("Arial", 14), fg="gray")
        self.info_label.pack(expand=True)

        self.last_result = None
    
    def _create_label(self, parent, text, bold=False, top_padding=10):
        font = ("Arial", 11, "bold") if bold else ("Arial", 11)
        tk.Label(parent, text=text, bg="lightgray", font=font).pack(pady=(top_padding, 0))

    def _open_files(self):
        paths = filedialog.askopenfilenames(
            title="이미지 선택 (여러 개 가능)",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.webp")]
        )
        if paths:
            for p in paths:
                if p not in self.image_paths:
                    self.image_paths.append(p)
            
            # UI 업데이트
            self._update_image_lists()
            self.info_label.config(text=f"{len(self.image_paths)}개 이미지 선택됨")
    
    def _update_image_lists(self):
        # 메인 이미지 (첫 번째)
        if self.image_paths:
            main_name = self.image_paths[0].split("/")[-1]
            self.main_image_label.config(text=main_name, fg="black")
        else:
            self.main_image_label.config(text="선택된 이미지 없음", fg="gray")
        
        # 배경 조각 이미지들
        self.listbox.delete(0, "end")
        for p in self.image_paths:
            self.listbox.insert("end", p.split("/")[-1])

    def _clear_selection(self):
        self.image_paths = []
        self._update_image_lists()
        self.info_label.config(text="선택 초기화됨")
        self.last_result = None

    def _generate_collage(self):
        if not self.image_paths:
            messagebox.showwarning("경고", "이미지를 하나 이상 선택하세요.")
            return
        pieces = max(1, int(self.pieces_var.get()))
        w = max(200, int(self.canvas_w.get()))
        h = max(200, int(self.canvas_h.get()))

        try:
            result = self.generator.generate(
                image_paths=self.image_paths,
                canvas_size=(w, h),
                pieces=pieces
            )
            self.last_result = result
            self._show_result_on_frame(result)
        except Exception as e:
            messagebox.showerror("오류", f"콜라주 생성 실패:\n{e}")

    def _show_result_on_frame(self, img_bgra):
        h, w = img_bgra.shape[:2]
        maxw = self.preview_frame.winfo_width() or 800
        maxh = self.preview_frame.winfo_height() or 600
        scale = min(maxw / w, maxh / h, 1.0)
        
        new_w, new_h = int(w * scale), int(h * scale)
        resized = cv2.resize(img_bgra, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        rgba = cv2.cvtColor(resized, cv2.COLOR_BGRA2RGBA)
        pil_img = Image.fromarray(rgba)
        
        self.tkimg = ImageTk.PhotoImage(pil_img)
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        lbl = tk.Label(self.preview_frame, image=self.tkimg)
        lbl.pack(expand=True)

    def _save_result(self):
        if self.last_result is None:
            messagebox.showinfo("정보", "저장할 결과가 없습니다. 먼저 콜라주를 생성하세요.")
            return
        path = filedialog.asksaveasfilename(
            title="결과 저장 (PNG 권장)",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPG", "*.jpg")]
        )
        if not path:
            return
        
        if path.lower().endswith(".jpg") or path.lower().endswith(".jpeg"):
            bgr = cv2.cvtColor(self.last_result, cv2.COLOR_BGRA2BGR)
            cv2.imwrite(path, bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])
        else:
            cv2.imwrite(path, self.last_result)
        
        messagebox.showinfo("저장완료", f"저장됨: {path}")

    def run(self):
        self.root.mainloop()