# ui/app.py

import sys
import os
from pathlib import Path

# ─── Make project root importable ─────────────────────────────────────────────
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend import db, parser, algorithms
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# ─── Page configuration ──────────────────────────────────────────────────────
st.set_page_config(page_title="Receipt Dashboard", layout="wide")

# ─── Ensure upload folder exists ─────────────────────────────────────────────
upload_folder = Path("sample_receipts")
upload_folder.mkdir(parents=True, exist_ok=True)

# ─── Initialize processed_files in session state ────────────────────────────
if "processed_files" not in st.session_state:
    st.session_state.processed_files = set()

# ─── Sidebar: Upload receipts ─────────────────────────────────────────────────
st.sidebar.title("Upload receipt / bill")
files = st.sidebar.file_uploader(
    "Choose files (.jpg, .png, .pdf, .txt)",
    type=["jpg", "png", "pdf", "txt"],
    accept_multiple_files=True
)
if files:
    for f in files:
        if f.name in st.session_state.processed_files:
            continue
        dest = upload_folder / f.name
        dest.write_bytes(f.getbuffer())
        rec = parser.parse_receipt(dest)
        with db.SessionLocal() as sess:
            sess.add(db.ReceiptORM(**rec.dict()))
            sess.commit()
        st.session_state.processed_files.add(f.name)
    st.sidebar.success("Uploaded & parsed ✔")

# ─── Sidebar: Filters ─────────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.subheader("Filters")
kw = st.sidebar.text_input("Vendor contains")
min_amt = st.sidebar.number_input("Min amount", value=0.0)
max_amt = st.sidebar.number_input("Max amount", value=1e6)
sd = st.sidebar.date_input("Start date")
ed = st.sidebar.date_input("End date")

# ─── Sidebar: Sorting ─────────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.subheader("Sort")
sort_field = st.sidebar.selectbox("Field", ["date", "amount", "vendor"])
order = st.sidebar.radio("Order", ["Ascending", "Descending"])

# ─── Load all receipts from the database ───────────────────────────────────────
with db.SessionLocal() as sess:
    rows = sess.query(db.ReceiptORM).all()

# Stash full set of DB IDs for deletion logic
all_db_ids = {r.id for r in rows}

# Build list of (id, Receipt) for in-memory operations
entries = [
    (r.id,
     parser.Receipt(
         vendor=r.vendor,
         date=r.date,
         amount=r.amount,
         category=r.category
     ))
    for r in rows
]

# ─── Apply filters ────────────────────────────────────────────────────────────
filtered = entries
if kw:
    filtered = [e for e in filtered if kw.lower() in e[1].vendor.lower()]
filtered = [e for e in filtered if min_amt <= e[1].amount <= max_amt]
filtered = [e for e in filtered if sd <= e[1].date <= ed]

# ─── Apply sorting via custom merge_sort ──────────────────────────────────────
def entry_key(e):
    return getattr(e[1], sort_field)

filtered = algorithms.merge_sort(filtered, key=entry_key)
if order == "Descending":
    filtered.reverse()

# ─── Build DataFrame for UI ───────────────────────────────────────────────────
data = [
    {"id": id_, "vendor": rec.vendor, "date": rec.date,
     "amount": rec.amount, "category": rec.category or ""}
    for id_, rec in filtered
]
df = pd.DataFrame(data)

# ─── Editable grid & deletion logic ───────────────────────────────────────────
st.header("All receipts")
edited = st.data_editor(df, num_rows="dynamic", use_container_width=True)

if st.button("Save manual edits"):
    kept_ids = set(edited["id"].tolist())
    to_delete = all_db_ids - kept_ids

    with db.SessionLocal() as sess:
        for rid in to_delete:
            rec = sess.get(db.ReceiptORM, rid)
            if rec:
                sess.delete(rec)
        for _, row in edited.iterrows():
            rec = sess.get(db.ReceiptORM, int(row["id"]))
            rec.vendor   = row["vendor"]
            rec.date     = row["date"]
            rec.amount   = row["amount"]
            rec.category = row["category"] or None
        sess.commit()

    st.success(f"Deleted {len(to_delete)} rows and updated {len(kept_ids)} rows.")

# ─── Export buttons (safe drop of 'id') ────────────────────────────────────────
export_df = edited.copy()
if "id" in export_df.columns:
    export_df = export_df.drop(columns=["id"])

csv_out  = export_df.to_csv(index=False)
json_out = export_df.to_json(orient="records", date_format="iso")

st.download_button("⬇️ Download CSV",  csv_out,  "receipts.csv",  "text/csv")
st.download_button("⬇️ Download JSON", json_out, "receipts.json", "application/json")

# ─── Statistics & charts ─────────────────────────────────────────────────────
if not edited.empty:
    recs = [
        parser.Receipt(
            vendor=r["vendor"],
            date=r["date"],
            amount=r["amount"],
            category=r["category"] or None
        )
        for _, r in edited.iterrows()
    ]

    st.subheader("Spending statistics")
    st.write(algorithms.stats(recs))

    st.subheader("Receipt Count by Vendor")
    vc = edited["vendor"].value_counts()
    fig1, ax1 = plt.subplots()
    vc.plot(kind="barh", ax=ax1)
    ax1.set_xlabel("Number of receipts")
    ax1.xaxis.set_major_locator(mtick.MaxNLocator(integer=True))
    st.pyplot(fig1)

    st.subheader("Spend Over Time (3‑Day MA)")
    ts = edited.groupby("date")["amount"].sum().sort_index()
    ma = ts.rolling(3, min_periods=1).mean()
    fig2, ax2 = plt.subplots()
    ax2.plot(ts.index, ts.values, marker="o", label="Daily Total")
    ax2.plot(ma.index, ma.values, linestyle="--", label="3‑Day MA")
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Amount")
    ax2.legend()
    plt.xticks(rotation=45)
    st.pyplot(fig2)
