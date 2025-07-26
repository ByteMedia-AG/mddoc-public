# PDF/A Embedded Data Specification

This document describes how serialized metadata and related files are embedded in the generated PDF/A documents using the `doc_pdfa` function.

## Embedded Attachments

Each PDF/A file generated via `doc_pdfa(doc_id)` includes the following embedded attachments:

### 1. Serialized Metadata

Two variants of the document metadata are embedded:

- `data.json`: The document and its related files serialized as JSON Lines (`jsonl`)
- `data.yaml`: The same data serialized in YAML format

Both files include:
- The `Doc` instance (title, text, metadata)
- All associated `File` instances (`doc.files.all()`)

These attachments allow external systems to extract structured data directly from the PDF.

### 2. File Attachments

All files associated with the document (`doc.files.all()`) are embedded in the PDF/A. Each file is attached using the following filename convention:

```
file.<file_id>.<file_uuid>.<file_extension>
```

Where:

- `<file_id>`: The database ID of the `File` object
- `<file_uuid>`: The unique UUID of the file
- `<file_extension>`: The original file extension (e.g., `pdf`, `jpg`, `zip`)

#### Example:

If a `File` object has:
- `id = 42`
- `uuid = 123e4567-e89b-12d3-a456-426614174000`
- `extension = "xml"`

Then the attached filename will be:

```
file.42.123e4567-e89b-12d3-a456-426614174000.xml
```

## Usage

To extract the embedded metadata or files from the PDF:

- Open the PDF using a tool that supports file attachments (e.g. Adobe Acrobat, `pdfdetach`, `pikepdf`)
- Look for:
  - `data.json` or `data.yaml` for document metadata
  - `file.*.*.*` entries for original file attachments

## Compliance

The resulting file is validated against PDF/A-3 standards. All embedded attachments are compliant with ISO 19005-3 requirements.