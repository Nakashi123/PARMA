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
# テーマ（参考用紙っぽい：背景は薄く、カードは白、強調は帯）
# =========================
theme = {
    "bg": "#F5F8FF",
    "paper": "#FFFFFF",
    "text": "#1b2a4a",
    "muted": "#526070",
    "line": "#E4EAF6",
    "accent": "#2F61D5",
    "soft": "#EEF3FF",
}

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
icons = {"P": "😊", "E": "🧩", "R": "🤝", "M": "🌱", "A": "🏁"}

# 追加指標（灰色を廃止して役割色に）
extra_colors = {
    "心の健康の総合得点": "#2F61D5",
    "気持ちの様子（いやな気持）": "#E74C3C",  # 低いほど良い
    "からだの調子": "#2ECC71",
    "ひとりぼっち感": "#9B59B6",             # 低いほど良い
    "全体的なしあわせ感": "#F1C40F",
}
extras_icons = {
    "心の健康の総合得点": "🧠",
    "気持ちの様子（いやな気持）": "🌧️",
    "からだの調子": "💪",
    "ひとりぼっち感": "🧍",
    "全体的なしあわせ感": "☀️",
}

# =========================
# ラベル・説明
# =========================
full_labels = {
    "P": "前向きな気持ち",
    "E": "集中して取り組むこと",
    "R": "人とのつながり",
    "M": "生きがいや目的",
    "A": "達成感",
}
descriptions = {
    "P": "楽しい気持ちや安心感、感謝など前向きな感情の豊かさの目安です。",
    "E": "物事に没頭したり夢中になって取り組める状態の目安です。",
    "R": "支え合えるつながりや信頼関係を感じられている状態の目安です。",
    "M": "人生に目的や価値を感じて生きている状態の目安です。",
    "A": "努力し、達成感や成長を感じられている状態の目安です。",
}
tips = {
    "P": ["感謝の気持ちをメモしてみる（感謝を書き出す）", "今日の良かったことを振り返る"],
    "E": ["小さな挑戦を設定する", "得意なことを活かす"],
    "R": ["感謝を伝える", "小さな親切をする"],
    "M": ["大切にしている価値を書き出す", "経験から学びを見つける"],
    "A": ["小さな目標を作る", "失敗を学びと捉える"],
}
extras_explanations = {
    "気持ちの様子（いやな気持）": "不安になったり、気分が沈んだり、いらいらしたりすることがどのくらいあるかの目安です。",
    "からだの調子": "体の調子や元気さについて、ご本人が感じた程度の目安です。",
    "ひとりぼっち感": "ひとりぼっちだと感じることがあるかの目安です。",
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
    "気持ちの様子（いやな気持）": [6, 13, 19],    # Negative Emotion (Q7,Q14,Q20)
    "からだの調子":  [3, 12, 17],                   # Physical Health (Q4,Q13,Q18)
    "ひとりぼっち感": [11],                          # Loneliness (Q12)
    "全体的なしあわせ感": [22],                      # Q23
}

# =========================
# 参考平均（“平均マーカー”用の目安）
# Butler & Kern (2016) の大規模ノルム（あなたが以前まとめた値）に基づく
# ※ Loneliness/Overall happinessは資料により扱いが変わるため平均マーカーは省略
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
    "ひとりぼっち感": np.nan,
    "全体的なしあわせ感": np.nan,
}

# “高いほど良い”方向（追加指標の判定方向）
higher_is_better_map = {
    "P": True, "E": True, "R": True, "M": True, "A": True,
    "心の健康の総合得点": True,
    "からだの調子": True,
    "全体的なしあわせ感": True,
    "気持ちの様子（いやな気持）": False,
    "ひとりぼっち感": False,
}

# =========================
# CSS（参考用紙の「縦カード＋大きい数値箱＋右帯」を再現）
# =========================
st.markdown(f"""
<style>
html, body {{
  background:{theme["bg"]};
  color:{theme["text"]};
  font-family:"BIZ UDPGothic","Meiryo",sans-serif;
  line-height:1.5;
}}
section.main > div {{ padding-top: 1rem; padding-bottom: 1rem; }}
.block-container {{ padding-top: 1rem; padding-bottom: 1rem; }}
div[data-testid="stVerticalBlock"] {{ gap: 0.65rem; }}
div[data-testid="stMarkdownContainer"] p {{ margin: 0.2rem 0 0.3rem 0; }}

.main-wrap {{ max-width: 1000px; margin: 0 auto; }}

h1 {{
  text-align:center;
  font-size:2.0rem;
  font-weight:1000;
  margin:0.2rem 0 0.25rem 0;
}}

.paper {{
  background:{theme["paper"]};
  border:1px solid {theme["line"]};
  border-radius:18px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.06);
  padding: 0.95rem 1.05rem;
}}

.header-grid {{
  display:grid;
  grid-template-columns: 1fr 290px;
  gap: 12px;
  align-items: stretch;
}}
@media (max-width: 920px) {{
  .header-grid {{ grid-template-columns: 1fr; }}
}}

.header-title {{
  font-size: 1.55rem;
  font-weight: 1000;
  color: {theme["text"]};
}}
.header-sub {{
  color:{theme["muted"]};
  font-size: 1.02rem;
  margin-top: 0.2rem;
}}

.band {{
  background: linear-gradient(180deg, {theme["accent"]} 0%, #244CAB 100%);
  color: #fff;
  border-radius: 16px;
  padding: 0.85rem 0.85rem;
  border: 1px solid rgba(255,255,255,0.25);
}}
.band .t {{
  font-weight:1000;
  font-size: 1.05rem;
  margin-bottom: 0.35rem;
}}
.meta-row {{
  display:flex;
  justify-content: space-between;
  gap: 10px;
  font-size: 0.96rem;
  line-height: 1.55;
}}
.meta-k {{ opacity: 0.85; }}
.meta-v {{ font-weight: 1000; }}

.section {{
  background:{theme["paper"]};
  border:1px solid {theme["line"]};
  border-radius:16px;
  padding: 0.85rem 0.95rem;
}}

.sec-head {{
  display:flex;
  align-items:center;
  justify-content: space-between;
  gap: 12px;
  padding: 0.55rem 0.75rem;
  border-radius: 14px;
  background: {theme["soft"]};
  border: 1px solid {theme["line"]};
  margin-bottom: 0.65rem;
}}
.sec-head .ttl {{
  font-size: 1.15rem;
  font-weight: 1000;
}}
.sec-head .sub {{
  color:{theme["muted"]};
  font-size: 0.96rem;
}}

.legend {{
  background: {theme["paper"]};
  border:1px solid {theme["line"]};
  border-radius:14px;
  padding: 0.7rem 0.75rem;
}}
.legend .cap {{
  font-weight:1000;
  margin-bottom: 0.25rem;
}}
.pills {{
  display:flex;
  flex-wrap: wrap;
  gap: 7px;
}}
.pill {{
  border-radius: 999px;
  padding: 4px 10px;
  font-weight: 1000;
  color: white;
  font-size: 0.92rem;
}}

.grid-5 {{
  display:grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
}}
@media (max-width: 980px) {{
  .grid-5 {{ grid-template-columns: repeat(2, 1fr); }}
}}
@media (max-width: 520px) {{
  .grid-5 {{ grid-template-columns: 1fr; }}
}}

.card {{
  background: {theme["paper"]};
  border:1px solid {theme["line"]};
  border-radius:16px;
  padding: 0.7rem 0.75rem;
}}
.card .c-head {{
  display:flex;
  align-items:center;
  justify-content: space-between;
  gap: 10px;
}}
.chip {{
  display:inline-flex;
  align-items:center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 999px;
  font-weight: 1000;
  color: #fff;
  font-size: 0.95rem;
}}
.card .desc {{
  color:{theme["muted"]};
  font-size: 0.92rem;
  line-height: 1.45;
  margin-top: 0.25rem;
  min-height: 2.8em;
}}

.value-box {{
  margin-top: 0.55rem;
  background: #fff;
  border: 2px solid {theme["line"]};
  border-radius: 14px;
  padding: 0.55rem 0.6rem;
  display:flex;
  align-items: baseline;
  justify-content: center;
  gap: 6px;
}}
.value-box .num {{
  font-size: 1.85rem;
  font-weight: 1000;
  color:#111;
}}
.value-box .unit {{
  font-size: 1.05rem;
  font-weight: 900;
  color:#444;
}}

.rank-row {{
  display:flex;
  align-items:center;
  justify-content: center;
  gap: 8px;
  margin-top: 0.45rem;
}}
.rank-badge {{
  min-width: 46px;
  text-align:center;
  padding: 3px 10px;
  border-radius: 999px;
  font-weight: 1000;
  font-size: 0.95rem;
  color:#fff;
}}
.stars {{
  font-size: 1.0rem;
  color: #f1c40f;
  letter-spacing: 1px;
}}

.posbar {{
  position: relative;
  height: 12px;
  border-radius: 999px;
  overflow: hidden;
  margin-top: 0.55rem;
  border: 1px solid {theme["line"]};
}}
.posbar .seg1 {{ position:absolute; left:0; top:0; height:100%; width:33.4%; background:#EAF0FF; }}
.posbar .seg2 {{ position:absolute; left:33.4%; top:0; height:100%; width:33.2%; background:#F3F6FB; }}
.posbar .seg3 {{ position:absolute; left:66.6%; top:0; height:100%; width:33.4%; background:#FFF5DD; }}
.posbar .marker {{
  position:absolute; top:-2px; width: 3px; height: 16px;
  background: #111; border-radius: 2px;
}}
.posbar .mean {{
  position:absolute; top:-2px; width: 3px; height: 16px;
  background: {theme["accent"]}; border-radius: 2px; opacity: 0.85;
}}
.poslabels {{
  display:flex;
  justify-content: space-between;
  color:{theme["muted"]};
  font-size: 0.84rem;
  margin-top: 0.22rem;
}}

.bigbar {{
  background: {theme["paper"]};
  border: 1px solid {theme["line"]};
  border-radius: 16px;
  padding: 0.85rem 0.9rem;
}}
.bigbar .top {{
  display:flex;
  align-items:center;
  justify-content: space-between;
  gap: 10px;
}}
.bigbar .title {{
  font-size: 1.12rem;
  font-weight: 1000;
}}
.bigmeter {{
  margin-top: 0.5rem;
  height: 24px;
  border-radius: 999px;
  background: #E0E0E0;
  overflow:hidden;
}}
.bigmeter .fill {{
  height:100%;
  border-radius: 999px;
}}
.bigscore {{
  margin-top: 0.35rem;
  text-align:center;
}}
.bigscore .num {{
  font-size: 2.10rem;
  font-weight: 1000;
  color:#111;
}}
.bigscore .unit {{
  font-size: 1.08rem;
  font-weight: 900;
  color:#444;
}}

.grid-2 {{
  display:grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}}
@media (max-width: 720px) {{
  .grid-2 {{ grid-template-columns: 1fr; }}
}}

.note {{
  background: #fff;
  border:1px solid {theme["line"]};
  border-radius: 14px;
  padding: 0.7rem 0.8rem;
  margin-top: 0.65rem;
}}
.note .cap {{
  font-weight: 1000;
  margin-bottom: 0.25rem;
}}
.note .tx {{
  color:#222;
  font-size: 0.98rem;
  line-height: 1.65;
}}
.note ul {{ margin: 0.35rem 0 0.1rem 1.1rem; }}
.note li {{ margin: 0.14rem 0; }}

.cite {{
  background: #FBFBFD;
  border:1px solid {theme["line"]};
  border-radius: 14px;
  padding: 0.75rem 0.85rem;
  margin-top: 0.75rem;
}}
.cite .cap {{
  font-weight: 1000;
  margin-bottom: 0.25rem;
}}
.cite .ref {{
  font-size: 0.94rem;
  line-height: 1.6;
}}

.footer {{
  border-top: 2px solid #DDD;
  margin-top: 1.2rem;
  padding-top: 0.8rem;
  color:#333;
  font-size: 0.98rem;
  line-height: 1.75;
}}
.footer .t {{
  font-weight: 1000;
  margin-bottom: 0.35rem;
}}

@media print {{
  @page {{ size: A4; margin: 10mm; }}
  html, body {{ background: white !important; }}
  * {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
  .print-page {{ break-after: page !important; page-break-after: always !important; }}
  .print-page:last-child {{ break-after: auto !important; page-break-after: auto !important; }}
  .no-print {{ display: none !important; }}
  .paper, .section, .card, .legend, .bigbar, .note, .cite {{ box-shadow: none !important; }}
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
# メタ情報（Excel列があれば拾う）
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
    return {"名前": name or "—", "年齢": age or "—", "性別": sex or "—", "ID": str(sid), "日付": date or "—"}

# =========================
# 判定（1〜5）＋色
# =========================
def rank_1to5(score: float, higher_is_better: bool = True) -> int:
    if np.isnan(score):
        return 0
    v = score if higher_is_better else (10 - score)
    if v >= 8.5: return 5
    if v >= 7.0: return 4
    if v >= 5.5: return 3
    if v >= 4.0: return 2
    return 1

def stars(rank: int) -> str:
    if rank <= 0:
        return ""
    return "★" * rank

def rank_color(rank: int) -> str:
    return {
        5: "#2E7D32",
        4: "#43A047",
        3: "#F9A825",
        2: "#FB8C00",
        1: "#E53935",
        0: "#9E9E9E",
    }.get(rank, "#9E9E9E")

# =========================
# UI 部品
# =========================
def render_legend():
    st.markdown(
        f"""
        <div class="legend">
          <div class="cap">判定の目安（1〜5）</div>
          <div class="pills">
            <span class="pill" style="background:{rank_color(5)};">5：とても良い</span>
            <span class="pill" style="background:{rank_color(4)};">4：良い</span>
            <span class="pill" style="background:{rank_color(3)};">3：普通</span>
            <span class="pill" style="background:{rank_color(2)};">2：やや低い</span>
            <span class="pill" style="background:{rank_color(1)};">1：低い</span>
          </div>
          <div style="margin-top:6px; color:{theme["muted"]}; font-size:0.92rem;">
            ※点数は0〜10点。判定は目安です。
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_posbar(score: float, mean: float):
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
        <div class="poslabels"><span>低い</span><span>平均</span><span>高い</span></div>
        """,
        unsafe_allow_html=True
    )

def render_domain_card(key: str, score: float, color: str, label: str, desc: str, icon: str):
    hib = higher_is_better_map.get(key, True)
    r = rank_1to5(score, hib) if not np.isnan(score) else 0
    mean = NORM_MEAN.get(key, np.nan)

    num = "—" if np.isnan(score) else f"{score:.1f}"
    badge = "—" if r == 0 else f"{r}"
    star_txt = stars(r)

    st.markdown(
        f"""
        <div class="card">
          <div class="c-head">
            <div class="chip" style="background:{color};">{icon} {label}</div>
            <div class="rank-badge" style="background:{rank_color(r)};">{badge}</div>
          </div>
          <div class="desc">{desc}</div>
          <div class="value-box">
            <span class="num">{num}</span><span class="unit">/10点</span>
          </div>
          <div class="rank-row">
            <span class="stars">{star_txt}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    render_posbar(score, mean)

def render_big_total(score: float, color: str):
    hib = higher_is_better_map["心の健康の総合得点"]
    r = rank_1to5(score, hib) if not np.isnan(score) else 0
    mean = NORM_MEAN.get("心の健康の総合得点", np.nan)

    width = "0%" if np.isnan(score) else f"{score * 10:.0f}%"
    num = "—" if np.isnan(score) else f"{score:.1f}"

    st.markdown(
        f"""
        <div class="bigbar">
          <div class="top">
            <div class="title">{extras_icons["心の健康の総合得点"]} 心の健康の総合得点</div>
            <div class="rank-badge" style="background:{rank_color(r)};">{("—" if r==0 else r)}</div>
          </div>
          <div class="bigmeter">
            <div class="fill" style="width:{width}; background:{color};"></div>
          </div>
          <div class="bigscore">
            <span class="num">{num}</span><span class="unit">/10点</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    render_posbar(score, mean)

def plot_perma_mini(perma_scores: dict):
    labels = ["P", "E", "R", "M", "A"]
    values = [perma_scores.get(k, np.nan) for k in labels]
    fig, ax = plt.subplots(figsize=(3.0, 2.2), dpi=160)
    ax.bar(labels, values, color=[colors[k] for k in labels])
    ax.set_ylim(0, 10)
    ax.set_yticks([])
    ax.set_title("PERMA（プロフィール）", fontsize=11)
    for i, v in enumerate(values):
        if not np.isnan(v):
            ax.text(i, v + 0.2, f"{v:.1f}", ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    st.pyplot(fig)

def render_intro():
    st.markdown(
        f"""
        <div class="note" style="border:2px solid {theme["accent"]}; background:{theme["soft"]};">
          <div class="cap">はじめに（この用紙でわかること）</div>
          <div class="tx">
            この用紙は <b>心の健康チェック</b>の結果です。<br>
            <b>今の心の元気さ</b>を 0〜10点で見える化しています。
            <ul>
              <li><b>心の5つの元気さ（PERMA）</b>：前向きな気持ち／集中／つながり／目的／達成感</li>
              <li><b>追加の指標</b>：心の健康の総合得点、気持ちの様子、からだの調子、ひとりぼっち感、全体的なしあわせ感</li>
            </ul>
            <div style="margin-top:6px; border-top:1px dashed #9aa6b2; padding-top:6px;">
              ※これは病気の診断ではありません。<b>今の自分の状態を知るための目安</b>としてご利用ください。
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_note_perma():
    st.markdown(
        f"""
        <div class="note">
          <div class="cap">※各指標の見方（PERMA）</div>
          <div class="tx">
            <ul>
              <li><b>P</b>：{descriptions["P"]}</li>
              <li><b>E</b>：{descriptions["E"]}</li>
              <li><b>R</b>：{descriptions["R"]}</li>
              <li><b>M</b>：{descriptions["M"]}</li>
              <li><b>A</b>：{descriptions["A"]}</li>
            </ul>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_note_extras():
    st.markdown(
        f"""
        <div class="note">
          <div class="cap">※各指標の意味（追加の指標）</div>
          <div class="tx">
            <ul>
              <li><b>気持ちの様子（いやな気持）とは？</b> → {extras_explanations["気持ちの様子（いやな気持）"]}</li>
              <li><b>からだの調子とは？</b> → {extras_explanations["からだの調子"]}</li>
              <li><b>ひとりぼっち感とは？</b> → {extras_explanations["ひとりぼっち感"]}</li>
              <li style="color:{theme["muted"]};">補足：気持ちの様子／ひとりぼっち感は「低いほど良い」方向として判定しています。</li>
            </ul>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_remarks():
    st.markdown(
        f"""
        <div class="note">
          <div class="cap">備考（このチェックの背景）</div>
          <div class="tx">
            このチェックは、ポジティブ心理学で提案される <b>PERMA</b>（5つの柱）をもとに、
            心の健康を<b>多面的</b>に見える化する考え方です。
            <ul>
              <li>PERMAは <b>P/E/R/M/A</b> の5要素で、要素ごとの点数を<b>プロフィール</b>として見るのが大切とされています。</li>
              <li>研究では、PERMAを測る <b>15項目</b>（各3問×5要素）に加えて、全体的なしあわせ感やネガティブ感情、孤独、身体の健康などの<b>追加項目</b>を含めた <b>23項目</b>の尺度が開発されています。</li>
              <li>一つの点数にまとめるより、<b>どの要素が高い/低いか</b>を見て、日常の工夫につなげることが推奨されています。</li>
            </ul>
          </div>
        </div>

        <div class="cite">
          <div class="cap">引用（根拠）</div>
          <div class="ref">
            Butler, J., &amp; Kern, M. L. (2016). <i>The PERMA-Profiler: A brief multidimensional measure of flourishing</i>.
            <i>International Journal of Wellbeing</i>, 6(3), 1–48. https://doi.org/10.5502/ijw.v6i3.526
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_norm_table():
    rows = []
    order = ["P","E","R","M","A","心の健康の総合得点","気持ちの様子（いやな気持）","からだの調子"]
    for k in order:
        mean = NORM_MEAN.get(k, np.nan)
        name = full_labels.get(k, k)
        sym = k if k in ["P","E","R","M","A"] else ""
        rows.append([sym, name, ("—" if np.isnan(mean) else f"{mean:.2f}")])
    df = pd.DataFrame(rows, columns=["記号", "項目", "参考平均（目安）"])
    st.dataframe(df, use_container_width=True, hide_index=True)

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

# -------------------------
# ヘッダー（参考用紙の右帯）
# -------------------------
st.markdown(
    f"""
    <div class="paper">
      <div class="header-grid">
        <div>
          <div class="header-title">わらトレ　心の健康チェック（結果報告書）</div>
          <div class="header-sub">心の5つの元気さ（PERMA）と、こころ・からだの状態をまとめます。</div>
        </div>
        <div class="band">
          <div class="t">あなたの情報</div>
          <div class="meta-row"><span class="meta-k">名前</span><span class="meta-v">{meta["名前"]}</span></div>
          <div class="meta-row"><span class="meta-k">年齢</span><span class="meta-v">{meta["年齢"]}</span></div>
          <div class="meta-row"><span class="meta-k">性別</span><span class="meta-v">{meta["性別"]}</span></div>
          <div class="meta-row"><span class="meta-k">ID</span><span class="meta-v">{meta["ID"]}</span></div>
          <div class="meta-row"><span class="meta-k">日付</span><span class="meta-v">{meta["日付"]}</span></div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

render_intro()

# =========================================================
# 1枚目：結果
# =========================================================
st.markdown("<div class='print-page page-1'>", unsafe_allow_html=True)

# 1-1 PERMA
c_main, c_side = st.columns([3.3, 1.2])
with c_main:
    st.markdown(
        f"""
        <div class="section">
          <div class="sec-head">
            <div class="ttl">1-1. 要素ごとにみた心の状態（PERMA）</div>
            <div class="sub">各項目：0〜10点</div>
          </div>
          <div class="grid-5">
        """,
        unsafe_allow_html=True
    )
    for k in ["P","E","R","M","A"]:
        render_domain_card(
            key=k,
            score=perma_scores.get(k, np.nan),
            color=colors[k],
            label=f"{k}：{full_labels[k]}",
            desc=descriptions[k],
            icon=icons[k],
        )
    st.markdown("</div></div>", unsafe_allow_html=True)

    # 見方（控えめカード）
    render_note_perma()

with c_side:
    render_legend()
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    plot_perma_mini(perma_scores)

# 1-2 こころ・からだ
st.markdown(
    f"""
    <div class="section" style="margin-top:10px;">
      <div class="sec-head">
        <div class="ttl">1-2. こころ・からだの調子</div>
        <div class="sub">総合→個別の順で見ます</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

# 総合（太バー＋巨大数値）
render_big_total(
    score=extras.get("心の健康の総合得点", np.nan),
    color=extra_colors["心の健康の総合得点"]
)

# 個別４項目（2列カード）
st.markdown("<div class='grid-2'>", unsafe_allow_html=True)
for key in ["からだの調子", "全体的なしあわせ感", "気持ちの様子（いやな気持）", "ひとりぼっち感"]:
    render_domain_card(
        key=key,
        score=extras.get(key, np.nan),
        color=extra_colors.get(key, theme["accent"]),
        label=key,
        desc=(""),
        icon=extras_icons.get(key, "📌"),
    )
st.markdown("</div>", unsafe_allow_html=True)

render_note_extras()

st.markdown("</div>", unsafe_allow_html=True)  # page-1 end

# =========================================================
# 2枚目：強みとおすすめ行動（紙の“コメント/提案”枠に寄せる）
# =========================================================
st.markdown("<div class='print-page page-2'>", unsafe_allow_html=True)

st.markdown(
    f"""
    <div class="section">
      <div class="sec-head">
        <div class="ttl">2. あなたの結果に基づく、強みとおすすめな行動</div>
        <div class="sub">日常生活でできる工夫</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

weak_keys = [k for k, v in perma_scores.items() if not np.isnan(v) and v <= 5]
strong_keys = [k for k, v in perma_scores.items() if not np.isnan(v) and v >= 7]

# 強み
if strong_keys:
    st.markdown(
        """
        <div class="note">
          <div class="cap">2-1. 満たされている要素（強み）</div>
          <div class="tx">
            <ul>
        """,
        unsafe_allow_html=True
    )
    for k in strong_keys:
        st.markdown(f"<li><b>{full_labels[k]}（{k}）</b>：{perma_scores[k]:.1f}/10点</li>", unsafe_allow_html=True)
    st.markdown("</ul></div></div>", unsafe_allow_html=True)

# おすすめ
if weak_keys:
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown(
            """
            <div class="note">
              <div class="cap">2-2. これから伸ばせる要素と具体的な行動例</div>
              <div class="tx">
            """,
            unsafe_allow_html=True
        )
        for k in weak_keys:
            st.markdown(f"**{icons.get(k,'💡')} {full_labels[k]}（{k}）**", unsafe_allow_html=True)
            for t in tips[k]:
                st.markdown(f"- {t}")
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

    with c2:
        st.image(
            "https://eiyoushi-hutaba.com/wp-content/uploads/2025/01/%E5%85%83%E6%B0%97%E3%81%AA%E3%82%B7%E3%83%8B%E3%82%A2%E3%81%AE%E4%BA%8C%E4%BA%BA%E3%80%80%E9%81%8B%E5%8B%95%E7%89%88.png",
            use_container_width=True
        )

# 参考用紙の「基準値」っぽく：このページ下に簡易の目安表
st.markdown(
    f"""
    <div class="section" style="margin-top:10px;">
      <div class="sec-head">
        <div class="ttl">得点の目安（参考）</div>
        <div class="sub">平均マーカーは“参考平均”です</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)
render_norm_table()

st.markdown("</div>", unsafe_allow_html=True)  # page-2 end

# =========================================================
# 3枚目：備考（読みやすく、根拠明記）
# =========================================================
st.markdown("<div class='print-page page-3'>", unsafe_allow_html=True)

st.markdown(
    f"""
    <div class="section">
      <div class="sec-head">
        <div class="ttl">3. 備考</div>
        <div class="sub">この結果の背景・見方</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

render_remarks()

st.markdown(
    """
    <div class="footer">
      <div class="t">この評価結果に関するお問い合わせ</div>
      <div>
        〈お問い合わせ先〉〒 474-0037<br>
        愛知県大府市半月町三丁目294番地<br>
        ☎ 0562-44-5551　研究代表者：李 相侖
      </div>
      <div style="margin-top:0.6rem; font-weight:900;">
        この度は、ご協力ありがとうございました。
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("</div>", unsafe_allow_html=True)  # page-3 end
st.markdown("</div>", unsafe_allow_html=True)  # main-wrap end
