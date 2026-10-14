
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
st.caption("Modul interaktif RFM Score, Customer Lifetime Value (CLV), dan Power BI.")

tab1, tab2, tab3, tab4 = st.tabs([
    "📘 Materi RFM",
    "🧮 Simulasi RFM",
    "📈 Implementasi di Power BI",
    "💰 Materi & Simulasi CLV"
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

    st.header("4. Rumus Perhitungan RFM")
    st.latex(r"R_i = T_{acuan} - \max(T_{transaksi,i})")
    st.markdown("**R (Recency)** = selisih hari antara tanggal acuan analisis dan tanggal transaksi terakhir pelanggan *i*. Nilai lebih kecil berarti pelanggan lebih baru bertransaksi. Pada aplikasi ini, tanggal acuan = satu hari setelah tanggal transaksi terbaru dalam dataset.")
    st.latex(r"F_i = \operatorname{COUNT\_DISTINCT}(InvoiceNo_i)")
    st.markdown("**F (Frequency)** = jumlah invoice berbeda milik pelanggan *i*. Jika `InvoiceNo` tidak tersedia, aplikasi menghitung jumlah baris transaksi, sehingga satu baris diasumsikan satu transaksi.")
    st.latex(r"M_i = \sum_{j=1}^{n_i} Amount_{ij}")
    st.markdown("**M (Monetary)** = total nilai `Amount` seluruh transaksi pelanggan *i*. Satuan mengikuti dataset; bukan otomatis rupiah.")

    st.header("5. Rumus RFM Score (Skala 1–5)")
    st.markdown("Aplikasi menggunakan **peringkat persentil (percentile rank)**, bukan batas kuintil tetap. Pelanggan dengan nilai sama mendapat peringkat rata-rata sehingga skornya sama.")
    st.latex(r"P_i = \frac{\operatorname{rank}_{average}(x_i)}{N}")
    st.latex(r"Score_i = \min(5,\max(1,\lceil 5P_i \rceil))")
    st.markdown("**Keterangan:** `N` = jumlah pelanggan; `rank_average` = rata-rata urutan nilai yang sama; `P` = posisi persentil (0–1); `⌈ ⌉` = pembulatan ke atas. Untuk **F dan M**, peringkat diurutkan dari nilai kecil menuju besar. Untuk **R**, peringkat dibalik: Recency yang lebih kecil memperoleh skor lebih tinggi.")
    st.latex(r"RFM_{kode} = concat(R_{score},F_{score},M_{score})")
    st.latex(r"RFM_{total} = R_{score}+F_{score}+M_{score}")
    st.markdown("**Contoh:** pelanggan dengan skor R=5, F=4, M=3 memiliki **kode RFM `543`** dan **skor total 12 dari 15**. Kode `543` bukan angka lima ratus empat puluh tiga dan tidak digunakan untuk operasi penjumlahan.")
    st.info("Skor 5 menandakan posisi relatif tinggi dibanding pelanggan lain pada dataset saat ini. Pada kumpulan data dengan banyak nilai sama, tidak semua skor 1–5 harus muncul. Segmentasi adalah aturan bisnis ilustratif, bukan klasifikasi universal.")

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
        data = pd.read_csv(uploaded, sep=None, engine="python", encoding="utf-8-sig")
        data.columns = data.columns.str.strip()
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

    data["InvoiceDate"] = pd.to_datetime(data["InvoiceDate"], errors="coerce", dayfirst=True)
    data["Amount"] = pd.to_numeric(data["Amount"], errors="coerce")
    data = data.dropna(subset=["CustomerID", "InvoiceDate", "Amount"])

    if data.empty:
        st.error("Tidak ada baris transaksi valid setelah pembersihan data. Periksa format tanggal dan Amount.")
        st.stop()

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
    rfm["RFM_Total"] = rfm["R_Score"] + rfm["F_Score"] + rfm["M_Score"]
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
    st.caption("RFM_Score adalah kode tiga digit (R,F,M); RFM_Total adalah penjumlahan tiga skor, rentang 3–15. Skor dihitung relatif terhadap pelanggan pada data unggahan.")
    with st.expander("🔎 Lihat contoh cara menghitung RFM Score dari data"):
        contoh_rfm = rfm[["CustomerID", "Recency", "Frequency", "Monetary", "R_Score", "F_Score", "M_Score", "RFM_Score", "RFM_Total"]].head(5)
        st.dataframe(contoh_rfm, use_container_width=True, hide_index=True)
        st.markdown("R: semakin kecil hari semakin baik; F: semakin banyak transaksi semakin baik; M: semakin besar total nilai transaksi semakin baik. Peringkat persentil masing-masing diubah menjadi skor 1–5.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Jumlah Pelanggan", len(rfm))
    c2.metric("Rata-rata Frequency", f"{rfm['Frequency'].mean():.1f}")
    c3.metric("Total Monetary (satuan asli data)", f"{rfm['Monetary'].sum():,.2f}")

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

# ======================================================
# TAB 4 - CLV
# ======================================================
with tab4:
    st.header("Customer Lifetime Value (CLV)")
    st.markdown("**Customer Lifetime Value** adalah perkiraan kontribusi nilai finansial seorang pelanggan sepanjang masa hubungan pelanggan dengan bisnis. RFM menggambarkan **perilaku historis**, sedangkan CLV memperkirakan **nilai selama horizon hubungan pelanggan** berdasarkan asumsi.")
    st.subheader("1. Rumus dasar CLV")
    st.latex(r"AOV = \frac{Total\ Revenue}{Jumlah\ Transaksi}")
    st.latex(r"Frekuensi\ Tahunan = \frac{Jumlah\ Transaksi}{Lama\ Observasi\ (tahun)}")
    st.latex(r"CLV_{revenue} = AOV \times Frekuensi\ Tahunan \times Lifetime\ (tahun)")
    st.latex(r"CLV_{margin} = CLV_{revenue} \times Margin\ Kontribusi")
    st.markdown("""
**Keterangan rumus:**
- **AOV (Average Order Value):** rata-rata nominal transaksi per invoice atau per baris transaksi jika invoice tidak ada.
- **Frekuensi tahunan:** perkiraan jumlah pembelian dalam satu tahun; dihitung dengan mengekstrapolasi transaksi selama periode observasi.
- **Lifetime:** perkiraan berapa tahun pelanggan terus membeli (asumsi pengguna, **tidak dapat disimpulkan langsung** dari dataset transaksi).
- **Margin kontribusi:** proporsi pendapatan setelah biaya variabel. Contoh 30% berarti 0,30. Ini bukan otomatis margin laba bersih.
- **CLV revenue:** perkiraan pendapatan kotor seumur hidup; **CLV margin:** perkiraan kontribusi seumur hidup sebelum biaya akuisisi/retensi, diskonto, dan biaya tetap.
""")
    st.info("Contoh hitung: AOV Rp30.000 × 12 pembelian/tahun × 3 tahun = CLV revenue Rp1.080.000. Jika margin kontribusi 30%, CLV margin = Rp324.000. Ini ilustrasi, bukan hasil dari dataset kopi.")
    st.subheader("2. Simulasi CLV berdasarkan data yang diunggah")
    st.warning("**Perhatian:** apabila `Amount` pada dataset merupakan angka normalisasi atau bukan nilai uang aktual, seluruh CLV hanya berupa indeks dalam satuan data, BUKAN nilai rupiah. Untuk CLV rupiah, unggah nominal transaksi sebenarnya.")
    a, b = st.columns(2)
    with a:
        lifetime = st.number_input("Asumsi lifetime pelanggan (tahun)", min_value=0.1, max_value=30.0, value=3.0, step=0.5, help="Perkiraan masa hubungan pelanggan yang ditetapkan untuk simulasi.")
    with b:
        margin_pct = st.slider("Asumsi margin kontribusi (%)", min_value=0, max_value=100, value=30, step=5)
    start_date = data["InvoiceDate"].min()
    end_date = data["InvoiceDate"].max()
    observed_days = max((end_date - start_date).days + 1, 1)
    observed_years = observed_days / 365.25
    clv_df = rfm[["CustomerID", "Frequency", "Monetary", "Segment", "RFM_Score", "RFM_Total"]].copy()
    clv_df["AOV"] = clv_df["Monetary"] / clv_df["Frequency"].replace(0, np.nan)
    clv_df["Frekuensi_Tahunan"] = clv_df["Frequency"] / observed_years
    clv_df["CLV_Revenue_Estimasi"] = clv_df["AOV"] * clv_df["Frekuensi_Tahunan"] * lifetime
    clv_df["CLV_Margin_Estimasi"] = clv_df["CLV_Revenue_Estimasi"] * margin_pct / 100
    st.caption(f"Periode observasi seluruh dataset: {start_date:%d-%m-%Y} sampai {end_date:%d-%m-%Y} ({observed_days} hari = {observed_years:.2f} tahun). Seluruh pelanggan memakai jendela observasi yang sama; hasil dapat bias untuk pelanggan yang baru bergabung.")
    metrics = st.columns(3)
    metrics[0].metric("Rata-rata CLV revenue (estimasi)", f"{clv_df['CLV_Revenue_Estimasi'].mean():,.2f}")
    metrics[1].metric("Rata-rata CLV margin (estimasi)", f"{clv_df['CLV_Margin_Estimasi'].mean():,.2f}")
    metrics[2].metric("Jumlah pelanggan", f"{len(clv_df):,}")
    st.dataframe(clv_df.round(3), use_container_width=True, hide_index=True)
    st.subheader("3. Contoh perhitungan seorang pelanggan")
    selected_customer = st.selectbox("Pilih CustomerID", options=clv_df["CustomerID"].astype(str).tolist())
    record = clv_df.loc[clv_df["CustomerID"].astype(str) == selected_customer].iloc[0]
    st.markdown(f"""**Pelanggan {selected_customer}**: total transaksi = **{int(record['Frequency'])}**, Monetary = **{record['Monetary']:,.3f}**.

AOV = {record['Monetary']:,.3f} ÷ {int(record['Frequency'])} = **{record['AOV']:,.3f}** satuan data/transaksi.

Frekuensi tahunan = {int(record['Frequency'])} ÷ {observed_years:.3f} = **{record['Frekuensi_Tahunan']:,.3f}** transaksi/tahun.

CLV revenue = {record['AOV']:,.3f} × {record['Frekuensi_Tahunan']:,.3f} × {lifetime:g} = **{record['CLV_Revenue_Estimasi']:,.3f}** satuan data.

CLV margin = {record['CLV_Revenue_Estimasi']:,.3f} × {margin_pct}% = **{record['CLV_Margin_Estimasi']:,.3f}** satuan data.""")
    st.subheader("4. RFM versus CLV untuk keputusan pemasaran")
    st.markdown("""- **RFM:** pelanggan mana yang baru membeli, sering membeli, dan memiliki belanja besar?
- **CLV:** berapa nilai jangka panjang yang *diperkirakan* jika asumsi frekuensi, lifetime, dan margin berlaku?
- **Contoh penggunaan:** prioritaskan layanan untuk pelanggan dengan skor RFM tinggi dan CLV margin tinggi; uji kampanye aktivasi pelanggan *At Risk* dengan nilai historis tinggi.

**Keterbatasan:** model CLV sederhana ini tidak memperkirakan churn, perubahan frekuensi beli, diskonto arus kas, biaya akuisisi (CAC), ataupun biaya retensi. Estimasinya bersifat edukatif, bukan prediksi CLV tervalidasi.
""")
    st.download_button("⬇️ Download hasil gabungan RFM & estimasi CLV untuk Power BI", data=clv_df.to_csv(index=False).encode("utf-8-sig"), file_name="rfm_clv_estimasi.csv", mime="text/csv")
