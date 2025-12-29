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
  color:{theme['text']};
  font-weight:800;
  font-size:1.2rem;
  padding:.6rem 1rem;
  border-left:8px solid {theme['accent']};
  border-radius:6px;
  margin-top:1rem;
  margin-bottom:.8rem;
}}

.underline {{
  font-weight:bold;
  border-bottom:3px solid;
  padding-bottom:2px;
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
    'P': ['感謝を書き出す', '今日の良かったことを振り返る'],
    'E': ['小さな挑戦を設定する', '得意なことを活かす'],
    'R': ['感謝を伝える', '小さな親切をする'],
    'M': ['大切にしている価値を書き出す', '経験から学びを見つける'],
    'A': ['小さな目標を作る', '失敗を学びと捉える'],
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

# =========================
# グラフ（棒グラフのみ）
# =========================
def plot_hist(perma_scores):
    labels = list(perma_scores.keys())
    values = list(perma_scores.values())

    fig, ax = plt.subplots(figsize=(3.4, 2.6), dpi=160)

    ax.bar(labels, values, color=[colors[k] for k in labels])
    ax.set_ylim(0, 10)
    ax.set_ylabel("")
    ax.set_xlabel("")
    ax.set_yticklabels([])
    ax.set_title("PERMA", fontsize=12)

    for x, v in zip(labels, values):
        if not np.isnan(v):
            ax.text(x, v + 0.25, f"{v:.1f}",
                    ha="center", va="bottom", fontsize=9)

    fig.tight_layout()
    st.pyplot(fig)

# =========================
# アプリ本体
# =========================
st.markdown('<div class="main-wrap">', unsafe_allow_html=True)
st.title("わらトレ　心の健康チェック")

uploaded = st.file_uploader(
    "Excelファイル（ID列＋6_1〜の列）をアップロードしてください",
    type="xlsx",
    key="main_file_uploader"
)

if not uploaded:
    st.stop()

df = pd.read_excel(uploaded)
id_list = df.iloc[:, 0].dropna().astype(str).tolist()
sid = st.selectbox("IDを選んでください", options=id_list)

# IDの下に説明文
st.info("""
このチェックは、ポジティブ心理学者 Martin Seligman が提唱した PERMAモデル に基づいて、心の健康や満たされている度合いを測定するものです。

PERMAとは 前向きな気持ち・集中・つながり・意味・達成感 の5要素で構成されており、
幸せを「心が満たされ、前向きに生きられている状態」としてとらえます。

また、この結果は診断ではなく、 あなたの今の状態を理解し、より良く生きるヒントを得るためのツールです。
""")

row = df[df.iloc[:, 0].astype(str) == sid]
if row.empty:
    st.warning("選択されたIDが見つかりません。")
    st.stop()

perma_scores, extras = compute_results(row)

# =========================
# あなたのスコアと各要素の説明
# =========================
st.markdown('<div class="section-header">あなたのスコアと各要素の説明</div>', unsafe_allow_html=True)

col_chart, col_desc = st.columns([1, 1.5])
with col_chart:
    plot_hist(perma_scores)

with col_desc:
    for k in ['P', 'E', 'R', 'M', 'A']:
        st.markdown(
            f"<span class='color-label' style='background:{colors[k]}'>{k}</span> "
            f"**{full_labels[k]}**：{descriptions[k]}",
            unsafe_allow_html=True
        )

# =========================
# あなたのスコア + 心の状態に関連する指標
# =========================
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### あなたのスコア")
    st.markdown("**0〜10点満点のうち、7点以上＝強み、4〜6点＝おおむね良好、3点以下＝サポートが必要**")
    for k in ['P', 'E', 'R', 'M', 'A']:
        v = perma_scores.get(k, np.nan)
        st.markdown(
            f"<span class='underline' style='border-color:{colors[k]};'>"
            f"{full_labels[k]}（{k}）"
            f"</span>：{score_label(v)}",
            unsafe_allow_html=True
        )

with col_right:
    st.markdown("### 心の状態に関連する指標")
    for k, v in extras.items():
        st.write(f"{k}：{score_label(v)}")

# =========================
# 強み & おすすめ行動
# =========================
weak_keys = [k for k, v in perma_scores.items() if not np.isnan(v) and v <= 5]
strong_keys = [k for k, v in perma_scores.items() if not np.isnan(v) and v >= 7]

# 強み（満たされている要素）
if strong_keys:
    st.markdown('<div class="section-header">あなたの強み（満たされている要素）</div>', unsafe_allow_html=True)
    for k in strong_keys:
        st.write(f"✔ {full_labels[k]}（{k}）：{score_label(perma_scores[k])}")

# スコア5点以下の要素のみ、おすすめ行動を表示
if weak_keys:
    st.markdown('<div class="section-header">あなたにおすすめな行動（例）</div>', unsafe_allow_html=True)

    col_left2, col_right2 = st.columns([2, 1])

    # 左：スコアが5点以下の要素に対するおすすめ行動
    with col_left2:
        for k in weak_keys:
            st.markdown(f"**{full_labels[k]}（{k}）**", unsafe_allow_html=True)
            for t in tips[k]:
                st.markdown(f"- {t}")

    # 右：指定の画像を表示（URL指定）
    with col_right2:
        st.image(
            "https://eiyoushi-hutaba.com/wp-content/uploads/2025/01/%E5%85%83%E6%B0%97%E3%81%AA%E3%82%B7%E3%83%8B%E3%82%A2%E3%81%AE%E4%BA%8C%E4%BA%BA%E3%80%80%E9%81%8B%E5%8B%95%E7%89%88.png",
            use_container_width=True
        )

# ラッパー<div>を閉じる　
st.markdown('</div>', unsafe_allow_html=True)
