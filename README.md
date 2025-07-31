# 🧾 PDF Content Extractor

This project is a versatile Python utility designed to **extract text, tables, and images from PDF files** using a combination of libraries such as `pdfplumber`, `Camelot`, `PyMuPDF`, `Tesseract OCR`, and `Unstructured`. It supports **asynchronous batch processing** and multiple output formats (CSV, JSON, TXT, Excel).

---

## 📦 Features

- 🔍 Text extraction via `pdfplumber`, with fallback to `Tesseract OCR`
- 📸 Image extraction from embedded content using `PyMuPDF`
- 📊 Table extraction using `Camelot` (`stream` and `lattice` modes)
- 📁 Multi-format output: `.csv`, `.json`, `.txt`, `.xlsx`
- 🧠 Unstructured content extraction using `unstructured` as a fallback
- ⚡ Asynchronous processing for multiple PDFs

---

## 🚀 Quick Start

### 1. **Clone the repository**
```bash
git clone https://github.com/yourusername/pdf-extractor.git
cd pdf-extractor
