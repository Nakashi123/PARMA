# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd, numpy as np
import matplotlib.pyplot as plt

# ===== 基本設定 =====
st.set_page_config(page_title="PERMAプロファイル", layout="centered")

BASE_FONT_PX = 19
H1_REM, H2_REM, H3_REM = 2.2, 1.9, 1.6
LINE_HEIGHT = 1.8
CARD_RADIUS_PX, CARD_PAD_REM = 12, 0.9
FONT_SCALE = 1.1

plt.rcParams.update({
    "font.size": int(13 * FONT_SCALE),
    "axes.titlesize": int(16 * FONT_SCALE),
    "axes.labelsize": int(14 * FONT_SCALE),
    "xtick.labelsize": int(12 * FONT_SCALE),
    "ytick.labelsize": int(12 * FONT_SCALE),
    "legend.fontsize": int(12 * FONT_SCALE),
    "font.sans-serif": [
        "Yu Gothic UI","Hiragino Kaku Gothic ProN","Meiryo",
        "Noto Sans JP","Noto Sans CJK JP","Helvetica","Arial","DejaVu Sans"
    ],
    "axes.unicode_minus": False,
})

# ===== CSS（印刷最適化 + セクション見切れ防止）=====
st.markdown(f"""
<style>
html, body, [class*="css"] {{
  font-size:{BASE_FONT_PX}px !important;
  line-height:{LINE_HEIGHT} !important;
  font-family:"Yu Gothic UI","Hiragino Kaku Gothic ProN","Meiryo","Noto Sans JP",sans-serif !important;
  color:#111 !important;
}}
h1 {{ font-size:{H1_REM}rem !important; font-weight:800; margin:0 0 .3rem 0; }}
h2 {{ font-size:{H2_REM}rem !important; font-weight:700; margin:.2rem 0 .4rem 0; }}
h3 {{ font-size:{H3_REM}rem !important; font-weight:700; margin:.1rem 0 .4rem 0; }}
.main-wrap {{ max-width: 860px; margin: 0 auto; }}

.section-card {{
  background:#fff; border:1px solid #e6e6e6; border-radius:{CARD_RADIUS_PX}px;
  padding:{CARD_PAD_REM}rem {CARD_PAD_REM+0.2}rem; margin:.6rem 0 .8rem 0;
  box-shadow:0 2px 6px rgba(0,0,0,.05);
  page-break-inside: avoid; break-inside: avoid;
}}
.section-title {{ border-bottom:2px solid #f0f0f0; padding-bottom:.25rem; margin-bottom:.45rem; }}

.force-break {{ break-after: page; page-break-after: always; height:0; margin:0; padding:0; }}

@media print {{
  @page {{ size: A4; margin: 13mm; }}
  html, body {{ zoom: 1; }}
  body, [class*="css"] {{ font-size: 16px !important; line-height: 1.55 !important; }}
  h1 {{ font-size: 1.9rem !important; }}
  h2 {{ font-size: 1.6rem !important; }}
  h3 {{ font-size: 1.3rem !important; }}
  .main-wrap {{ max-width: 720px; }}
  .section-card {{ margin:.45rem 0 .6rem 0; padding:.65rem .75rem; }}
  .stApp [data-testid="stToolbar"],
  .stApp [data-testid="stDecoration"],
  .stApp [data-testid="stStatusWidget"],
  .stApp [data-testid="stSidebar"],
  .stApp [data-testid="collapsedControl"] {{ display: none !important; }}
  .stApp {{ padding: 0 !important; }}
}}
</style>
""", unsafe_allow_html=True)

# ===== PERMA 定義 =====
perma_indices = {
    'Positive Emotion':[0,1,2],
    'Engagement':[3,4,5],
    'Relationships':[6,7,8],
    'Meaning':[9,10,11],
    'Accomplishment':[12,13,14],
}
perma_short_keys = ['P','E','R','M','A']
full_labels = {
    'P':'Pー前向きな気持ち（Positive Emotion）',
    'E':'Eー集中して取り組むこと（Engagement）',
    'R':'Rー人間関係（Relationships）',
    'M':'Mー意味づけ（Meaning）',
    'A':'Aー達成感（Accomplishment）',
}
descriptions = {
    'P':'楽しい気持ちや感謝、安心感など、気分の明るさや心のゆとりが感じられること。',
    'E':'物事に没頭し、時間を忘れて集中している感覚があること。',
    'R':'家族や友人、地域とのつながりを感じ、支え合えていること。',
    'M':'自分の人生に目的や価値を見いだし、「自分にとって大切なこと」に沿って生きていること。',
    'A':'目標に向かって取り組み、できた・やり遂げたという手応えがあること。',
}
colors = ['#D81B60','#E65100','#2E7D32','#1E88E5','#6A1B9A']

# ===== ユーティリティ =====
def compute_results(selected_row: pd.DataFrame):
    cols = [c for c in selected_row.columns if str(c).startswith("6_")]
    vals = pd.to_numeric(selected_row[cols].values.flatten(), errors='coerce')
    res = {}
    for k, idx in perma_indices.items():
        scores = [vals[i] for i in idx if i < len(vals) and not np.isnan(vals[i])]
        res[k] = float(np.mean(scores)) if scores else 0.0
    return res

def plot_radar(results):
    labels = list(results.keys())
    values = list(results.values())
    values += values[:1]
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    # ← 要求通り「今の1/2サイズ」程度に小型化
    fig, ax = plt.subplots(figsize=(2.0, 2.0), subplot_kw=dict(polar=True), dpi=220)
    for i in range(len(labels)):
        ax.plot([angles[i], angles[i+1]], [values[i], values[i+1]],
                color=colors[i], linewidth=1.4)
    ax.fill(angles, values, alpha=0.10, color="#888")
    ax.set_thetagrids(np.degrees(angles[:-1]), ['P','E','R','M','A'],
                      fontsize=9, fontweight='bold')
    ax.set_ylim(0, 10)
    ax.set_rticks([2, 6, 10])
    ax.tick_params(axis='y', labelsize=8)
    ax.grid(alpha=0.3, linewidth=0.8)
    fig.tight_layout(pad=0.15)
    st.pyplot(fig, use_container_width=False)

# ===== 画面本体 =====
st.markdown('<div class="main-wrap">', unsafe_allow_html=True)
st.title("PERMAプロファイル")
st.caption("※ 本ツールはスクリーニングであり医療的診断ではありません。")

# --- ID入力タブ（アップロード & 選択） ---
uploaded = st.file_uploader("Excel（.xlsx）をアップロード（左端=ID、6_1〜=スコア）", type="xlsx")

if uploaded:
    try:
        df = pd.read_excel(uploaded)
        id_list = df.iloc[:, 0].dropna().astype(str).tolist()
        sid = st.selectbox("IDを選んでください", options=id_list, index=0)
        selected_row = df[df.iloc[:, 0].astype(str) == sid]

        # === ページ切替コマンド（ここで改ページ） ===
        st.markdown('<div class="force-break"></div>', unsafe_allow_html=True)

        if selected_row.empty:
            st.warning("選択されたIDに該当する行がありません。")
        else:
            results = compute_results(selected_row)

            # ===== 同一ページ：レーダーチャート（右に説明） =====
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><h3>レーダーチャート</h3></div>', unsafe_allow_html=True)

            col1, col2 = st.columns([2, 3])
            with col1:
                plot_radar(results)
            with col2:
                st.markdown(
                    "この図は、しあわせを支える5つの要素（PERMA）の自己評価です。  \n"
                    "点数が高いほどその要素が生活のなかで満たされていることを示し、  \n"
                    "どこが強みで、どこに伸びしろがあるかが一目でわかります。"
                )
            st.markdown('</div>', unsafe_allow_html=True)

            # ===== 同一ページ：各要素の説明 =====
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><h3>各要素の説明</h3></div>', unsafe_allow_html=True)
            colA, colB = st.columns(2)
            with colA:
                for k in ['P', 'E', 'R']:
                    st.markdown(f"**{full_labels[k]}**：{descriptions[k]}")
            with colB:
                for k in ['M', 'A']:
                    st.markdown(f"**{full_labels[k]}**：{descriptions[k]}")
            st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"データ読み込み時にエラーが発生しました：{e}")
else:
    st.info("まずはExcel（.xlsx）をアップロードしてください。")

st.markdown('</div>', unsafe_allow_html=True)
