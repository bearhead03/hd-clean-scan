# hd-clean-scan

[中文](#中文) | [English](#english)

## 中文

hd-clean-scan 是一个把手机拍摄的纸质文件整理成高清 A4 PDF 的 Codex skill。它会校正拍摄角度，裁掉桌面和其他杂物，压平不均匀的光线，再根据文件类型加深文字，或保留彩色公章、签名和批注。每份 PDF 在交付前都会经过渲染检查，确认没有裁字、黑边、过曝或颜色丢失。它适合处理合同、票据、表格和手写笔记，但不会把普通放大包装成清晰度修复，也不会声称能恢复原图中不存在的细节。

使用示例：

```text
使用 $hd-clean-scan 把这张文档照片制作成高清净白扫描版 PDF。
```

## English

hd-clean-scan is a Codex skill for turning phone photos of paper documents into clean, high-resolution A4 PDFs. It corrects perspective, crops away the desk and other clutter, evens out uneven lighting, and either strengthens the text or keeps colored seals, signatures, and notes intact, depending on the document. Every PDF is rendered and checked before delivery for clipped content, dark borders, blown highlights, or lost color. It works well for contracts, receipts, forms, and handwritten notes, but it does not present ordinary upscaling as detail recovery or claim to restore information missing from the source photo.

Example:

```text
Use $hd-clean-scan to turn this document photo into a clean, high-resolution scanned PDF.
```

## Install

```bash
npx skills add bearhead03/hd-clean-scan -g -y
```

## Contents

- `SKILL.md`: workflow, quality rules, and usage guidance
- `scripts/scan_to_pdf.py`: perspective correction, clean-white processing, and A4 PDF generation
- `agents/openai.yaml`: skill metadata for Codex
