import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Fraktal Batik", layout="wide")

# ─────────────────────────── HEADER ───────────────────────────
st.title("🎨 Fraktal Batik – Julia Set Chaos")
st.markdown("**Proyek UAS – Kelompok 8** | Kalkulus Lanjut")
st.markdown("---")

# ─────────────────────────── FUNGSI ───────────────────────────
def julia_set(width=950, height=950, c=complex(-0.4, 0.6), max_iter=380):
    x = np.linspace(-1.85, 1.85, width)
    y = np.linspace(-1.85, 1.85, height)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    img = np.zeros((height, width), dtype=float)
    with np.errstate(over='ignore', invalid='ignore'):
        for _ in range(max_iter):
            Z = Z**2 + c
            mask = np.abs(Z) < 4
            img[mask] += 1
    return img / max_iter

def batik_transform(img, rotation=0, mirror=True):
    if mirror:
        img = np.fliplr(img)
    img = np.rot90(img, k=rotation // 90)
    return img

def render_to_buf(img, cmap, figsize=8, dpi=300, title=None):
    """Render img ke BytesIO PNG dan kembalikan (fig PNG bytes, matplotlib fig)."""
    fig, ax = plt.subplots(figsize=(figsize, figsize))
    ax.imshow(img, cmap=cmap, interpolation='bilinear')
    ax.axis('off')
    if title:
        ax.set_title(title, fontsize=8, pad=4)
    plt.tight_layout(pad=0)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight', dpi=dpi, pad_inches=0)
    buf.seek(0)
    return buf, fig

# ─────────────────────────── SESSION STATE ───────────────────────────
if "preset_results" not in st.session_state:
    st.session_state.preset_results = []   # list of (name, buf_bytes, fig)
if "free_results" not in st.session_state:
    st.session_state.free_results = []     # list of (title, buf_bytes, fig)

# ─────────────────────────── PRESET DETAIL ───────────────────────────
preset_patterns = {
    "🔴 Parang Merah Api":      (complex(0.1,   0.65),  'hot',      380, "Motif parang klasik dengan warna api membara"),
    "🟡 Kawung Emas":           (complex(-0.4,  0.6),   'copper',   400, "Motif kawung berkilau seperti emas"),
    "🔵 Lereng Biru Putih":     (complex(0.285, 0.01),  'plasma',   420, "Motif lereng biru muda bertekstur"),
    "🟠 Sidomukti Oranye":      (complex(-0.8,  0.156), 'inferno',  380, "Motif sidomukti dengan nuansa oranye"),
    "🟢 Truntum Hijau Zamrud":  (complex(-0.7,  0.27),  'viridis',  450, "Motif truntum halus warna zamrud"),
    "💜 Parang Kusumo Ungu":    (complex(0.355, 0.355), 'twilight', 380, "Motif parang kusumo elegan nuansa ungu"),
    "⚪ Ceplok Perak":          (complex(-0.4,  0.8),   'gray',     460, "Motif ceplok minimalis monokrom perak"),
    "🌈 Mega Mendung Prisma":   (complex(-0.1,  0.651), 'rainbow',  500, "Motif mega mendung spektrum warna penuh"),
}

# ─────────────────────────── SIDEBAR ───────────────────────────
st.sidebar.title("⚙️ Menu Utama")
mode = st.sidebar.radio(
    "Pilih Mode Generate",
    ["🖼️ Pola Batik Detail (Preset Kurasi)", "🎲 Pola Bebas (Jumlah Sesukamu)"],
    index=0
)
st.sidebar.markdown("---")

# ══════════════════════════════════════════════════
#  MODE 1 — PRESET DETAIL
# ══════════════════════════════════════════════════
if mode == "🖼️ Pola Batik Detail (Preset Kurasi)":

    st.header("🖼️ Pola Batik Detail – Preset Kurasi")
    st.markdown(
        "Pilih satu atau beberapa pola dari **8 preset** yang sudah dikurasi. "
        "Setiap pola dirender dengan resolusi & iterasi tinggi untuk hasil maksimal."
    )

    # ── Pilihan pola
    st.subheader("Pilih Pola")
    with st.expander("ℹ️ Pilih pola yang ingin di-generate", expanded=True):
        selected = []
        cols_check = st.columns(2)
        for idx, (name, (c, cmap, iters, desc)) in enumerate(preset_patterns.items()):
            with cols_check[idx % 2]:
                checked = st.checkbox(f"{name}", value=True, key=f"chk_{idx}")
                st.caption(f"*{desc}*")
                if checked:
                    selected.append((name, c, cmap, iters))

    # ── Kontrol kualitas
    st.subheader("Pengaturan Kualitas")
    col_q1, col_q2 = st.columns(2)
    with col_q1:
        resolution = st.select_slider(
            "Resolusi Gambar", options=[512, 700, 950, 1200], value=950,
            help="Resolusi lebih tinggi = lebih detail, tapi lebih lama"
        )
    with col_q2:
        iter_boost = st.slider(
            "Bonus Iterasi Tambahan", 0, 200, 0, step=50,
            help="Tambah iterasi di atas default tiap preset"
        )
    mirror_opt = st.checkbox("🪞 Aktifkan Efek Mirror (Simetri Batik)", value=True)
    rotate_opt = st.selectbox("🔄 Rotasi Global", [0, 90, 180, 270], index=0)

    # ── Tombol generate
    if selected:
        if st.button(f"🚀 Generate {len(selected)} Pola Batik", type="primary", use_container_width=True):
            results = []
            progress = st.progress(0, text="Memulai rendering…")
            for i, (name, c, cmap, base_iter) in enumerate(selected):
                total_iter = base_iter + iter_boost
                img = julia_set(resolution, resolution, c, total_iter)
                img = batik_transform(img, rotation=rotate_opt, mirror=mirror_opt)
                buf, fig = render_to_buf(img, cmap, figsize=8, dpi=300)
                results.append((name, buf.read(), fig))
                progress.progress((i + 1) / len(selected), text=f"Rendering {i+1}/{len(selected)}…")
            progress.empty()
            st.session_state.preset_results = results
            st.success(f"✅ {len(selected)} pola berhasil di-generate!")

    else:
        st.warning("⚠️ Pilih minimal satu pola terlebih dahulu.")

    # ── Tampilkan hasil (persisten via session_state)
    if st.session_state.preset_results:
        st.markdown("---")
        st.subheader("✨ Hasil Generate")
        cols_out = st.columns(2)
        for i, (name, png_bytes, fig) in enumerate(st.session_state.preset_results):
            with cols_out[i % 2]:
                st.subheader(name)
                st.pyplot(fig)
                st.download_button(
                    label=f"⬇️ Download {name}",
                    data=png_bytes,
                    file_name=f"batik_{name.replace(' ', '_')}.png",
                    mime="image/png",
                    key=f"dl_preset_{i}"
                )

# ══════════════════════════════════════════════════
#  MODE 2 — BEBAS TANPA BATAS
# ══════════════════════════════════════════════════
else:

    st.header("🎲 Pola Bebas – Jumlah Sesukamu")
    st.markdown(
        "Generate pola fraktal batik secara **acak** dalam jumlah **berapa pun** yang kamu mau. "
        "Tidak ada batas — semakin banyak, semakin beragam!"
    )

    st.subheader("Pengaturan")
    col_a, col_b = st.columns(2)
    with col_a:
        jumlah = st.number_input(
            "Jumlah Pola yang Ingin Di-generate",
            min_value=1, max_value=None, value=9, step=1,
            help="Masukkan angka berapa pun — tidak ada batas maksimal!"
        )
    with col_b:
        max_iter_free = st.slider(
            "Iterasi (Detail Pola)", min_value=100, max_value=800, value=350, step=50,
            help="Iterasi lebih besar = lebih detail, tapi lebih lama"
        )

    col_c, col_d = st.columns(2)
    with col_c:
        res_free = st.select_slider(
            "Resolusi", options=[256, 512, 700, 950], value=700
        )
    with col_d:
        kolom_tampil = st.selectbox("Jumlah Kolom Tampilan", [2, 3, 4, 5], index=1)

    with st.expander("🔧 Pengaturan Lanjutan – Rentang Parameter c (Opsional)"):
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            real_min = st.number_input("Real Min", value=-0.9, step=0.05, format="%.2f")
            real_max = st.number_input("Real Max", value=0.4,  step=0.05, format="%.2f")
        with col_r2:
            imag_min = st.number_input("Imag Min", value=-0.3, step=0.05, format="%.2f")
            imag_max = st.number_input("Imag Max", value=0.8,  step=0.05, format="%.2f")
        all_cmaps = st.multiselect(
            "Pilih Palet Warna",
            ['hot', 'copper', 'inferno', 'magma', 'plasma', 'viridis',
             'twilight', 'rainbow', 'gray', 'bone', 'spring', 'cool'],
            default=['hot', 'copper', 'inferno', 'magma']
        )
        if not all_cmaps:
            all_cmaps = ['hot', 'copper', 'inferno', 'magma']

    mirror_free = st.checkbox("🪞 Efek Mirror", value=True)

    # ── Tombol generate
    if st.button(f"🎲 Generate {int(jumlah)} Pola Acak", type="primary", use_container_width=True):
        n = int(jumlah)
        results = []
        progress = st.progress(0, text="Memulai rendering…")
        for i in range(n):
            real_part = np.random.uniform(real_min, real_max)
            imag_part = np.random.uniform(imag_min, imag_max)
            c    = complex(real_part, imag_part)
            cmap = np.random.choice(all_cmaps)
            rot  = int(np.random.choice([0, 90, 180, 270]))

            img = julia_set(res_free, res_free, c, max_iter_free)
            img = batik_transform(img, rotation=rot, mirror=mirror_free)
            title = f"Pola #{i+1}  c=({real_part:.3f}+{imag_part:.3f}j)"
            buf, fig = render_to_buf(img, cmap, figsize=6, dpi=200, title=title)
            results.append((title, buf.read(), fig))
            progress.progress((i + 1) / n, text=f"Rendering pola {i+1}/{n}…")

        progress.empty()
        st.session_state.free_results = results
        st.success(f"🎉 {n} pola fraktal batik berhasil di-generate!")
        st.balloons()

    # ── Tampilkan hasil (persisten via session_state)
    if st.session_state.free_results:
        st.markdown("---")
        st.subheader(f"✨ Hasil: {len(st.session_state.free_results)} Pola Fraktal Batik")
        grid_cols = st.columns(kolom_tampil)
        for i, (title, png_bytes, fig) in enumerate(st.session_state.free_results):
            with grid_cols[i % kolom_tampil]:
                st.pyplot(fig)
                st.download_button(
                    label=f"⬇️ Download #{i+1}",
                    data=png_bytes,
                    file_name=f"batik_acak_{i+1}.png",
                    mime="image/png",
                    key=f"dl_free_{i}"
                )

# ─────────────────────────── FOOTER ───────────────────────────
st.markdown("---")
st.caption(
    "💡 **Tips:** Mode Preset menghasilkan motif lebih mirip batik tradisional. "
    "Mode Bebas cocok untuk eksplorasi fraktal tanpa batas."
)