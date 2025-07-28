"""
Upstream requirements
---------------------
```bash
pip install pymupdf scikit-learn numpy
```
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import fitz  # PyMuPDF
from sklearn.cluster import DBSCAN
import numpy as np

# Internal helpers


def _cluster_font_sizes(sizes: List[float]) -> List[Tuple[float, int]]:
    """Cluster similar font sizes using DBSCAN.

    Returns a list of tuples `(representative_size, cluster_size)` sorted by
    descending representative_size (i.e. biggest fonts first).
    """
    if not sizes:
        return []

    X = np.array(sizes).reshape(-1, 1)
    clustering = DBSCAN(eps=0.75, min_samples=3).fit(X)
    labels = clustering.labels_

    clusters: Dict[int, List[float]] = {}
    for size, label in zip(sizes, labels):
        clusters.setdefault(label, []).append(size)

    compact = [
        (max(v), len(v)) for label, v in clusters.items() if label != -1  # ignore noise
    ]
    compact.sort(reverse=True, key=lambda t: t[0])
    return compact

# Public API


def extract_outline(pdf_path: str | Path) -> Dict:
    """Return a dict with *title* and a flat **outline** list of headings.

    Example output
    --------------
    ```json
    {
      "title": "Sample Report",
      "outline": [
        {"level": "H1", "text": "Introduction", "page": 1},
        {"level": "H2", "text": "Background", "page": 2}
      ]
    }
    ```
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(path)

    with fitz.open(path) as doc:
        all_sizes: List[float] = []
        line_records: List[Tuple[int, float, float, float, str, int]] = []

        # Pass 1: collect font sizes & line metadata
        for page_no, page in enumerate(doc, start=1):
            blocks = page.get_text("dict")["blocks"]
            for b_idx, block in enumerate(blocks):
                for line in block.get("lines", []):
                    spans = line.get("spans", [])
                    if not spans:
                        continue
                    size = spans[0]["size"]
                    all_sizes.append(size)
                    text = "".join(span["text"] for span in spans).strip()
                    if text:
                        y0, x0 = line["bbox"][1], line["bbox"][0]
                        line_records.append((b_idx, y0, x0, size, text, page_no))

        # Determine hierarchy by clustering sizes
        clusters = _cluster_font_sizes(all_sizes)
        hierarchy = {}
        for rank, (rep_size, _count) in enumerate(clusters):
            hierarchy[rep_size] = (
                "Title",
                "H1",
                "H2",
                "H3",
                "H4",
            )[min(rank, 4)]

        # Build outline structure
        outline = {"title": None, "outline": []}
        for b_idx, y0, x0, size, text, page_no in sorted(line_records):
            rep_size = min(hierarchy, key=lambda s: abs(s - size))
            level = hierarchy[rep_size]
            if level == "Title" and not outline["title"]:
                outline["title"] = text
            elif level != "Title":
                outline["outline"].append({"level": level, "text": text, "page": page_no})

        # Fallback title resolution
        if not outline["title"]:
            meta_title = doc.metadata.get("title")
            outline["title"] = meta_title or (
                outline["outline"][0]["text"] if outline["outline"] else "Untitled"
            )

    return outline

# CLI entry point



def _cli():
    if len(sys.argv) < 2:
        print("Usage: python outline.py <pdf_path> [output.json]", file=sys.stderr)
        sys.exit(1)

    pdf_path = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        result = extract_outline(pdf_path)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    dumped = json.dumps(result, indent=2, ensure_ascii=False)
    if out_path:
        Path(out_path).write_text(dumped, encoding="utf-8")
    else:
        print(dumped)


if __name__ == "__main__":
    _cli()
