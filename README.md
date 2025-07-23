# Receipt Dashboard

## Objective

This project automates the tedious process of manually entering receipt and bill data, saving time and reducing errors. By uploading photos, scans, PDFs, or text files, you can:

- Extract structured fields (vendor, date, amount, category) through OCR and rule-based parsing
- Store validated records in a local SQLite database
- Interactively review, correct, filter, and explore your spending
- Export cleaned data for reporting or integration with other tools

For full project details and UI mockups, see **[ReceiptDashboard.pdf](https://drive.google.com/file/d/1HfXXxJRKP5jhHaoW57zxPOJylAVaWemz/view?usp=sharing)**.


---

## Problem Statement

Tracking expenses from paper or digital receipts often requires manual data entry, which is slow and error-prone. This tool solves that by automating extraction and providing an end-to-end workflow for ingestion, validation, storage, analysis, and export.

---

## Use Cases

- Small business expense tracking and reimbursement
- Personal budgeting and spending analysis
- Finance teams processing vendor invoices
- Any role that needs quick insights from heterogeneous receipt formats

---

## Project Structure & Architecture

```
receipt-app/
│
├── backend/                     # Processing and storage
│   ├── models.py        # Pydantic schemas and validation
│   ├── db.py            # SQLAlchemy ORM setup and SQLite engine
│   ├── parser.py        # OCR extraction and rule-based parsing
│   ├── algorithms.py    # Search, sort, and aggregation functions
│   └── __init__.py
│
├── ui/                          # User interface layer
│   └── app.py           # Streamlit dashboard
│
├── sample_receipts/      # Example files for local testing
│
├── receipts.db           # SQLite database generated at runtime
├── ReceiptDashboard.pdf  # Project specification and UI mockups
└── README.md             # This documentation
```

- **Backend**:
  - **Data ingestion**: Handles `.jpg`, `.png`, `.pdf`, `.txt`
  - **OCR & parsing**: Uses Tesseract + regex patterns
  - **Validation**: Pydantic models enforce types and non-negative amounts
  - **Storage**: ACID-compliant SQLite via SQLAlchemy ORM

- **Algorithms**:
  - **Searching**: Keyword-, range-, and date-based filters
  - **Sorting**: Custom merge sort for vendor, date, amount
  - **Aggregation**: Sum, mean, median, mode, frequency distributions

- **UI (Streamlit)**:
  - Upload, filtering, sorting controls in sidebar
  - Editable, deletable data grid with persistence
  - Export buttons for CSV and JSON
  - Visualizations: bar chart for vendor counts, time-series with moving average

---

## User Journey

1. **Start**: Activate Python environment and launch the dashboard with `streamlit run ui/app.py`.
2. **Upload**: Drag and drop or browse for receipt images/PDFs/text.
3. **Parse & Store**: Files are OCR’d, parsed, and saved to SQLite automatically.
4. **Filter & Sort**: Narrow down records by vendor keyword, amount range, and date window; choose sort field and order.
5. **Review & Edit**: Inline edit or delete any row; click **Save manual edits** to update the database.
6. **Export**: Download the cleaned dataset as CSV or JSON.
7. **Analyze**: View spending statistics and charts to gain insights.

---

## Setup & Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd receipt-app
   ```

2. **Install system dependencies**
   - **Tesseract-OCR**
     - Windows: download and install, then add `C:\Program Files\Tesseract-OCR` to `PATH`
     - macOS: `brew install tesseract`
     - Linux: `sudo apt install tesseract-ocr`
   - **Poppler** (for PDF conversion)
     - Windows: download the zip, add `poppler-*/bin` to `PATH`
     - macOS: `brew install poppler`
     - Linux: `sudo apt install poppler-utils`

3. **Create a Python virtual environment**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

4. **Install Python packages**
   ```bash
   pip install --upgrade pip
   pip install streamlit sqlalchemy pydantic pandas numpy matplotlib pillow pytesseract pdf2image python-magic python-dateutil
   ```

5. **Verify installations**
   ```bash
   tesseract -v
   pdftoppm -v
   ```

---

## Limitations

- **OCR Accuracy**: Depends on image quality and Tesseract’s limitations; handwriting or low-contrast scans may fail.
- **Rule-based Parsing**: May not cover all date or currency formats; rare formats could be misparsed.
- **Single-page PDFs**: Only the first page is processed; multi-page receipts require extension.
- **Currency Support**: Currently handles amounts without explicit currency conversion; multi-currency receipts are not supported.

---

## Assumptions

- Receipts contain at least one recognizable date and numeric amount.
- The highest numeric value on a receipt is the total amount.
- Vendor name appears on the first meaningful line of text.
- Categories can be heuristically assigned via vendor keywords.

---