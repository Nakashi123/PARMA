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
extra_colors = {
    "こころのつらさ": "#9FA8DA",   # やや青み
    "からだの調子":   "#80CBC4",   # 緑系
    "ひとりぼっち感": "#FFAB91", # オレンジ系
    "しあわせ感":     "#FFE082", # 黄色系
}
theme = {
    "bg": "#FAFAFA",
    "card_bg": "#FFFFFF",
    "accent": "#4E73DF",
    "text": "#222",
    "bar_bg": "#EEF2FB"
}

# =========================
# CSSスタイル
# =========================
st.markdown(f"""
<style>
html, body, [class*="css"] {{
  background-color:{theme['bg']};
  color:{theme['text']};
  font-family:"BIZ UDPGothic","Meiryo",sans-serif;
  line-height:1.6;
}}

div.block-container {{
  padding-top: 0.5rem !important;
  padding-bottom: 0.5rem !important;
}}

.main-wrap {{
  max-width:880px;
  margin:0 auto;
}}

h1 {{
  text-align:center;
  color:#333;
  margin-top:0.4em;
  font-size:1.9rem;
  font-weight:800;
}}

.section-header {{
  background:{theme['bar_bg']};
  color:#333;
  font-weight:800;
  font-size:1.1rem;
  padding:.5rem .9rem;
  border-left:8px solid {theme['accent']};
  border-radius:6px;
  margin-top:0.9rem;
  margin-bottom:.4rem;
}}

.section-caption {{
  font-size:0.9rem;
  color:#555;
  margin-bottom:0.3rem;
}}

.result-info {{
  display:flex;
  justify-content:space-between;
  align-items:center;
  font-size:0.9rem;
  margin-bottom:0.4rem;
}}

.result-info span {{
  margin-right:1.0rem;
}}

.factor-grid {{
  display:grid;
  gap:0.55rem;
  margin-top:0.3rem;
}}

.factor-grid.perma {{
  grid-template-columns:repeat(3, minmax(0, 1fr));
}}

.factor-grid.extra {{
  grid-template-columns:repeat(2, minmax(0, 1fr));
}}

@media (max-width: 900px) {{
  .factor-grid.perma {{
    grid-template-columns:repeat(2, minmax(0, 1fr));
  }}
}}

.factor-card {{
  background:{theme['card_bg']};
  border-radius:12px;
  padding:0.55rem 0.7rem 0.5rem;
  box-shadow:0 1px 3px rgba(0,0,0,.08);
  min-height:100px;
  display:flex;
  flex-direction:column;
  justify-content:space-between;
}}

.factor-title {{
  font-size:0.9rem;
  font-weight:700;
}}

.factor-sub {{
  font-size:0.75rem;
  color:#555;
  margin-top:0.1rem;
}}

.factor-score {{
  font-size:1.6rem;
  font-weight:800;
  margin-top:0.1rem;
}}

.factor-score span {{
  font-size:0.8rem;
  margin-left:0.1rem;
}}

.factor-level {{
  font-size:0.8rem;
  font-weight:700;
  padding:2px 7px;
  border-radius:999px;
  display:inline-block;
  margin-top:0.2rem;
}}

.level-high {{
  background:#E3F2FD;
  color:#1565C0;
}}

.level-mid {{
  background:#FFF8E1;
  color:#EF6C00;
}}

.level-low {{
  background:#FFEBEE;
  color:#C62828;
}}

.level-na {{
  background:#ECEFF1;
  color:#455A64;
}}

.note-box {{
  font-size:0.85rem;
  background:#FFFDE7;
  border-radius:8px;
  padding:0.55rem 0.7rem;
  margin-top:0.4rem;
  border:1px solid #FFE082;
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
    'こころのつらさ':[6,13,19],
    'からだの調子':[3,12,17],
    'ひとりぼっち感':[11],
    'しあわせ感':[22],
}

full_labels = {
    'P':'前向きな気持ち',
    'E':'集中して取り組むこと',
    'R':'人とのつながり',
    'M':'生きがいや目的',
    'A':'達成感',
}

# （説明や行動提案は、別ページを作る場合用に残しておく）
descriptions = {
    'P':'楽しい気持ちや感謝、安心感、心のゆとりを感じることができています。',
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

def judge_level(score: float):
    """スコアから一言コメントとレベルクラスを返す"""
    if np.isnan(score):
        return "未測定", "level-na"
    if score >= 7:
        return "とても良い", "level-high"
    if score >= 4:
        return "おおむね良好", "level-mid"
    return "少し低め", "level-low"

# =========================
# シンプル棒グラフ（PERMAバランス）
# =========================
def plot_histogram(perma_scores):
    labels = list(perma_scores.keys())  # P, E, R, M, A
    values = list(perma_scores.values())
    colors_list = [colors[k] for k in labels]

    fig, ax = plt.subplots(figsize=(4,3), dpi=160)
    bars = ax.bar(labels, values, color=colors_list, alpha=0.9)

    for bar, val in zip(bars, values):
        if np.isnan(val):
            continue
        ax.text(bar.get_x() + bar.get_width()/2, val + 0.25, f"{val:.1f}",
                ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax.set_ylim(0, 10)
    ax.set_title("PERMA のバランス", fontsize=11, fontweight='bold')
    ax.set_ylabel("")
    ax.grid(axis='y', alpha=0.25)
    fig.tight_layout()
    st.pyplot(fig)

# =========================
# カードHTML生成
# =========================
def render_perma_cards(perma_scores):
    cards_html = '<div class="factor-grid perma">'
    for k in ['P','E','R','M','A']:
        s = perma_scores.get(k, np.nan)
        label, lv_class = judge_level(s)
        score_txt = f"{s:.1f}" if not np.isnan(s) else "-"
        cards_html += f"""
        <div class="factor-card" style="border-top:5px solid {colors[k]};">
          <div>
            <div class="factor-title">{k}　{full_labels[k]}</div>
          </div>
          <div>
            <div class="factor-score">{score_txt}<span>/10</span></div>
            <div class="factor-level {lv_class}">{label}</div>
          </div>
        </div>
        """
    cards_html += "</div>"
    st.markdown(cards_html, unsafe_allow_html=True)

def render_extra_cards(extras):
    cards_html = '<div class="factor-grid extra">'
    for name, s in extras.items():
        label, lv_class = judge_level(s)
        score_txt = f"{s:.1f}" if not np.isnan(s) else "-"
        color = extra_colors.get(name, "#B0BEC5")
        cards_html += f"""
        <div class="factor-card" style="border-top:5px solid {color};">
          <div>
            <div class="factor-title">{name}</div>
          </div>
          <div>
            <div class="factor-score">{score_txt}<span>/10</span></div>
            <div class="factor-level {lv_class}">{label}</div>
          </div>
        </div>
        """
    cards_html += "</div>"
    st.markdown(cards_html, unsafe_allow_html=True)

# =========================
# Streamlit本体（結果報告書 1ページ）
# =========================
st.markdown('<div class="main-wrap">', unsafe_allow_html=True)

uploaded = st.file_uploader("Excelファイル（ID列＋6_1〜6_23列）をアップロードしてください", type="xlsx")

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

perma_scores, extras = compute_results(selected_row)

# ---- タイトル＆基本情報 ----
st.title("心の健康チェック　結果報告書")

st.markdown(
    f"""
<div class="result-info">
  <div>
    <span><b>ID：{sid}</b></span>
  </div>
  <div class="section-caption">
    0〜10点であらわしています。点数が高いほど、その面がしっかりしていることを示します。
  </div>
</div>
""",
    unsafe_allow_html=True
)

# ---- PERMA 5要素 ----
st.markdown('<div class="section-header">PERMA（5つのしあわせの柱）</div>', unsafe_allow_html=True)

col_left, col_right = st.columns([1.8, 1.1])

with col_left:
    render_perma_cards(perma_scores)

with col_right:
    plot_histogram(perma_scores)

# ---- こころとからだのようす（元・補助指標） ----
st.markdown('<div class="section-header">こころとからだのようす</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-caption">PERMA と同じく、しあわせを支える大切な要素です。</div>',
    unsafe_allow_html=True
)
render_extra_cards(extras)

# ---- 注意書き（短く） ----
st.markdown(
    """
<div class="note-box">
<ul style="padding-left:1.1rem; margin:0;">
  <li>結果は「良い・悪い」を決めるものではなく、今のようすを知るためのものです。</li>
  <li>気になるところは、できそうなことから少しずつ取り組んでみましょう。</li>
  <li>この結果は医療的な診断ではありません。</li>
</ul>
</div>
""",
    unsafe_allow_html=True
)

st.markdown('</div>', unsafe_allow_html=True)
