import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from PIL import Image

import threading

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}

import re

def numeric_key(path: Path):
    """
    提取文件名中的数字用于排序：
    1.jpg, 2.jpg, 10.jpg -> 正确顺序
    """
    nums = re.findall(r'\d+', path.stem)
    return int(nums[0]) if nums else float('inf')

def images_to_pdf(folder: Path, output_pdf: Path):
    files = [p for p in folder.iterdir() if p.suffix.lower() in IMG_EXTS]
    files.sort(key=numeric_key)

    if not files:
        raise ValueError("文件夹中没有图片")

    images = []
    for f in files:
        img = Image.open(f)
        if img.mode != "RGB":
            img = img.convert("RGB")
        images.append(img)

    images[0].save(
        output_pdf,
        save_all=True,
        append_images=images[1:]
    )

    return output_pdf

def choose_folder():
    # 防止重复点击（并给用户一个“正在处理”的反馈）
    btn.config(state="disabled")
    status_var.set("处理中…")

    folder = filedialog.askdirectory(title="选择图片文件夹")
    if not folder:
        btn.config(state="normal")
        status_var.set("")
        return

    folder_path = Path(folder)
    output_pdf = folder_path / f"{folder_path.name}.pdf"

    def worker():
        try:
            out = images_to_pdf(folder_path, output_pdf)
            root.after(0, lambda: messagebox.showinfo("完成", f"已生成：\n{out}"))
        except Exception as e:
            root.after(0, lambda: messagebox.showerror("错误", str(e)))
        finally:
            root.after(0, lambda: (btn.config(state="normal"), status_var.set("")))

    threading.Thread(target=worker, daemon=True).start()

# ===== GUI =====
root = tk.Tk()
root.title("JPG 合成 PDF")
root.geometry("360x160")
root.resizable(False, False)

status_var = tk.StringVar(value="")

label = tk.Label(root, text="选择一个包含 JPG/PNG 的文件夹\n合成一个 PDF",
                 font=("Arial", 11))
label.pack(pady=20)

btn = tk.Button(root, text="选择文件夹并生成 PDF",
                width=25, height=2, command=choose_folder)
btn.pack()

status_label = tk.Label(root, textvariable=status_var, font=("Arial", 10))
status_label.pack(pady=(8, 0))

root.mainloop()