WebP 图片合并为 PDF

双击“启动工具.cmd”，选择 ZIP 压缩包或包含 .webp 图片的文件夹。会递归查找图片，并按路径/文件名排序合并。生成的 PDF 位于本工具目录下的 output 文件夹中。

目前压缩包格式支持 ZIP；RAR/7z 暂不支持。

需要 Python 3 和 Pillow。首次使用前运行：
  py -m pip install Pillow
