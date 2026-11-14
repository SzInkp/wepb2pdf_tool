from pathlib import Path
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageOps

BASE = Path(__file__).resolve().parent


def collect_webp(source: Path):
    if source.is_dir():
        return sorted((p for p in source.rglob("*") if p.is_file() and p.suffix.lower() == ".webp"), key=lambda p: str(p.relative_to(source)).lower())
    if source.suffix.lower() == ".zip":
        # Read directly from ZIP; no extraction to disk is needed.
        return sorted((n for n in zipfile.ZipFile(source).namelist() if not n.endswith("/") and Path(n).suffix.lower() == ".webp"), key=str.lower)
    return []


def create_pdf(source: Path, output: Path):
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
        output.mkdir(exist_ok=True)
        target = output / f"{source.stem if source.is_file() else source.name}.pdf"
        pages[0].save(target, "PDF", save_all=True, append_images=pages[1:], resolution=150)
        return len(pages)
    finally:
        for page in pages:
            page.close()
        if archive:
            archive.close()


def run():
    root = tk.Tk()
    root.withdraw()
    choice = messagebox.askyesnocancel("选择来源", "是：选择压缩包（目前支持 ZIP）\n否：选择文件夹", parent=root)
    if choice is None:
        root.destroy()
        return
    if choice:
        selected = filedialog.askopenfilename(title="选择 ZIP 压缩包", filetypes=[("ZIP 压缩包", "*.zip"), ("所有文件", "*.*")])
    else:
        selected = filedialog.askdirectory(title="选择包含 WebP 图片的文件夹")
    if not selected:
        root.destroy()
        return
    source = Path(selected)
    try:
        count = create_pdf(source, BASE / "output")
        if count:
            messagebox.showinfo("完成", f"已合并 {count} 张图片：\n{BASE / 'output' / (source.stem if source.is_file() else source.name)}.pdf", parent=root)
        else:
            messagebox.showinfo("没有找到图片", "所选文件夹或 ZIP 压缩包中没有 .webp 文件。", parent=root)
    except zipfile.BadZipFile:
        messagebox.showerror("无法读取压缩包", "该文件不是有效的 ZIP 压缩包。", parent=root)
    except Exception as exc:
        messagebox.showerror("转换失败", f"处理时出错：\n{exc}", parent=root)
    finally:
        root.destroy()

if __name__ == "__main__":
    run()
