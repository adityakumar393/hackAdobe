# PDF‑Outline‑Extractor

**Team Aazad Parindey – Adobe India Hackathon 2025**  
Aditya Kumar & Rai Chirag Kumar, National Institute of Technology Patna

A fast, single‑pass Python utility that generates a logical outline (Title, H1–H4) from PDF documents, even when the source file lacks bookmarks or uses complex, multi‑column layouts. The script can be used directly or installed as a library.

---

## 1  Overview

Technical documentation, research papers and white papers often ship without a usable bookmark tree, making navigation difficult. `PDF‑Outline‑Extractor` addresses this by analysing font metrics, clustering heading sizes, and producing a clean JSON outline in one pass over the document.

---

## 2  Key Features

| Category | Description |
| -------- | ----------- |
| Single‑pass processing | Streams each page once, collecting font statistics and text concurrently. |
| Automatic heading detection | Clusters font sizes with DBSCAN, mapping the largest cluster to body text and larger clusters to Title / H1–H4. |
| Column‑aware ordering | Sorts by block, vertical position, then horizontal position, preserving reading order in multi‑column PDFs. |
| Robust fall‑backs | If no suitable title font is found, the tool falls back to PDF metadata or the first visible line. |
| Library and CLI usage | Import `extract_outline()` from Python code or run `python outline.py <file.pdf>` to output JSON on the command line. |

---

## 3  Installation

### 3.1 Prerequisites
* Python 3.8 or later
* PyMuPDF
* scikit‑learn
* NumPy


## 4  Quick Start

### 4.1 Command‑line Interface
```bash
python outline.py Report.pdf            # prints JSON to stdout
python outline.py Report.pdf outline.json  # writes JSON to file
```

### 4.2 Library Usage
```python
from outline import extract_outline

outline = extract_outline("Report.pdf")
print(outline["title"])
for h in outline["outline"]:
    print(f"{h['level']} – page {h['page']}: {h['text']}")
```

Sample output:
```json
{
  "title": "Sample Report",
  "outline": [
    {"level": "H1", "text": "Introduction", "page": 1},
    {"level": "H2", "text": "Background", "page": 2}
  ]
}
```

---

## 5  Performance

| Document | Pages | Execution Time* |
| -------- | ----- | --------------- |
| Two‑column academic journal | 24 | 1.2 s |
| Technical manual | 300 | 9.7 s |

*Measured on an Apple M1 system running Python 3.11. Times include file I/O.

---


