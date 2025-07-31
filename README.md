# 📄 PDF Extraction Tool

This project is a Python-based tool to extract content from both **text-based** and **scanned** PDF files. It supports:

- Text extraction from digital PDFs
- OCR-based extraction from scanned PDFs (with table recognition)
- Detection of tables (even borderless ones) using PaddleOCR
- Saving extracted data in formats: `.txt`, `.csv`, `.xlsx`, `.png`
- Asynchronous processing of multiple PDF files
- Summary report generation after each run

---

## 🚀 Features

- ✅ Automatically detects whether PDF is text-based or scanned
- 📄 Extracts raw text and structured content
- 📊 Recognizes tables and saves them in CSV/Excel format
- 🖼️ Extracts embedded images (for scanned PDFs)
- 📋 Summary report includes pages processed, tables found, images saved
- ⚡ Asynchronous mode for handling large-scale, multi-user input

---

## 🛠️ Installation

Create a virtual environment and install the dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

---
##  📈 Output Format
Extracted text: .txt

Extracted tables: .csv or .xlsx (one file per table)

Extracted images: .png

Summary report printed to console


