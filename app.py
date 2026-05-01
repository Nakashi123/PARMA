# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Optional

st.set_page_config(page_title="わらトレ 心の健康チェック", layout="centered")

plt.rcParams.update({
    "font.sans-serif": ["BIZ UDPGothic", "Meiryo", "Noto Sans JP"],
    "axes.unicode_minus": False,
    "font.size": 12,
})

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

st.markdown(f"""
<style>
html, body {{
  background:{theme["bg"]};
  color:{theme["text"]};
  font-family:"BIZ UDPGothic","Meiryo",sans-serif;
}}

.block-container {{
  padding-top:0.7rem;
  padding-bottom:0.7rem;
  max-width:900px;
}}

.main-wrap {{
  max-width:900px;
  margin:0 auto;
}}

.report-title {{
  text-align:center;
  font-size:1.75rem;
  font-weight:900;
  margin:0.2rem 0 0.6rem 0;
}}

.report-header {{
  display:flex;
  justify-content:space-between;
  align-items:flex-start;
  margin-bottom:0.45rem;
}}

.header-spacer {{
  width:230px;
}}

.name-box {{
  width:230px;
  background:white;
  border:2px solid #C9D4EE;
  border-radius:10px;
  padding:0.55rem 0.75rem;
}}

.name-label {{
  font-size:1rem;
  font-weight:900;
  color:#1b2a4a;
  margin-bottom:0.25rem;
}}

.name-line {{
  height:1.9rem;
  border-bottom:2px solid #8898bf;
}}

.section-header {{
  background:{theme["bar_bg"]};
  font-weight:900;
  font-size:1.08rem;
  padding:.45rem .8rem;
  border-left:7px solid {theme["accent"]};
  border-radius:8px;
  margin-top:0.5rem;
  margin-bottom:.35rem;
}}

.score-card {{
  background:white;
  border:1px solid #E5E9F2;
  border-radius:10px;
  padding:0.5rem 0.7rem;
  margin-bottom:0.32rem;
  break-inside:avoid;
  page-break-inside:avoid;
}}

.score-title {{
  font-weight:900;
  font-size:0.98rem;
  margin-bottom:0.14rem;
  line-height:1.3;
}}

.score-title.big {{
  font-size:1.08rem;
}}

.meter {{
  background:#E4E7ED;
  border-radius:999px;
  height:12px;
  width:100%;
  overflow:hidden;
}}

.meter.big {{
  height:17px;
}}

.meter-fill {{
  height:100%;
  border-radius:999px;
}}

.meter-score-text {{
  font-size:0.9rem;
  margin-top:3px;
  color:#333;
  line-height:1.15;
}}

.score-strong {{
  font-size:2.05rem;
  font-weight:1000;
  color:#111;
}}

.meter-score-text.big .score-strong {{
  font-size:2.35rem;
}}

.simple-note,
.mini-note,
.perma-box,
.cite-box {{
  background:white;
  border:1px solid #E6EAF5;
  border-radius:10px;
  padding:0.65rem 0.85rem;
  margin:0.35rem 0;
  font-size:0.92rem;
  line-height:1.55;
  break-inside:avoid;
  page-break-inside:avoid;
}}

.mini-note .cap,
.cite-box .cap {{
  font-weight:900;
  color:#1b2a4a;
  font-size:0.96rem;
  margin-bottom:0.2rem;
}}

.mini-note ul {{
  margin:0.2rem 0 0.05rem 1.1rem;
}}

.mini-note li {{
  margin:0.08rem 0;
}}

.perma-box {{
  border:2px solid {theme["accent"]};
}}

.perma-highlight {{
  color:{theme["accent"]};
  font-weight:900;
}}

.cite-box .ref {{
  font-size:0.82rem;
  line-height:1.45;
}}

.footer-box {{
  border-top:2px solid #DDD;
  margin-top:0.5rem;
  padding-top:0.45rem;
  font-size:0.82rem;
  color:#333;
  line-height:1.45;
}}

.footer-title {{
  font-weight:900;
}}

.footer-thanks {{
  margin-top:0.25rem;
  font-weight:900;
}}

.action-title {{
  font-size:1.15rem;
  font-weight:900;
  margin:0.35rem 0 0.15rem 0;
}}

.action-list {{
  margin:0 0 0.25rem 1.1rem;
  font-size:0.92rem;
  line-height:1.45;
}}

.print-page {{
  background:white;
}}

.no-print {{
  display:block;
}}

@media print {{

  @page {{
    size:A4 portrait;
    margin:8mm 9mm 8mm 9mm;
  }}

  html, body {{
    background:white !important;
  }}

  * {{
    -webkit-print-color-adjust:exact !important;
    print-color-adjust:exact !important;
  }}

  .no-print {{
    display:none !important;
  }}

  header,
  footer,
  [data-testid="stHeader"],
  [data-testid="stToolbar"],
  [data-testid="stDecoration"],
  [data-testid="stStatusWidget"] {{
    display:none !important;
  }}

  .block-container {{
    max-width:none !important;
    padding:0 !important;
  }}

  .main-wrap {{
    max-width:none !important;
    margin:0 !important;
  }}

  .print-page {{
    height:281mm !important;
    box-sizing:border-box !important;
    overflow:hidden !important;
    break-after:page !important;
    page-break-after:always !important;
    padding:0 !important;
  }}

  .print-page:last-child {{
    break-after:auto !important;
    page-break-after:auto !important;
  }}

  .report-title {{
    font-size:1.55rem !important;
    margin:0 0 0.45rem 0 !important;
  }}

  .report-header {{
    margin-bottom:0.25rem !important;
  }}

  .name-box {{
    width:215px !important;
    padding:0.45rem 0.65rem !important;
  }}

  .name-label {{
    font-size:0.9rem !important;
  }}

  .name-line {{
    height:1.55rem !important;
  }}

  .section-header {{
    font-size:0.98rem !important;
    padding:0.38rem 0.65rem !important;
    margin-top:0.38rem !important;
    margin-bottom:0.25rem !important;
  }}

  .score-card {{
    padding:0.42rem 0.55rem !important;
    margin-bottom:0.22rem !important;
  }}

  .score-title {{
    font-size:0.88rem !important;
  }}

  .meter {{
    height:10px !important;
  }}

  .meter.big {{
    height:14px !important;
  }}

  .meter-score-text {{
    font-size:0.78rem !important;
    margin-top:2px !important;
  }}

  .score-strong {{
    font-size:1.75rem !important;
  }}

  .meter-score-text.big .score-strong {{
    font-size:2.0rem !important;
  }}

  .simple-note,
  .mini-note,
  .perma-box,
  .cite-box {{
    font-size:0.78rem !important;
    line-height:1.42 !important;
    padding:0.48rem 0.65rem !important;
    margin:0.25rem 0 !important;
  }}

  .mini-note .cap,
  .cite-box .cap {{
    font-size:0.82rem !important;
  }}

  .mini-note ul {{
    margin:0.12rem 0 0 1rem !important;
  }}

  .cite-box .ref {{
    font-size:0.72rem !important;
  }}

  .footer-box {{
    font-size:0.72rem !important;
    line-height:1.35 !important;
    margin-top:0.35rem !important;
    padding-top:0.35rem !important;
  }}

  .action-title {{
    font-size:0.95rem !important;
    margin:0.22rem 0 0.08rem 0 !important;
  }}

  .action-list {{
    font-size:0.78rem !important;
    line-height:1.35 !important;
    margin-bottom:0.12rem !important;
  }}

  img {{
    max-height:120px !important;
    object-fit:contain !important;
  }}

  div[data-testid="stVerticalBlock"] {{
    gap:0.18rem !important;
  }}
}}
</style>
""", unsafe_allow_html=True)

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
    "P": ["感謝の気持ちをメモしてみる", "今日の良かったことを振り返る"],
    "E": ["小さな挑戦を設定する", "得意なことを活かす"],
    "R": ["感謝を伝える", "小さな親切をする"],
    "M": ["大切にしている価値を書き出す", "経験から学びを見つける"],
    "A": ["小さな目標を作る", "失敗を学びと捉える"],
}

action_emojis = {
    "P": "😊",
    "E": "🧩",
    "R": "🤝",
    "M": "🌱",
    "A": "🏁",
}

extras_explanations = {
    "気持ちの様子（いやな気持）": "不安になったり、気分が沈んだり、いらいらしたりすることがどのくらいあるかにおける結果です。",
    "からだの調子": "体の調子や元気さについて、ご本人が感じた程度の結果です。",
    "ひとりぼっち感": "ひとりぼっちだと感じることがあるかの結果です。",
}

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

def render_meter_block(title: str, score: float, color: Optional[str] = None, big: bool = False):
    if np.isnan(score):
        width = "0%"
        score_html = "未回答"
    else:
        width = f"{score * 10:.0f}%"
        score_html = f"<span class='score-strong'>{score:.1f}</span>/10点"

    bar_color = color if color is not None else "#999999"
    meter_class = "meter big" if big else "meter"
    score_class = "meter-score-text big" if big else "meter-score-text"
    title_class = "score-title big" if big else "score-title"

    st.markdown(
        f"""
        <div class="score-card">
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

    fig, ax = plt.subplots(figsize=(2.15, 1.55), dpi=150)
    ax.bar(labels, values, color=[colors[k] for k in labels])
    ax.set_ylim(0, 10)
    ax.set_yticks([])
    ax.set_title("PERMA", fontsize=10)

    for i, v in enumerate(values):
        if not np.isnan(v):
            ax.text(i, v + 0.18, f"{v:.1f}", ha="center", va="bottom", fontsize=8)

    fig.tight_layout(pad=0.35)
    st.pyplot(fig)

def render_name_box():
    st.markdown(
        """
        <div class="name-box">
          <div class="name-label">氏名</div>
          <div class="name-line"></div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_report_header(show_name: bool = True):
    st.markdown('<div class="report-header">', unsafe_allow_html=True)
    st.markdown('<div class="header-spacer"></div>', unsafe_allow_html=True)
    st.markdown('<div class="report-title">わらトレ　心の健康チェック</div>', unsafe_allow_html=True)
    if show_name:
        render_name_box()
    else:
        st.markdown('<div class="header-spacer"></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_intro_box():
    st.markdown(
        """
        <div class="simple-note">
          <b>はじめに（この用紙でわかること）</b><br>
          この用紙は、心の健康チェックの結果です。
          今の心の元気さを、0〜10点で確認できます。
          点数が高いところは「今の強み」、低いところは「これから整えるヒント」としてご覧ください。
        </div>
        """,
        unsafe_allow_html=True
    )

def render_perma_howto_note():
    st.markdown(
        f"""
        <div class="mini-note">
          <div class="cap">各指標の見方</div>
          <ul>
            <li><b>P（前向きな気持ち）</b>：{descriptions["P"]}</li>
            <li><b>E（集中して取り組むこと）</b>：{descriptions["E"]}</li>
            <li><b>R（人とのつながり）</b>：{descriptions["R"]}</li>
            <li><b>M（生きがいや目的）</b>：{descriptions["M"]}</li>
            <li><b>A（達成感）</b>：{descriptions["A"]}</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_extras_meaning_note():
    st.markdown(
        f"""
        <div class="mini-note">
          <div class="cap">各指標の意味</div>
          <ul>
            <li><b>気持ちの様子（いやな気持）</b>：{extras_explanations["気持ちの様子（いやな気持）"]}</li>
            <li><b>からだの調子</b>：{extras_explanations["からだの調子"]}</li>
            <li><b>ひとりぼっち感</b>：{extras_explanations["ひとりぼっち感"]}</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_remarks_box():
    st.markdown(
        """
        <div class="perma-box">
          <p><span class="perma-highlight">このチェックで見ていること</span></p>
          <p>
            この用紙は、心の元気さを <span class="perma-highlight">5つの面（PERMA）</span> で見る方法をもとにしています。
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
          <ul>
            <li><b>P</b>：前向きな気持ち（うれしさ・安心・満足など）</li>
            <li><b>E</b>：集中して取り組むこと（夢中になって時間を忘れるような没頭）</li>
            <li><b>R</b>：人とのつながり（支えられている・大切にされている感覚）</li>
            <li><b>M</b>：生きがいや目的（家族・地域・趣味・目標など）</li>
            <li><b>A</b>：達成感（毎日のやることをこなせた感覚も含みます）</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="mini-note">
          <div class="cap">② この尺度（PERMA-Profiler）について</div>
          <ul>
            <li>研究では、PERMAを短い質問で測れるように <b>PERMA-Profiler</b> が開発されています。</li>
            <li><b>PERMAの15問</b>に、<b>追加の8問</b>を加えた、合計<b>23問</b>の形式です。</li>
            <li>点数は<b>0〜10点</b>で、たとえば<b>7/10点</b>は「だいたい7割くらい」と考えると分かりやすいです。</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="mini-note">
          <div class="cap">③ 結果の使い方（おすすめ）</div>
          <ul>
            <li><b>高いところ</b>：今の強み（保てている部分）</li>
            <li><b>低いところ</b>：疲れや環境の影響が出ているかもしれない部分（整えるヒント）</li>
            <li>くり返して確認し、<b>変化</b>（上がった／下がった）を見ると役立ちます。</li>
            <li>つらさが強い場合は、身近な人や専門職に相談する<b>きっかけ</b>にもなります。</li>
          </ul>
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
        st.markdown('<div class="report-title">わらトレ　心の健康チェック</div>', unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "Excelファイル（ID列＋6_1〜6_23 の列）をアップロードしてください",
            type="xlsx"
        )

        if uploaded:
            df = pd.read_excel(uploaded)
            id_list = df.iloc[:, 0].dropna().astype(str).tolist()

            if len(id_list) == 0:
                st.error("ID列に有効な値がありません。")
            else:
                sid = st.selectbox("IDを選んでください", options=id_list)

                if st.button("このIDで結果を表示"):
                    st.session_state.df = df
                    st.session_state.sid = sid
                    st.session_state.ready = True
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

ui.empty()

st.markdown('<div class="main-wrap">', unsafe_allow_html=True)

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

# 1ページ目：1-1 + 1-2
st.markdown("<div class='print-page page-1'>", unsafe_allow_html=True)

render_report_header(show_name=True)
render_intro_box()

st.markdown('<div class="section-header">1-1. 要素ごとにみた心の状態</div>', unsafe_allow_html=True)

col_meter, col_chart = st.columns([2.35, 0.9])

with col_meter:
    left_col, right_col = st.columns(2)

    with left_col:
        for k in ["P", "E", "R"]:
            render_meter_block(f"{k}：{full_labels[k]}", perma_scores.get(k, np.nan), colors[k])

    with right_col:
        for k in ["M", "A"]:
            render_meter_block(f"{k}：{full_labels[k]}", perma_scores.get(k, np.nan), colors[k])

with col_chart:
    plot_hist(perma_scores)

render_perma_howto_note()

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
    with (cL if i % 2 == 0 else cR):
        render_meter_block(label, extras.get(key, np.nan), extra_colors.get(key))

render_extras_meaning_note()

st.markdown("</div>", unsafe_allow_html=True)

# 2ページ目：2-1 + 2-2
st.markdown("<div class='print-page page-2'>", unsafe_allow_html=True)

st.markdown('<div class="section-header">2-1. 満たされている心の健康の要素（強み）</div>', unsafe_allow_html=True)

if strong_keys:
    for k in strong_keys:
        render_meter_block(
            f"✓ {full_labels[k]}（{k}）",
            perma_scores.get(k, np.nan),
            colors[k]
        )
else:
    st.markdown(
        """
        <div class="simple-note">
          今回は、7点以上の項目はありませんでした。<br>
          ただし、どの項目も今後の変化を見る上で大切な手がかりになります。
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown('<div class="section-header">2-2. これから伸ばせる要素と具体的な行動例</div>', unsafe_allow_html=True)

if weak_keys:
    c1, c2 = st.columns([2.15, 0.85])

    with c1:
        st.markdown(
            """
            <div class="simple-note">
              点数が低めだったところは、悪い結果ではありません。<br>
              これから少しずつ整えていける「ヒント」として見てください。
            </div>
            """,
            unsafe_allow_html=True
        )

        for k in weak_keys:
            emoji = action_emojis.get(k, "💡")
            items = "".join([f"<li>{t}</li>" for t in tips[k]])
            st.markdown(
                f"""
                <div class="action-title">{emoji} {full_labels[k]}（{k}）</div>
                <ul class="action-list">{items}</ul>
                """,
                unsafe_allow_html=True
            )

    with c2:
        st.image(
            "https://eiyoushi-hutaba.com/wp-content/uploads/2025/01/%E5%85%83%E6%B0%97%E3%81%AA%E3%82%B7%E3%83%8B%E3%82%A2%E3%81%AE%E4%BA%8C%E4%BA%BA%E3%80%80%E9%81%8B%E5%8B%95%E7%89%88.png",
            use_container_width=True
        )
else:
    st.markdown(
        """
        <div class="simple-note">
          今回は、5点以下の項目はありませんでした。<br>
          今の良い状態を保つことを意識してみてください。
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("</div>", unsafe_allow_html=True)

# 3ページ目：備考
st.markdown("<div class='print-page page-3'>", unsafe_allow_html=True)

st.markdown('<div class="section-header">3. 備考</div>', unsafe_allow_html=True)

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
