# -*- coding: utf-8 -*-
import os
from typing import Optional, Dict, List

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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
  background-color: {theme['bg']};
  color: {theme['text']};
  font-family: "BIZ UDPGothic", "Meiryo", sans-serif;
}}

.main-wrap {{
  max-width: 880px;
  margin: 0 auto;
}}

.section-header {{
  background: {theme['bar_bg']};
  font-weight: 900;
  font-size: 1.15rem;
  padding: .55rem 1rem;
  border-left: 8px solid {theme['accent']};
  border-radius: 8px;
  margin-top: 0.9rem;
  margin-bottom: 0.7rem;
}}

.page-header {{
  background: white;
  border-left: 10px solid {theme['accent']};
  border-radius: 14px;
  padding: 1.0rem 1.2rem;
  margin: 0.9rem 0;
}}

.page-header .title {{
  font-size: 1.45rem;
  font-weight: 950;
}}

.page-header .sub {{
  font-size: 1.02rem;
}}

.score-card {{
  background: white;
  border-radius: 12px;
  padding: 0.7rem 0.95rem;
  margin-bottom: 0.6rem;
  border: 1px solid #EEF2FB;
}}

.meter {{
  background: #E0E0E0;
  border-radius: 999px;
  height: 14px;
  width: 100%;
}}

.meter-fill {{
  height: 100%;
  border-radius: 999px;
}}

.meter-score-text {{
  font-size: 1.05rem;
  margin-top: 4px;
}}

.meter-score-text .score-strong {{
  font-size: 1.28rem;
  font-weight: 1000;
}}

.mini-note {{
  background: white;
  border: 1px solid #E6EAF5;
  border-radius: 12px;
  padding: 0.65rem 0.85rem;
  margin: 0.55rem 0;
}}

.perma-box {{
  border: 3px solid {theme['accent']};
  border-radius: 12px;
  padding: 1.05rem 1.25rem;
  background: white;
  margin-bottom: 0.8rem;
}}

.footer-box {{
  border-top: 2px solid #DDD;
  margin-top: 1.6rem;
  padding-top: 1rem;
}}

.footer-title {{
  font-weight: 900;
}}

.footer-thanks {{
  margin-top: 0.85rem;
  font-weight: 800;
}}

.spacer-6 {{
  height: 6px;
}}

.spacer-10 {{
  height: 10px;
}}

.force-break {{
  display: block;
  height: 0;
}}

.perma-row {{
  background: white;
  border-radius: 12px;
  padding: 0.8rem 0.9rem;
  margin-bottom: 0.7rem;
  border: 1px solid #EEF2FB;
}}

.perma-left {{
  padding-right: 0.4rem;
}}

.perma-chart-box {{
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding-right: 0.25rem;
}}

.growth-illust-wrap {{
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0.2rem 0 0.4rem 0;
}}

.small-muted {{
  font-size: 0.9rem;
  color: #666;
}}

@media print {{
  @page {{
    size: A4;
    margin: 8mm;
  }}

  .force-break {{
    break-before: page !important;
    page-break-before: always !important;
  }}

  img {{
    max-height: 72px !important;
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

# =========================
# 計算関数
# =========================
def safe_float(x, default=np.nan):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def clamp_score(x: float, lo: float = 0.0, hi: float = 10.0) -> float:
    x = safe_float(x, 0.0)
    return max(lo, min(hi, x))


def compute_domain_avg(vals: List[float], idx: List[int]) -> float:
    scores = []
    for i in idx:
        if i < len(vals):
            v = safe_float(vals[i], np.nan)
            if not np.isnan(v):
                scores.append(v)
    return float(np.mean(scores)) if scores else np.nan

# =========================
# 改ページ
# =========================
def FORCE_PAGE_BREAK():
    st.markdown('<div class="force-break"></div>', unsafe_allow_html=True)

# =========================
# 共通表示関数
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


def render_small_histogram(
    score: float,
    color: str,
    x_max: float = 10.0,
    width: float = 3.35,
    height: float = 1.65,
):
    score = clamp_score(score, 0.0, x_max)

    fig, ax = plt.subplots(figsize=(width, height), dpi=180)
    ax.barh([0], [x_max], color="#E9EEF8", height=0.42)
    ax.barh([0], [score], color=color, height=0.42)

    ax.set_xlim(0, x_max)
    ax.set_ylim(-0.6, 0.6)
    ax.set_xticks([])
    ax.set_yticks([])

    for spine in ax.spines.values():
        spine.set_visible(False)

    label_x = min(score + 0.18, x_max - 0.20)
    align = "left"
    if score >= x_max - 0.8:
        label_x = score - 0.15
        align = "right"

    ax.text(
        label_x,
        0,
        f"{score:.1f}",
        va="center",
        ha=align,
        fontsize=10.5,
        fontweight="bold"
    )

    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    plt.tight_layout(pad=0.4)
    return fig


def render_meter_card(title: str, score: float, color: str):
    score = clamp_score(score)
    percent = score / 10 * 100
    st.markdown(
        f"""
        <div class="score-card">
            <div style="font-weight:900; margin-bottom:0.35rem;">{title}</div>
            <div class="meter">
                <div class="meter-fill" style="width:{percent:.1f}%; background:{color};"></div>
            </div>
            <div class="meter-score-text">
                <span class="score-strong">{score:.1f}</span> / 10
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_perma_summary_box(domain_scores: Dict[str, float]):
    st.markdown('<div class="perma-box">', unsafe_allow_html=True)
    st.markdown("**PERMAの5つの要素**")
    st.markdown(
        """
P：前向きな気持ち  
E：集中して取り組むこと  
R：人とのつながり  
M：生きがいや目的  
A：達成感
        """
    )

    valid_scores = [safe_float(domain_scores.get(k), np.nan) for k in ["P", "E", "R", "M", "A"]]
    valid_scores = [x for x in valid_scores if not np.isnan(x)]
    overall = float(np.mean(valid_scores)) if valid_scores else np.nan

    if not np.isnan(overall):
        st.markdown(f"**心の健康の総合得点：{overall:.1f} / 10**")

    st.markdown('</div>', unsafe_allow_html=True)


def render_perma_item(key: str, score: float):
    label = full_labels.get(key, key)
    desc = descriptions.get(key, "")
    color = colors.get(key, theme["accent"])

    st.markdown('<div class="perma-row">', unsafe_allow_html=True)
    left_col, right_col = st.columns([1.55, 1.0], gap="medium")

    with left_col:
        st.markdown(
            f"""
            <div class="perma-left">
                <div style="font-weight:900; font-size:1.08rem; color:{color};">
                    {key}：{label}
                </div>
                <div style="margin-top:0.25rem; line-height:1.7;">
                    {desc}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with right_col:
        st.markdown('<div class="perma-chart-box">', unsafe_allow_html=True)
        fig = render_small_histogram(
            score=safe_float(score, 0.0),
            color=color,
            width=3.35,
            height=1.65
        )
        st.pyplot(fig, use_container_width=False)
        plt.close(fig)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def render_extras_meaning_note():
    st.markdown(
        """
        <div class="mini-note">
          <b>補足の見かた</b><br>
          「いやな気持ち」は点が高いほど、その気持ちを感じやすい可能性があります。<br>
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


def get_strengths_and_growth(domain_scores: Dict[str, float]):
    pairs = [(k, safe_float(v, np.nan)) for k, v in domain_scores.items() if not np.isnan(safe_float(v, np.nan))]
    pairs_sorted = sorted(pairs, key=lambda x: x[1], reverse=True)
    strengths = pairs_sorted[:2]
    growth = pairs_sorted[-2:] if len(pairs_sorted) >= 2 else pairs_sorted
    return strengths, growth


def recommendation_text(key: str) -> str:
    recs = {
        "P": "気分が少し上がる活動を、短時間でも日常に入れてみましょう。好きな音楽、散歩、ほっとできる時間づくりが役立ちます。",
        "E": "時間を忘れて取り組めることを少しずつ増やしてみましょう。無理のない範囲で、楽しめる作業や趣味を続けることが大切です。",
        "R": "身近な人との会話やあいさつ、短い交流でもつながりの感覚を保ちやすくなります。",
        "M": "自分にとって大切なことや、続けたい役割を振り返る時間を持つと、生きがいや目的を感じやすくなります。",
        "A": "小さな目標を立てて、できたことを確認する習慣が達成感につながります。",
    }
    return recs.get(key, "無理のない範囲で、日常の中の小さな行動を積み重ねていきましょう。")


def render_growth_illustration(image_path: Optional[str] = None, width_px: int = 120):
    st.markdown('<div class="growth-illust-wrap">', unsafe_allow_html=True)

    if image_path and os.path.exists(image_path):
        st.image(image_path, width=width_px)
    else:
        st.markdown(
            f"""
            <div style="
                width:{width_px}px;
                height:{width_px}px;
                border-radius:16px;
                background:#F4F7FD;
                border:1px solid #E1E7F5;
                display:flex;
                align-items:center;
                justify-content:center;
                font-size:2rem;
            ">
                🌱
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# サンプルデータ
# ここは既存ロジックに置き換えてください
# =========================
def load_demo_scores():
    domain_scores = {
        "P": 6.8,
        "E": 7.4,
        "R": 6.1,
        "M": 7.0,
        "A": 6.5,
    }

    extras = {
        "心の健康の総合得点": 6.8,
        "気持ちの様子（いやな気持）": 3.2,
        "からだの調子": 6.4,
        "ひとりぼっち感": 2.8,
        "全体的なしあわせ感": 7.1,
    }
    return domain_scores, extras

# =========================
# メイン
# =========================
def main():
    st.title("わらトレ　心の健康チェック")

    domain_scores, extras = load_demo_scores()
    strengths, growth = get_strengths_and_growth(domain_scores)

    # --- 1ページ目 ---
    page_header(
        "1. あなたの心の健康チェック結果",
        "PERMAの5つの要素と、こころ・からだの調子の目安をまとめています。"
    )

    st.markdown('<div class="section-header">1-1. 要素ごとに見た心の状態</div>', unsafe_allow_html=True)

    render_perma_summary_box(domain_scores)

    for key in ["P", "E", "R", "M", "A"]:
        render_perma_item(key, domain_scores.get(key, np.nan))

    # --- 2ページ目開始 ---
    FORCE_PAGE_BREAK()

    st.markdown('<div class="section-header">1-2. こころ・からだの調子</div>', unsafe_allow_html=True)

    for name in [
        "心の健康の総合得点",
        "気持ちの様子（いやな気持）",
        "からだの調子",
        "ひとりぼっち感",
        "全体的なしあわせ感",
    ]:
        render_meter_card(
            title=name,
            score=extras.get(name, np.nan),
            color=extra_colors.get(name, theme["accent"])
        )

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
                  <div style="font-weight:900; color:{colors.get(key, theme['accent'])}; font-size:1.06rem;">
                    {key}：{full_labels.get(key, key)}（{score:.1f} / 10）
                  </div>
                  <div style="margin-top:0.35rem; line-height:1.7;">
                    {descriptions.get(key, "")}<br>
                    この要素は、今の生活の中で比較的保たれている強みとして考えられます。
                  </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("強みの表示に必要なデータがありません。")

    # --- 2-2 ---
    st.markdown('<div class="section-header">2-2. これから伸ばせる要素と具体的な行動ライン</div>', unsafe_allow_html=True)

    if growth:
        for key, score in growth:
            left_col, right_col = st.columns([1.45, 0.9], gap="medium")

            with left_col:
                st.markdown(
                    f"""
                    <div class="score-card">
                      <div style="font-weight:900; color:{colors.get(key, theme['accent'])}; font-size:1.06rem;">
                        {key}：{full_labels.get(key, key)}（{score:.1f} / 10）
                      </div>
                      <div style="margin-top:0.4rem; line-height:1.75;">
                        {recommendation_text(key)}
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with right_col:
                render_growth_illustration(image_path=None, width_px=120)
    else:
        st.info("おすすめ行動の表示に必要なデータがありません。")

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


if __name__ == "__main__":
    main()
