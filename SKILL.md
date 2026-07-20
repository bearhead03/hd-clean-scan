---
name: hd-clean-scan
description: Convert photographed paper documents into high-resolution clean-white A4 PDFs by correcting perspective, removing surrounding backgrounds, flattening uneven lighting, strengthening text, and preserving colored seals or signatures. Use for requests such as “扫描成电子版”, “高清净白扫描版”, “把这张文件照片转成 PDF”, photographed contracts, receipts, forms, handwritten notes, or similar JPEG/PNG document images.
---

# 高清净白扫描

把文档照片制作成标准 A4、300 DPI 的高清净白扫描 PDF。优先保留原始内容，不重新排版或改写文字。

## 工作流

1. 用图像查看工具检查原图原始分辨率。
2. 记录纸张四角坐标，顺序必须为左上、右上、右下、左下。坐标应略微位于纸张内侧，避免桌面和黑边；不得裁掉正文、印章、签名或边缘批注。
3. 选择模式：
   - 合同、证照、发票、有彩色公章或彩色批注：使用 `color`。
   - 纯黑白打印件或手写笔记：使用 `grayscale`。
   - 不确定时使用 `auto`，并在渲染后检查颜色是否正确保留。
4. 先调用 workspace dependency loader 取得 bundled Python 和 Poppler 路径；不要假定系统默认 `python` 已安装 `reportlab`。
5. 使用 bundled Python 运行 `scripts/scan_to_pdf.py`。
6. 用 Poppler 的实际 `pdftoppm` 可执行文件将最终 PDF 渲染成 PNG，按页面逐一检查。若包装命令不可用，从 bundled dependencies 下定位 `pdftoppm.exe`。发现裁切、黑边、模糊、过曝、文字断裂或印章褪色时，调整四角或处理参数后重跑。
7. 只交付通过视觉检查的最终 PDF。提示用户：应用内缩略预览可能偏模糊，应以下载后在 PDF 阅读器中的显示效果为准。

## 命令

```powershell
python scripts/scan_to_pdf.py `
  --input "C:\path\photo.jpg" `
  --output "C:\path\outputs\文件_高清净白扫描版.pdf" `
  --corners "120,130;1240,105;1195,1710;130,1640" `
  --mode color
```

`--corners` 接受原图像素坐标，格式为 `左上;右上;右下;左下`。如纸张充满整个画面且边缘无需裁切，可省略；脚本会使用完整图像。

## 质量标准

- 输出单页或逐页标准 A4 PDF，页面图像为 2480 × 3508 像素（300 DPI）。
- 纸张背景接近纯白，但不得因强行二值化损失细小文字、铅笔痕迹或浅色方格。
- 黑色文字清晰、连续，不出现明显锐化光晕。
- 彩色公章、签名和批注保持原色，不转黑、不褪色。
- 去除桌面、阴影、线缆和纸外背景；装订孔属于文档时可保留，若用户要求无边扫描则从安全内侧裁除。
- 不进行 OCR 重排，不擅自修改合同、签名、印章或手写内容。
- 原图分辨率决定上限；不要声称放大能恢复源图中不存在的细节。

## 多页文件

对每张照片分别生成经过检查的页面图像或单页 PDF，再使用 `pypdf` 按用户给定顺序合并。所有页面使用相同的 A4 尺寸和一致的净白强度。

## 依赖

优先使用 Codex bundled workspace Python；需要 `Pillow`、`numpy`、`reportlab`。视觉检查需要 Poppler 的 `pdftoppm`。
