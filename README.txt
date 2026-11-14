WebP 图片合并为 PDF

双击“启动工具.cmd”打开图形界面。
- 选择一个图片文件夹：递归查找 .webp 图片并合并。
- 批量选择图片文件夹：在目录浏览窗口中用 Ctrl/Shift 多选文件夹；双击可进入目录，路径框支持粘贴路径。选中目录各生成一个 PDF。
- 批量选择 ZIP 压缩包：可一次选择多个 ZIP，每个压缩包各生成一个 PDF。
- 快速打开 output 文件夹：打开工具目录下的结果文件夹。

PDF 按路径或文件名排序，保存在本工具目录的 output 文件夹。当前支持 ZIP，不支持 RAR/7z。

需要 Python 3 和 Pillow。首次使用前运行：
  py -m pip install Pillow
