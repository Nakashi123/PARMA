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
  line-height:1.5;
}}

section.main > div {{ padding-top: 0.5rem; padding-bottom: 0.5rem; }}
.block-container {{ padding-top: 0.6rem; padding-bottom: 0.8rem; }}
div[data-testid="stVerticalBlock"] {{ gap: 0.45rem; }}
div[data-testid="stMarkdownContainer"] p {{ margin: 0.15rem 0 0.25rem 0; }}
div[data-testid="stMarkdownContainer"] ul {{ margin: 0.2rem 0 0.2rem 1.0rem; }}
div[data-testid="stMarkdownContainer"] li {{ margin: 0.1rem 0; }}

.main-wrap {{
  max-width: 880px;
  margin: 0 auto;
}}

h1 {{
  text-align:center;
  font-size:1.9rem;
  font-weight:900;
  margin-top:0.2rem;
  margin-bottom:0.25rem;
}}

.title-row {{
  display:flex;
  justify-content:space-between;
  align-items:center;
  gap:1rem;
  margin:0.2rem 0 0.4rem 0;
  padding:0.1rem 0;
}}

.title-row .main-title {{
  font-size:1.9rem;
  font-weight:950;
  color:#1b2a4a;
  line-height:1.2;
}}

.title-row .id-chip {{
  flex-shrink:0;
  background:#FFFFFF;
  border:2px solid #D8E3F8;
  border-radius:999px;
  padding:0.32rem 0.85rem;
  font-size:0.95rem;
  font-weight:800;
  color:#2A3B5F;
  white-space:nowrap;
}}

.section-header {{
  background:{theme['bar_bg']};
  font-weight:900;
  font-size:1.08rem;
  padding:.45rem .9rem;
  border-left:7px solid {theme['accent']};
  border-radius:8px;
  margin-top:0.35rem;
  margin-bottom:.45rem;
}}

.page-header {{
  background: white;
  border: 2px solid #E6EAF5;
  border-left: 9px solid {theme['accent']};
  border-radius: 12px;
  padding: 0.7rem 0.95rem;
  margin: 0.35rem 0 0.45rem 0;
  box-shadow: 0 1px 5px rgba(0,0,0,0.05);
}}
.page-header .title {{
  font-size: 1.2rem;
  font-weight: 950;
  color: #1b2a4a;
  margin-bottom: 0.05rem;
}}
.page-header .sub {{
  font-size: 0.96rem;
  color: #223;
}}

.score-card {{
  background:white;
  border-radius:10px;
  padding:0.42rem 0.72rem;
  margin-bottom:0.34rem;
  box-shadow:0 1px 3px rgba(0,0,0,0.06);
}}
.score-title {{
  font-weight:850;
  font-size:0.98rem;
  margin-bottom:0.14rem;
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
  font-size: 1.08rem;
  margin-top: 4px;
  color:#333;
}}
.meter-score-text .score-strong {{
  font-size: 1.55rem;
  font-weight: 1000;
  letter-spacing: 0.2px;
  color:#111;
}}

.score-card.big {{
  padding: 0.55rem 0.82rem;
}}
.score-title.big {{
  font-size: 1.02rem;
  font-weight: 950;
  margin-bottom: 0.18rem;
}}
.meter.big {{
  height: 19px;
}}
.meter-score-text.big {{
  font-size: 1.14rem;
}}
.meter-score-text.big .score-strong {{
  font-size: 1.75rem;
}}

.mini-note {{
  background: #FFFFFF;
  border: 1px solid #E6EAF5;
  border-radius: 11px;
  padding: 0.5rem 0.72rem;
  margin: 0.35rem 0 0.3rem 0;
}}
.mini-note .cap {{
  font-weight: 900;
  color: #1b2a4a;
  font-size: 0.94rem;
  margin-bottom: 0.18rem;
}}
.mini-note .txt {{
  font-size: 0.94rem;
  color: #222;
  line-height: 1.5;
}}
.mini-note ul {{
  margin: 0.2rem 0 0.05rem 1.0rem;
}}
.mini-note li {{
  margin: 0.08rem 0;
}}

.perma-box {{
  border:2px solid {theme['accent']};
  border-radius:12px;
  padding:0.75rem 0.95rem;
  margin-top:0.3rem;
  background:white;
}}
.perma-box p {{
  font-size:0.96rem;
  color:#222;
  margin-bottom:0.4rem;
  line-height:1.55;
}}
.perma-highlight {{
  color:{theme['accent']};
  font-weight:900;
}}

.cite-box {{
  background: #FBFBFD;
  border: 1px solid #E6EAF5;
  border-radius: 10px;
  padding: 0.55rem 0.75rem;
  margin-top: 0.35rem;
  color: #333;
}}
.cite-box .cap {{
  font-weight: 900;
  color: #1b2a4a;
  margin-bottom: 0.15rem;
}}
.cite-box .ref {{
  font-size: 0.9rem;
  line-height: 1.45;
}}

.footer-box {{
  border-top: 2px solid #DDD;
  margin-top: 0.9rem;
  padding-top: 0.65rem;
  font-size: 0.92rem;
  color: #333;
  line-height: 1.6;
}}
.footer-title {{
  font-weight: 900;
  margin-bottom: 0.25rem;
}}
.footer-thanks {{
  margin-top: 0.5rem;
  font-weight: 800;
}}

.action-list p,
.action-list li {{
  font-size: 0.98rem;
  line-height: 1.45;
}}

.print-page {{
  background: transparent;
}}

.page-note {{
  font-size: 0.92rem;
  color: #333;
  margin-top: 0.1rem;
}}

.no-print {{
  display: block;
}}

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

  .no-print {{
    display:none !important;
  }}

  .main-wrap {{
    max-width: none !important;
  }}

  body {{
    margin-top: -2mm !important;
  }}

  .title-row {{
    margin: 0 0 0.2rem 0 !important;
  }}

  .title-row .main-title {{
    font-size: 1.45rem !important;
  }}

  .title-row .id-chip {{
    font-size: 0.78rem !important;
    padding: 0.18rem 0.55rem !important;
    border-width: 1.4px !important;
  }}

  .page-header {{
    padding: 0.45rem 0.65rem !important;
    margin: 0.2rem 0 0.28rem 0 !important;
  }}
  .page-header .title {{
    font-size: 1.0rem !important;
    margin-bottom: 0 !important;
  }}
  .page-header .sub {{
    font-size: 0.82rem !important;
  }}

  .section-header {{
    font-size: 0.95rem !important;
    padding: 0.26rem 0.62rem !important;
    margin-top: 0.2rem !important;
    margin-bottom: 0.25rem !important;
  }}

  .score-card {{
    padding: 0.28rem 0.48rem !important;
    margin-bottom: 0.18rem !important;
    border-radius: 8px !important;
    box-shadow: none !important;
  }}

  .score-title {{
    font-size: 0.82rem !important;
    margin-bottom: 0.08rem !important;
  }}

  .score-title.big {{
    font-size: 0.86rem !important;
  }}

  .meter {{
    height: 10px !important;
  }}

  .meter.big {{
    height: 14px !important;
  }}

  .meter-score-text {{
    font-size: 0.92rem !important;
    margin-top: 2px !important;
  }}

  .meter-score-text .score-strong {{
    font-size: 1.22rem !important;
  }}

  .meter-score-text.big {{
    font-size: 0.98rem !important;
  }}

  .meter-score-text.big .score-strong {{
    font-size: 1.34rem !important;
  }}

  .mini-note {{
    padding: 0.34rem 0.5rem !important;
    margin: 0.2rem 0 0.18rem 0 !important;
    border-radius: 8px !important;
    box-shadow: none !important;
  }}

  .mini-note .cap {{
    font-size: 0.82rem !important;
    margin-bottom: 0.08rem !important;
  }}

  .mini-note .txt {{
    font-size: 0.8rem !important;
    line-height: 1.28 !important;
  }}

  .mini-note ul {{
    margin: 0.12rem 0 0.02rem 0.92rem !important;
  }}

  .mini-note li {{
    margin: 0.04rem 0 !important;
  }}

  .perma-box {{
    padding: 0.45rem 0.62rem !important;
    margin-top: 0.15rem !important;
  }}

  .perma-box p {{
    font-size: 0.82rem !important;
    line-height: 1.35 !important;
    margin-bottom: 0.2rem !important;
  }}

  .cite-box {{
    padding: 0.38rem 0.52rem !important;
    margin-top: 0.2rem !important;
    border-radius: 8px !important;
    box-shadow: none !important;
  }}

  .cite-box .cap {{
    font-size: 0.82rem !important;
  }}

  .cite-box .ref {{
    font-size: 0.76rem !important;
    line-height: 1.28 !important;
  }}

  .footer-box {{
    margin-top: 0.45rem !important;
    padding-top: 0.35rem !important;
    font-size: 0.78rem !important;
    line-height: 1.35 !important;
  }}

  .footer-title {{
    margin-bottom: 0.15rem !important;
  }}

  .footer-thanks {{
    margin-top: 0.25rem !important;
  }}

  .action-list p,
  .action-list li {{
    font-size: 0.84rem !important;
    line-height: 1.3 !important;
  }}

  .page-note {{
    font-size: 0.78rem !important;
  }}

  img {{
    max-height: 110px !important;
    object-fit: contain !important;
  }}

  div[data-testid="stImage"] img {{
    max-height: 110px !important;
    object-fit: contain !important;
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
    "気持ちの様子（いやな気持）": "不安になったり、気分が沈んだり、いらいらしたりすることがどのくらいあるかにおける結果です。",
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
    "からだの調子": [3, 12, 17],
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

# =========================
# 表示関数
# =========================
def render_title_row_with_id(title: str, sid: str):
    st.markdown(
        f"""
        <div class="title-row">
          <div class="main-title">{title}</div>
          <div class="id-chip">ID：{sid}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

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
    fig, ax = plt.subplots(figsize=(2.55, 1.95), dpi=160)
    ax.bar(labels, values, color=[colors[k] for k in labels])
    ax.set_ylim(0, 10)
    ax.set_yticks([])
    ax.set_title("PERMA", fontsize=11, pad=3)
    for i, v in enumerate(values):
        if not np.isnan(v):
            ax.text(i, v + 0.18, f"{v:.1f}", ha="center", va="bottom", fontsize=8)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis='x', labelsize=9)
    fig.tight_layout(pad=0.6)
    st.pyplot(fig, use_container_width=False)

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
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

ui.empty()

# =========================
# データ取得
# =========================
df = st.session_state.df
sid = st.session_state.sid
row = df[df.iloc[:, 0].astype(str) == str(sid)]

if row.empty:
    st.warning("選択されたIDが見つかりません。最初からやり直してください。")
    st.session_state.ready = False
    st.rerun()

perma_scores, extras = compute_results(row)

weak_keys = [k for k, v in perma_scores.items() if not np.isnan(v) and v <= 5]
strong_keys = [k for k, v in perma_scores.items() if not np.isnan(v) and v >= 7]

# =========================
# 結果表示
# =========================
st.markdown('<div class="main-wrap">', unsafe_allow_html=True)

# =========================================================
# 1ページ目：タイトル+ID、1-1、各指標の見方（Aまで）
# =========================================================
st.markdown("<div class='print-page page-1'>", unsafe_allow_html=True)

render_title_row_with_id("わらトレ　心の健康チェック", str(sid))
page_header("1. 結果（あなたの心の状態）", "心の5つの元気さを点数で確認します。")

st.markdown('<div class="section-header">1-1. 要素ごとにみた心の状態</div>', unsafe_allow_html=True)

col_meter, col_chart = st.columns([2.2, 0.9])
with col_meter:
    c1, c2 = st.columns(2)
    with c1:
        for k in ["P", "E", "R"]:
            render_meter_block(f"{k}：{full_labels[k]}", perma_scores.get(k, np.nan), colors[k], big=False)
    with c2:
        for k in ["M", "A"]:
            render_meter_block(f"{k}：{full_labels[k]}", perma_scores.get(k, np.nan), colors[k], big=False)
with col_chart:
    plot_hist(perma_scores)

render_perma_howto_note()

st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 2ページ目：必ず改ページ、1-2〜2-2まで
# =========================================================
st.markdown("<div class='print-page page-2'>", unsafe_allow_html=True)

page_header(
    "2. こころ・からだの調子と、おすすめの行動",
    "こころ・からだの状態と、これから意識しやすい行動例をまとめています。"
)

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

g1, g2 = st.columns(2)
for i, (key, label) in enumerate(grid_order):
    v = extras.get(key, np.nan)
    target_col = g1 if i % 2 == 0 else g2
    with target_col:
        render_meter_block(label, v, extra_colors.get(key, None), big=False)

render_extras_meaning_note()

if strong_keys:
    st.markdown('<div class="section-header">2-1. 満たされている心の健康の要素（強み）</div>', unsafe_allow_html=True)
    s1, s2 = st.columns(2)
    for i, k in enumerate(strong_keys):
        target_col = s1 if i % 2 == 0 else s2
        with target_col:
            render_meter_block(
                f"✔ {full_labels[k]}（{k}）",
                perma_scores.get(k, np.nan),
                colors[k],
                big=False
            )

if weak_keys:
    st.markdown('<div class="section-header">2-2. これから伸ばせる要素と具体的な行動例</div>', unsafe_allow_html=True)
    a1, a2 = st.columns([2.2, 1.0])

    with a1:
        st.markdown('<div class="action-list">', unsafe_allow_html=True)
        for k in weak_keys:
            emoji = action_emojis.get(k, "💡")
            st.markdown(f"**{emoji} {full_labels[k]}（{k}）**")
            for t in tips[k]:
                st.markdown(f"- {t}")
        st.markdown('</div>', unsafe_allow_html=True)

    with a2:
        st.image(
            "https://eiyoushi-hutaba.com/wp-content/uploads/2025/01/%E5%85%83%E6%B0%97%E3%81%AA%E3%82%B7%E3%83%8B%E3%82%A2%E3%81%AE%E4%BA%8C%E4%BA%BA%E3%80%80%E9%81%8B%E5%8B%95%E7%89%88.png",
            use_container_width=True
        )

st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 3ページ目：必ず改ページ、備考のみ
# =========================================================
st.markdown("<div class='print-page page-3'>", unsafe_allow_html=True)

page_header("3. 備考", "この評価に関する詳しい情報です。")
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

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
