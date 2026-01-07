# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd, numpy as np
import matplotlib.pyplot as plt

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
    "P": "#F28B82",  # ピンク
    "E": "#FDD663",  # 黄色
    "R": "#81C995",  # 緑
    "M": "#AECBFA",  # 水色
    "A": "#F9AB00",  # オレンジ
}
theme = {
    "bg": "#FAFAFA",
    "bar_bg": "#EEF2FB",
    "accent": "#4E73DF",
    "text": "#222",
}

# =========================
# CSS
# =========================
st.markdown(f"""
<style>
html, body, [class*="css"] {{
  background-color:{theme['bg']};
  color:{theme['text']};
  font-family:"BIZ UDPGothic","Meiryo",sans-serif;
  line-height:1.8;
}}

.main-wrap {{ max-width:980px; margin:0 auto; }}

h1 {{
  text-align:center;
  color:#333;
  margin-top:0.4em;
  font-size:2rem;
  font-weight:800;
}}

.section-header {{
  background:{theme['bar_bg']};
  color:{theme['text']};
  font-weight:800;
  font-size:1.2rem;
  padding:.6rem 1rem;
  border-left:8px solid {theme['accent']};
  border-radius:6px;
  margin-top:1rem;
  margin-bottom:.8rem;
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
</style>
""", unsafe_allow_html=True)

# =========================
# PERMA定義
# =========================
full_labels = {
    'P': '前向きな気持ち',
    'E': '集中して取り組むこと',
    'R': '人とのつながり',
    'M': '生きがいや目的',
    'A': '達成感',
}

descriptions = {
    'P': '楽しい気持ちや安心感、感謝など前向きな感情の豊かさを示します。',
    'E': '物事に没頭したり夢中になって取り組める状態を示します。',
    'R': '支え合えるつながりや信頼関係を感じられている状態です。',
    'M': '人生に目的や価値を感じて生きている状態です。',
    'A': '努力し、達成感や成長を感じられている状態です。',
}

tips = {
    'P': ['今日あった「よかったこと」を3つ書いてみましょう。', '「ありがとう」と感じたことをメモしてみましょう。'],
    'E': ['短い時間（10〜15分）の「集中タイム」を作ってみましょう。', '得意なこと・好きなことに取り組む時間を少し増やしてみましょう。'],
    'R': ['最近会っていない人に、電話や手紙で一言だけメッセージを送ってみましょう。', '身近な人に「ありがとう」を1つ伝えてみましょう。'],
    'M': ['自分が大切にしていること（家族・健康・趣味など）を3つ書き出してみましょう。', 'これまでの経験から「学んだこと」を1つ思い出してみましょう。'],
    'A': ['今日できたことを1つ書き出してみましょう。', '大きな目標を「小さな一歩」に分けて、まず1つだけやってみましょう。'],
}

# アイコン（視覚的に分かりやすく）
perma_icons = {
    'P': '😊',
    'E': '🎯',
    'R': '🤝',
    'M': '🌱',
    'A': '🏅',
}
extra_icons = {
    'こころのつらさ': '💭',
    'からだの調子': '💪',
    'ひとりぼっち感': '🌧️',
    'しあわせ感': '🌈',
}

# =========================
# 質問項目のインデックス
# =========================
perma_indices = {
    'P': [4, 9, 21],
    'E': [2, 10, 20],
    'R': [5, 14, 18],
    'M': [0, 8, 16],
    'A': [1, 7, 15],
}
extra_indices = {
    'こころのつらさ': [6, 13, 19],
    'からだの調子': [3, 12, 17],
    'ひとりぼっち感': [11],
    'しあわせ感': [22],
}

# =========================
# 計算関数
# =========================
def compute_domain_avg(vals, idx):
    scores = [vals[i] for i in idx if i < len(vals) and not np.isnan(vals[i])]
    return float(np.mean(scores)) if scores else np.nan

def compute_results(row):
    cols = [c for c in row.columns if str(c).startswith("6_")]
    vals = pd.to_numeric(row[cols].values.flatten(), errors="coerce")
    perma = {k: compute_domain_avg(vals, v) for k, v in perma_indices.items()}
    extras = {k: compute_domain_avg(vals, v) for k, v in extra_indices.items()}
    return perma, extras

def score_label(v: float) -> str:
    if np.isnan(v):
        return "未回答"
    s = int(round(v))
    if s >= 7:
        cat = "（強み）"
    elif s >= 4:
        cat = "（おおむね良好）"
    else:
        cat = "（サポートが必要）"
    return f"{s}/10点{cat}"

def score_category(v: float):
    """カテゴリ名と色（バッジ用）"""
    if np.isnan(v):
        return "未回答", "#9E9E9E"
    s = int(round(v))
    if s >= 7:
        return "強み", "#43A047"        # 緑
    elif s >= 4:
        return "おおむね良好", "#FB8C00"  # オレンジ
    else:
        return "サポートが必要", "#E53935"  # 赤

def render_score_card(title, short, score, color, icon=""):
    """③のイメージ：顔＋名前＋点数＋横棒だけのシンプルカード"""
    cat, cat_color = score_category(score)

    if np.isnan(score):
        s_int = "ー"
        width = 0
        score_text = "未回答"
    else:
        s_int = int(round(score))
        width = max(0, min(100, s_int * 10))
        score_text = f"{s_int} / 10点"

    st.markdown(f"""
    <div style="
        background-color:white;
        border-radius:12px;
        padding:8px 10px;
        margin-bottom:8px;
        border:1px solid #E0E0E0;
        font-size:0.9rem;
    ">
      <div style="display:flex; align-items:center; gap:4px; margin-bottom:4px;">
        <span style="font-size:1.3rem;">{icon}</span>
        <span style="font-weight:bold; font-size:0.95rem;">{short} {title}</span>
      </div>
      <div style="display:flex; align-items:center; gap:4px; margin-bottom:4px;">
        <span>{score_text}</span>
        <span style="
            padding:1px 8px;
            border-radius:999px;
            background:{cat_color};
            color:white;
            font-size:0.75rem;
        ">{cat}</span>
      </div>
      <div style="
          background:#E0E0E0;
          border-radius:999px;
          height:12px;
          overflow:hidden;
      ">
        <div style="
            background:{color};
            width:{width}%;
            height:100%;
        "></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

def render_legend():
    st.markdown("""
    <div style="
        background-color:#F5F5F5;
        border-radius:10px;
        padding:6px 10px;
        margin-bottom:10px;
        border:1px solid #E0E0E0;
        font-size:0.85rem;
    ">
      <b>スコアの目安</b><br>
      <span style="display:inline-block;width:12px;height:12px;background:#C8E6C9;border-radius:3px;border:1px solid #81C784;margin-right:4px;"></span>
      強み（7〜10点）　
      <span style="display:inline-block;width:12px;height:12px;background:#FFE0B2;border-radius:3px;border:1px solid #FFB74D;mar
