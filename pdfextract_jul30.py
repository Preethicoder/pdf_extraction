import asyncio
import os
import json
import fitz  # PyMuPDF
import pdfplumber
import camelot
import pytesseract
from pdf2image import convert_from_path
from unstructured.partition.pdf import partition_pdf


def extract_images_from_pdf(file_path, output_folder):
    """
    Extract all embedded images from the PDF and save them as PNG files.

    Args:
        file_path (str): Path to the PDF file.
        output_folder (str): Folder where images will be saved.

    Returns:
        list: List of saved image file paths.
    """
    os.makedirs(output_folder, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    image_paths = []

    pdf_doc = fitz.open(file_path)
    for page_num, page in enumerate(pdf_doc, start=1):
        images = page.get_images(full=True)
        for img_index, img in enumerate(images, start=1):
            xref = img[0]
            pix = fitz.Pixmap(pdf_doc, xref)

            if pix.n < 5:  # GRAY or RGB
                img_path = os.path.join(output_folder, f"{base_name}_page{page_num}_img{img_index}.png")
                pix.save(img_path)
            else:  # CMYK: convert to RGB first
                pix = fitz.Pixmap(fitz.csRGB, pix)
                img_path = os.path.join(output_folder, f"{base_name}_page{page_num}_img{img_index}.png")
                pix.save(img_path)

            image_paths.append(img_path)

    return image_paths


def _ocr_text(pdf_path):
    """
    Perform OCR on PDF by converting pages to images and extracting text.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        str: Extracted text from OCR.
    """
    images = convert_from_path(pdf_path)
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img)
    return text


def save_txt(text, output_path):
    """
    Save plain text to a file.

    Args:
        text (str): Text content to save.
        output_path (str): File path to save the text.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)


def save_csv_camelot(dataframes, output_path):
    """
    Save multiple Camelot DataFrames as CSV with table separators.

    Args:
        dataframes (list): List of pandas DataFrames.
        output_path (str): File path to save CSV.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        for idx, df in enumerate(dataframes):
            f.write(f"--- Table {idx + 1} ---\n")
            f.write(df.to_csv(index=False))
            f.write("\n")


def save_json_camelot(dataframes, output_path):
    """
    Save multiple Camelot DataFrames as a JSON array.

    Args:
        dataframes (list): List of pandas DataFrames.
        output_path (str): File path to save JSON.
    """
    all_data = [df.to_dict(orient="records") for df in dataframes]
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2)


def extract_from_pdf(file_path, method="auto", output_folder="extracted_output"):
    """
    Extract content from PDF using various methods.

    Args:
        file_path (str): Path to the PDF file.
        method (str): Extraction method: auto, csv, json, txt, excel, unstructured.
        output_folder (str): Folder to save extracted outputs.

    Returns:
        str: Success message with saved file path(s).

    Raises:
        ValueError: If no content found or invalid method.
    """
    os.makedirs(output_folder, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(file_path))[0]

    all_tables_camelot = []
    full_text_pdfplumber = ""
    image_paths = []
    pages_count = 0

    # Extract text using pdfplumber
    try:
        with pdfplumber.open(file_path) as pdf:
            pages_count = len(pdf.pages)
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text_pdfplumber += text + "\n"
    except Exception as e:
        print(f"Warning: Text extraction with pdfplumber failed: {e}")

    # Extract images using PyMuPDF
    try:
        image_paths = extract_images_from_pdf(file_path, output_folder)
        if image_paths:
            print(f"🖼️ Extracted {len(image_paths)} images: {image_paths}")
    except Exception as e:
        print(f"Warning: Image extraction failed: {e}")

    # Extract tables using Camelot
    try:
        tables = camelot.read_pdf(file_path, flavor="stream", pages="all")
        if not tables:
            tables = camelot.read_pdf(file_path, flavor="lattice", pages="all")
        for table in tables:
            all_tables_camelot.append(table.df)
    except Exception as e:
        print(f"Warning: Camelot table extraction failed: {e}")

    # Summary info to print after extraction
    def print_summary():
        print("\n=== Extraction Summary ===")
        print(f"PDF file: {file_path}")
        print(f"Pages processed: {pages_count}")
        print(f"Tables found: {len(all_tables_camelot)}")
        print(f"Images saved: {len(image_paths)}")
        print("==========================\n")

    # Choose output based on method
    if method == "csv":
        if all_tables_camelot:
            output_path = os.path.join(output_folder, f"{base_name}_tables.csv")
            save_csv_camelot(all_tables_camelot, output_path)
            print_summary()
            return f"✅ CSV saved to: {output_path}"
        else:
            raise ValueError("❌ No tables found for CSV export using Camelot.")

    elif method == "json":
        if all_tables_camelot:
            output_path = os.path.join(output_folder, f"{base_name}_tables.json")
            save_json_camelot(all_tables_camelot, output_path)
            print_summary()
            return f"✅ JSON saved to: {output_path}"
        else:
            raise ValueError("❌ No tables found for JSON export using Camelot.")

    elif method == "txt":
        if full_text_pdfplumber.strip():
            output_path = os.path.join(output_folder, f"{base_name}.txt")
            save_txt(full_text_pdfplumber, output_path)
            print_summary()
            return f"✅ Text saved to: {output_path}"
        else:
            ocr_text = _ocr_text(file_path)
            output_path = os.path.join(output_folder, f"{base_name}_ocr.txt")
            save_txt(ocr_text, output_path)
            print_summary()
            return f"✅ OCR text saved to: {output_path}"

    elif method == "excel":
        if all_tables_camelot:
            output_messages = []
            for i, df in enumerate(all_tables_camelot):
                excel_file = os.path.join(output_folder, f"{base_name}_table_{i + 1}.xlsx")
                df.to_excel(excel_file, index=False)
                output_messages.append(f"Saved table {i + 1} to {excel_file}")
            print_summary()
            return "✅ " + "\n✅ ".join(output_messages)
        else:
            raise ValueError("❌ No tables found for Excel export using Camelot.")

    elif method == "auto":
        if all_tables_camelot:
            output_messages = []
            for i, df in enumerate(all_tables_camelot):
                excel_file = os.path.join(output_folder, f"{base_name}_table_{i + 1}.xlsx")
                df.to_excel(excel_file, index=False)
                output_messages.append(f"Saved table {i + 1} to {excel_file}")
            print_summary()
            return "✅ Auto-detected: Tables → Excel files saved:\n" + "\n".join(output_messages)

        elif full_text_pdfplumber.strip():
            output_path = os.path.join(output_folder, f"{base_name}.txt")
            save_txt(full_text_pdfplumber, output_path)
            print_summary()
            return f"✅ Auto-detected: Text → TXT saved to: {output_path}"

        else:
            ocr_text = _ocr_text(file_path)
            if ocr_text.strip():
                output_path = os.path.join(output_folder, f"{base_name}_ocr.txt")
                save_txt(ocr_text, output_path)
                print_summary()
                return f"✅ Auto-detected: OCR text saved to: {output_path}"
            else:
                try:
                    elements = partition_pdf(file_path, strategy="fast")
                    structured_text = "\n\n".join(
                        f"[{el.category}] {el.text.strip()}" for el in elements if el.text
                    )
                    if structured_text.strip():
                        output_path = os.path.join(output_folder, f"{base_name}_structured.txt")
                        save_txt(structured_text, output_path)
                        print_summary()
                        return f"✅ Auto-detected: Structured parsing (unstructured) → saved to: {output_path}"
                    else:
                        raise ValueError("❌ No content found in PDF even with unstructured parsing.")
                except Exception as e:
                    raise ValueError(f"❌ Final fallback failed: {e}")

    elif method == "unstructured":
        elements = partition_pdf(file_path, strategy="fast")
        structured_text = "\n\n".join(f"[{el.category}] {el.text.strip()}" for el in elements if el.text)
        if structured_text.strip():
            output_path = os.path.join(output_folder, f"{base_name}_structured.txt")
            save_txt(structured_text, output_path)
            print_summary()
            return f"✅ Unstructured text saved to: {output_path}"
        else:
            raise ValueError("❌ No content found in PDF using unstructured method.")

    else:
        raise ValueError("❌ Invalid method. Choose from: auto, csv, json, txt, excel, unstructured.")


async def process_pdf_async(file_path, method="auto", output_folder="extracted_output"):
    loop= asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        extract_from_pdf,
        file_path, method, output_folder  # pass arguments
    )
    print(result)  # show summary after completion
    return result



async def main():
    pdf_files = [
        "./sample_pdf/arztbrief_innere_medizin.pdf",
        "./sample_pdf/gesamtes LV.pdf",
        "./sample_pdf/scansmpl.pdf",
        "./sample_pdf/Laborbefund.pdf"
    ]

    tasks = [process_pdf_async(file,method="auto") for file in pdf_files]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
