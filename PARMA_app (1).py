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
    "font.sans-serif": ["BIZ UDPGothic", "Meiryo", "Noto Sans JP", "IPAexGothic", "sans-serif"],
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

.spacer-6 {{ height:6px; }}
.spacer-10 {{ height:10px; }}

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

required_domain_cols = ["P", "E", "R", "M", "A"]
optional_extra_cols = [
    "心の健康の総合得点",
    "気持ちの様子（いやな気持）",
    "からだの調子",
    "ひとりぼっち感",
    "全体的なしあわせ感",
]

# =========================
# 計算関数
# =========================
def compute_domain_avg(vals, idx):
    scores = [vals[i] for i in idx if i < len(vals)]
    return float(np.mean(scores)) if scores else np.nan


def safe_float(x, default=np.nan):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def clamp_score(x, min_value=0.0, max_value=10.0):
    x = safe_float(x, np.nan)
    if np.isnan(x):
        return np.nan
    return max(min_value, min(max_value, x))

# =========================
# 強制改ページ
# =========================
def FORCE_PAGE_BREAK():
    st.markdown('<div class="force-break"></div>', unsafe_allow_html=True)

# =========================
# 補助関数
# =========================
def page_header(title: str, subtitle: Optional[str] = None):
    subtitle_html = f'<div class="sub">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f"""
        <div class="page-header">
          <div class="title">{title}</div>
          {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True
    )


def render_extras_meaning_note():
    st.markdown(
        """
        <div class="mini-note">
          <b>補足</b><br>
          「気持ちの様子（いやな気持）」は、点が高いほどその気持ちを感じやすい可能性があります。<br>
          「からだの調子」「全体的なしあわせ感」は、点が高いほどよい状態の目安です。<br>
          「ひとりぼっち感」は、点が高いほど孤独を感じやすい可能性があります。
        </div>
        """,
        unsafe_allow_html=True
    )


def render_remarks_box():
    st.markdown(
        """
        <div class="mini-note">
          <b>備考</b><br>
          この結果は、その時点でのこころの健康の様子を簡単に振り返るためのものです。<br>
          医学的な診断を行うものではありません。<br>
          気になる状態が続く場合には、かかりつけ医や専門職へご相談ください。
        </div>
        """,
        unsafe_allow_html=True
    )


def get_strengths_and_growth(domain_scores: dict):
    valid = [(k, safe_float(v, np.nan)) for k, v in domain_scores.items()]
    valid = [(k, v) for k, v in valid if not np.isnan(v)]
    if not valid:
        return [], []
    sorted_scores = sorted(valid, key=lambda x: x[1], reverse=True)
    strengths = sorted_scores[:2]
    growth = sorted_scores[-2:] if len(sorted_scores) >= 2 else sorted_scores
    return strengths, growth


def recommendation_text(key: str) -> str:
    recs = {
        "P": "気分が少し上がる活動を、短時間でも日常に入れてみましょう。",
        "E": "夢中になれる作業や趣味を、無理のない範囲で続けてみましょう。",
        "R": "身近な人とのあいさつや短い会話でも、つながりを保つ助けになります。",
        "M": "自分にとって大切なことや、続けたい役割を振り返る時間を持つのがおすすめです。",
        "A": "小さな目標を立てて、できたことを確認する習慣が達成感につながります。",
    }
    return recs.get(key, "無理のない範囲で、日常の中の小さな行動を積み重ねていきましょう。")

# =========================
# グラフ表示
# =========================
def render_small_bar(score: float, color: str):
    score = clamp_score(score)
    if np.isnan(score):
        st.write("データなし")
        return

    fig, ax = plt.subplots(figsize=(3.0, 0.55), dpi=180)
    ax.barh([0], [10], color="#E9EEF8", height=0.42)
    ax.barh([0], [score], color=color, height=0.42)
    ax.set_xlim(0, 10)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")
    plt.tight_layout(pad=0.2)
    st.pyplot(fig, use_container_width=False)
    plt.close(fig)


def render_meter_card(title: str, score: float, color: str):
    score = clamp_score(score)
    if np.isnan(score):
        score_text = "データなし"
        width_percent = 0
    else:
        score_text = f"{score:.1f} / 10"
        width_percent = score * 10

    st.markdown(
        f"""
        <div class="score-card">
          <div style="font-weight:900; margin-bottom:0.35rem;">{title}</div>
          <div class="meter">
            <div class="meter-fill" style="width:{width_percent:.1f}%; background:{color};"></div>
          </div>
          <div class="meter-score-text"><span class="score-strong">{score_text}</span></div>
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================
# Excel読込
# =========================
def load_scores_from_excel(uploaded_file):
    df = pd.read_excel(uploaded_file)

    if df.empty:
        raise ValueError("Excelファイルが空です。")

    missing = [c for c in required_domain_cols if c not in df.columns]
    if missing:
        raise ValueError(f"必要な列が不足しています: {', '.join(missing)}")

    row = df.iloc[0]

    domain_scores = {col: clamp_score(row[col]) for col in required_domain_cols}

    extra_scores = {}
    for col in optional_extra_cols:
        if col in df.columns:
            extra_scores[col] = clamp_score(row[col])

    if "心の健康の総合得点" not in extra_scores:
        valid = [v for v in domain_scores.values() if not np.isnan(v)]
        extra_scores["心の健康の総合得点"] = float(np.mean(valid)) if valid else np.nan

    return df, domain_scores, extra_scores

# =========================
# 画面
# =========================
st.title("わらトレ　心の健康チェック")

uploaded_file = st.file_uploader("Excelファイルを添付してください", type=["xlsx", "xls"])

if uploaded_file is None:
    st.info("Excelファイルをアップロードすると結果が表示されます。")
    st.stop()

try:
    df, domain_scores, extra_scores = load_scores_from_excel(uploaded_file)
except Exception as e:
    st.error(f"Excelの読み込みでエラーが出ました: {e}")
    st.stop()

strengths, growth = get_strengths_and_growth(domain_scores)

# --- 1ページ目 ---
page_header(
    "1. あなたの心の健康チェック結果",
    "PERMAの5つの要素と、こころ・からだの調子の目安をまとめています。"
)

st.markdown('<div class="section-header">1-1. 要素ごとに見た心の状態</div>', unsafe_allow_html=True)

for key in ["P", "E", "R", "M", "A"]:
    c1, c2 = st.columns([1.55, 1.0], gap="medium")
    with c1:
        st.markdown(
            f"""
            <div class="score-card">
              <div style="font-weight:900; color:{colors.get(key, theme['accent'])};">
                {key}：{full_labels[key]}
              </div>
              <div style="margin-top:0.25rem;">
                {descriptions[key]}
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c2:
        render_small_bar(domain_scores.get(key, np.nan), colors.get(key, theme["accent"]))

# --- 2ページ目開始 ---
FORCE_PAGE_BREAK()

st.markdown('<div class="section-header">1-2. こころ・からだの調子</div>', unsafe_allow_html=True)

for label in optional_extra_cols:
    if label in extra_scores:
        render_meter_card(label, extra_scores.get(label, np.nan), extra_colors.get(label, theme["accent"]))

render_extras_meaning_note()

st.markdown("<div class='spacer-10'></div>", unsafe_allow_html=True)

page_header(
    "2. あなたの結果に基づく、強みとおすすめな行動",
    "結果からみたご本人の強みと、日常生活でおすすめできることをまとめます。"
)

st.markdown("<div class='spacer-6'></div>", unsafe_allow_html=True)

# --- 2-1 ---
st.markdown('<div class="section-header">2-1. 満たされている心の健康の要素（強み）</div>', unsafe_allow_html=True)

if strengths:
    for key, score in strengths:
        st.markdown(
            f"""
            <div class="score-card">
              <div style="font-weight:900; color:{colors.get(key, theme['accent'])}; font-size:1.05rem;">
                {key}：{full_labels.get(key, key)}（{score:.1f} / 10）
              </div>
              <div style="margin-top:0.35rem; line-height:1.7;">
                {descriptions.get(key, "")}
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# --- 2-2 ---
st.markdown('<div class="section-header">2-2. これから伸ばせる要素と具体的な行動ライン</div>', unsafe_allow_html=True)

if growth:
    for key, score in growth:
        c1, c2 = st.columns([1.45, 0.9], gap="medium")
        with c1:
            st.markdown(
                f"""
                <div class="score-card">
                  <div style="font-weight:900; color:{colors.get(key, theme['accent'])}; font-size:1.05rem;">
                    {key}：{full_labels.get(key, key)}（{score:.1f} / 10）
                  </div>
                  <div style="margin-top:0.35rem; line-height:1.75;">
                    {recommendation_text(key)}
                  </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c2:
            st.markdown(
                """
                <div class="score-card" style="text-align:center; font-size:2rem;">
                  🌱
                </div>
                """,
                unsafe_allow_html=True
            )

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
