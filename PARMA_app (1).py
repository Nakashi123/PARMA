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
  line-height:1.9;
}}
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
.meter-score-text {{ font-size:0.95rem; margin-top:2px; color:#444; }}

.perma-box {{
  border:3px solid {theme['accent']};
  border-radius:12px;
  padding:1.05rem 1.25rem;
  margin-top:0.5rem;
  background:white;
}}
.perma-box p {{
  font-size:1.06rem;
  color:#222;
  margin-bottom:0.85rem;
}}
.perma-highlight {{
  color:{theme['accent']};
  font-weight:900;
}}

/* ===== 冒頭の「かんたん説明」ボックス ===== */
.intro-box {{
  background: #ffffff;
  border: 2px solid #E6EAF5;
  border-left: 10px solid {theme['accent']};
  border-radius: 14px;
  padding: 0.9rem 1.1rem;
  margin: 0.8rem 0 0.9rem 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}}
.intro-title {{
  font-size: 1.10rem;
  font-weight: 950;
  color: #1b2a4a;
  margin-bottom: 0.25rem;
}}
.intro-text {{
  font-size: 1.02rem;
  color: #222;
  line-height: 1.8;
}}
.intro-list {{
  margin: 0.35rem 0 0.15rem 0;
  padding-left: 1.2rem;
}}
.intro-note {{
  margin-top: 0.35rem;
  color: #333;
  font-size: 0.98rem;
}}

/* ===== お問い合わせフッター ===== */
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

/* ===== 3枚目の「5要素説明」を2列にするためのグリッド ===== */
.desc-grid {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}}
.desc-item {{
  background: #fff;
  border-radius: 12px;
  padding: 0.55rem 0.85rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}}
.desc-item .head {{
  display:flex;
  align-items:center;
  gap:8px;
  margin-bottom: 0.15rem;
}}
.desc-item .chip {{
  display:inline-block;
  min-width: 28px;
  text-align:center;
  padding: 3px 8px;
  border-radius: 10px;
  color: white;
  font-weight: 900;
}}
.desc-item .label {{ font-weight: 900; }}
.desc-item .text {{
  font-size: 0.98rem;
  line-height: 1.65;
  color:#222;
}}

@media (max-width: 680px) {{
  .desc-grid {{ grid-template-columns: 1fr; }}
}}

/* ===== 見出し孤立防止（印刷時に効かせる） ===== */
.keep-together {{}}
.force-page-break {{ display:none; }}

@media print {{
  @page {{
    size: A4;
    margin: 10mm;
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

  .page-3 {{
    break-before: page !important;
    page-break-before: always !important;
  }}

  .force-page-break {{
    display:block !important;
    break-before: page !important;
    page-break-before: always !important;
    height: 0 !important;
  }}

  .section-header {{
    break-after: avoid !important;
    page-break-after: avoid !important;
  }}

  .keep-together {{
    break-inside: avoid !important;
    page-break-inside: avoid !important;
  }}

  .page-header, .score-card, .perma-box, .footer-box, .intro-box,
  img, figure,
  div[data-testid="stHorizontalBlock"], div[data-testid="column"],
  .desc-item {{
    break-inside: avoid !important;
    page-break-inside: avoid !important;
  }}

  h1 {{
    font-size: 1.65rem !important;
    margin-top: 0.15rem !important;
    margin-bottom: 0.2rem !important;
  }}

  .page-header {{
    padding: 0.75rem 0.95rem !important;
    margin: 0.55rem 0 0.55rem 0 !important;
  }}
  .page-header .title {{
    font-size: 1.18rem !important;
  }}
  .page-header .sub {{
    font-size: 0.96rem !important;
  }}

  .section-header {{
    font-size: 1.05rem !important;
    padding: 0.45rem 0.85rem !important;
    margin-top: 0.55rem !important;
    margin-bottom: 0.45rem !important;
  }}

  .score-card {{
    padding: 0.45rem 0.75rem !important;
    margin-bottom: 0.35rem !important;
  }}
  .meter {{ height: 12px !important; }}
  .meter-score-text {{ font-size: 0.92rem !important; }}

  .intro-box {{
    padding: 0.75rem 0.95rem !important;
    margin: 0.55rem 0 0.55rem 0 !important;
  }}
  .intro-title {{ font-size: 1.02rem !important; }}
  .intro-text {{ font-size: 0.98rem !important; }}
  .intro-note {{ font-size: 0.95rem !important; }}

  .perma-box {{ padding: 0.85rem 1.05rem !important; }}
  .perma-box p {{
    font-size: 0.98rem !important;
    margin-bottom: 0.55rem !important;
  }}

  .desc-item .text {{
    font-size: 0.94rem !important;
    line-height: 1.55 !important;
  }}

  .footer-box {{
    margin-top: 1.0rem !important;
    padding-top: 0.65rem !important;
    font-size: 0.92rem !important;
  }}
  .footer-thanks {{ margin-top: 0.55rem !important; }}

  .page-header, .score-card, .desc-item, .intro-box {{
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
    "P": ["感謝を書き出す", "今日の良かったことを振り返る"],
    "E": ["小さな挑戦を設定する", "得意なことを活かす"],
    "R": ["感謝を伝える", "小さな親切をする"],
    "M": ["大切にしている価値を書き出す", "経験から学びを見つける"],
    "A": ["小さな目標を作る", "失敗を学びと捉える"],
}
action_emojis = {"P": "😊", "E": "🧩", "R": "🤝", "M": "🌱", "A": "🏁"}

# =========================
# 換算（提示条件を厳密に反映）
# Excel列：6_1〜6_23 を Q1〜Q23 とみなす
# 0始まり index：Qn -> n-1
# =========================
perma_indices = {
    "P": [4, 9, 21],     # Q5, Q10, Q22
    "E": [2, 10, 20],    # Q3, Q11, Q21
    "R": [5, 14, 18],    # Q6, Q15, Q19
    "M": [0, 8, 16],     # Q1, Q9, Q17
    "A": [1, 7, 15],     # Q2, Q8, Q16
}
extra_indices = {
    "こころのつらさ": [6, 13, 19],   # Negative Emotion
    "からだの調子":  [3, 12, 17],   # Physical Health
    "ひとりぼっち感": [11],          # Loneliness
    "全体的なしあわせ感": [22],      # Q23
}

# =========================
# 計算関数
# =========================
def compute_domain_avg(vals: np.ndarray, idx: list[int]) -> float:
    scores = [vals[i] for i in idx if i < len(vals) and not np.isnan(vals[i])]
    return float(np.mean(scores)) if scores else np.nan

def compute_results(row: pd.DataFrame):
    # 6_1〜6_23 を数値順に並べる（列順の崩れ対策）
    cols = [c for c in row.columns if str(c).startswith("6_")]
    cols = sorted(cols, key=lambda x: int(str(x).split("_")[1]))

    vals = pd.to_numeric(row[cols].values.flatten(), errors="coerce")

    # PERMA（5領域）
    perma = {k: compute_domain_avg(vals, v) for k, v in perma_indices.items()}

    # 追加項目（こころ/からだ/ひとりぼっち/しあわせ）
    extras = {k: compute_domain_avg(vals, v) for k, v in extra_indices.items()}

    # 心の健康の総合得点（PERMA15項目 + 全体的なしあわせ感 の16項目平均）
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
def render_meter_block(title: str, score: float, color: Optional[str] = None):
    if np.isnan(score):
        width = "0%"
        score_text = "未回答"
    else:
        width = f"{score * 10:.0f}%"
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

def render_desc_grid_html() -> str:
    order = ["P", "E", "R", "M", "A"]
    items = []
    for k in order:
        items.append(
            f'<div class="desc-item">'
            f'<div class="head">'
            f'<span class="chip" style="background:{colors[k]};">{k}</span>'
            f'<span class="label">{full_labels[k]}</span>'
            f'</div>'
            f'<div class="text">{descriptions[k]}</div>'
            f'</div>'
        )
    return '<div class="desc-grid">' + "".join(items) + '</div>'

def render_intro_box():
    st.markdown(
        f"""
        <div class="intro-box">
          <div class="intro-title">この結果用紙は「心の健康チェック」です</div>
          <div class="intro-text">
            このチェックは <b>PERMA（パーマ）</b>という考え方を使って、<b>今の心の状態</b>を0〜10点で分かりやすく見える化したものです。<br>
            <ul class="intro-list">
              <li><b>心の5つの元気さ</b>（前向きな気持ち／集中／つながり／生きがい／達成感）が分かります。</li>
              <li><b>こころのつらさ</b>や<b>からだの調子</b>、<b>ひとりぼっち感</b>なども一緒に確認できます。</li>
            </ul>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================
# セッション（アップロードUIを消す）
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

# ★ 冒頭に「かんたん説明」を追加
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
# 1枚目
# =========================================================
st.markdown("<div class='print-page page-1'>", unsafe_allow_html=True)
page_header("1. 結果（あなたの心の状態）", "PERMA の5つの要素と、こころ・からだの今の状態を点数で確認します。")

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

st.markdown('<div class="section-header">1-2. こころ・からだの調子</div>', unsafe_allow_html=True)

extras_display_order = [
    ("心の健康の総合得点", "心の健康の総合得点"),
    ("こころのつらさ", "こころのつらさ"),
    ("からだの調子", "からだの調子"),
    ("ひとりぼっち感", "ひとりぼっち感"),
    ("全体的なしあわせ感", "全体的なしあわせ感"),
]

col_ex1, col_ex2 = st.columns(2)
for i, (key, label) in enumerate(extras_display_order):
    v = extras.get(key, np.nan)
    col = col_ex1 if i % 2 == 0 else col_ex2
    with col:
        render_meter_block(label, v, None)

st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 2枚目
# =========================================================
st.markdown("<div class='print-page page-2'>", unsafe_allow_html=True)
page_header("2. 強みとおすすめ行動", "満たされているところを大切にしつつ、これから伸ばせる要素を確認します。")

weak_keys = [k for k, v in perma_scores.items() if not np.isnan(v) and v <= 5]
strong_keys = [k for k, v in perma_scores.items() if not np.isnan(v) and v >= 7]

if strong_keys:
    st.markdown('<div class="section-header">2-1. 満たされている心の健康の要素</div>', unsafe_allow_html=True)
    for k in strong_keys:
        st.write(f"✔ {full_labels[k]}（{k}）：{score_label(perma_scores[k])}")

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
# 3枚目
# =========================================================
st.markdown("<div class='print-page page-3'>", unsafe_allow_html=True)
page_header("3. 備考", "この評価に関する詳しい情報は以下の通りです。")

st.markdown("<div class='keep-together'>", unsafe_allow_html=True)
st.markdown('<div class="section-header">3-1. PERMAとは？</div>', unsafe_allow_html=True)
st.markdown(
    f"""
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
        で構成されており、
        「心が満たされ、前向きに生きられている状態」をとらえるための枠組みです。
      </p>
      <p>
        この結果は診断ではなく、「今の自分の状態を知る」「どうすれば自分らしく過ごせそうか」を
        考えるための資料としてお使いください。
      </p>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='keep-together'>", unsafe_allow_html=True)
st.markdown('<div class="section-header">3-2. 5つの要素のくわしい説明</div>', unsafe_allow_html=True)
st.markdown(render_desc_grid_html(), unsafe_allow_html=True)

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

st.markdown("</div>", unsafe_allow_html=True)  # print-page end
st.markdown("</div>", unsafe_allow_html=True)  # main-wrap end
