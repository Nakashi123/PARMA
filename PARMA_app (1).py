# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Optional

# =========================
# 基本設定
# =========================
st.set_page_config(page_title="わらトレ　心の健康チェック", layout="centered")

plt.rcParams.update({
    "font.sans-serif": ["BIZ UDPGothic", "Meiryo", "Noto Sans JP"],
    "axes.unicode_minus": False,
    "font.size": 12,
})

# =========================
# カラー設定
# =========================
colors = {
    "P": "#F28B82",
    "E": "#FDD663",
    "R": "#81C995",
    "M": "#AECBFA",
    "A": "#F9AB00",
}

extra_colors = {
    "心の健康の総合得点": "#4E73DF",
    "気持ちの様子（いやな気持）": "#E74C3C",
    "からだの調子": "#2ECC71",
    "ひとりぼっち感": "#9B59B6",
    "全体的なしあわせ感": "#F1C40F",
}

theme = {
    "bg": "#FAFAFA",
    "accent": "#4E73DF",
    "text": "#222",
    "bar_bg": "#EEF2FB",
}

# =========================
# CSS
# =========================
st.markdown(f"""
<style>
html, body {{
  background-color:{theme['bg']};
  color:{theme['text']};
  font-family:"BIZ UDPGothic","Meiryo",sans-serif;
}}

.main-wrap {{ max-width: 880px; margin: 0 auto; }}

.section-header {{
  background:{theme['bar_bg']};
  font-weight:900;
  font-size:1.15rem;
  padding:.55rem 1rem;
  border-left:8px solid {theme['accent']};
  border-radius:8px;
  margin-top:0.9rem;
  margin-bottom:.7rem;
}}

.page-header {{
  background:white;
  border-left:10px solid {theme['accent']};
  border-radius:14px;
  padding:1.0rem 1.2rem;
  margin:0.9rem 0;
}}

.page-header .title {{
  font-size:1.45rem;
  font-weight:950;
}}

.page-header .sub {{
  font-size:1.02rem;
}}

.score-card {{
  background:white;
  border-radius:12px;
  padding:0.55rem 0.9rem;
  margin-bottom:0.55rem;
}}

.meter {{
  background:#E0E0E0;
  border-radius:999px;
  height:14px;
  width:100%;
}}

.meter-fill {{
  height:100%;
  border-radius:999px;
}}

.meter-score-text {{
  font-size:1.05rem;
  margin-top:4px;
}}

.meter-score-text .score-strong {{
  font-size:1.28rem;
  font-weight:1000;
}}

.mini-note {{
  background:white;
  border:1px solid #E6EAF5;
  border-radius:12px;
  padding:0.65rem 0.85rem;
  margin:0.55rem 0;
}}

.perma-box {{
  border:3px solid {theme['accent']};
  border-radius:12px;
  padding:1.05rem 1.25rem;
  background:white;
}}

.footer-box {{
  border-top:2px solid #DDD;
  margin-top:1.6rem;
  padding-top:1rem;
}}

.footer-title {{
  font-weight:900;
}}

.footer-thanks {{
  margin-top:0.85rem;
  font-weight:800;
}}

/* ===== 追加：ちょい余白 ===== */
.spacer-6 {{ height:6px; }}
.spacer-10 {{ height:10px; }}

/* ===== 強制改ページ ===== */
.force-break {{
  display:block;
  height:0;
}}

@media print {{
  @page {{ size:A4; margin:8mm; }}

  .force-break {{
    break-before:page !important;
    page-break-before:always !important;
  }}

  img {{
    max-height:60px !important;
  }}
}}
</style>
""", unsafe_allow_html=True)

# =========================
# 定義
# =========================
full_labels = {
    "P": "前向きな気持ち",
    "E": "集中して取り組むこと",
    "R": "人とのつながり",
    "M": "生きがいや目的",
    "A": "達成感",
}

descriptions = {
    "P": "楽しい気持ちや安心感など前向きな感情の豊かさ。",
    "E": "夢中になって取り組める状態。",
    "R": "支え合えるつながりを感じられる状態。",
    "M": "人生に目的や価値を感じている状態。",
    "A": "達成感や成長を感じられる状態。",
}

# =========================
# 計算関数
# =========================
def compute_domain_avg(vals, idx):
    scores = [vals[i] for i in idx if i < len(vals)]
    return float(np.mean(scores)) if scores else np.nan

# =========================
# 強制改ページ
# =========================
def FORCE_PAGE_BREAK():
    st.markdown('<div class="force-break"></div>', unsafe_allow_html=True)

# =========================
# 表示部分（抜粋）
# =========================

# --- 1ページ目 ---
st.title("わらトレ　心の健康チェック")

# ...（ここはあなたの既存ロジックそのまま）

# --- 2ページ目開始 ---
FORCE_PAGE_BREAK()

st.markdown('<div class="section-header">1-2. こころ・からだの調子</div>', unsafe_allow_html=True)

# ...（こころ・からだ表示処理）

render_extras_meaning_note()

# 👇ここに少し余白追加
st.markdown("<div class='spacer-10'></div>", unsafe_allow_html=True)

page_header(
    "2. あなたの結果に基づく、強みとおすすめな行動",
    "結果からみたご本人の強みと、日常生活でおすすめできることをまとめます。"
)

# 👇さらに少し余白（2-1との間）
st.markdown("<div class='spacer-6'></div>", unsafe_allow_html=True)

# --- 2-1 ---
st.markdown('<div class="section-header">2-1. 満たされている心の健康の要素（強み）</div>', unsafe_allow_html=True)

# ...（強み表示）

# --- 3ページ目開始 ---
FORCE_PAGE_BREAK()

page_header("3. 備考", "この評価に関する詳しい情報は以下の通りです。")

render_remarks_box()

st.markdown(
    """
    <div class="footer-box">
      <div class="footer-title">この評価結果に関するお問い合わせ</div>
      〒474-0037 愛知県大府市半月町三丁目294番地<br>
      ☎0562-44-5551 研究代表者：李 相侖
      <div class="footer-thanks">この度は、ご協力ありがとうございました。</div>
    </div>
    """,
    unsafe_allow_html=True
)
