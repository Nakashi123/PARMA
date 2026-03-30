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
    "E": "#F4C542",
    "R": "#78C88C",
    "M": "#9CC4FF",
    "A": "#F4B000",
}

extra_colors = {
    "心の健康の総合得点": "#4E73DF",
    "気持ちの様子（いやな気持）": "#E74C3C",
    "からだの調子": "#2ECC71",
    "ひとりぼっち感": "#9B59B6",
    "全体的なしあわせ感": "#F1C40F",
}

theme = {
    "bg": "#F6F7FB",
    "accent": "#4E73DF",
    "text": "#222222",
    "bar_bg": "#EEF2FB",
    "soft_blue": "#DDE7FF",
    "border": "#E3E7F1",
    "card": "#FFFFFF",
    "muted": "#666666",
    "track": "#D9D9D9",
}

# =========================
# CSS
# =========================
st.markdown(f"""
<style>
html, body, [class*="css"]  {{
  background-color:{theme['bg']};
  color:{theme['text']};
  font-family:"BIZ UDPGothic","Meiryo",sans-serif;
}}

.block-container {{
  max-width: 900px;
  padding-top: 1.0rem;
  padding-bottom: 2rem;
}}

.main-wrap {{
  max-width: 880px;
  margin: 0 auto;
}}

.title-main {{
  text-align:center;
  font-size:2.1rem;
  font-weight:900;
  margin-bottom:1.0rem;
  letter-spacing:0.02em;
}}

.info-box {{
  background:#F9FBFF;
  border:4px solid #5B84EA;
  border-radius:20px;
  padding:1.15rem 1.25rem 1.0rem 1.25rem;
  margin-bottom:1rem;
}}

.info-title {{
  font-size:1.45rem;
  font-weight:900;
  margin-bottom:0.45rem;
}}

.info-text {{
  font-size:1.02rem;
  line-height:1.8;
}}

.dashed-divider {{
  border-top:2px dashed #C9CEDB;
  margin:0.6rem 0;
}}

.section-card {{
  background:white;
  border-radius:16px;
  box-shadow:0 1px 3px rgba(0,0,0,0.08);
  border:1px solid {theme['border']};
  overflow:hidden;
  margin-bottom:0.8rem;
}}

.section-head {{
  display:flex;
  align-items:center;
  background:#F7F8FC;
  padding:0.8rem 1rem;
  font-weight:900;
  font-size:1.65rem;
}}

.section-head::before {{
  content:"";
  display:inline-block;
  width:10px;
  height:2.0rem;
  border-radius:6px;
  background:{theme['accent']};
  margin-right:0.8rem;
}}

.section-sub {{
  padding:0 1rem 0.9rem 1rem;
  font-weight:700;
  color:#333;
  font-size:1.02rem;
}}

.subsection-wrap {{
  margin-top:0.55rem;
  margin-bottom:0.55rem;
}}

.subsection-head {{
  background:#EEF2FB;
  border-radius:8px;
  padding:0.5rem 0.9rem;
  font-weight:900;
  font-size:1.3rem;
  margin-bottom:0.65rem;
}}

.card {{
  background:white;
  border-radius:14px;
  border:1px solid {theme['border']};
  box-shadow:0 1px 2px rgba(0,0,0,0.04);
  padding:0.8rem 0.9rem;
  margin-bottom:0.6rem;
}}

.score-title {{
  font-size:1.25rem;
  font-weight:900;
  margin-bottom:0.45rem;
}}

.score-inline {{
  font-size:1.45rem;
  font-weight:900;
  line-height:1.0;
}}

.score-inline small {{
  font-size:0.95rem;
  font-weight:700;
  color:#444;
}}

.track {{
  width:100%;
  height:14px;
  background:{theme['track']};
  border-radius:999px;
  overflow:hidden;
}}

.fill {{
  height:100%;
  border-radius:999px;
}}

.note-box {{
  background:white;
  border:1px solid {theme['border']};
  border-radius:14px;
  box-shadow:0 1px 2px rgba(0,0,0,0.04);
  padding:0.9rem 1rem;
  margin-top:0.5rem;
  margin-bottom:0.75rem;
}}

.note-title {{
  font-weight:900;
  font-size:1.12rem;
  margin-bottom:0.35rem;
}}

.note-box ul {{
  margin-top:0.25rem;
  margin-bottom:0;
  padding-left:1.3rem;
}}

.note-box li {{
  margin-bottom:0.28rem;
  line-height:1.7;
}}

.perma-mini-wrap {{
  background:white;
  border:1px solid {theme['border']};
  border-radius:6px;
  display:flex;
  justify-content:center;
  align-items:center;
  padding:0.2rem;
  width:100%;
}}

.mini-perma-label {{
  text-align:center;
  font-size:0.68rem;
  color:#555;
  margin-bottom:0.1rem;
}}

.strength-check {{
  font-size:1.08rem;
  font-weight:900;
  margin-bottom:0.2rem;
}}

.recommend-box {{
  background:white;
  border-radius:14px;
  border:1px solid {theme['border']};
  padding:0.6rem 0.8rem;
  margin-bottom:0.45rem;
}}

.recommend-heading {{
  font-size:1.22rem;
  font-weight:900;
  margin-bottom:0.3rem;
}}

.recommend-box ul {{
  margin-top:0.1rem;
  margin-bottom:0.1rem;
  padding-left:1.35rem;
}}

.recommend-box li {{
  line-height:1.8;
  margin-bottom:0.1rem;
}}

.illust-box {{
  display:flex;
  justify-content:center;
  align-items:flex-start;
  padding-top:0.6rem;
  font-size:4.4rem;
}}

.footer-area {{
  border-top:2px solid #D8DCE5;
  margin-top:1rem;
  padding-top:0.9rem;
  font-size:1.02rem;
  line-height:1.8;
}}

.footer-area .footer-title {{
  font-size:1.06rem;
  font-weight:900;
  margin-bottom:0.25rem;
}}

.reference-box {{
  background:white;
  border:1px solid {theme['border']};
  border-radius:14px;
  padding:0.8rem 1rem;
  margin-top:0.55rem;
}}

.reference-title {{
  font-weight:900;
  margin-bottom:0.3rem;
}}

.force-break {{
  display:block;
  height:0;
}}

.spacer-6 {{ height:6px; }}
.spacer-10 {{ height:10px; }}
.spacer-14 {{ height:14px; }}

@media print {{
  @page {{ size:A4; margin:8mm; }}

  .force-break {{
    break-before:page !important;
    page-break-before:always !important;
  }}

  img {{
    max-height:72px !important;
  }}
}}
</style>
""", unsafe_allow_html=True)

# =========================
# ラベル定義
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
    "M": "人生に目的・人生に目的や価値を感じて生きている状態です。",
    "A": "努力し、達成感や成長を感じられている状態です。",
}

# =========================
# ユーティリティ
# =========================
def safe_float(x, default=np.nan):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def clamp_score(x, lo=0.0, hi=10.0):
    x = safe_float(x, np.nan)
    if np.isnan(x):
        return np.nan
    return max(lo, min(hi, x))


def compute_domain_avg(vals, idx):
    scores = [vals[i] for i in idx if i < len(vals) and pd.notna(vals[i])]
    return float(np.mean(scores)) if scores else np.nan


def FORCE_PAGE_BREAK():
    st.markdown('<div class="force-break"></div>', unsafe_allow_html=True)


def page_header(title: str, subtitle: Optional[str] = None):
    st.markdown(
        f"""
        <div class="section-card">
          <div class="section-head">{title}</div>
          {"<div class='section-sub'>" + subtitle + "</div>" if subtitle else ""}
        </div>
        """,
        unsafe_allow_html=True
    )


def section_subheader(text: str):
    st.markdown(f'<div class="subsection-head">{text}</div>', unsafe_allow_html=True)


# =========================
# Excel読込
# =========================
def load_scores_from_excel(uploaded_file):
    df = pd.read_excel(uploaded_file)
    if df.empty:
        raise ValueError("Excelファイルが空です。")

    required_cols = ["ID"] + [f"6_{i}" for i in range(1, 24)]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"必要な列が不足しています: {', '.join(missing)}")
    return df


def calc_scores_from_row(row: pd.Series):
    vals = [safe_float(row[f"6_{i}"], np.nan) for i in range(1, 24)]

    domain_scores = {
        "P": compute_domain_avg(vals, [0, 1, 2]),
        "E": compute_domain_avg(vals, [3, 4, 5]),
        "R": compute_domain_avg(vals, [6, 7, 8]),
        "M": compute_domain_avg(vals, [9, 10, 11]),
        "A": compute_domain_avg(vals, [12, 13, 14]),
    }

    overall_happiness = safe_float(row["6_16"])
    negative_emotion = np.nanmean([safe_float(row["6_17"]), safe_float(row["6_18"]), safe_float(row["6_19"])])
    loneliness = safe_float(row["6_20"])
    physical_health = np.nanmean([safe_float(row["6_21"]), safe_float(row["6_22"]), safe_float(row["6_23"])])
    overall_wellbeing = np.nanmean([domain_scores[k] for k in ["P", "E", "R", "M", "A"]] + [overall_happiness])

    domain_scores = {k: clamp_score(v) for k, v in domain_scores.items()}
    extra_scores = {
        "心の健康の総合得点": clamp_score(overall_wellbeing),
        "からだの調子": clamp_score(physical_health),
        "気持ちの様子（いやな気持）": clamp_score(negative_emotion),
        "全体的なしあわせ感": clamp_score(overall_happiness),
        "ひとりぼっち感": clamp_score(loneliness),
    }
    return domain_scores, extra_scores


def get_strengths_and_growth(domain_scores: dict):
    valid = [(k, safe_float(v, np.nan)) for k, v in domain_scores.items()]
    valid = [(k, v) for k, v in valid if not np.isnan(v)]
    if not valid:
        return [], []
    sorted_scores = sorted(valid, key=lambda x: x[1], reverse=True)
    strengths = sorted_scores[:2]
    growth = sorted_scores[:2:-1]  # not used
    lowest_two = sorted(valid, key=lambda x: x[1])[:2]
    return strengths, lowest_two

# =========================
# 描画関数
# =========================
def render_score_bar_only(score: float, color: str):
    score = clamp_score(score)
    width_percent = 0 if np.isnan(score) else score * 10
    st.markdown(
        f"""
        <div class="track">
          <div class="fill" style="width:{width_percent:.1f}%; background:{color};"></div>
        </div>
        <div class="score-inline" style="margin-top:0.35rem;">{score:.1f}<small>/10点</small></div>
        """,
        unsafe_allow_html=True
    )


def render_mini_perma_chart(domain_scores: dict):
    order = ["P", "E", "R", "M", "A"]
    vals = [0 if np.isnan(domain_scores.get(k, np.nan)) else domain_scores.get(k, 0) for k in order]
    cols = [colors[k] for k in order]

    fig, ax = plt.subplots(figsize=(2.3, 1.55), dpi=200)
    x = np.arange(len(order))
    ax.bar(x, vals, color=cols, width=0.62)
    ax.set_ylim(0, 10)
    ax.set_xticks(x)
    ax.set_xticklabels(order, fontsize=7)
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color("#CCCCCC")
        spine.set_linewidth(0.8)

    for i, v in enumerate(vals):
        ax.text(i, v + 0.18, f"{v:.0f}", ha="center", va="bottom", fontsize=6)

    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    plt.tight_layout(pad=0.4)
    st.markdown('<div class="mini-perma-label">PERMA</div>', unsafe_allow_html=True)
    st.markdown('<div class="perma-mini-wrap">', unsafe_allow_html=True)
    st.pyplot(fig, use_container_width=False)
    st.markdown('</div>', unsafe_allow_html=True)
    plt.close(fig)


def render_note_box_page1():
    st.markdown(
        """
        <div class="note-box">
          <div class="note-title">各指標の見方</div>
          <ul>
            <li><b>P（前向きな気持ち）</b>：楽しい気持ちや安心感、感謝など前向きな感情の豊かさを示します。</li>
            <li><b>E（集中して取り組むこと）</b>：物事に没頭したり夢中になって取り組める状態を示します。</li>
            <li><b>R（人とのつながり）</b>：支え合えるつながりや信頼関係を感じられている状態です。</li>
            <li><b>M（生きがいや目的）</b>：人生に目的や価値を感じて生きている状態です。</li>
            <li><b>A（達成感）</b>：努力し、達成感や成長を感じられている状態です。</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_note_box_page2():
    st.markdown(
        """
        <div class="note-box">
          <div class="note-title">各指標の意味</div>
          <ul>
            <li><b>気持ちの様子（いやな気持）</b>：不安になったり、気分が沈んだり、いらいらしたりすることがどのくらいあるかによる結果です。</li>
            <li><b>からだの調子</b>：体の調子や元気さについて、ご本人が感じた程度の結果です。</li>
            <li><b>ひとりぼっち感</b>：ひとりぼっちだと感じることがあるかの結果です。</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_remarks_box():
    st.markdown(
        """
        <div class="info-box" style="margin-top:0.2rem;">
          <div class="info-title" style="font-size:1.15rem; color:#4E73DF;">このチェックで見ていること</div>
          <div class="info-text">
            この用紙は、心の元気さを <b>5つの面（PERMA）</b> で見る方法をもとにしています。<br>
            5つの面をそれぞれ見ることで、「どこが保てているか」「どこを整えるとよさそうか」を考えやすくします。
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="note-box">
          <div class="note-title">① PERMA（5つの面）とは</div>
          <ul>
            <li><b>P：前向きな気持ち</b>（うれしさ・安心・満足など）</li>
            <li><b>E：集中して取り組むこと</b>（夢中になって時間を忘れるような没頭＝フロー）</li>
            <li><b>R：人とのつながり</b>（支えられている・大切にされている感覚）</li>
            <li><b>M：生きがいや目的</b>（家族・地域・趣味・目標など「自分にとって大切なもの」）</li>
            <li><b>A：達成感</b>（大きな成果だけでなく、毎日のやることをこなせた感覚も含みます）</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="note-box">
          <div class="note-title">② この尺度（PERMA-Profiler）について</div>
          <ul>
            <li>研究では、PERMAを短い質問で測れるように PERMA-Profiler が開発されています。</li>
            <li>PERMAの15問（5つ×3問）に、追加の8問（気持ちの様子／からだの調子／ひとりぼっち感／全体的なしあわせ感など）を加えた、合計23問の形式です。</li>
            <li>点数は0〜10点で、たとえば7/10点は「だいたい7割くらい」と考えると分かりやすいです。</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="note-box">
          <div class="note-title">③ 結果の使い方（おすすめ）</div>
          <ul>
            <li><b>高いところ</b>：今の強み（保てている部分）</li>
            <li><b>低いところ</b>：疲れや環境の影響が出ているかもしれない部分（整えるヒント）</li>
            <li>1回で決めつけず、時々くり返して変化（上がった／下がった）を見ると役立ちます。</li>
            <li>「つらさが強い」「生活が大変」などが続く場合は、身近な人や専門職に相談するきっかけにもなります。</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="reference-box">
          <div class="reference-title">引用（根拠）</div>
          Butler, J., &amp; Kern, M. L. (2016). <i>The PERMA-Profiler: A brief multidimensional measure of flourishing.</i><br>
          <i>International Journal of Wellbeing</i>, 6(3), 1–48. https://doi.org/10.5502/ijw.v6i3.526
        </div>
        """,
        unsafe_allow_html=True
    )


def render_intro_box():
    st.markdown(
        """
        <div class="info-box">
          <div class="info-title">はじめに（この用紙でわかること）</div>
          <div class="info-text">
            この用紙は、心の健康チェックの結果です。<br>
            今の心の元気さを、0〜10点でわかりやすく見える化しています。
            <ul style="margin-top:0.35rem; margin-bottom:0.2rem;">
              <li>心の5つの元気さ（前向きな気持ち／集中して取り組むこと／人とのつながり／生きがいや目的／達成感）</li>
              <li>心の健康の総合得点、気持ちの様子（いやな気持）、からだの調子、ひとりぼっち感、全体的なしあわせ感</li>
            </ul>
            <div class="dashed-divider"></div>
            ※これは病気の診断ではありません。今の自分の状態を知るための目安としてご利用ください。
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_strengths(strengths):
    for key, score in strengths:
        st.markdown(
            f'<div class="strength-check">✓ {full_labels.get(key, key)}（{key}）</div>',
            unsafe_allow_html=True
        )
        render_score_bar_only(score, colors.get(key, theme["accent"]))
        st.markdown("<div class='spacer-10'></div>", unsafe_allow_html=True)


def recommendation_bullets(key: str):
    recs = {
        "P": [
            "感謝の気持ちをメモしてみる（感謝を書き出す）",
            "今日の良かったことを振り返る",
        ],
        "E": [
            "少しでも集中できた時間を見つけて増やす",
            "好きな作業を短時間でも続けてみる",
        ],
        "R": [
            "身近な人へのあいさつや声かけを増やす",
            "安心して話せる人との時間を少しつくる",
        ],
        "M": [
            "大切にしている価値を書き出す",
            "経験から学びを見つける",
        ],
        "A": [
            "小さな目標を1つ決めてみる",
            "できたことを毎日1つ振り返る",
        ],
    }
    return recs.get(key, ["無理のない範囲で、日常の中の小さな行動を積み重ねてみましょう。"])


def render_growth(growth):
    left, right = st.columns([1.55, 0.65], gap="medium")
    with left:
        for key, score in growth:
            emoji = {"P": "😊", "M": "🌱", "E": "✨", "R": "🤝", "A": "🏆"}.get(key, "🌱")
            st.markdown(
                f"""
                <div class="recommend-box">
                  <div class="recommend-heading">{emoji} {full_labels.get(key, key)}（{key}）</div>
                  <ul>
                    {''.join([f'<li>{item}</li>' for item in recommendation_bullets(key)])}
                  </ul>
                </div>
                """,
                unsafe_allow_html=True
            )
    with right:
        st.markdown('<div class="illust-box">🙌</div>', unsafe_allow_html=True)

# =========================
# メイン
# =========================
st.markdown('<div class="title-main">わらトレ　心の健康チェック</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Excelファイルを添付してください", type=["xlsx", "xls"])

if uploaded_file is None:
    st.info("Excelファイルをアップロードすると結果が表示されます。")
    st.stop()

try:
    df = load_scores_from_excel(uploaded_file)
except Exception as e:
    st.error(f"Excelの読み込みでエラーが出ました: {e}")
    st.stop()

id_list = df["ID"].dropna().astype(str).tolist()
if not id_list:
    st.error("ID列に有効なデータがありません。")
    st.stop()

selected_id = st.selectbox("結果を表示するIDを選んでください", id_list)

selected_row = df[df["ID"].astype(str) == selected_id]
if selected_row.empty:
    st.error("選択したIDのデータが見つかりません。")
    st.stop()

row = selected_row.iloc[0]
domain_scores, extra_scores = calc_scores_from_row(row)
strengths, growth = get_strengths_and_growth(domain_scores)

# =========================
# 1ページ目
# =========================
render_intro_box()

page_header("1. 結果（あなたの心の状態）", "心の5つの元気さと、こころ・からだの今の状態を点数で確認します。")

st.markdown('<div class="subsection-wrap">', unsafe_allow_html=True)
section_subheader("1-1. 要素ごとにみた心の状態")

left_grid, right_grid = st.columns([2.2, 2.2], gap="small")
with left_grid:
    for key in ["P", "E", "R"]:
        st.markdown(f'<div class="card"><div class="score-title">{key}：{full_labels[key]}</div>', unsafe_allow_html=True)
        render_score_bar_only(domain_scores.get(key, np.nan), colors[key])
        st.markdown('</div>', unsafe_allow_html=True)

with right_grid:
    top_left, top_right = st.columns([1.65, 1.0], gap="small")
    with top_left:
        st.markdown(f'<div class="card"><div class="score-title">M：{full_labels["M"]}</div>', unsafe_allow_html=True)
        render_score_bar_only(domain_scores.get("M", np.nan), colors["M"])
        st.markdown('</div>', unsafe_allow_html=True)

    with top_right:
        st.markdown('<div class="card" style="padding:0.45rem 0.5rem;">', unsafe_allow_html=True)
        render_mini_perma_chart(domain_scores)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="card"><div class="score-title">A：{full_labels["A"]}</div>', unsafe_allow_html=True)
    render_score_bar_only(domain_scores.get("A", np.nan), colors["A"])
    st.markdown('</div>', unsafe_allow_html=True)

render_note_box_page1()
st.markdown('</div>', unsafe_allow_html=True)

# =========================
# 2ページ目
# =========================
FORCE_PAGE_BREAK()

st.markdown('<div class="subsection-wrap">', unsafe_allow_html=True)
section_subheader("1-2. こころ・からだの調子")

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="score-title">心の健康の総合得点</div>', unsafe_allow_html=True)
render_score_bar_only(extra_scores.get("心の健康の総合得点", np.nan), extra_colors["心の健康の総合得点"])
st.markdown('</div>', unsafe_allow_html=True)

col_a, col_b = st.columns(2, gap="small")
with col_a:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="score-title">からだの調子</div>', unsafe_allow_html=True)
    render_score_bar_only(extra_scores.get("からだの調子", np.nan), extra_colors["からだの調子"])
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="score-title">気持ちの様子（いやな気持）</div>', unsafe_allow_html=True)
    render_score_bar_only(extra_scores.get("気持ちの様子（いやな気持）", np.nan), extra_colors["気持ちの様子（いやな気持）"])
    st.markdown('</div>', unsafe_allow_html=True)

with col_b:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="score-title">全体的なしあわせ感</div>', unsafe_allow_html=True)
    render_score_bar_only(extra_scores.get("全体的なしあわせ感", np.nan), extra_colors["全体的なしあわせ感"])
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="score-title">ひとりぼっち感</div>', unsafe_allow_html=True)
    render_score_bar_only(extra_scores.get("ひとりぼっち感", np.nan), extra_colors["ひとりぼっち感"])
    st.markdown('</div>', unsafe_allow_html=True)

render_note_box_page2()
st.markdown('</div>', unsafe_allow_html=True)

page_header("2. あなたの結果に基づく、強みとおすすめな行動", "結果からみたご本人の強みと、日常生活でおすすめできることをまとめます。")

section_subheader("2-1. 満たされている心の健康の要素（強み）")
render_strengths(strengths)

section_subheader("2-2. これから伸ばせる要素と具体的な行動例")
render_growth(growth)

# =========================
# 3ページ目
# =========================
FORCE_PAGE_BREAK()

page_header("3. 備考", "この評価に関する詳しい情報は以下の通りです。")
render_remarks_box()

st.markdown(
    """
    <div class="footer-area">
      <div class="footer-title">この評価結果に関するお問い合わせは以下まで</div>
      <div><b>〈お問い合わせ先〉</b> 〒474-0037</div>
      <div>愛知県大府市半月町三丁目294番地</div>
      <div>☎ 0562-44-5551　研究代表者：李 相侖</div>
      <div style="margin-top:0.4rem; font-weight:900;">この度は、ご協力ありがとうございました。</div>
    </div>
    """,
    unsafe_allow_html=True
)
