# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, List, Dict

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
  padding:0.75rem 0.95rem;
  margin-bottom:0.65rem;
  box-shadow: 0 1px 3px rgba(0,0,0,.06);
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

div[data-testid="stRadio"] > label {{
  font-weight: 700;
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

# PERMA-Profiler 15項目 + 補足8項目
questions = [
    ("P", "あなたは、ふだん前向きな気持ちになることがどれくらいありますか。"),
    ("E", "あなたは、何かに夢中になったり集中したりすることがどれくらいありますか。"),
    ("R", "あなたは、人との関わりやつながりに満足していますか。"),
    ("M", "あなたは、自分のしていることに意味や価値を感じますか。"),
    ("A", "あなたは、何かをやりとげたと感じることがどれくらいありますか。"),

    ("P", "あなたは、楽しいと感じることがどれくらいありますか。"),
    ("E", "あなたは、時間を忘れるほど何かに没頭することがありますか。"),
    ("R", "あなたには、困ったときに頼れる人がいますか。"),
    ("M", "あなたは、自分の人生に目的があると感じますか。"),
    ("A", "あなたは、自分が達成してきたことに満足していますか。"),

    ("P", "あなたは、日々の中で希望を感じることがありますか。"),
    ("E", "あなたは、活動の中で生き生きしていると感じますか。"),
    ("R", "あなたは、周囲の人に受け入れられていると感じますか。"),
    ("M", "あなたは、自分らしく生きられていると感じますか。"),
    ("A", "あなたは、自分なりに前に進めていると感じますか。"),

    ("全体的なしあわせ感", "全体として、あなたはどれくらい幸せですか。"),
    ("気持ちの様子（いやな気持）", "あなたは、いやな気持ち（不安・怒り・悲しみなど）をどれくらい感じますか。"),
    ("気持ちの様子（いやな気持）", "あなたは、落ち着かない・イライラする感じをどれくらい感じますか。"),
    ("気持ちの様子（いやな気持）", "あなたは、気分がしずむことがどれくらいありますか。"),
    ("ひとりぼっち感", "あなたは、ひとりぼっちだと感じることがどれくらいありますか。"),
    ("からだの調子", "あなたは、自分のからだの調子をどれくらい良いと感じますか。"),
    ("からだの調子", "あなたは、日常生活を送るうえで体力があると感じますか。"),
    ("からだの調子", "あなたは、健康状態に満足していますか。"),
]

# =========================
# 計算関数
# =========================
def compute_domain_avg(vals: List[float], idx: List[int]) -> float:
    scores = [vals[i] for i in idx if i < len(vals)]
    return float(np.mean(scores)) if scores else np.nan

def mean_or_nan(values: List[float]) -> float:
    valid = [v for v in values if v is not None and not pd.isna(v)]
    return float(np.mean(valid)) if valid else np.nan

def score_to_comment(score: float) -> str:
    if pd.isna(score):
        return "評価できません。"
    if score >= 8:
        return "とても良い状態です。"
    if score >= 6:
        return "比較的保たれています。"
    if score >= 4:
        return "まずまずですが、少し意識して整える余地があります。"
    return "やや低めで、日々の過ごし方を見直すヒントがありそうです。"

def neg_score_comment(score: float) -> str:
    if pd.isna(score):
        return "評価できません。"
    if score <= 2:
        return "いやな気持ちは比較的少ない状態です。"
    if score <= 4:
        return "大きな問題ではないかもしれませんが、波があるかもしれません。"
    if score <= 6:
        return "少し負担がたまっている可能性があります。"
    return "つらさが強めかもしれません。必要に応じて身近な人や専門職に相談してください。"

def get_strengths(domain_scores: Dict[str, float]) -> List[str]:
    sorted_items = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
    top = [k for k, _ in sorted_items[:2]]
    messages = []
    for k in top:
        messages.append(f"「{full_labels[k]}」があなたの強みとしてみられます。{descriptions[k]}")
    return messages

def get_recommendations(domain_scores: Dict[str, float]) -> List[str]:
    sorted_items = sorted(domain_scores.items(), key=lambda x: x[1])
    low = [k for k, _ in sorted_items[:2]]
    recs = []
    mapping = {
        "P": "気分が少し上がることを1日の中に1つ入れてみましょう。散歩、音楽、日なたぼっこなど小さなことで大丈夫です。",
        "E": "短い時間でも集中できる活動を取り入れてみましょう。読書、手作業、趣味など“ちょっと夢中になれること”がおすすめです。",
        "R": "あいさつや短い会話など、無理のない人との関わりを少し増やしてみましょう。",
        "M": "自分にとって大切なことを振り返る時間を持つのがおすすめです。『今日は何がよかったか』を考えるだけでも役立ちます。",
        "A": "小さな目標を決めて、できたことを確認してみましょう。『できた』の積み重ねが力になります。",
    }
    for k in low:
        recs.append(mapping[k])
    return recs

# =========================
# 表示用関数
# =========================
def FORCE_PAGE_BREAK():
    st.markdown('<div class="force-break"></div>', unsafe_allow_html=True)

def page_header(title: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div class="page-header">
          <div class="title">{title}</div>
          <div class="sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def section_header(title: str):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)

def render_meter_card(label: str, score: float, color: str, description: Optional[str] = None):
    safe_score = 0 if pd.isna(score) else max(0, min(10, score))
    width_pct = safe_score * 10

    desc_html = f"<div style='margin-top:6px; color:#444;'>{description}</div>" if description else ""
    st.markdown(
        f"""
        <div class="score-card">
          <div style="font-weight:900; font-size:1.08rem;">{label}</div>
          <div class="meter" style="margin-top:8px;">
            <div class="meter-fill" style="width:{width_pct}%; background:{color};"></div>
          </div>
          <div class="meter-score-text">
            点数：<span class="score-strong">{safe_score:.1f}</span> / 10
          </div>
          {desc_html}
        </div>
        """,
        unsafe_allow_html=True
    )

def render_extras_meaning_note():
    st.markdown(
        """
        <div class="mini-note">
          <b>補足項目の見方</b><br>
          「心の健康の総合得点」は、PERMAの5つの要素全体をまとめた目安です。<br>
          「気持ちの様子（いやな気持）」と「ひとりぼっち感」は、<b>低いほど負担が少ない</b>ことを表します。<br>
          「からだの調子」と「全体的なしあわせ感」は、<b>高いほど良い状態</b>を表します。
        </div>
        """,
        unsafe_allow_html=True
    )

def render_remarks_box():
    st.markdown(
        """
        <div class="mini-note">
          <b>この結果について</b><br>
          この評価は、現在の心とからだの状態を振り返るための参考情報です。<br>
          医学的な診断を行うものではありません。体調や気分の変化が強い場合、または困りごとが続く場合には、
          医療機関や専門職への相談もご検討ください。<br><br>
          また、結果はその日の体調や気分、最近の出来事の影響を受けることがあります。
          一度きりではなく、少し時間をおいて見直すことも大切です。
        </div>
        """,
        unsafe_allow_html=True
    )

def show_answer_form():
    st.markdown(
        """
        <div class="mini-note">
          各質問について、0〜10点でお答えください。<br>
          0は「まったくあてはまらない」、10は「とてもあてはまる」です。
        </div>
        """,
        unsafe_allow_html=True
    )

    values = []
    for i, (_, q) in enumerate(questions, start=1):
        val = st.slider(
            f"{i}. {q}",
            min_value=0,
            max_value=10,
            value=5,
            key=f"q_{i}"
        )
        values.append(val)
    return values

# =========================
# アプリ本体
# =========================
st.title("わらトレ　心の健康チェック")

page_header(
    "ご自身のこころの状態をふり返ってみましょう",
    "PERMAの考え方にもとづいて、心の健康の5つの要素と補足項目を確認します。"
)

show_answer_form()

if st.button("結果を表示する", type="primary"):
    vals = [st.session_state[f"q_{i}"] for i in range(1, len(questions) + 1)]

    # 15項目のPERMA本体
    p_idx = [0, 5, 10]
    e_idx = [1, 6, 11]
    r_idx = [2, 7, 12]
    m_idx = [3, 8, 13]
    a_idx = [4, 9, 14]

    P = compute_domain_avg(vals, p_idx)
    E = compute_domain_avg(vals, e_idx)
    R = compute_domain_avg(vals, r_idx)
    M = compute_domain_avg(vals, m_idx)
    A = compute_domain_avg(vals, a_idx)

    overall_wellbeing = mean_or_nan(vals[0:15] + [vals[15]])   # 15 PERMA + 幸福感
    negative_emotion = mean_or_nan(vals[16:19])                # 不安・怒り・悲しみ相当
    loneliness = vals[19]                                      # 単独項目
    physical_health = mean_or_nan(vals[20:23])                 # からだの調子3項目
    happiness = vals[15]                                       # 全体的なしあわせ感

    domain_scores = {"P": P, "E": E, "R": R, "M": M, "A": A}

    # --- 1ページ目 ---
    section_header("1-1. 心の健康の5つの要素（PERMA）")

    for k in ["P", "E", "R", "M", "A"]:
        render_meter_card(
            full_labels[k],
            domain_scores[k],
            colors[k],
            f"{descriptions[k]} {score_to_comment(domain_scores[k])}"
        )

    # --- 2ページ目開始 ---
    FORCE_PAGE_BREAK()

    st.markdown('<div class="section-header">1-2. こころ・からだの調子</div>', unsafe_allow_html=True)

    render_meter_card(
        "心の健康の総合得点",
        overall_wellbeing,
        extra_colors["心の健康の総合得点"],
        score_to_comment(overall_wellbeing)
    )
    render_meter_card(
        "気持ちの様子（いやな気持）",
        negative_emotion,
        extra_colors["気持ちの様子（いやな気持）"],
        neg_score_comment(negative_emotion)
    )
    render_meter_card(
        "からだの調子",
        physical_health,
        extra_colors["からだの調子"],
        score_to_comment(physical_health)
    )
    render_meter_card(
        "ひとりぼっち感",
        loneliness,
        extra_colors["ひとりぼっち感"],
        "この項目は低いほど、孤立感が少ない状態を示します。"
    )
    render_meter_card(
        "全体的なしあわせ感",
        happiness,
        extra_colors["全体的なしあわせ感"],
        score_to_comment(happiness)
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

    strengths = get_strengths(domain_scores)
    for msg in strengths:
        st.markdown(f'<div class="mini-note">● {msg}</div>', unsafe_allow_html=True)

    # --- 2-2 ---
    st.markdown('<div class="section-header">2-2. おすすめな行動</div>', unsafe_allow_html=True)

    recs = get_recommendations(domain_scores)
    for msg in recs:
        st.markdown(f'<div class="mini-note">● {msg}</div>', unsafe_allow_html=True)

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
else:
    st.info("質問に回答したあと、「結果を表示する」を押してください。")
