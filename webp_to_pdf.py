from pathlib import Path
import os
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageOps

BASE = Path(__file__).resolve().parent
OUTPUT = BASE / "output"


def collect_webp(source: Path):
    if source.is_dir():
        return sorted((p for p in source.rglob("*") if p.is_file() and p.suffix.lower() == ".webp"), key=lambda p: str(p.relative_to(source)).lower())
    if source.suffix.lower() == ".zip":
        with zipfile.ZipFile(source) as archive:
            return sorted((n for n in archive.namelist() if not n.endswith("/") and Path(n).suffix.lower() == ".webp"), key=str.lower)
    return []


def create_pdf(source: Path):
    pages = []
    archive = zipfile.ZipFile(source) if source.is_file() else None
    try:
        files = collect_webp(source)
        for item in files:
            if archive:
                with archive.open(item) as stream, Image.open(stream) as im:
                    pages.append(ImageOps.exif_transpose(im).convert("RGB"))
            else:
                with Image.open(item) as im:
                    pages.append(ImageOps.exif_transpose(im).convert("RGB"))
        if not pages:
            return 0
        OUTPUT.mkdir(exist_ok=True)
        target = OUTPUT / f"{source.stem if source.is_file() else source.name}.pdf"
        pages[0].save(target, "PDF", save_all=True, append_images=pages[1:], resolution=150)
        return len(pages)
    finally:
        for page in pages:
            page.close()
        if archive:
            archive.close()


def open_output():
    OUTPUT.mkdir(exist_ok=True)
    os.startfile(str(OUTPUT))


def pick_folder():
    selected = filedialog.askdirectory(title="选择包含 WebP 图片的文件夹")
    if selected:
        process([Path(selected)])


def pick_folders():
    # Tk's standard folder picker only supports one folder. Use a small directory
    # browser with extended selection so users can select several sibling folders.
    win = tk.Toplevel()
    win.title("批量选择图片文件夹")
    win.geometry("650x460")
    win.transient()
    current = tk.StringVar(value=str(Path.home()))
    tk.Label(win, text="当前路径：").pack(anchor="w", padx=10, pady=(10, 0))
    path_entry = tk.Entry(win, textvariable=current)
    path_entry.pack(fill="x", padx=10)
    listing = tk.Listbox(win, selectmode=tk.EXTENDED, height=18)
    listing.pack(fill="both", expand=True, padx=10, pady=10)
    entries = []

    def populate(path_text=None):
        path = Path(path_text or current.get()).expanduser()
        try:
            dirs = sorted((x for x in path.iterdir() if x.is_dir()), key=lambda x: x.name.lower())
        except Exception as exc:
            messagebox.showerror("无法打开路径", str(exc), parent=win)
            return
        current.set(str(path.resolve()))
        listing.delete(0, tk.END)
        entries.clear()
        for folder in dirs:
            listing.insert(tk.END, folder.name)
            entries.append(folder)

    def enter_selected(event=None):
        selected = listing.curselection()
        if selected:
            populate(entries[selected[0]])

    def select_and_process():
        selected = listing.curselection()
        chosen = [entries[i] for i in selected]
        if not chosen:
            messagebox.showinfo("请选择文件夹", "请在列表中选择一个或多个文件夹。", parent=win)
            return
        win.destroy()
        process(chosen)

    listing.bind("<Double-Button-1>", enter_selected)
    path_entry.bind("<Return>", lambda event: populate())
    controls = tk.Frame(win)
    controls.pack(fill="x", padx=10, pady=(0, 10))
    tk.Button(controls, text="上一级", command=lambda: populate(Path(current.get()).parent)).pack(side="left")
    tk.Label(controls, text="可用 Ctrl/Shift 多选；双击文件夹进入。路径框也可粘贴路径。").pack(side="left", padx=10)
    tk.Button(controls, text="处理选中的文件夹", command=select_and_process).pack(side="right")
    populate()


def pick_archives():
    selected = filedialog.askopenfilenames(title="批量选择 ZIP 压缩包", filetypes=[("ZIP 压缩包", "*.zip"), ("所有文件", "*.*")])
    if selected:
        process([Path(x) for x in selected])


def process(sources):
    results, errors = [], []
    for source in sources:
        try:
            count = create_pdf(source)
            results.append(f"{source.name}: {count} 张图片" if count else f"{source.name}: 未找到 .webp 图片")
        except Exception as exc:
            errors.append(f"{source.name}: {exc}")
    summary = "\n".join(results + (["", "处理失败："] + errors if errors else []))
    if results and not errors:
        messagebox.showinfo("处理完成", summary + f"\n\nPDF 已保存到：\n{OUTPUT}")
    else:
        messagebox.showwarning("处理结果", summary + f"\n\n输出文件夹：\n{OUTPUT}")


def run():
    root = tk.Tk()
    root.title("WebP 图片合并为 PDF")
    root.geometry("430x290")
    root.resizable(False, False)
    tk.Label(root, text="WebP 图片合并为 PDF", font=("Microsoft YaHei UI", 16, "bold")).pack(pady=(24, 8))
    tk.Label(root, text="可批量选择文件夹或 ZIP 压缩包，结果保存到 output。", wraplength=380).pack(pady=(0, 14))
    tk.Button(root, text="选择一个图片文件夹", width=28, command=pick_folder).pack(pady=4)
    tk.Button(root, text="批量选择图片文件夹", width=28, command=pick_folders).pack(pady=4)
    tk.Button(root, text="批量选择 ZIP 压缩包", width=28, command=pick_archives).pack(pady=5)
    tk.Button(root, text="快速打开 output 文件夹", width=28, command=open_output).pack(pady=5)
    root.mainloop()

if __name__ == "__main__":
    run()
