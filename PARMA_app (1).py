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
# CSSスタイル（透明バー削除＆余白調整）
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
  margin:0.6rem 0; /* ← 少し詰める */
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

/* ✅ Streamlit の不要な透明バーを完全除去 */
div[data-testid="stVerticalBlock"] > div:has(> div[class*="stMarkdown"]) {{
  margin-top: 0 !important;
  margin-bottom: 0 !important;
  padding-top: 0 !important;
  padding-bottom: 0 !important;
}}
div.block-container {{
  padding-top: 1rem !important;
  padding-bottom: 1rem !important;
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
extra_indices = {
    'ネガティブ感情':[6,13,19],
    '健康感':[3,12,17],
    '孤独感':[11],
    '幸福感':[22],
}

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
tips = {
    'P':['感謝を込めた手紙を書く','その日の「良かったこと」を3つ書く'],
    'E':['自分の得意なことを活かす','小さな挑戦を設定して取り組む'],
    'R':['日常で小さな親切を行う','家族や友人に感謝を伝える'],
    'M':['自分の大切にしている価値を書き出す','過去の困難を乗り越えた経験を振り返る'],
    'A':['小さな目標を達成する習慣を作る','失敗も学びととらえる'],
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
# レーダーチャート（文字色も要素色）
# =========================
def plot_radar(perma_scores):
    labels = list(perma_scores.keys())
    values = list(perma_scores.values())
    values += values[:1]
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(3.8,3.8), subplot_kw=dict(polar=True), dpi=160)
    ax.set_theta_offset(np.pi/2)
    ax.set_theta_direction(-1)

    # 項目ごとの線と色
    for i, k in enumerate(labels):
        ax.plot([angles[i], angles[i+1]], [values[i], values[i+1]], color=colors[k], linewidth=2.5)
    ax.fill(angles, values, alpha=0.1, color="#888")

    # ラベルを要素色で表示
    for i, label in enumerate(labels):
        ax.text(angles[i], 10.6, label, color=colors[label], fontsize=12, fontweight='bold',
                ha='center', va='center')

    ax.set_ylim(0,10)
    ax.set_rticks([2,5,8])
    ax.grid(alpha=0.3)
    ax.set_xticklabels([])
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
        name_display = f"{sid}様"
        st.write(f"以下は、あなたの日ごろの気持ちについての結果です。")

        perma_scores, extras = compute_results(selected_row)

        # === レーダーチャート ===
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">PERMAバランスチャート</div>', unsafe_allow_html=True)
        plot_radar(perma_scores)
        st.markdown('</div>', unsafe_allow_html=True)

        # === 各要素の説明 ===
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">各要素の説明</div>', unsafe_allow_html=True)
        for k in ['P','E','R','M','A']:
            st.markdown(
                f"<span class='color-label' style='background:{colors[k]}'>{k}</span> "
                f"**{full_labels[k]}**：{descriptions[k]}",
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

        # === 結果のまとめ（整数表示） ===
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">結果のまとめ</div>', unsafe_allow_html=True)
        st.markdown("""
        **0〜10点満点のうち、7点以上＝強み、4〜6点＝おおむね良好、3点以下＝サポートが必要**  
        以下は、PERMAの各要素ごとのスコアです。
        """)
        for k,v in perma_scores.items():
            st.write(f"{k}（{full_labels[k]}）：{int(round(v))} 点")
        st.markdown('</div>', unsafe_allow_html=True)

        # === 補助指標 ===
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">補助指標（あくまで参考程度にしてください）</div>', unsafe_allow_html=True)
        for k,v in extras.items():
            if not np.isnan(v):
                st.write(f"{k}：{int(round(v))} 点")
        st.markdown('</div>', unsafe_allow_html=True)

        # === おすすめ活動 ===
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">あなたにおすすめな行動（例）</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            for k in ['P','E','R']:
                st.markdown(f"**{full_labels[k]}**", unsafe_allow_html=True)
                for t in tips[k]:
                    st.markdown(f"- {t}")
        with col2:
            for k in ['M','A']:
                st.markdown(f"**{full_labels[k]}**", unsafe_allow_html=True)
                for t in tips[k]:
                    st.markdown(f"- {t}")
        st.markdown('</div>', unsafe_allow_html=True)

        # === 注意事項 ===
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">この結果を受け取るうえで大切なこと</div>', unsafe_allow_html=True)
        st.markdown("""
        - 結果は“良い・悪い”ではなく、あなたの**今の状態や環境**を表しています。  
        - 改善のためには、**無理せず小さな一歩**から始めましょう（例：1日5分の散歩）。  
        - このチェックは**医療的診断ではありません**。気分の落ち込みが続く場合は、専門職にご相談ください。
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

# PDF生成関数
def generate_pdf(perma_scores, extras, tips, chart_path):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>わらトレ　心の健康チェック</b>", styles['Title']))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("以下は、あなたの日ごろの気持ちについての結果です。", styles['Normal']))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("<b>PERMAバランスチャート</b>", styles['Heading2']))
    story.append(Image(chart_path, width=10*cm, height=10*cm))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("<b>結果のまとめ</b>", styles['Heading2']))
    story.append(Paragraph("0〜10点満点のうち、7点以上＝強み、4〜6点＝おおむね良好、3点以下＝サポートが必要", styles['Normal']))
    for k, v in perma_scores.items():
        story.append(Paragraph(f"{k}：{int(round(v))} 点", styles['Normal']))

    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("<b>補助指標（参考）</b>", styles['Heading2']))
    for k, v in extras.items():
        if not np.isnan(v):
            story.append(Paragraph(f"{k}：{int(round(v))} 点", styles['Normal']))

    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("<b>あなたにおすすめな行動（例）</b>", styles['Heading2']))
    for k, acts in tips.items():
        story.append(Paragraph(f"<b>{full_labels[k]}</b>", styles['Normal']))
        for act in acts:
            story.append(Paragraph(f"・{act}", styles['Normal']))
        story.append(Spacer(1, 0.1*cm))

    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("<b>この結果を受け取るうえで大切なこと</b>", styles['Heading2']))
    story.append(Paragraph(
        "・結果は“良い・悪い”ではなく、あなたの今の状態や環境を表しています。<br/>"
        "・改善のためには、無理せず小さな一歩から始めましょう（例：1日5分の散歩）。<br/>"
        "・このチェックは医療的診断ではありません。気分の落ち込みが続く場合は、専門職にご相談ください。",
        styles['Normal']
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer

# チャート画像を一時保存
chart_path = "chart_tmp.png"
plt.savefig(chart_path, dpi=200)

pdf_buffer = generate_pdf(perma_scores, extras, tips, chart_path)
st.download_button(
    label="📥 結果をPDFで保存",
    data=pdf_buffer,
    file_name=f"PERMA_report_{sid}.pdf",
    mime="application/pdf"
)

else:
    st.info("まずはExcelファイルをアップロードしてください。")

st.markdown('</div>', unsafe_allow_html=True)
