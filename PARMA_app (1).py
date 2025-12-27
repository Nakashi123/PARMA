# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd, numpy as np
import matplotlib.pyplot as plt

# =========================
# 基本設定
# =========================
st.set_page_config(page_title="心の健康チェック　結果のご報告", layout="centered")

plt.rcParams.update({
    "font.sans-serif": ["BIZ UDPGothic", "Meiryo", "Noto Sans JP"],
    "axes.unicode_minus": False,
    "font.size": 12,
})

# =========================
# カラーテーマ
# =========================
pillar_colors = {
    "P": "#F28B82",  # 前向きな気持ち
    "E": "#FDD663",  # 集中して取り組むこと
    "R": "#81C995",  # 人とのつながり
    "M": "#AECBFA",  # 生きがいや目的
    "A": "#F9AB00",  # 達成感
}

extra_colors = {
    "こころのつらさ":   "#9FA8DA",
    "からだの調子":     "#80CBC4",
    "ひとりぼっち感": "#FFAB91",
    "しあわせ感":       "#FFE082",
}

theme = {
    "bg": "#F5F5F5",
    "card_bg": "#FFFFFF",
    "accent": "#4E73DF",
    "text": "#222222",
    "bar_bg": "#E3EAFD",
}

# =========================
# CSS（見た目の調整）
# =========================
st.markdown(f"""
<style>
html, body, [class*="css"] {{
  background-color: {theme['bg']};
  color: {theme['text']};
  font-family: "BIZ UDPGothic", "Meiryo", sans-serif;
  line-height: 1.7;
}}

div.block-container {{
  padding-top: 0.5rem !important;
  padding-bottom: 0.5rem !important;
}}

.main-wrap {{
  max-width: 880px;
  margin: 0 auto;
}}

h1 {{
  text-align: center;
  color: #333333;
  margin-top: 0.6em;
  margin-bottom: 0.6em;
  font-size: 2.1rem;
  font-weight: 800;
}}

.section-header {{
  background: {theme['bar_bg']};
  color: #333333;
  font-weight: 800;
  font-size: 1.1rem;
  padding: 0.55rem 0.9rem;
  border-left: 8px solid {theme['accent']};
  border-radius: 6px;
  margin-top: 1.0rem;
  margin-bottom: 0.4rem;
}}

.section-caption {{
  font-size: 0.95rem;
  color: #555555;
  margin-bottom: 0.3rem;
}}

.result-info {{
  font-size: 0.95rem;
  margin-bottom: 0.4rem;
}}

.result-info span {{
  margin-right: 1.0rem;
}}

.note-box {{
  font-size: 0.9rem;
  background: #FFFDE7;
  border-radius: 8px;
  padding: 0.6rem 0.75rem;
  margin-top: 0.7rem;
  border: 1px solid #FFE082;
}}

@media print {{
  @page {{
    size: A4;
    margin: 15mm;
  }}
}}
</style>
""", unsafe_allow_html=True)

# =========================
# 質問票の定義
# =========================
perma_indices = {
    "P": [4, 9, 21],    # 前向きな気持ち
    "E": [2, 10, 20],   # 集中して取り組むこと
    "R": [5, 14, 18],   # 人とのつながり
    "M": [0, 8, 16],    # 生きがいや目的
    "A": [1, 7, 15],    # 達成感
}
extra_indices = {
    "こころのつらさ":   [6, 13, 19],
    "からだの調子":     [3, 12, 17],
    "ひとりぼっち感": [11],
    "しあわせ感":       [22],
}

pillar_labels = {
    "P": "前向きな気持ち",
    "E": "集中して取り組むこと",
    "R": "人とのつながり",
    "M": "生きがいや目的",
    "A": "達成感",
}

# =========================
# スコア計算
# =========================
def compute_domain_avg(vals, idx_list):
    scores = [vals[i] for i in idx_list if i < len(vals) and not np.isnan(vals[i])]
    return float(np.mean(scores)) if scores else np.nan

def compute_results(selected_row: pd.DataFrame):
    cols = [c for c in selected_row.columns if str(c).startswith("6_")]
    vals = pd.to_numeric(selected_row[cols].values.flatten(), errors="coerce")
    perma_scores = {k: compute_domain_avg(vals, idx) for k, idx in perma_indices.items()}
    extra_scores = {k: compute_domain_avg(vals, idx) for k, idx in extra_indices.items()}
    return perma_scores, extra_scores

# =========================
# スコアのコメント
# =========================
def judge_level(score: float):
    if np.isnan(score):
        return "未測定", "gray"
    if score >= 7:
        return "とても良い状態", "high"
    if score >= 4:
        return "おおむね良い状態", "mid"
    return "少し気をつけたい状態", "low"

# =========================
# 棒グラフ（5つのしあわせの柱）
# =========================
def plot_pillar_bar(perma_scores):
    labels = [pillar_labels[k] for k in ["P", "E", "R", "M", "A"]]
    values = [perma_scores.get(k, np.nan) for k in ["P", "E", "R", "M", "A"]]
    colors = [pillar_colors[k] for k in ["P", "E", "R", "M", "A"]]

    fig, ax = plt.subplots(figsize=(5.2, 3.2), dpi=160)
    pos = np.arange(len(labels))
    bars = ax.bar(pos, values, color=colors, alpha=0.9)

    for b, v in zip(bars, values):
        if np.isnan(v):
            continue
        ax.text(b.get_x() + b.get_width()/2, v + 0.25, f"{v:.1f}",
                ha="center", va="bottom", fontsize=9, fontweight="bold")

    ax.set_ylim(0, 10)
    ax.set_xticks(pos)
    ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=9)
    ax.set_ylabel("点数（0〜10点）", fontsize=10)
    ax.set_title("5つのしあわせの柱のバランス", fontsize=11, fontweight="bold")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    st.pyplot(fig)

# =========================
# カード描画（HTMLはここだけ・1枚ずつ）
# =========================
def render_card(title: str, score: float, color: str):
    label, level_tag = judge_level(score)
    score_text = f"{score:.1f}" if not np.isnan(score) else "-"

    if level_tag == "high":
        level_bg = "#E3F2FD"; level_fg = "#1565C0"
    elif level_tag == "mid":
        level_bg = "#FFF8E1"; level_fg = "#EF6C00"
    elif level_tag == "low":
        level_bg = "#FFEBEE"; level_fg = "#C62828"
    else:
        level_bg = "#ECEFF1"; level_fg = "#455A64"

    html = f"""
    <div style="
        background-color:{theme['card_bg']};
        border-radius:12px;
        padding:8px 10px 7px;
        box-shadow:0 1px 3px rgba(0,0,0,0.08);
        border-top:5px solid {color};
        min-height:95px;
    ">
      <div style="font-size:0.95rem;font-weight:700;margin-bottom:2px;">
        {title}
      </div>
      <div style="font-size:1.7rem;font-weight:800;margin-top:2px;">
        {score_text}<span style="font-size:0.85rem;">／10点</span>
      </div>
      <div style="
        display:inline-block;
        margin-top:3px;
        padding:2px 7px;
        border-radius:999px;
        font-size:0.85rem;
        font-weight:700;
        background:{level_bg};
        color:{level_fg};
      ">
        {label}
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_pillar_cards(perma_scores):
    # 1段目（3枚）
    row1 = ["P", "E", "R"]
    cols = st.columns(3)
    for col, key in zip(cols, row1):
        with col:
            render_card(pillar_labels[key], perma_scores.get(key, np.nan), pillar_colors[key])
    # 2段目（2枚）
    row2 = ["M", "A"]
    cols = st.columns(2)
    for col, key in zip(cols, row2):
        with col:
            render_card(pillar_labels[key], perma_scores.get(key, np.nan), pillar_colors[key])

def render_extra_cards(extra_scores):
    keys = ["こころのつらさ", "からだの調子", "ひとりぼっち感", "しあわせ感"]
    # 1段目
    row1 = keys[:2]
    cols = st.columns(2)
    for col, name in zip(cols, row1):
        with col:
            render_card(name, extra_scores.get(name, np.nan), extra_colors[name])
    # 2段目
    row2 = keys[2:]
    cols = st.columns(2)
    for col, name in zip(cols, row2):
        with col:
            render_card(name, extra_scores.get(name, np.nan), extra_colors[name])

# =========================
# Streamlit 本体
# =========================
st.markdown('<div class="main-wrap">', unsafe_allow_html=True)

st.title("心の健康チェック　結果のご報告")

uploaded = st.file_uploader(
    "結果が入っている Excel ファイル（1列目にID、6_1〜6_23列）を選んでください。",
    type="xlsx"
)

if not uploaded:
    st.info("まずは Excel ファイルをアップロードしてください。")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

df = pd.read_excel(uploaded)
id_list = df.iloc[:, 0].dropna().astype(str).tolist()

sid = st.selectbox("結果を見たい方のIDを選んでください。", options=id_list)
selected_row = df[df.iloc[:, 0].astype(str) == sid]

if selected_row.empty:
    st.warning("選択されたIDが見つかりません。")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

perma_scores, extra_scores = compute_results(selected_row)

# ① 全体のようす
st.markdown('<div class="section-header">全体のようす</div>', unsafe_allow_html=True)
st.markdown(
    f"""
<div class="result-info">
  <span><b>ID：{sid}</b></span>
  <span>0〜10点であらわしています。点数が高いほど、その面がしっかりしていることを示します。</span>
</div>
""",
    unsafe_allow_html=True
)

col_graph, col_text = st.columns([1.1, 1.1])
with col_graph:
    plot_pillar_bar(perma_scores)
with col_text:
    st.markdown("**5つのしあわせの柱（各10点満点）**")
    for key in ["P", "E", "R", "M", "A"]:
        score = perma_scores.get(key, np.nan)
        label, _ = judge_level(score)
        score_text = "- 点" if np.isnan(score) else f"{int(round(score))} 点"
        st.write(f"- {pillar_labels[key]}：{score_text}　（{label}）")

# ② 5つのしあわせの柱（カード）
st.markdown('<div class="section-header">5つのしあわせの柱</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-caption">こころの健康を支える5つの面です。数字が大きいほど、その面がしっかりしていることをあらわします。</div>',
    unsafe_allow_html=True
)
render_pillar_cards(perma_scores)

# ③ 心とからだのしあわせ（補助指標を主要要素として扱う）
st.markdown('<div class="section-header">心とからだのしあわせ</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-caption">こころのつらさ・からだの調子・ひとりぼっち感・しあわせ感など、しあわせに関わる大切な面です。</div>',
    unsafe_allow_html=True
)
render_extra_cards(extra_scores)

# ④ 結果を見るときのポイント
st.markdown(
    """
<div class="note-box">
<ul style="padding-left: 1.2rem; margin: 0;">
  <li>この結果は、「良い・悪い」を決めるためのものではなく、今のようすを知るためのものです。</li>
  <li>気になるところがあれば、できそうなことから少しずつ始めていきましょう。</li>
  <li>この結果だけで病気の診断を行うものではありません。心配な点があれば、主治医にご相談ください。</li>
</ul>
</div>
""",
    unsafe_allow_html=True
)

st.markdown('</div>', unsafe_allow_html=True)
