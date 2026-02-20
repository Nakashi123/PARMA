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

# 追加指標（見やすさ重視）
extra_colors = {
    "心の健康の総合得点": "#4E73DF",          # 青：総合
    "気持ちの様子（いやな気持）": "#E74C3C",  # 赤：ネガティブ感情（※値は“低い方が良い”）
    "からだの調子": "#2ECC71",               # 緑：健康
    "ひとりぼっち感": "#9B59B6",             # 紫：孤独（※値は“低い方が良い”想定）
    "全体的なしあわせ感": "#F1C40F",          # 黄：幸福感
}

theme = {
    "bg": "#FAFAFA",
    "accent": "#4E73DF",
    "text": "#222",
    "bar_bg": "#EEF2FB",
    "muted": "#58606a",
    "line": "#E6EAF5",
}

# =========================
# 表示テキスト
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
# 換算（Excel列：6_1〜6_23）
# =========================
perma_indices = {
    "P": [4, 9, 21],     # Q5, Q10, Q22
    "E": [2, 10, 20],    # Q3, Q11, Q21
    "R": [5, 14, 18],    # Q6, Q15, Q19
    "M": [0, 8, 16],     # Q1, Q9, Q17
    "A": [1, 7, 15],     # Q2, Q8, Q16
}
extra_indices = {
    "気持ちの様子（いやな気持）": [6, 13, 19],    # Negative Emotion (Q7, Q14, Q20)
    "からだの調子":  [3, 12, 17],                   # Physical Health (Q4, Q13, Q18)
    "ひとりぼっち感": [11],                          # Loneliness (Q12)
    "全体的なしあわせ感": [22],                      # Q23
}

# =========================
# 参考値（“平均”帯の中央に使う）
# ※ Butler & Kern (2016) Appendix の大規模ノルム等（あなたが以前まとめてくれた値）
# ※ ここでは「目安の平均」として提示（比較バーの“平均”マーク）
# =========================
NORM_MEAN = {
    "P": 6.69,
    "E": 7.25,
    "R": 6.90,
    "M": 7.06,
    "A": 7.21,
    "心の健康の総合得点": 7.02,
    "気持ちの様子（いやな気持）": 4.46,
    "からだの調子": 6.94,
    # Loneliness は単項目で資料により値が変動しうるため “表示だけ”に留める（平均マークは空）
    "ひとりぼっち感": np.nan,
    "全体的なしあわせ感": np.nan,
}

# =========================
# CSS（配布用っぽい “帯＋ブロック完結” を意識）
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

.main-wrap {{ max-width: 920px; margin: 0 auto; }}

h1 {{
  text-align:center;
  font-size:2rem;
  font-weight:900;
  margin-top:0.35rem;
  margin-bottom:0.35rem;
}}

.section-header {{
  background:{theme['bar_bg']};
  font-weight:900;
  font-size:1.12rem;
  padding:.55rem 1rem;
  border-left:8px solid {theme['accent']};
  border-radius:10px;
  margin-top:0.9rem;
  margin-bottom:.65rem;
}}

.page-header {{
  background: white;
  border: 2px solid {theme['line']};
  border-left: 10px solid {theme['accent']};
  border-radius: 14px;
  padding: 0.95rem 1.1rem;
  margin: 0.85rem 0 0.85rem 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}}

.header-grid {{
  display: grid;
  grid-template-columns: 1fr 260px;
  gap: 12px;
  align-items: stretch;
}}
@media (max-width: 860px) {{
  .header-grid {{ grid-template-columns: 1fr; }}
}}

.header-title {{
  font-size: 1.55rem;
  font-weight: 1000;
  color: #1b2a4a;
  margin-bottom: 0.15rem;
}}
.header-sub {{
  font-size: 1.02rem;
  color: {theme['muted']};
}}

.side-band {{
  background: linear-gradient(180deg, {theme['accent']} 0%, #3559b8 100%);
  color: white;
  border-radius: 14px;
  padding: 0.85rem 0.85rem;
  border: 2px solid rgba(255,255,255,0.25);
}}
.side-band .t {{
  font-weight: 1000;
  font-size: 1.05rem;
  letter-spacing: 0.3px;
  margin-bottom: 0.35rem;
}}
.side-band .meta {{
  font-size: 0.95rem;
  line-height: 1.55;
  opacity: 0.95;
}}
.meta-row {{
  display:flex;
  justify-content: space-between;
  gap: 10px;
}}
.meta-key {{ opacity: 0.85; }}
.meta-val {{ font-weight: 900; }}

.intro-box {{
  background: #F7FAFF;
  border: 3px solid {theme['accent']};
  border-radius: 16px;
  padding: 1.0rem 1.15rem;
  margin: 0.8rem 0 1.0rem 0;
  box-shadow: 0 3px 10px rgba(0,0,0,0.08);
}}
.intro-title {{
  font-size: 1.16rem;
  font-weight: 1000;
  color: #1b2a4a;
  margin-bottom: 0.45rem;
}}
.intro-text {{
  font-size: 1.02rem;
  color: #111;
  line-height: 1.75;
}}
.intro-note {{
  margin-top: 0.5rem;
  padding-top: 0.4rem;
  border-top: 1px dashed #999;
  color: #333;
  font-size: 0.98rem;
}}

.score-card {{
  background:white;
  border-radius:14px;
  padding:0.65rem 0.9rem;
  margin-bottom:0.55rem;
  box-shadow:0 1px 3px rgba(0,0,0,0.06);
  border: 1px solid {theme['line']};
}}
.score-head {{
  display:flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 0.25rem;
}}
.score-title {{
  font-weight:950;
  font-size: 1.02rem;
  color:#1b2a4a;
}}
.rank-badge {{
  min-width: 48px;
  text-align:center;
  padding: 4px 10px;
  border-radius: 999px;
  font-weight: 1000;
  font-size: 0.95rem;
  color: white;
}}
.rank-stars {{
  font-size: 0.98rem;
  color: #f1c40f;
  letter-spacing: 1px;
  margin-left: 8px;
}}

.meter {{
  background:#E0E0E0;
  border-radius:999px;
  height:14px;
  width:100%;
  overflow:hidden;
}}
.meter-fill {{ height:100%; border-radius:999px; }}

/* ① 点数を大きく＆太字 */
.meter-score-text {{
  font-size: 1.05rem;
  margin-top: 5px;
  color:#333;
}}
.meter-score-text .score-strong {{
  font-size: 1.30rem;
  font-weight: 1000;
  color:#111;
}}

/* ③ 総合バー（太く長い） */
.score-card.big {{
  padding: 0.85rem 1.0rem;
}}
.meter.big {{
  height: 22px;
}}
.meter-score-text.big .score-strong {{
  font-size: 1.55rem;
}}
.score-title.big {{
  font-size: 1.10rem;
  font-weight: 1000;
}}

/* ④ 比較バー（低い〜平均〜高い） */
.posbar {{
  position: relative;
  height: 12px;
  border-radius: 999px;
  overflow: hidden;
  margin-top: 10px;
  border: 1px solid {theme['line']};
}}
.posbar .seg1 {{ position:absolute; left:0; top:0; height:100%; width:33.4%; background:#E8EEF9; }}
.posbar .seg2 {{ position:absolute; left:33.4%; top:0; height:100%; width:33.2%; background:#F3F6FB; }}
.posbar .seg3 {{ position:absolute; left:66.6%; top:0; height:100%; width:33.4%; background:#FFF5DD; }}
.posbar .marker {{
  position:absolute; top:-2px;
  width: 3px; height: 16px;
  background: #111;
  border-radius: 2px;
}}
.posbar .mean {{
  position:absolute; top:-2px;
  width: 3px; height: 16px;
  background: {theme['accent']};
  border-radius: 2px;
  opacity: 0.85;
}}
.posbar-labels {{
  display:flex;
  justify-content: space-between;
  font-size: 0.86rem;
  color: {theme['muted']};
  margin-top: 4px;
}}

/* 凡例カード（判定1〜5） */
.legend-box {{
  background: white;
  border: 1px solid {theme['line']};
  border-radius: 14px;
  padding: 0.7rem 0.85rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}}
.legend-box .cap {{
  font-weight: 1000;
  color:#1b2a4a;
  margin-bottom: 0.25rem;
}}
.legend-box .row {{
  display:flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items:center;
  color:#333;
  font-size: 0.96rem;
}}
.pill {{
  border-radius: 999px;
  padding: 4px 10px;
  font-weight: 900;
  color: white;
  font-size: 0.92rem;
}}

/* 控えめ補足 */
.mini-note {{
  background: #FFFFFF;
  border: 1px solid {theme['line']};
  border-radius: 12px;
  padding: 0.65rem 0.85rem;
  margin: 0.55rem 0 0.65rem 0;
}}
.mini-note .cap {{
  font-weight: 1000;
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

/* 備考（読みやすいブロック） */
.perma-box {{
  border:2px solid {theme['accent']};
  border-radius:14px;
  padding:0.95rem 1.05rem;
  margin-top:0.5rem;
  background:white;
}}
.perma-box p {{
  font-size:1.02rem;
  color:#222;
  margin-bottom:0.55rem;
  line-height: 1.7;
}}
.perma-highlight {{
  color:{theme['accent']};
  font-weight:1000;
}}

.cite-box {{
  background: #FBFBFD;
  border: 1px solid {theme['line']};
  border-radius: 12px;
  padding: 0.75rem 0.9rem;
  margin-top: 0.7rem;
  color: #333;
}}
.cite-box .cap {{
  font-weight: 1000;
  color: #1b2a4a;
  margin-bottom: 0.25rem;
}}
.cite-box .ref {{
  font-size: 0.95rem;
  line-height: 1.6;
}}

.footer-box {{
  border-top: 2px solid #DDD;
  margin-top: 1.4rem;
  padding-top: 0.9rem;
  font-size: 0.98rem;
  color: #333;
  line-height: 1.8;
}}
.footer-title {{
  font-weight: 1000;
  margin-bottom: 0.35rem;
}}
.footer-thanks {{
  margin-top: 0.75rem;
  font-weight: 900;
}}

/* 印刷 */
.keep-together {{}}
.force-page-break {{ display:none; }}

@media print {{
  @page {{ size: A4; margin: 10mm; }}
  html, body {{ background: white !important; }}

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

  .page-header, .score-card, .intro-box, .mini-note, .legend-box, .perma-box, .cite-box, .footer-box,
  img, figure,
  div[data-testid="stHorizontalBlock"], div[data-testid="column"] {{
    break-inside: avoid !important;
    page-break-inside: avoid !important;
  }}

  .score-card, .intro-box, .mini-note, .legend-box, .perma-box, .cite-box {{
    box-shadow: none !important;
  }}

  .no-print {{ display: none !important; }}
}}
</style>
""", unsafe_allow_html=True)

# =========================
# 計算
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
# 判定（1〜5）＆★
# =========================
def rank_1to5(score: float, higher_is_better: bool = True) -> int:
    if np.isnan(score):
        return 0
    v = score if higher_is_better else (10 - score)
    if v >= 8.5:
        return 5
    if v >= 7.0:
        return 4
    if v >= 5.5:
        return 3
    if v >= 4.0:
        return 2
    return 1

def stars(rank: int) -> str:
    if rank <= 0:
        return ""
    return "★" * rank

def rank_color(rank: int) -> str:
    # 低→高 で見やすい色
    return {
        5: "#2E7D32",
        4: "#43A047",
        3: "#F9A825",
        2: "#FB8C00",
        1: "#E53935",
        0: "#9E9E9E",
    }.get(rank, "#9E9E9E")

# 追加指標の“向き”（高いほど良いか）
higher_is_better_map = {
    "P": True, "E": True, "R": True, "M": True, "A": True,
    "心の健康の総合得点": True,
    "からだの調子": True,
    "全体的なしあわせ感": True,
    "気持ちの様子（いやな気持）": False,  # 低いほど良い
    "ひとりぼっち感": False,              # 低いほど良い（※解釈として）
}

# =========================
# メタ情報（Excelに列があれば拾う）
# =========================
def pick_first_existing(row: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    for c in candidates:
        if c in row.columns:
            val = row.iloc[0][c]
            if pd.notna(val):
                return str(val)
    return None

def get_meta(row: pd.DataFrame, sid: str) -> dict:
    name = pick_first_existing(row, ["名前", "氏名", "name", "Name"])
    age = pick_first_existing(row, ["年齢", "age", "Age"])
    sex = pick_first_existing(row, ["性別", "sex", "Sex", "gender", "Gender"])
    date = pick_first_existing(row, ["検査日", "日付", "date", "Date"])
    return {
        "名前": name or "—",
        "年齢": age or "—",
        "性別": sex or "—",
        "ID": str(sid),
        "日付": date or "—",
    }

# =========================
# 描画関数
# =========================
def render_legend():
    st.markdown(
        f"""
        <div class="legend-box">
          <div class="cap">判定の目安（1〜5）</div>
          <div class="row">
            <span class="pill" style="background:{rank_color(5)};">5：とても良い</span>
            <span class="pill" style="background:{rank_color(4)};">4：良い</span>
            <span class="pill" style="background:{rank_color(3)};">3：普通</span>
            <span class="pill" style="background:{rank_color(2)};">2：やや低い</span>
            <span class="pill" style="background:{rank_color(1)};">1：低い</span>
          </div>
          <div style="margin-top:6px; font-size:0.92rem; color:{theme['muted']};">
            ※点数は0〜10点。判定は「目安」です。
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_position_bar(score: float, mean: float):
    # score: 0-10 -> 0-100%
    if np.isnan(score):
        marker_left = "0%"
    else:
        marker_left = f"{max(0, min(100, score * 10)):.1f}%"
    mean_html = ""
    if not np.isnan(mean):
        mean_left = f"{max(0, min(100, mean * 10)):.1f}%"
        mean_html = f"<div class='mean' style='left:{mean_left};'></div>"

    st.markdown(
        f"""
        <div class="posbar">
          <div class="seg1"></div><div class="seg2"></div><div class="seg3"></div>
          {mean_html}
          <div class="marker" style="left:{marker_left};"></div>
        </div>
        <div class="posbar-labels">
          <span>低い</span><span>平均</span><span>高い</span>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_meter_block(title: str, score: float, color: Optional[str], higher_is_better: bool, big: bool = False, norm_mean: float = np.nan):
    if np.isnan(score):
        width = "0%"
        score_html = "未回答"
        r = 0
    else:
        width = f"{score * 10:.0f}%"
        score_html = f"<span class='score-strong'>{score:.1f}</span>/10点"
        r = rank_1to5(score, higher_is_better=higher_is_better)

    bar_color = color if color is not None else "#999999"
    big_class = "big" if big else ""
    meter_class = "meter big" if big else "meter"
    score_class = "meter-score-text big" if big else "meter-score-text"
    title_class = "score-title big" if big else "score-title"

    badge = ""
    if r > 0:
        badge = f"""
        <div style="display:flex; align-items:center; gap:6px;">
          <div class="rank-badge" style="background:{rank_color(r)};">{r}</div>
          <div class="rank-stars">{stars(r)}</div>
        </div>
        """
    else:
        badge = f"<div class='rank-badge' style='background:{rank_color(0)};'>—</div>"

    st.markdown(
        f"""
        <div class="score-card {big_class}">
          <div class="score-head">
            <div class="{title_class}">{title}</div>
            {badge}
          </div>
          <div class="{meter_class}">
            <div class="meter-fill" style="width:{width}; background:{bar_color};"></div>
          </div>
          <div class="{score_class}">{score_html}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 参考用紙の「位置づけグラフ」に近い要素として比較バーを付ける
    render_position_bar(score, norm_mean)

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

def render_intro_box():
    st.markdown(
        """
        <div class="intro-box">
          <div class="intro-title">はじめに（この用紙でわかること）</div>
          <div class="intro-text">
            この用紙は、<b>心の健康チェック</b>の結果です。<br>
            <b>今の心の元気さ</b>を、0〜10点でわかりやすく見える化しています。
            <ul>
              <li><b>心の5つの元気さ（PERMA）</b>：前向きな気持ち／集中／つながり／目的／達成感</li>
              <li><b>追加の指標</b>：心の健康の総合得点、気持ちの様子（いやな気持）、からだの調子、ひとりぼっち感、全体的なしあわせ感</li>
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
          <div class="cap">※各指標の見方（PERMA）</div>
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
          <div class="cap">※各指標の意味（追加の指標）</div>
          <div class="txt">
            <ul>
              <li><b>気持ちの様子（いやな気持）とは？</b> → {extras_explanations["気持ちの様子（いやな気持）"]}</li>
              <li><b>からだの調子とは？</b> → {extras_explanations["からだの調子"]}</li>
              <li><b>ひとりぼっち感とは？</b> → {extras_explanations["ひとりぼっち感"]}</li>
              <li style="color:#58606a;"><b>補足</b>：気持ちの様子／ひとりぼっち感は「低いほど良い」方向の目安で判定しています。</li>
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
          <p><span class="perma-highlight">備考：このチェックの背景</span></p>
          <p>
            このチェックは、ポジティブ心理学で提案されている
            <span class="perma-highlight">PERMA（5つの柱）</span>をもとに、
            心の健康を多面的（いくつかの面から）に見える化する考え方です。
          </p>
          <p style="color:{theme['muted']}; font-size:0.98rem;">
            ※結果は「良い／悪い」を決めるものではなく、生活の中で整えるヒントにするためのものです。
          </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="mini-note">
          <div class="cap">※PERMA-Profiler（尺度）について（わかりやすく）</div>
          <div class="txt">
            <ul>
              <li>PERMAの5要素を、短い質問で測れるように作られたのが <b>PERMA-Profiler</b> です。</li>
              <li><b>15問（5要素×3問）</b>に加えて、<b>全体的なしあわせ感</b>、<b>気持ちの様子</b>、<b>ひとりぼっち感</b>、<b>からだの調子</b>などをみる <b>8項目</b>があり、合計<b>23項目</b>です。</li>
              <li>点数は <b>0〜10点</b>で、<b>プロフィール（形）</b>として見るのが良いとされています。</li>
            </ul>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="mini-note">
          <div class="cap">※結果の見方（おすすめ）</div>
          <div class="txt">
            <ul>
              <li><b>高いところ</b>：今の強み（保てているところ）</li>
              <li><b>低いところ</b>：これから整えたいところ（伸ばせる余地）</li>
              <li>一回だけで決めず、気が向いた時に繰り返して <b>変化</b>を見ると役立ちます。</li>
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
# セッション（アップロードUI）
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

df = st.session_state.df
sid = st.session_state.sid
row = df[df.iloc[:, 0].astype(str) == str(sid)]
if row.empty:
    st.warning("選択されたIDが見つかりません。最初からやり直してください。")
    st.session_state.ready = False
    st.rerun()

perma_scores, extras = compute_results(row)
meta = get_meta(row, sid)

# =========================
# 参考用紙の「右帯」っぽいヘッダー
# =========================
st.markdown(
    f"""
    <div class="page-header">
      <div class="header-grid">
        <div>
          <div class="header-title">わらトレ　心の健康チェック（結果報告書）</div>
          <div class="header-sub">心の5つの元気さ（PERMA）と、こころ・からだの状態をまとめます。</div>
        </div>
        <div class="side-band">
          <div class="t">あなたの情報</div>
          <div class="meta">
            <div class="meta-row"><span class="meta-key">名前</span><span class="meta-val">{meta["名前"]}</span></div>
            <div class="meta-row"><span class="meta-key">年齢</span><span class="meta-val">{meta["年齢"]}</span></div>
            <div class="meta-row"><span class="meta-key">性別</span><span class="meta-val">{meta["性別"]}</span></div>
            <div class="meta-row"><span class="meta-key">ID</span><span class="meta-val">{meta["ID"]}</span></div>
            <div class="meta-row"><span class="meta-key">日付</span><span class="meta-val">{meta["日付"]}</span></div>
          </div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

render_intro_box()

# =========================================================
# 1枚目
# =========================================================
st.markdown("<div class='print-page page-1'>", unsafe_allow_html=True)

# ---- 1-1
st.markdown('<div class="section-header">1-1. 要素ごとにみた心の状態（PERMA）</div>', unsafe_allow_html=True)

# 参考用紙の「凡例（判定目安）」を、ここで常に見えるように配置
col_main, col_legend = st.columns([3, 1])
with col_legend:
    render_legend()

with col_main:
    col_meter, col_chart = st.columns([2, 1])
    with col_meter:
        col_left, col_right = st.columns(2)
        with col_left:
            for k in ["P", "E", "R"]:
                render_meter_block(
                    f"{action_emojis.get(k,'')} {k}：{full_labels[k]}",
                    perma_scores.get(k, np.nan),
                    colors[k],
                    higher_is_better_map[k],
                    big=False,
                    norm_mean=NORM_MEAN.get(k, np.nan),
                )
        with col_right:
            for k in ["M", "A"]:
                render_meter_block(
                    f"{action_emojis.get(k,'')} {k}：{full_labels[k]}",
                    perma_scores.get(k, np.nan),
                    colors[k],
                    higher_is_better_map[k],
                    big=False,
                    norm_mean=NORM_MEAN.get(k, np.nan),
                )
    with col_chart:
        plot_hist(perma_scores)

render_perma_howto_note()

# ---- 1-2
st.markdown('<div class="section-header">1-2. こころ・からだの調子</div>', unsafe_allow_html=True)

# 総合（太く長い）
render_meter_block(
    "心の健康の総合得点",
    extras.get("心の健康の総合得点", np.nan),
    extra_colors["心の健康の総合得点"],
    higher_is_better_map["心の健康の総合得点"],
    big=True,
    norm_mean=NORM_MEAN.get("心の健康の総合得点", np.nan),
)

# 4項目を2列で（指定順）
grid_order = [
    "からだの調子",
    "全体的なしあわせ感",
    "気持ちの様子（いやな気持）",
    "ひとりぼっち感",
]
cL, cR = st.columns(2)
for i, key in enumerate(grid_order):
    v = extras.get(key, np.nan)
    col = cL if i % 2 == 0 else cR
    with col:
        render_meter_block(
            key,
            v,
            extra_colors.get(key, None),
            higher_is_better_map.get(key, True),
            big=False,
            norm_mean=NORM_MEAN.get(key, np.nan),
        )

render_extras_meaning_note()

st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 2枚目
# =========================================================
st.markdown("<div class='print-page page-2'>", unsafe_allow_html=True)

st.markdown(
    f"""
    <div class="section-header">2. あなたの結果に基づく、強みとおすすめな行動</div>
    """,
    unsafe_allow_html=True
)

weak_keys = [k for k, v in perma_scores.items() if not np.isnan(v) and v <= 5]
strong_keys = [k for k, v in perma_scores.items() if not np.isnan(v) and v >= 7]

if strong_keys:
    st.markdown('<div class="mini-note"><div class="cap">2-1. 満たされている心の健康の要素（強み）</div><div class="txt"><ul>', unsafe_allow_html=True)
    for k in strong_keys:
        st.markdown(f"<li><b>{full_labels[k]}（{k}）</b>：{perma_scores[k]:.1f}/10点</li>", unsafe_allow_html=True)
    st.markdown('</ul></div></div>', unsafe_allow_html=True)

if weak_keys:
    st.markdown('<div class="mini-note"><div class="cap">2-2. これから伸ばせる要素と具体的な行動例</div><div class="txt">', unsafe_allow_html=True)
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
    st.markdown('</div></div>', unsafe_allow_html=True)

st.markdown("<div class='force-page-break'></div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 3枚目
# =========================================================
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

st.markdown("</div>", unsafe_allow_html=True)  # print-page end
st.markdown("</div>", unsafe_allow_html=True)  # main-wrap end
