# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd, numpy as np
import matplotlib.pyplot as plt

# =========================
# 基本設定
# =========================
st.set_page_config(page_title="わらトレ　心の健康チェック", layout="centered")

plt.rcParams.update({
    "font.sans-serif": ["BIZ UDPGothic","Meiryo","Noto Sans JP"],
    "axes.unicode_minus": False,
    "font.size": 12,
})

# =========================
# カラーテーマ
# =========================
colors = {
    "P": "#F28B82",  # ピンク
    "E": "#FDD663",  # 黄色
    "R": "#81C995",  # 緑
    "M": "#AECBFA",  # 水色
    "A": "#F9AB00",  # オレンジ
}
theme = {
    "bg": "#FAFAFA",
    "card_bg": "#FFFFFF",
    "accent": "#4E73DF",
    "text": "#222",
}

# =========================
# CSSスタイル
# =========================
st.markdown(f"""
<style>
html, body, [class*="css"] {{
  background-color:{theme['bg']};
  color:{theme['text']};
  font-family:"BIZ UDPGothic","Meiryo",sans-serif;
  line-height:1.8;
}}
.main-wrap {{ max-width:860px; margin:0 auto; }}
h1 {{ text-align:center; color:#333; margin-top:0.4em; }}
.section-card {{
  background:{theme['card_bg']};
  border-radius:14px;
  box-shadow:0 3px 8px rgba(0,0,0,0.07);
  padding:1rem 1.4rem;
  margin:1rem 0;
}}
.section-title {{
  font-weight:700;
  border-left:8px solid {theme['accent']};
  padding-left:.5rem;
  margin-bottom:.6rem;
}}
.advice-box {{
  background:#FFF8E1;
  border-left:6px solid #FFD54F;
  padding:.7rem 1rem;
  border-radius:10px;
  font-size:1rem;
  color:#333;
}}
.color-label {{
  font-weight:bold;
  padding:2px 8px;
  border-radius:6px;
  color:white;
}}
</style>
""", unsafe_allow_html=True)

# =========================
# データ定義
# =========================
perma_indices = {
    'P':[4,9,21],
    'E':[2,10,20],
    'R':[5,14,18],
    'M':[0,8,16],
    'A':[1,7,15],
}
extra_indices = {'Negative Emotion':[6,13,19],'Health':[3,12,17],'Loneliness':[11],'Happiness':[22]}

full_labels = {
    'P':'前向きな気持ち（Positive Emotion）',
    'E':'集中して取り組むこと（Engagement）',
    'R':'人とのつながり（Relationships）',
    'M':'生きがいや目的（Meaning）',
    'A':'達成感（Accomplishment）',
}
descriptions = {
    'P':'楽しい気持ちや感謝、安心感など、心のゆとりを感じることができています。',
    'E':'夢中で取り組む時間や没頭できる活動が生活の中にあります。',
    'R':'家族や友人、地域とのつながりを感じ、支え合えていることを示します。',
    'M':'自分の人生に目的や価値を見いだし、大切なことに沿って生きています。',
    'A':'目標に向かって取り組み、やり遂げた達成感を感じられています。',
}

# =========================
# 計算関数
# =========================
def compute_domain_avg(vals, idx_list):
    scores = [vals[i] for i in idx_list if i < len(vals) and not np.isnan(vals[i])]
    return float(np.mean(scores)) if scores else np.nan

def compute_results(selected_row: pd.DataFrame):
    cols = [c for c in selected_row.columns if str(c).startswith("6_")]
    vals = pd.to_numeric(selected_row[cols].values.flatten(), errors='coerce')
    perma_scores = {k: compute_domain_avg(vals, idx) for k, idx in perma_indices.items()}
    extras = {k: compute_domain_avg(vals, idx) for k, idx in extra_indices.items()}
    return perma_scores, extras

# =========================
# レーダーチャート
# =========================
def plot_radar(perma_scores):
    labels = list(perma_scores.keys())
    values = list(perma_scores.values())
    values += values[:1]
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(3.4,3.4), subplot_kw=dict(polar=True), dpi=160)
    ax.set_theta_offset(np.pi/2)
    ax.set_theta_direction(-1)

    for i, k in enumerate(labels):
        ax.plot([angles[i], angles[i+1]], [values[i], values[i+1]],
                color=colors[k], linewidth=2.5)
    ax.fill(angles, values, alpha=0.1, color="#999")
    ax.set_thetagrids(np.degrees(angles[:-1]), labels, fontsize=11, fontweight='bold')
    ax.set_ylim(0,10)
    ax.set_rticks([2,5,8])
    ax.grid(alpha=0.3)
    fig.tight_layout(pad=0.2)
    st.pyplot(fig)

# =========================
# 本体
# =========================
st.markdown('<div class="main-wrap">', unsafe_allow_html=True)
st.title("わらトレ　心の健康チェック")

uploaded = st.file_uploader("Excelファイル（ID列＋6_1〜6_23列）をアップロードしてください", type="xlsx")

if uploaded:
    df = pd.read_excel(uploaded)
    id_list = df.iloc[:,0].dropna().astype(str).tolist()
    sid = st.selectbox("IDを選んでください", options=id_list)
    selected_row = df[df.iloc[:,0].astype(str)==sid]

    if selected_row.empty:
        st.warning("選択されたIDが見つかりません。")
    else:
        # 名前としてIDを利用
        name_display = f"{sid}様"
        st.write(f"以下は、**{name_display}の日ごろの気持ち**についての結果です。")

        perma_scores, extras = compute_results(selected_row)

        # === レーダーチャート ===
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">PERMAバランスチャート</div>', unsafe_allow_html=True)
        plot_radar(perma_scores)
        st.markdown('</div>', unsafe_allow_html=True)

        # === 各要素の説明（色を統一） ===
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">各要素の説明</div>', unsafe_allow_html=True)
        for k in ['P','E','R','M','A']:
            st.markdown(
                f"<span class='color-label' style='background:{colors[k]}'>{k}</span> "
                f"**{full_labels[k]}**：{descriptions[k]}",
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

        # === 結果のまとめ ===
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">結果のまとめ</div>', unsafe_allow_html=True)
        st.markdown("""
        **0〜10点満点のうち、7点以上＝強み、4〜6点＝おおむね良好、3点以下＝サポートが必要**  
        以下は、PERMAの各要素ごとのスコアです。
        """)
        for k,v in perma_scores.items():
            st.write(f"{k}（{full_labels[k]}）：{v:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

        # === 補助指標 ===
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">補助指標</div>', unsafe_allow_html=True)
        for k,v in extras.items():
            if not np.isnan(v):
                st.write(f"{k}：{v:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

        # === コメント ===
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">アドバイス</div>', unsafe_allow_html=True)
        st.markdown("""
        - 高いスコアはあなたの強みとして活かしましょう。  
        - 少し低めの要素は、日々の工夫でゆっくり伸ばせます。  
        - 「感謝を記録する」「趣味の時間を作る」など小さな実践を続けることで、心の健康を維持できます。
        """)
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("まずはExcelファイルをアップロードしてください。")

st.markdown('</div>', unsafe_allow_html=True)
