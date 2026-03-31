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
# CSS（画面用 + 印刷/PDF用）
# =========================
st.markdown(f"""
<style>
html, body {{
  background-color:{theme['bg']};
  color:{theme['text']};
  font-family:"BIZ UDPGothic","Meiryo",sans-serif;
  line-height:1.55;
}}

section.main > div {{ padding-top: 1rem; padding-bottom: 1rem; }}
.block-container {{ padding-top: 1rem; padding-bottom: 1rem; }}
div[data-testid="stVerticalBlock"] {{ gap: 0.65rem; }}
div[data-testid="stMarkdownContainer"] p {{ margin: 0.25rem 0 0.35rem 0; }}
div[data-testid="stMarkdownContainer"] ul {{ margin: 0.35rem 0 0.35rem 1.2rem; }}
div[data-testid="stMarkdownContainer"] li {{ margin: 0.18rem 0; }}

.main-wrap {{ max-width: 880px; margin: 0 auto; }}

h1 {{
  text-align:center;
  font-size:2rem;
  font-weight:900;
  margin-top:0.4rem;
  margin-bottom:0.4rem;
}}

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
  background: white;
  border: 2px solid #E6EAF5;
  border-left: 10px solid {theme['accent']};
  border-radius: 14px;
  padding: 1.0rem 1.2rem;
  margin: 0.9rem 0 0.9rem 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}}
.page-header .title {{
  font-size: 1.45rem;
  font-weight: 950;
  color: #1b2a4a;
  margin-bottom: 0.15rem;
}}
.page-header .sub {{
  font-size: 1.02rem;
  color: #223;
}}

.score-card {{
  background:white;
  border-radius:12px;
  padding:0.55rem 0.9rem;
  margin-bottom:0.55rem;
  box-shadow:0 1px 3px rgba(0,0,0,0.06);
}}
.score-title {{
  font-weight:800;
  margin-bottom:0.2rem;
}}

.meter {{
  background:#E0E0E0;
  border-radius:999px;
  height:14px;
  width:100%;
  overflow:hidden;
}}
.meter-fill {{ height:100%; border-radius:999px; }}

.meter-score-text {{
  font-size: 1.05rem;
  margin-top: 4px;
  color:#333;
}}
.meter-score-text .score-strong {{
  font-size: 1.28rem;
  font-weight: 1000;
  letter-spacing: 0.2px;
  color:#111;
}}

.score-card.big {{
  padding: 0.75rem 1.0rem;
}}
.meter.big {{
  height: 22px;
}}
.meter-score-text.big .score-strong {{
  font-size: 1.45rem;
}}
.score-title.big {{
  font-size: 1.08rem;
  font-weight: 950;
  margin-bottom: 0.25rem;
}}

.perma-box {{
  border:3px solid {theme['accent']};
  border-radius:12px;
  padding:1.05rem 1.25rem;
  margin-top:0.5rem;
  background:white;
}}
.perma-box p {{
  font-size:1.04rem;
  color:#222;
  margin-bottom:0.75rem;
  line-height: 1.7;
}}
.perma-highlight {{
  color:{theme['accent']};
  font-weight:900;
}}

.intro-box {{
  background: #F7FAFF;
  border: 3px solid {theme['accent']};
  border-radius: 16px;
  padding: 1.1rem 1.3rem;
  margin: 0.9rem 0 1.1rem 0;
  box-shadow: 0 3px 10px rgba(0,0,0,0.08);
}}
.intro-title {{
  font-size: 1.20rem;
  font-weight: 1000;
  color: #1b2a4a;
  margin-bottom: 0.45rem;
}}
.intro-text {{
  font-size: 1.05rem;
  color: #111;
  line-height: 1.75;
}}
.intro-list {{
  margin: 0.5rem 0 0.3rem 0;
  padding-left: 1.3rem;
}}
.intro-list li {{
  margin-bottom: 0.3rem;
}}
.intro-note {{
  margin-top: 0.5rem;
  padding-top: 0.4rem;
  border-top: 1px dashed #999;
  color: #333;
  font-size: 1.0rem;
}}

.mini-note {{
  background: #FFFFFF;
  border: 1px solid #E6EAF5;
  border-radius: 12px;
  padding: 0.65rem 0.85rem;
  margin: 0.55rem 0 0.65rem 0;
}}
.mini-note .cap {{
  font-weight: 900;
  color: #1b2a4a;
  font-size: 0.98rem;
  margin-bottom: 0.25rem;
}}
.mini-note .txt {{
  font-size: 0.98rem;
  color: #222;
  line-height: 1.65;
}}
.mini-note ul {{
  margin: 0.35rem 0 0.1rem 1.1rem;
}}
.mini-note li {{
  margin: 0.14rem 0;
}}

.cite-box {{
  background: #FBFBFD;
  border: 1px solid #E6EAF5;
  border-radius: 12px;
  padding: 0.75rem 0.9rem;
  margin-top: 0.7rem;
  color: #333;
}}
.cite-box .cap {{
  font-weight: 900;
  color: #1b2a4a;
  margin-bottom: 0.25rem;
}}
.cite-box .ref {{
  font-size: 0.95rem;
  line-height: 1.6;
}}

.footer-box {{
  border-top: 2px solid #DDD;
  margin-top: 1.6rem;
  padding-top: 1.0rem;
  font-size: 0.98rem;
  color: #333;
  line-height: 1.8;
}}
.footer-title {{
  font-weight: 900;
  margin-bottom: 0.4rem;
}}
.footer-thanks {{
  margin-top: 0.85rem;
  font-weight: 800;
}}

.keep-together {{}}
.force-page-break {{ display:none; }}

@media print {{

  @page {{
    size: A4;
    margin: 8mm;
  }}

  html, body {{
    background: white !important;
  }}

  * {{
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }}

  .print-page {{
    break-after: page !important;
    page-break-after: always !important;
  }}

  .print-page:last-child {{
    break-after: auto !important;
    page-break-after: auto !important;
  }}

  .force-page-break {{
    display:block !important;
    break-before: page !important;
    page-break-before: always !important;
    height: 0 !important;
  }}

  body {{
    margin-top: -4mm !important;
  }}

  h1 {{
    font-size: 1.55rem !important;
    margin-top: 0.05rem !important;
    margin-bottom: 0.15rem !important;
  }}

  .page-header {{
    padding: 0.6rem 0.85rem !important;
    margin: 0.4rem 0 0.4rem 0 !important;
  }}

  .section-header {{
    font-size: 1.0rem !important;
    padding: 0.35rem 0.75rem !important;
    margin-top: 0.45rem !important;
    margin-bottom: 0.35rem !important;
  }}

  .score-card {{
    padding: 0.4rem 0.65rem !important;
    margin-bottom: 0.28rem !important;
  }}

  .meter {{ height: 11px !important; }}

  .meter-score-text {{
    font-size: 0.88rem !important;
  }}

  .meter-score-text .score-strong {{
    font-size: 1.0rem !important;
  }}

  .mini-note {{
    padding: 0.5rem 0.7rem !important;
    margin: 0.35rem 0 0.35rem 0 !important;
  }}

  .mini-note .cap {{
    font-size: 0.9rem !important;
  }}

  .mini-note .txt {{
    font-size: 0.9rem !important;
    line-height: 1.45 !important;
  }}

  .mini-note li {{
    margin: 0.1rem 0 !important;
  }}

  img {{
    max-height: 140px !important;
    object-fit: contain !important;
  }}

  .perma-box {{
    padding: 0.7rem 0.9rem !important;
  }}

  .perma-box p {{
    font-size: 0.9rem !important;
    line-height: 1.45 !important;
    margin-bottom: 0.4rem !important;
  }}

  .cite-box {{
    padding: 0.5rem 0.7rem !important;
    font-size: 0.85rem !important;
  }}

  .footer-box {{
    margin-top: 0.8rem !important;
    padding-top: 0.5rem !important;
    font-size: 0.85rem !important;
  }}

  .footer-thanks {{
    margin-top: 0.4rem !important;
  }}

  .page-header, .score-card, .intro-box, .mini-note, .cite-box {{
    box-shadow: none !important;
  }}

  .no-print {{
    display: none !important;
  }}
}}
</style>
""", unsafe_allow_html=True)

# =========================
# 定義（表示用）
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
    "P": ["感謝の気持ちをメモしてみる（感謝を書き出す）", "今日の良かったことを振り返る"],
    "E": ["小さな挑戦を設定する", "得意なことを活かす"],
    "R": ["感謝を伝える", "小さな親切をする"],
    "M": ["大切にしている価値を書き出す", "経験から学びを見つける"],
    "A": ["小さな目標を作る", "失敗を学びと捉える"],
}
action_emojis = {"P": "😊", "E": "🧩", "R": "🤝", "M": "🌱", "A": "🏁"}

extras_explanations = {
    "不安やいらいら感": "不安になったり、気分が沈んだり、いらいらしたりすることがどのくらいあるかにおける結果です。",
    "からだの調子": "体の調子や元気さについて、ご本人が感じた程度の結果です。",
    "ひとりぼっち感": "ひとりぼっちだと感じることがあるかの結果です。",
}

# =========================
# 換算
# =========================
perma_indices = {
    "P": [4, 9, 21],
    "E": [2, 10, 20],
    "R": [5, 14, 18],
    "M": [0, 8, 16],
    "A": [1, 7, 15],
}

extra_indices = {
    "気持ちの様子（いやな気持）": [6, 13, 19],
    "からだの調子":  [3, 12, 17],
    "ひとりぼっち感": [11],
    "全体的なしあわせ感": [22],
}

# =========================
# 計算関数
# =========================
def compute_domain_avg(vals: np.ndarray, idx: list[int]) -> float:
    scores = [vals[i] for i in idx if i < len(vals) and not np.isnan(vals[i])]
    return float(np.mean(scores)) if scores else np.nan

def compute_results(row: pd.DataFrame):
    cols = [c for c in row.columns if str(c).startswith("6_")]
    cols = sorted(cols, key=lambda x: int(str(x).split("_")[1]))
    vals = pd.to_numeric(row[cols].values.flatten(), errors="coerce")

    perma = {k: compute_domain_avg(vals, v) for k, v in perma_indices.items()}
    extras = {k: compute_domain_avg(vals, v) for k, v in extra_indices.items()}

    perma_15_indices = sorted({i for idxs in perma_indices.values() for i in idxs})
    overall_wellbeing_indices = perma_15_indices + [22]
    extras["心の健康の総合得点"] = compute_domain_avg(vals, overall_wellbeing_indices)

    return perma, extras

def score_label(v: float) -> str:
    if np.isnan(v):
        return "未回答"
    return f"{v:.1f}/10点"

# =========================
# 表示関数
# =========================
def render_meter_block(title: str, score: float, color: Optional[str] = None, big: bool = False):
    if np.isnan(score):
        width = "0%"
        score_html = "未回答"
    else:
        width = f"{score * 10:.0f}%"
        score_html = f"<span class='score-strong'>{score:.1f}</span>/10点"
    bar_color = color if color is not None else "#999999"

    big_class = "big" if big else ""
    meter_class = "meter big" if big else "meter"
    score_class = "meter-score-text big" if big else "meter-score-text"
    title_class = "score-title big" if big else "score-title"

    st.markdown(
        f"""
        <div class="score-card {big_class}">
          <div class="{title_class}">{title}</div>
          <div class="{meter_class}">
            <div class="meter-fill" style="width:{width}; background:{bar_color};"></div>
          </div>
          <div class="{score_class}">{score_html}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def plot_hist(perma_scores: dict):
    labels = ["P", "E", "R", "M", "A"]
    values = [perma_scores.get(k, np.nan) for k in labels]
    fig, ax = plt.subplots(figsize=(2.9, 2.25), dpi=160)
    ax.bar(labels, values, color=[colors[k] for k in labels])
    ax.set_ylim(0, 10)
    ax.set_yticks([])
    ax.set_title("PERMA", fontsize=12)
    for i, v in enumerate(values):
        if not np.isnan(v):
            ax.text(i, v + 0.22, f"{v:.1f}", ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    st.pyplot(fig)

def page_header(title: str, sub: str):
    st.markdown(
        f"""
        <div class="page-header">
          <div class="title">{title}</div>
          <div class="sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_intro_box():
    st.markdown(
        """
        <div class="intro-box">
          <div class="intro-title">はじめに（この用紙でわかること）</div>
          <div class="intro-text">
            この用紙は、<b>心の健康チェック</b>の結果です。<br>
            <b>今の心の元気さ</b>を、0〜10点でわかりやすく見える化しています。
            <ul class="intro-list">
              <li><b>心の5つの元気さ</b>（前向きな気持ち／集中して取り組むこと／人とのつながり／生きがいや目的／達成感）</li>
              <li><b>心の健康の総合得点</b>、<b>気持ちの様子（いやな気持）</b>、<b>からだの調子</b>、<b>ひとりぼっち感</b>、<b>全体的なしあわせ感</b></li>
            </ul>
            <div class="intro-note">
              ※これは病気の診断ではありません。<b>今の自分の状態を知るための目安</b>としてご利用ください。
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_perma_howto_note():
    st.markdown(
        f"""
        <div class="mini-note">
          <div class="cap">各指標の見方</div>
          <div class="txt">
            <ul>
              <li><b>P（前向きな気持ち）</b>：{descriptions["P"]}</li>
              <li><b>E（集中して取り組むこと）</b>：{descriptions["E"]}</li>
              <li><b>R（人とのつながり）</b>：{descriptions["R"]}</li>
              <li><b>M（生きがいや目的）</b>：{descriptions["M"]}</li>
              <li><b>A（達成感）</b>：{descriptions["A"]}</li>
            </ul>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_extras_meaning_note():
    st.markdown(
        f"""
        <div class="mini-note">
          <div class="cap">各指標の意味</div>
          <div class="txt">
            <ul>
              <li><b>気持ちの様子（いやな気持）</b>：{extras_explanations["気持ちの様子（いやな気持）"]}</li>
              <li><b>からだの調子</b>：{extras_explanations["からだの調子"]}</li>
              <li><b>ひとりぼっち感</b>：{extras_explanations["ひとりぼっち感"]}</li>
            </ul>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_remarks_box():
    st.markdown(
        f"""
        <div class="perma-box">
          <p><span class="perma-highlight">このチェックで見ていること</span></p>
          <p>
            この用紙は、心の元気さを <span class="perma-highlight">5つの面（PERMA）</span> で見る方法をもとにしています。<br>
            5つの面をそれぞれ見ることで、「どこが保てているか」「どこを整えるとよさそうか」を考えやすくします。
          </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="mini-note">
          <div class="cap">① PERMA（5つの面）とは</div>
          <div class="txt">
            <ul>
              <li><b>P</b>：前向きな気持ち（うれしさ・安心・満足など）</li>
              <li><b>E</b>：集中して取り組むこと（夢中になって時間を忘れるような没頭＝フロー）</li>
              <li><b>R</b>：人とのつながり（支えられている・大切にされている感覚）</li>
              <li><b>M</b>：生きがいや目的（家族・地域・趣味・目標など「自分にとって大切なもの」）</li>
              <li><b>A</b>：達成感（大きな成果だけでなく、毎日のやることをこなせた感覚も含みます）</li>
            </ul>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="mini-note">
          <div class="cap">② この尺度（PERMA-Profiler）について</div>
          <div class="txt">
            <ul>
              <li>研究では、PERMAを短い質問で測れるように <b>PERMA-Profiler</b> が開発されています。</li>
              <li><b>PERMAの15問</b>（5つ×各3問）に、<b>追加の8問</b>（気持ちの様子／からだの調子／ひとりぼっち感／全体的なしあわせ感 など）を加えた、合計<b>23問</b>の形式です。</li>
              <li>点数は<b>0〜10点</b>で、たとえば<b>7/10点</b>は「だいたい7割くらい」と考えると分かりやすいです。</li>
            </ul>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="mini-note">
          <div class="cap">③ 結果の使い方（おすすめ）</div>
          <div class="txt">
            <ul>
              <li><b>高いところ</b>：今の強み（保てている部分）</li>
              <li><b>低いところ</b>：疲れや環境の影響が出ているかもしれない部分（整えるヒント）</li>
              <li>1回で決めつけず、時々くり返して<b>変化</b>（上がった／下がった）を見ると役立ちます。</li>
              <li>「つらさが強い」「生活が大変」などが続く場合は、身近な人や専門職に相談する<b>きっかけ</b>にもなります。</li>
            </ul>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="cite-box">
          <div class="cap">引用（根拠）</div>
          <div class="ref">
            Butler, J., &amp; Kern, M. L. (2016). <i>The PERMA-Profiler: A brief multidimensional measure of flourishing</i>.
            <i>International Journal of Wellbeing</i>, 6(3), 1–48. https://doi.org/10.5502/ijw.v6i3.526
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================
# セッション
# =========================
if "ready" not in st.session_state:
    st.session_state.ready = False
if "df" not in st.session_state:
    st.session_state.df = None
if "sid" not in st.session_state:
    st.session_state.sid = None

ui = st.empty()

if not st.session_state.ready:
    with ui.container():
        st.markdown('<div class="main-wrap no-print">', unsafe_allow_html=True)
        st.title("わらトレ　心の健康チェック")
        uploaded = st.file_uploader(
            "Excelファイル（ID列＋6_1〜6_23 の列）をアップロードしてください",
            type="xlsx"
        )
        if uploaded:
            df = pd.read_excel(uploaded)
            id_list = df.iloc[:, 0].dropna().astype(str).tolist()
            sid = st.selectbox("IDを選んでください", options=id_list)
            if st.button("このIDで結果を表示"):
                st.session_state.df = df
                st.session_state.sid = sid
                st.session_state.ready = True
                st.rerun()
    st.stop()

ui.empty()

# =========================
# 結果表示
# =========================
st.markdown('<div class="main-wrap">', unsafe_allow_html=True)
st.title("わらトレ　心の健康チェック")
render_intro_box()

df = st.session_state.df
sid = st.session_state.sid
row = df[df.iloc[:, 0].astype(str) == str(sid)]
if row.empty:
    st.warning("選択されたIDが見つかりません。最初からやり直してください。")
    st.session_state.ready = False
    st.rerun()

perma_scores, extras = compute_results(row)

# =========================================================
# 1枚目：1-1 + 各指標の見方 まで
# =========================================================
st.markdown("<div class='print-page page-1'>", unsafe_allow_html=True)
page_header("1. 結果（あなたの心の状態）", "心の5つの元気さと、こころ・からだの今の状態を点数で確認します。")

st.markdown('<div class="section-header">1-1. 要素ごとにみた心の状態</div>', unsafe_allow_html=True)
col_meter, col_chart = st.columns([2, 1])
with col_meter:
    col_left, col_right = st.columns(2)
    with col_left:
        for k in ["P", "E", "R"]:
            render_meter_block(f"{k}：{full_labels[k]}", perma_scores.get(k, np.nan), colors[k])
    with col_right:
        for k in ["M", "A"]:
            render_meter_block(f"{k}：{full_labels[k]}", perma_scores.get(k, np.nan), colors[k])
with col_chart:
    plot_hist(perma_scores)

render_perma_howto_note()

# ★ ここで1ページ目を閉じる
st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 2枚目：1-2 こころ・からだの調子 から必ず開始
# =========================================================
st.markdown("<div class='print-page page-2'>", unsafe_allow_html=True)

st.markdown('<div class="section-header">1-2. こころ・からだの調子</div>', unsafe_allow_html=True)

render_meter_block(
    "心の健康の総合得点",
    extras.get("心の健康の総合得点", np.nan),
    extra_colors["心の健康の総合得点"],
    big=True
)

grid_order = [
    ("からだの調子", "からだの調子"),
    ("全体的なしあわせ感", "全体的なしあわせ感"),
    ("気持ちの様子（いやな気持）", "気持ちの様子（いやな気持）"),
    ("ひとりぼっち感", "ひとりぼっち感"),
]
cL, cR = st.columns(2)
for i, (key, label) in enumerate(grid_order):
    v = extras.get(key, np.nan)
    col = cL if i % 2 == 0 else cR
    with col:
        render_meter_block(label, v, extra_colors.get(key, None))

render_extras_meaning_note()

st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 3枚目
# =========================================================
st.markdown("<div class='print-page page-3'>", unsafe_allow_html=True)

page_header(
    "2. あなたの結果に基づく、強みとおすすめな行動",
    "結果からみたご本人の強みと、日常生活でおすすめできることをまとめます。"
)

weak_keys = [k for k, v in perma_scores.items() if not np.isnan(v) and v <= 5]
strong_keys = [k for k, v in perma_scores.items() if not np.isnan(v) and v >= 7]

if strong_keys:
    st.markdown('<div class="section-header">2-1. 満たされている心の健康の要素（強み）</div>', unsafe_allow_html=True)
    for k in strong_keys:
        render_meter_block(
            f"✔ {full_labels[k]}（{k}）",
            perma_scores.get(k, np.nan),
            colors[k],
            big=False
        )

if weak_keys:
    st.markdown('<div class="section-header">2-2. これから伸ばせる要素と具体的な行動例</div>', unsafe_allow_html=True)
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

st.markdown("<div class='force-page-break'></div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 4枚目
# =========================================================
st.markdown("<div class='print-page page-4'>", unsafe_allow_html=True)
page_header("3. 備考", "この評価に関する詳しい情報は以下の通りです。")

render_remarks_box()

st.markdown(
    """
    <div class="footer-box">
      <div class="footer-title">この評価結果に関するお問い合わせは以下まで</div>
      <div>
        〈お問い合わせ先〉〒 474-0037<br>
        愛知県大府市半月町三丁目294番地<br>
        ☎ 0562-44-5551　研究代表者：李 相侖
      </div>
      <div class="footer-thanks">
        この度は、ご協力ありがとうございました。
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("</div>", unsafe_allow_html=True)  # print-page end
st.markdown("</div>", unsafe_allow_html=True)  # main-wrap end
