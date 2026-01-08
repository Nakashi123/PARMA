# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
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
    "P": "#F28B82",
    "E": "#FDD663",
    "R": "#81C995",
    "M": "#AECBFA",
    "A": "#F9AB00",
}
theme = {
    "bg": "#FAFAFA",
    "accent": "#4E73DF",
    "text": "#222",
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
  line-height:1.9;
}}

.main-wrap {{ max-width:880px; margin:0 auto; }}

h1 {{
  text-align:center;
  font-size:2rem;
  font-weight:800;
}}

.section-header {{
  background:#EEF2FB;
  font-weight:800;
  font-size:1.2rem;
  padding:.6rem 1rem;
  border-left:8px solid {theme['accent']};
  border-radius:6px;
  margin-top:1.2rem;
  margin-bottom:.8rem;
}}

.score-card {{
  background:white;
  border-radius:10px;
  padding:0.6rem 0.9rem;
  margin-bottom:0.6rem;
  box-shadow:0 1px 3px rgba(0,0,0,0.06);
}}

.score-title {{
  font-weight:700;
  margin-bottom:0.2rem;
}}

.meter {{
  background:#E0E0E0;
  border-radius:999px;
  height:14px;
  width:100%;
  overflow:hidden;
}}

.meter-fill {{
  height:100%;
  border-radius:999px;
}}

.meter-score-text {{
  font-size:0.9rem;
  margin-top:2px;
}}

.color-chip {{
  display:inline-block;
  padding:2px 8px;
  border-radius:8px;
  color:white;
  font-weight:800;
  margin-right:6px;
}}

.perma-box {{
  border:3px solid {theme['accent']};
  border-radius:12px;
  padding:1.2rem 1.4rem;
  margin-top:1rem;
  background:white;
}}

.perma-box p {{
  font-size:1.05rem;
  color:#222;
  margin-bottom:0.9rem;
}}

.perma-highlight {{
  color:{theme['accent']};
  font-weight:800;
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
    "P": "楽しい気持ちや安心感、感謝など前向きな感情の豊かさを示します。",
    "E": "物事に没頭したり夢中になって取り組める状態を示します。",
    "R": "支え合えるつながりや信頼関係を感じられている状態です。",
    "M": "人生に目的や価値を感じて生きている状態です。",
    "A": "努力し、達成感や成長を感じられている状態です。",
}

tips = {
    "P": ["感謝を書き出す", "今日の良かったことを振り返る"],
    "E": ["小さな挑戦を設定する", "得意なことを活かす"],
    "R": ["感謝を伝える", "小さな親切をする"],
    "M": ["大切にしている価値を書き出す"],
    "A": ["小さな目標を作る"],
}

action_emojis = {
    "P": "😊", "E": "🧩", "R": "🤝", "M": "🌱", "A": "🏁"
}

perma_indices = {
    "P": [4, 9, 21],
    "E": [2, 10, 20],
    "R": [5, 14, 18],
    "M": [0, 8, 16],
    "A": [1, 7, 15],
}

# =========================
# 関数
# =========================
def compute_avg(vals, idx):
    return float(np.mean([vals[i] for i in idx if i < len(vals) and not np.isnan(vals[i])]))

def render_meter(title, score, color):
    width = f"{score*10:.0f}%" if not np.isnan(score) else "0%"
    st.markdown(f"""
    <div class="score-card">
      <div class="score-title">{title}</div>
      <div class="meter">
        <div class="meter-fill" style="width:{width};background:{color};"></div>
      </div>
      <div class="meter-score-text">{score:.1f}/10点</div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# アプリ本体
# =========================
st.markdown('<div class="main-wrap">', unsafe_allow_html=True)
st.title("わらトレ　心の健康チェック")

uploaded = st.file_uploader("Excelファイルをアップロード", type="xlsx")
if not uploaded:
    st.stop()

df = pd.read_excel(uploaded)
sid = st.selectbox("IDを選択", df.iloc[:,0].astype(str))
row = df[df.iloc[:,0].astype(str)==sid]

vals = pd.to_numeric(row.filter(like="6_").values.flatten(), errors="coerce")
perma = {k: compute_avg(vals,v) for k,v in perma_indices.items()}

# =========================
# 冒頭説明
# =========================
st.markdown(
"この評価用紙は、**心の元気度（PERMAの5要素）と今の心の状態を、点数で見える化するチェック**です。"
)

# =========================
# PERMA結果
# =========================
st.markdown('<div class="section-header">PERMAの5つの要素と今の状態</div>', unsafe_allow_html=True)

c1, c2 = st.columns([2,1])

with c1:
    for k in ["P","E","R","M","A"]:
        render_meter(f"{k}：{full_labels[k]}", perma[k], colors[k])

with c2:
    fig, ax = plt.subplots(figsize=(3,2.6))
    ax.bar(perma.keys(), perma.values(), color=[colors[k] for k in perma])
    ax.set_ylim(0,10)
    ax.set_yticks([])
    for i,(k,v) in enumerate(perma.items()):
        ax.text(i, v+0.2, f"{v:.1f}", ha="center")
    st.pyplot(fig)

# =========================
# ★ 1枚目の最後：おすすめ行動
# =========================
st.markdown('<div class="section-header">今日からできそうなこと（おすすめ行動の例）</div>', unsafe_allow_html=True)

for k,v in perma.items():
    if v <= 5:
        st.markdown(f"**{action_emojis[k]} {full_labels[k]}**")
        for t in tips[k]:
            st.markdown(f"- {t}")

# =========================
# 備考：PERMAとは？
# =========================
st.markdown('<div class="section-header">PERMAとは？</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="perma-box">
<p>
このチェックは、ポジティブ心理学者 Martin Seligman が提唱した PERMAモデル に基づいて、
<span class="perma-highlight">心の健康や満たされている度合い</span>を測定するものです。
</p>

<p>
PERMAとは
<span class="perma-highlight">
前向きな気持ち（P）・集中して取り組むこと（E）・人とのつながり（R）・
生きがいや目的（M）・達成感（A）の5要素
</span>
で構成されています。
</p>

<p>
この結果は診断ではなく、今の自分の状態を知り、
これからの過ごし方を考えるための資料としてお使いください。
</p>
</div>
""", unsafe_allow_html=True)

# =========================
# 詳しい説明（色対応）
# =========================
st.markdown('<div class="section-header">5つの要素のくわしい説明</div>', unsafe_allow_html=True)

for k in ["P","E","R","M","A"]:
    st.markdown(f"""
    <div class="score-card">
      <span class="color-chip" style="background:{colors[k]};">{k}</span>
      <b>{full_labels[k]}</b><br>
      {descriptions[k]}
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
