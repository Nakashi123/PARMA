# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd, numpy as np
import matplotlib.pyplot as plt

# =========================
# 基本設定
# =========================
st.set_page_config(page_title="わらトレ　心の健康チェック", layout="centered")

plt.rcParams.update({
    "font.sans-serif": ["BIZ UDPGothic","Meiryo","Noto Sans JP"],
    "axes.unicode_minus": False,
    "font.size": 12,
})

# =========================
# カラーテーマ
# =========================
colors = {
    "P": "#F28B82",  # ピンク
    "E": "#FDD663",  # 黄色
    "R": "#81C995",  # 緑
    "M": "#AECBFA",  # 水色
    "A": "#F9AB00",  # オレンジ
}
theme = {
    "bg": "#FAFAFA",
    "card_bg": "#FFFFFF",
    "accent": "#4E73DF",
    "text": "#222",
    "bar_bg": "#EEF2FB"
}

# =========================
# CSSスタイル（帯見出し化＋レイアウト調整）
# =========================
st.markdown(f"""
<style>
html, body, [class*="css"] {{
  background-color:{theme['bg']};
  color:{theme['text']};
  font-family:"BIZ UDPGothic","Meiryo",sans-serif;
  line-height:1.8;
}}

.main-wrap {{ max-width:880px; margin:0 auto; }}

h1 {{
  text-align:center;
  color:#333;
  margin-top:0.4em;
  font-size:2rem;
  font-weight:800;
}}

.section-header {{
  background:{theme['bar_bg']};
  color:#333;
  font-weight:800;
  font-size:1.2rem;
  padding:.6rem 1rem;
  border-left:8px solid {theme['accent']};
  border-radius:6px;
  margin-top:1rem;
  margin-bottom:.8rem;
}}

.section-card {{
  background:{theme['card_bg']};
  border-radius:14px;
  box-shadow:0 2px 6px rgba(0,0,0,0.05);
  padding:1rem 1.2rem;
  margin:0.8rem 0;
}}

.color-label {{
  font-weight:bold;
  padding:2px 8px;
  border-radius:6px;
  color:white;
}}

div.block-container {{
  padding-top: 0.5rem !important;
  padding-bottom: 0.5rem !important;
}}

@media print {{
  @page {{
    size: A4;
    margin: 15mm;
  }}
  .page-break {{
    page-break-before: always;
  }}
}}
</style>
""", unsafe_allow_html=True)

# =========================
# データ定義
# =========================
perma_indices = {
    'P':[4,9,21],
    'E':[2,10,20],
    'R':[5,14,18],
    'M':[0,8,16],
    'A':[1,7,15],
}
extra_indices = {
    'ネガティブ感情':[6,13,19],
    '健康感':[3,12,17],
    '孤独感':[11],
    '幸福感':[22],
}

full_labels = {
    'P':'前向きな気持ち（Positive Emotion）',
    'E':'集中して取り組むこと（Engagement）',
    'R':'人とのつながり（Relationships）',
    'M':'生きがいや目的（Meaning）',
    'A':'達成感（Accomplishment）',
}
descriptions = {
    'P':'楽しい気持ちや感謝、安心感など、心のゆとりを感じることができています。',
    'E':'夢中で取り組む時間や没頭できる活動が生活の中にあります。',
    'R':'家族や友人、地域とのつながりを感じ、支え合えていることを示します。',
    'M':'自分の人生に目的や価値を見いだし、大切なことに沿って生きています。',
    'A':'目標に向かって取り組み、やり遂げた達成感を感じられています。',
}
tips = {
    'P':['感謝を込めた手紙を書く','その日の「良かったこと」を3つ書く'],
    'E':['自分の得意なことを活かす','小さな挑戦を設定して取り組む'],
    'R':['日常で小さな親切を行う','家族や友人に感謝を伝える'],
    'M':['自分の大切にしている価値を書き出す','過去の困難を乗り越えた経験を振り返る'],
    'A':['小さな目標を達成する習慣を作る','失敗も学びととらえる'],
}

# =========================
# 計算関数
# =========================
def compute_domain_avg(vals, idx_list):
    scores = [vals[i] for i in idx_list if i < len(vals) and not np.isnan(vals[i])]
    return float(np.mean(scores)) if scores else np.nan

def compute_results(selected_row: pd.DataFrame):
    cols = [c for c in selected_row.columns if str(c).startswith("6_")]
    vals = pd.to_numeric(selected_row[cols].values.flatten(), errors='coerce')
    perma_scores = {k: compute_domain_avg(vals, idx) for k, idx in perma_indices.items()}
    extras = {k: compute_domain_avg(vals, idx) for k, idx in extra_indices.items()}
    return perma_scores, extras

# =========================
# レーダーチャート
# =========================
def plot_radar(perma_scores):
    labels = list(perma_scores.keys())
    values = list(perma_scores.values())
    values += values[:1]
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(3.2,3.2), subplot_kw=dict(polar=True), dpi=160)
    ax.set_theta_offset(np.pi/2)
    ax.set_theta_direction(-1)
    for i, k in enumerate(labels):
        ax.plot([angles[i], angles[i+1]], [values[i], values[i+1]], color=colors[k], linewidth=2.3)
    ax.fill(angles, values, alpha=0.15, color="#888")

    for i, label in enumerate(labels):
        ax.text(angles[i], 10.5, label, color=colors[label], fontsize=11, fontweight='bold',
                ha='center', va='center')

    ax.set_ylim(0,10)
    ax.set_rticks([2,5,8])
    ax.grid(alpha=0.3)
    ax.set_xticklabels([])
    fig.tight_layout(pad=0.1)
    st.pyplot(fig)

# =========================
# Streamlit本体
# =========================
st.markdown('<div class="main-wrap">', unsafe_allow_html=True)
st.title("わらトレ　心の健康チェック")

uploaded = st.file_uploader("Excelファイル（ID列＋6_1〜6_23列）をアップロードしてください", type="xlsx")

# ---- 1ページ目 ----
if not uploaded:
    st.info("まずはExcelファイルをアップロードしてください。")
    st.stop()

df = pd.read_excel(uploaded)
id_list = df.iloc[:,0].dropna().astype(str).tolist()
sid = st.selectbox("IDを選んでください", options=id_list)
selected_row = df[df.iloc[:,0].astype(str)==sid]

if selected_row.empty:
    st.warning("選択されたIDが見つかりません。")
    st.stop()

# ---- ページ区切り ----
st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)

# ---- 2ページ目：チャート＋まとめ ----
st.markdown('<div class="section-header">PERMAバランスチャート・結果のまとめ</div>', unsafe_allow_html=True)
col_chart, col_summary = st.columns([1, 1.2])
with col_chart:
    plot_radar(compute_results(selected_row)[0])
with col_summary:
    perma_scores, extras = compute_results(selected_row)
    st.markdown("**0〜10点満点のうち、7点以上＝強み、4〜6点＝おおむね良好、3点以下＝サポートが必要**")
    for k,v in perma_scores.items():
        st.write(f"{k}（{full_labels[k]}）：{int(round(v))} 点")

st.markdown('<div class="section-header">各要素の説明</div>', unsafe_allow_html=True)
for k in ['P','E','R','M','A']:
    st.markdown(f"<span class='color-label' style='background:{colors[k]}'>{k}</span> **{full_labels[k]}**：{descriptions[k]}", unsafe_allow_html=True)

# ---- ページ区切り ----
st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)

# ---- 3ページ目：おすすめ＋補助指標＋注意 ----
st.markdown('<div class="section-header">あなたにおすすめな行動（例）</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    for k in ['P','E','R']:
        st.markdown(f"**{full_labels[k]}**", unsafe_allow_html=True)
        for t in tips[k]:
            st.markdown(f"- {t}")
with col2:
    for k in ['M','A']:
        st.markdown(f"**{full_labels[k]}**", unsafe_allow_html=True)
        for t in tips[k]:
            st.markdown(f"- {t}")

# 横並び：補助指標＋大切なこと
st.markdown('<div class="section-header">さいごに</div>', unsafe_allow_html=True)
colL, colR = st.columns([0.9, 1.1])
with colL:
    st.markdown("### 補助指標（参考）")
    for k,v in extras.items():
        if not np.isnan(v):
            st.write(f"{k}：{int(round(v))} 点")
with colR:
    st.markdown("### これらの結果を受け取るうえで大切なこと")
    st.markdown("""
    - 結果は“良い・悪い”ではなく、あなたの**今の状態や環境**を表しています。  
    - 改善のためには、**無理せず小さな一歩**から始めましょう（例：1日5分の散歩）。  
    - このチェックは**医療的診断ではありません**。気分の落ち込みが続く場合は、専門職にご相談ください。
    """)

st.markdown('</div>', unsafe_allow_html=True)
