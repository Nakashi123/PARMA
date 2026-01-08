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

.summary-card {{
  background:white;
  border-radius:12px;
  padding:0.9rem 1.1rem;
  margin-top:0.7rem;
  margin-bottom:0.9rem;
  box-shadow:0 1px 5px rgba(0,0,0,0.08);
  display:flex;
  flex-wrap:wrap;
  gap:0.6rem;
  align-items:center;
  justify-content:space-between;
}}

.summary-title {{
  font-weight:700;
  font-size:1rem;
  margin-bottom:0.2rem;
}}

.summary-score {{
  font-size:2.0rem;
  font-weight:800;
}}

.summary-text {{
  font-size:0.95rem;
  max-width:420px;
}}

.score-card {{
  background:white;
  border-radius:10px;
  padding:0.6rem 0.8rem;
  margin-bottom:0.5rem;
  box-shadow:0 1px 3px rgba(0,0,0,0.06);
}}

.score-title {{
  font-weight:700;
  margin-bottom:0.15rem;
}}

.score-value {{
  font-size:1.3rem;
  font-weight:800;
  margin-bottom:0.1rem;
}}

.score-comment {{
  font-size:0.9rem;
  color:#555;
}}

/* 物差しバー */
.meter {{
  background:#E0E0E0;
  border-radius:999px;
  height:14px;
  width:100%;
  margin-top:4px;
  margin-bottom:2px;
  overflow:hidden;
}}

.meter-fill {{
  height:100%;
  border-radius:999px;
}}

.meter-score-text {{
  font-size:0.9rem;
  margin-top:2px;
  color:#444;
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
# 1枚目では「アルファベット + 一言」のみ使用
full_labels = {
    'P': '前向きな気持ち',
    'E': '集中して取り組むこと',
    'R': '人とのつながり',
    'M': '生きがいや目的',
    'A': '達成感',
}

# 2枚目（備考）で使う、もともとの説明文
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

# おすすめ行動用の絵文字
action_emojis = {
    'P': '😊',  # 前向きな気持ち
    'E': '🧩',  # 集中
    'R': '🤝',  # つながり
    'M': '🌱',  # 生きがい・目的
    'A': '🏁',  # 達成感
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
    """カテゴリ名は付けず、素の点数だけを返す"""
    if np.isnan(v):
        return "未回答"
    s = int(round(v))
    return f"{s}/10点"

# =========================
# グラフ（棒グラフ：必要なら使用）
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
# 物差しバー描画
# =========================
def render_meter_block(title: str, score: float, color: str | None = None):
    """タイトル + 物差しバー + 数字をまとめて表示"""
    if np.isnan(score):
        width = "0%"
        score_text = "未回答"
    else:
        width = f"{score * 10:.0f}%"   # 0〜10点 → 0〜100%
        score_text = f"{score:.1f}/10点"

    bar_color = color if color is not None else "#999999"

    st.markdown(
        f"""
        <div class="score-card">
          <div class="score-title">{title}</div>
          <div class="meter">
            <div class="meter-fill" style="width:{width}; background:{bar_color};"></div>
          </div>
          <div class="meter-score-text">{score_text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

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

row = df[df.iloc[:, 0].astype(str) == sid]
if row.empty:
    st.warning("選択されたIDが見つかりません。")
    st.stop()

perma_scores, extras = compute_results(row)

# 1枚目（結果）・2枚目（備考）のタブ
tab_main, tab_note = st.tabs(["1枚目：結果", "2枚目：備考・この結果の見方"])

# =========================
# 1枚目：メイン結果
# =========================
with tab_main:
    st.markdown('<div class="section-header">PERMAの5つの要素と今の状態</div>', unsafe_allow_html=True)

    # 5要素を「アルファベット + 一言」＋ 物差しバーで表示
    col_left, col_right = st.columns(2)

    with col_left:
        for k in ['P', 'E', 'R']:
            v = perma_scores.get(k, np.nan)
            title = f"{k}：{full_labels[k]}"   # 例）P：前向きな気持ち
            render_meter_block(title, v, colors[k])

    with col_right:
        for k in ['M', 'A']:
            v = perma_scores.get(k, np.nan)
            title = f"{k}：{full_labels[k]}"
            render_meter_block(title, v, colors[k])

    st.markdown('<div class="section-header">心の状態に関連する項目</div>', unsafe_allow_html=True)

    # こころ・からだ・ひとりぼっち感・しあわせ感も物差しで（色はニュートラル）
    col_ex1, col_ex2 = st.columns(2)
    extras_items = list(extras.items())

    for i, (k, v) in enumerate(extras_items):
        col = col_ex1 if i % 2 == 0 else col_ex2
        with col:
            render_meter_block(k, v, None)

    # ========= おすすめ行動（絵文字つき） =========
    weak_keys = [k for k, v in perma_scores.items() if not np.isnan(v) and v <= 5]
    strong_keys = [k for k, v in perma_scores.items() if not np.isnan(v) and v >= 7]

    if strong_keys:
        st.markdown('<div class="section-header">今のあなたの「いいところ」</div>', unsafe_allow_html=True)
        for k in strong_keys:
            st.write(f"・{k}：{full_labels[k]}　（{score_label(perma_scores[k])}）")

    if weak_keys:
        st.markdown('<div class="section-header">今日からできそうなこと（おすすめ行動）</div>', unsafe_allow_html=True)
        st.markdown("やってみやすそうなものを、1つだけ選んでみましょう。")

        c1, c2 = st.columns([2, 1])

        with c1:
            for k in weak_keys:
                emoji = action_emojis.get(k, "💡")
                st.markdown(f"**{emoji} {full_labels[k]}（{k}）**", unsafe_allow_html=True)
                for t in tips[k]:
                    st.markdown(f"- {t}")

        with c2:
            st.image(
                "https://eiyoushi-hutaba.com/wp-content/uploads/2025/01/%E5%85%83%E6%B0%97%E3%81%AA%E3%82%B7%E3%83%8B%E3%82%A2%E3%81%AE%E4%BA%8C%E4%BA%BA%E3%80%80%E9%81%8B%E5%8B%95%E7%89%88.png",
                use_container_width=True
            )

# =========================
# 2枚目：備考・PERMAとは？
# =========================
with tab_note:
    st.markdown("### PERMAとは？")
    st.info("""
このチェックは、ポジティブ心理学者 Martin Seligman が提唱した PERMAモデル に基づいて、
心の健康や満たされている度合いを測定するものです。

PERMAとは **前向きな気持ち（P）・集中して取り組むこと（E）・人とのつながり（R）・
生きがいや目的（M）・達成感（A）** の5要素で構成されており、
「心が満たされ、前向きに生きられている状態」をとらえるための枠組みです。

この結果は診断ではなく、「今の自分の状態を知る」「どうすれば自分らしく過ごせそうか」を
考えるための資料としてお使いください。
""")

    st.markdown("### 5つの要素のくわしい説明")

    for k in ['P', 'E', 'R', 'M', 'A']:
        st.markdown(f"**{k}：{full_labels[k]}**")
        st.markdown(f"- {descriptions[k]}")

    st.markdown("### この結果の見方のめやす")
    st.markdown("""
- 点数は **0〜10点** です。数字が高いほど、その要素が「今は比較的満たされている」ことを表します。  
- 時期や体調によって変動します。**一度の結果で「よい／悪い」を決めつけない**ようにしましょう。  
- 気になるところがあれば、一人で抱え込まず、家族やスタッフと一緒に確認していきましょう。
""")

st.markdown('</div>', unsafe_allow_html=True)
