import os
import fitz  # PyMuPDF
import jsonlines
import re

PDF_DIR = "../data"
OUT_DIR = "../processed_chunks"
os.makedirs(OUT_DIR, exist_ok=True)

MAX_CHUNK_LENGTH = 1000  # karakter bazlı sınır (isteğe göre ayarlanabilir)


def split_long_chunk(madde_text, madde_title, source, page_number, chunk_id):
    sub_chunks = []
    current_lines = []
    char_count = 0

    lines = madde_text.split("\n")
    for line in lines:
        if (
            re.match(r"^[a-zçğıöşü]\)", line.strip())  # alt madde a), b), c) gibi
            or re.match(r"^\d+\)", line.strip())       # ya da 1), 2) gibi
        ) and char_count > MAX_CHUNK_LENGTH:
            # uzunluk sınırını aştıysak, chunk'ı kaydet
            sub_chunks.append({
                "text": madde_title + "\n" + "\n".join(current_lines),
                "source": source,
                "page_number": page_number,
                "chunk_id": chunk_id
            })
            chunk_id += 1
            current_lines = [line]
            char_count = len(line)
        else:
            current_lines.append(line)
            char_count += len(line)

    # son kalan kısmı da ekle
    if current_lines:
        sub_chunks.append({
            "text": madde_title + "\n" + "\n".join(current_lines),
            "source": source,
            "page_number": page_number,
            "chunk_id": chunk_id
        })

    return sub_chunks


def extract_chunks_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    chunks = []
    current_lines = []
    current_page = None
    chunk_id = 0
    current_madde_title = ""

    for page_index in range(len(doc)):
        page = doc.load_page(page_index)
        lines = page.get_text().splitlines()

        for line in lines:
            text = line.strip()
            if not text:
                continue

            if text.startswith("MADDE"):
                # önceki maddeyi kaydet
                if current_lines:
                    full_text = "\n".join(current_lines)
                    if len(full_text) > MAX_CHUNK_LENGTH:
                        chunks += split_long_chunk(
                            full_text, current_madde_title,
                            os.path.basename(pdf_path), current_page, chunk_id)
                        chunk_id = chunks[-1]["chunk_id"] + 1
                    else:
                        chunks.append({
                            "text": current_madde_title + "\n" + full_text,
                            "source": os.path.basename(pdf_path),
                            "page_number": current_page,
                            "chunk_id": chunk_id
                        })
                        chunk_id += 1

                # yeni madde başlat
                current_lines = []
                current_page = page_index + 1
                current_madde_title = text
            else:
                if current_lines is not None:
                    current_lines.append(text)

    # son maddeyi de ekle
    if current_lines:
        full_text = "\n".join(current_lines)
        if len(full_text) > MAX_CHUNK_LENGTH:
            chunks += split_long_chunk(
                full_text, current_madde_title,
                os.path.basename(pdf_path), current_page, chunk_id)
        else:
            chunks.append({
                "text": current_madde_title + "\n" + full_text,
                "source": os.path.basename(pdf_path),
                "page_number": current_page,
                "chunk_id": chunk_id
            })

    return chunks


def main():
    for fname in os.listdir(PDF_DIR):
        if not fname.lower().endswith(".pdf"):
            continue
        path = os.path.join(PDF_DIR, fname)
        chunks = extract_chunks_from_pdf(path)
        out_path = os.path.join(OUT_DIR, fname.replace(".pdf", ".jsonl"))
        with jsonlines.open(out_path, mode="w") as writer:
            writer.write_all(chunks)
        print(f"✅ Processed {fname}: {len(chunks)} chunks")

if __name__ == "__main__":
    main()
