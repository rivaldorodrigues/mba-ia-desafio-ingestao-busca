# pypdf

**Package**: `pypdf`
**Docs**: https://pypdf.readthedocs.io/en/stable/
**Version used**: `>=6.14.2`

Pure-Python PDF library for reading, splitting, merging, and extracting text and metadata from PDF files.

Used directly (via `PdfReader`) or indirectly through LangChain's `PyPDFLoader`.

---

## Basic usage

### Read a PDF

```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")

print(f"Total pages: {len(reader.pages)}")
print(f"Metadata: {reader.metadata}")
```

### Extract text from a single page

```python
page = reader.pages[0]
text = page.extract_text()
print(text)
```

### Extract text from all pages

```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")
full_text = ""

for page in reader.pages:
    full_text += page.extract_text()

print(full_text)
```

---

## extract_text() options

```python
page.extract_text(
    orientations=(0, 90, 180, 270),  # which text orientations to include
    space_width=200.0,  # default space width when not found in font
    extraction_mode="plain",  # "plain" (default) or "layout"
)
```

### Layout-preserving extraction

Use `extraction_mode="layout"` to preserve the rendered horizontal/vertical layout of the page.

```python
# Preserve layout (whitespace matches rendered PDF)
text = page.extract_text(extraction_mode="layout")

# Preserve horizontal spacing, remove excess blank lines
text = page.extract_text(extraction_mode="layout", layout_mode_space_vertically=False)

# Adjust horizontal spacing weight
text = page.extract_text(extraction_mode="layout", layout_mode_scale_weight=1.0)

# Include rotated text (excluded by default in layout mode)
text = page.extract_text(extraction_mode="layout", layout_mode_strip_rotated=False)
```

---

## Metadata

```python
reader = PdfReader("document.pdf")
meta = reader.metadata

print(meta.title)
print(meta.author)
print(meta.subject)
print(meta.creator)
print(meta.producer)
print(meta.creation_date)
```

---

## Custom visitor — extract from a specific region

Use a visitor function to filter text by position (e.g., skip headers/footers).

```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")
page = reader.pages[0]

parts = []


def visitor_body(text, cm, tm, font_dict, font_size):
    y = tm[5]  # vertical position
    if 50 < y < 720:  # skip header (y > 720) and footer (y < 50)
        parts.append(text)


page.extract_text(visitor_text=visitor_body)
body_text = "".join(parts)
```

---

## Password-protected PDFs

```python
reader = PdfReader("protected.pdf")

if reader.is_encrypted:
    reader.decrypt("password123")

text = reader.pages[0].extract_text()
```

---

## Integration with LangChain

`PyPDFLoader` from `langchain-community` wraps `pypdf` automatically.

```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("document.pdf")
documents = loader.load()
# Returns list[Document], one Document per page
# document.page_content = extracted text
# document.metadata = {"source": "document.pdf", "page": 0}
```

### Load + split in one step

```python
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

loader = PyPDFLoader("document.pdf")
pages = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.split_documents(pages)
print(f"Split into {len(chunks)} chunks")
```

---

## Common gotchas

| Issue | Cause | Solution |
|-------|-------|----------|
| Empty text from `extract_text()` | PDF uses scanned images | Use an OCR tool (e.g., `pytesseract`) |
| Garbled text | Non-standard encoding | Try `extraction_mode="layout"` |
| Missing spaces | `space_width` too high | Lower `space_width` (e.g., `100.0`) |
| Wrong order | Complex multi-column layout | Use visitor to parse by coordinates |
