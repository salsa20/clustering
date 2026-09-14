
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(
    page_title="RFM Analysis untuk Bisnis",
    page_icon="📊",
    layout="wide"
)

st.title("📊 RFM Analysis untuk Segmentasi Pelanggan")
st.caption("Materi sederhana RFM Analysis dan kaitannya dengan Power BI sebagai tools dashboard.")

tab1, tab2, tab3 = st.tabs([
    "📘 Materi RFM",
    "🧮 Simulasi RFM",
    "📈 Implementasi di Power BI"
])

# ======================================================
# TAB 1 - MATERI
# ======================================================
with tab1:
    st.header("1. Apa itu RFM Analysis?")
    st.markdown("""
**RFM Analysis** adalah metode segmentasi pelanggan berdasarkan perilaku transaksi pelanggan.

RFM terdiri dari:

- **Recency (R)** → seberapa baru pelanggan terakhir melakukan transaksi.
- **Frequency (F)** → seberapa sering pelanggan melakukan transaksi.
- **Monetary (M)** → seberapa besar total nilai transaksi pelanggan.

Tujuan utama RFM adalah membantu perusahaan memahami pelanggan mana yang paling aktif,
paling loyal, bernilai tinggi, atau mulai tidak aktif.
""")

    st.info("""
**Contoh kasus bisnis:**  
Sebuah toko online memiliki ribuan pelanggan. Manajemen tidak ingin memberikan promosi
yang sama kepada semua pelanggan. Dengan RFM, perusahaan dapat membedakan pelanggan
yang sangat loyal, pelanggan potensial, serta pelanggan yang mulai tidak aktif.
Hasil segmentasi ini dapat digunakan untuk menentukan strategi promosi yang lebih tepat.
""")

    st.header("2. Konsep RFM")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader("Recency")
        st.write("""
Mengukur jumlah hari sejak transaksi terakhir pelanggan.

Semakin **kecil Recency**, semakin baru pelanggan melakukan transaksi.
""")

    with c2:
        st.subheader("Frequency")
        st.write("""
Mengukur jumlah transaksi pelanggan.

Semakin **besar Frequency**, semakin sering pelanggan bertransaksi.
""")

    with c3:
        st.subheader("Monetary")
        st.write("""
Mengukur total nilai transaksi pelanggan.

Semakin **besar Monetary**, semakin tinggi nilai pelanggan bagi bisnis.
""")

    st.header("3. Contoh Interpretasi")

    contoh = pd.DataFrame({
        "Customer": ["A", "B", "C"],
        "Recency": [5, 40, 120],
        "Frequency": [12, 6, 2],
        "Monetary": [8_000_000, 3_500_000, 500_000],
        "Interpretasi": [
            "Sangat aktif dan bernilai tinggi",
            "Cukup aktif",
            "Mulai tidak aktif"
        ]
    })
    st.dataframe(contoh, use_container_width=True, hide_index=True)

    st.success("""
**Intinya:** pelanggan dengan Recency rendah, Frequency tinggi, dan Monetary tinggi
biasanya merupakan pelanggan terbaik.
""")

# ======================================================
# TAB 2 - SIMULASI
# ======================================================
with tab2:
    st.header("Simulasi Perhitungan RFM")

    st.markdown("""
Upload file transaksi dengan minimal kolom:

- `CustomerID`
- `InvoiceDate`
- `Amount`

Kolom `InvoiceNo` bersifat opsional. Jika tersedia, Frequency dihitung berdasarkan jumlah invoice unik.
Jika tidak tersedia, Frequency dihitung berdasarkan jumlah baris transaksi.
""")

    uploaded = st.file_uploader("Upload CSV transaksi", type=["csv"])

    if uploaded is not None:
        data = pd.read_csv(uploaded)
    else:
        np.random.seed(42)
        customers = [f"C{1000+i}" for i in range(30)]
        dates = pd.date_range("2026-01-01", "2026-06-30", freq="D")
        rows = []
        invoice_no = 1
        for customer in customers:
            for d in np.random.choice(dates, size=np.random.randint(2, 10), replace=False):
                rows.append({
                    "CustomerID": customer,
                    "InvoiceNo": f"INV{invoice_no:04d}",
                    "InvoiceDate": pd.Timestamp(d),
                    "Amount": np.random.randint(50_000, 1_500_000)
                })
                invoice_no += 1
        data = pd.DataFrame(rows)
        st.caption("Belum ada file yang di-upload. Aplikasi menggunakan data contoh.")

    required = {"CustomerID", "InvoiceDate", "Amount"}
    if not required.issubset(data.columns):
        st.error("File harus memiliki kolom CustomerID, InvoiceDate, dan Amount.")
        st.stop()

    data["InvoiceDate"] = pd.to_datetime(data["InvoiceDate"], errors="coerce")
    data["Amount"] = pd.to_numeric(data["Amount"], errors="coerce")
    data = data.dropna(subset=["CustomerID", "InvoiceDate", "Amount"])

    st.subheader("Data Transaksi")
    st.dataframe(data.head(20), use_container_width=True, hide_index=True)

    reference_date = data["InvoiceDate"].max() + pd.Timedelta(days=1)

    if "InvoiceNo" in data.columns:
        frequency = ("InvoiceNo", "nunique")
    else:
        frequency = ("InvoiceDate", "count")

    rfm = data.groupby("CustomerID").agg(
        Recency=("InvoiceDate", lambda x: (reference_date - x.max()).days),
        Frequency=frequency,
        Monetary=("Amount", "sum")
    ).reset_index()

    # Robust percentile scoring 1-5
    def score_high_good(series):
        pct = series.rank(method="average", pct=True)
        return np.ceil(pct * 5).clip(1, 5).astype(int)

    def score_low_good(series):
        pct = series.rank(method="average", pct=True, ascending=False)
        return np.ceil(pct * 5).clip(1, 5).astype(int)

    rfm["R_Score"] = score_low_good(rfm["Recency"])
    rfm["F_Score"] = score_high_good(rfm["Frequency"])
    rfm["M_Score"] = score_high_good(rfm["Monetary"])
    rfm["RFM_Score"] = (
        rfm["R_Score"].astype(str) +
        rfm["F_Score"].astype(str) +
        rfm["M_Score"].astype(str)
    )

    def segment(row):
        r, f, m = row["R_Score"], row["F_Score"], row["M_Score"]

        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"
        elif r >= 3 and f >= 4:
            return "Loyal Customers"
        elif r >= 4 and f <= 3:
            return "Potential Loyalist"
        elif r <= 2 and f >= 3:
            return "At Risk"
        elif r <= 2 and f <= 2:
            return "Hibernating"
        else:
            return "Regular Customers"

    rfm["Segment"] = rfm.apply(segment, axis=1)

    st.subheader("Hasil RFM")
    st.dataframe(rfm, use_container_width=True, hide_index=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Jumlah Pelanggan", len(rfm))
    c2.metric("Rata-rata Frequency", f"{rfm['Frequency'].mean():.1f}")
    c3.metric("Total Monetary", f"Rp{rfm['Monetary'].sum():,.0f}".replace(",", "."))

    st.subheader("Distribusi Segmentasi Pelanggan")

    seg = (
        rfm["Segment"]
        .value_counts()
        .rename_axis("Segment")
        .reset_index(name="Jumlah")
    )

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(seg["Segment"], seg["Jumlah"])
    ax.set_ylabel("Jumlah Pelanggan")
    ax.set_xlabel("Segment")
    ax.set_title("Distribusi Segmentasi RFM")
    ax.tick_params(axis="x", rotation=25)
    st.pyplot(fig, clear_figure=True)

    dominant_segment = seg.iloc[0]["Segment"]
    dominant_count = int(seg.iloc[0]["Jumlah"])

    st.markdown("#### Interpretasi")
    st.write(
        f"Segmen terbesar pada data saat ini adalah **{dominant_segment}** "
        f"dengan **{dominant_count} pelanggan**. "
        "Informasi ini dapat digunakan untuk menentukan fokus strategi pemasaran."
    )

    st.subheader("Contoh Strategi per Segmen")

    strategi = pd.DataFrame({
        "Segment": [
            "Champions",
            "Loyal Customers",
            "Potential Loyalist",
            "At Risk",
            "Hibernating",
            "Regular Customers"
        ],
        "Strategi": [
            "Reward, loyalty program, early access produk",
            "Cross-selling dan program loyalitas",
            "Dorong repeat order dengan promo personal",
            "Reactivation campaign dan reminder",
            "Win-back campaign atau survei penyebab churn",
            "Promo reguler dan edukasi produk"
        ]
    })
    st.dataframe(strategi, use_container_width=True, hide_index=True)

    csv = rfm.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download hasil RFM untuk Power BI",
        data=csv,
        file_name="rfm_customer_segment.csv",
        mime="text/csv"
    )

# ======================================================
# TAB 3 - POWER BI
# ======================================================
with tab3:
    st.header("RFM Analysis dengan Power BI")

    st.markdown("""
Setelah proses RFM selesai, hasilnya dapat diekspor ke CSV lalu digunakan sebagai
**data source di Power BI**.

Power BI berfungsi sebagai tools visualisasi dan dashboard sehingga hasil segmentasi
RFM lebih mudah dipahami oleh manajemen.
""")

    st.subheader("Alur Sederhana")

    st.code(
"""Data Transaksi
      ↓
Python / RFM Analysis
      ↓
RFM Customer Segment.csv
      ↓
Power BI
      ↓
Dashboard Segmentasi Pelanggan""",
        language="text"
    )

    st.subheader("Visual yang Disarankan di Power BI")

    dashboard = pd.DataFrame({
        "Visual Power BI": [
            "Card",
            "Donut / Bar Chart",
            "Scatter Plot",
            "Table",
            "Slicer"
        ],
        "Isi": [
            "Total pelanggan, total monetary, average frequency",
            "Jumlah pelanggan per segment RFM",
            "Frequency vs Monetary",
            "CustomerID, R, F, M, RFM Score, Segment",
            "Filter Segment, R Score, F Score, M Score"
        ]
    })
    st.dataframe(dashboard, use_container_width=True, hide_index=True)

    st.subheader("Contoh Layout Dashboard")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Customer", "1.250")
    c2.metric("Champions", "215")
    c3.metric("At Risk", "175")

    st.markdown("""
Di bawah kartu KPI, dashboard dapat menampilkan:

1. **Bar Chart** → jumlah pelanggan berdasarkan segment.
2. **Scatter Plot** → hubungan Frequency dan Monetary.
3. **Customer Table** → detail pelanggan dan nilai RFM.
4. **Slicer** → filter berdasarkan segment atau score.

### Manfaat untuk Bisnis
Dashboard RFM membantu manajemen menjawab pertanyaan seperti:

- Siapa pelanggan terbaik?
- Pelanggan mana yang perlu dipertahankan?
- Siapa yang mulai berisiko tidak aktif?
- Segmen mana yang menghasilkan nilai transaksi terbesar?
- Kepada siapa promosi sebaiknya diberikan?
""")

    st.info("""
**Power BI tidak harus menghitung seluruh RFM dari awal.**
Pendekatan yang sederhana untuk pembelajaran adalah melakukan proses scoring dan segmentasi
dengan Python, kemudian menggunakan Power BI untuk visualisasi, filtering, dan monitoring dashboard.
""")
