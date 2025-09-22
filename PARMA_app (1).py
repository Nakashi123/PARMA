# -*- coding: utf-8 -*-
import io, base64
import streamlit as st
import pandas as pd, numpy as np
import matplotlib.pyplot as plt

# =========================
# 基本設定
# =========================
st.set_page_config(page_title="PERMAプロファイル", layout="centered")

# 画面用（高齢者向けには大きめ）、ただし印刷時は別CSSで縮小
BASE_FONT_PX = 19
H1_REM, H2_REM, H3_REM = 2.2, 1.9, 1.6
LINE_HEIGHT = 1.8
CARD_RADIUS_PX, CARD_PAD_REM = 12, 0.9
FONT_SCALE = 1.1  # 図のフォント

plt.rcParams.update({
    "font.size": int(13 * FONT_SCALE),
    "axes.titlesize": int(16 * FONT_SCALE),
    "axes.labelsize": int(14 * FONT_SCALE),
    "xtick.labelsize": int(12 * FONT_SCALE),
    "ytick.labelsize": int(12 * FONT_SCALE),
    "legend.fontsize": int(12 * FONT_SCALE),
    "font.sans-serif": [
        "Yu Gothic UI","Hiragino Kaku Gothic ProN","Meiryo",
        "Noto Sans JP","Noto Sans CJK JP","Helvetica","Arial","DejaVu Sans"
    ],
    "axes.unicode_minus": False,
})

# =========================
# CSS（印刷最適化）
# =========================
st.markdown(f"""
<style>
html, body, [class*="css"] {{
  font-size:{BASE_FONT_PX}px !important;
  line-height:{LINE_HEIGHT} !important;
  font-family:"Yu Gothic UI","Hiragino Kaku Gothic ProN","Meiryo","Noto Sans JP",sans-serif !important;
  color:#111 !important;
}}
h1 {{ font-size:{H1_REM}rem !important; font-weight:800; margin:0 0 .3rem 0; }}
h2 {{ font-size:{H2_REM}rem !important; font-weight:700; margin:.2rem 0 .4rem 0; }}
h3 {{ font-size:{H3_REM}rem !important; font-weight:700; margin:.1rem 0 .4rem 0; }}
.main-wrap {{ max-width: 860px; margin: 0 auto; }}

.section-card {{
  background:#fff; border:1px solid #e6e6e6; border-radius:{CARD_RADIUS_PX}px;
  padding:{CARD_PAD_REM}rem {CARD_PAD_REM+0.2}rem; margin:.6rem 0 .8rem 0;
  box-shadow:0 2px 6px rgba(0,0,0,.05);
  page-break-inside: avoid;
  break-inside: avoid;
}}

.section-title {{ border-bottom:2px solid #f0f0f0; padding-bottom:.25rem; margin-bottom:.45rem; }}

.page-1, .page-2 {{ page-break-inside: avoid; break-inside: avoid; }}
.force-break {{ break-after: page; page-break-after: always; height: 0 !important; margin: 0 !important; padding: 0 !important; }}

@media print {{
  @page {{ size: A4; margin: 13mm; }}
  html, body {{ zoom: 1; }}
  /* 印刷時は文字少しだけ縮小＆行間締める */
  body, [class*="css"] {{ font-size: 16px !important; line-height: 1.55 !important; }}
  h1 {{ font-size: 1.9rem !important; }}
  h2 {{ font-size: 1.6rem !important; }}
  h3 {{ font-size: 1.3rem !important; }}
  .main-wrap {{ max-width: 720px; }}
  .section-card {{ margin: .45rem 0 .6rem 0; padding: .65rem .75rem; }}
  /* StreamlitのUI非表示 */
  .stApp [data-testid="stToolbar"],
  .stApp [data-testid="stDecoration"],
  .stApp [data-testid="stStatusWidget"],
  .stApp [data-testid="stSidebar"],
  .stApp [data-testid="collapsedControl"] {{ display: none !important; }}
  .stApp {{ padding: 0 !important; }}
}}
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
.page { page-break-after: always; }
.first-page .grid1{
  display:grid; grid-template-columns: 240px 1fr; gap:16px; align-items:start;
}
.first-page .left .chart-sm{ width: 220px; height:auto; display:block; }
.first-page .right .desc-2col{
  column-count: 2; column-gap: 18px;
}
.first-page .h3{
  font-weight:700; font-size:1.2rem; border-bottom:2px solid #f0f0f0; margin:0 0 8px 0; padding-bottom:2px;
}
/* 印刷最適化：A4縦 */
@media print{
  @page { size: A4; margin: 12mm; }
  header, footer, .stApp [data-testid="stToolbar"], .stApp [data-testid="stDecoration"],
  .stApp [data-testid="stStatusWidget"], .stApp [data-testid="stSidebar"],
  .stApp [data-testid="collapsedControl"]{ display:none !important; }
  .stApp{ padding:0 !important; }
}
</style>
""", unsafe_allow_html=True)

# ===== 1ページ目：レーダーチャート + 各要素の説明（必ず1枚に収める） =====
img_b64_small = make_radar_png_base64(results, size_in=3.6, dpi=160)

first_page_html = f"""
<div class="page first-page">
  <div class="grid1">
    <div class="left">
      <div class="h3">レーダーチャート</div>
      <img class="chart-sm" src="{img_b64_small}" />
    </div>
    <div class="right">
      <div class="h3">各要素の説明</div>
      <div class="desc-2col">
        <p><b>{full_labels['P']}</b>：{descriptions['P']}</p>
        <p><b>{full_labels['E']}</b>：{descriptions['E']}</p>
        <p><b>{full_labels['R']}</b>：{descriptions['R']}</p>
        <p><b>{full_labels['M']}</b>：{descriptions['M']}</p>
        <p><b>{full_labels['A']}</b>：{descriptions['A']}</p>
      </div>
    </div>
  </div>
</div>
"""
st.markdown(first_page_html, unsafe_allow_html=True)

# =========================
# 定義
# =========================
perma_indices = {
    'Positive Emotion':[0,1,2],
    'Engagement':[3,4,5],
    'Relationships':[6,7,8],
    'Meaning':[9,10,11],
    'Accomplishment':[12,13,14],
}
perma_short_keys = ['P','E','R','M','A']
full_labels = {
    'P':'Pー前向きな気持ち（Positive Emotion）',
    'E':'Eー集中して取り組む（Engagement）',
    'R':'Rー人間関係（Relationships）',
    'M':'Mー意味づけ（Meaning）',
    'A':'Aー達成感（Accomplishment）',
}
descriptions = {
    'P':'楽しい気持ちや感謝、安心感など、気分の明るさや心のゆとりが感じられること。',
    'E':'物事に没頭し、時間を忘れて集中している感覚があること。',
    'R':'家族や友人、地域とのつながりを感じ、支え合えていること。',
    'M':'自分の人生に目的や価値を見いだし、「自分にとって大切なこと」に沿って生きていること。',
    'A':'目標に向かって取り組み、できた・やり遂げたという手応えがあること。',
}
tips = {
    'P':['感謝を込めた手紙を書く','毎日その日の「良かったこと」を三つ書く','最近うまくいった出来事を思い出す'],
    'E':['自分の得意なことを行う','自分の強みを書く','呼吸に集中して心を落ち着ける'],
    'R':['日常で小さな親切を行う','周囲の人に喜びを伝える'],
    'M':['自分の価値に合った目標を立てる','困難を振り返る','得られた新しい意味を考える'],
    'A':['小さな習慣を積み重ねる','失敗も学びととらえる','明確な目標を決める'],
}
colors = ['#D81B60','#E65100','#2E7D32','#1E88E5','#6A1B9A']

# =========================
# ユーティリティ
# =========================
def compute_results(selected_row: pd.DataFrame):
    cols = [c for c in selected_row.columns if str(c).startswith("6_")]
    vals = pd.to_numeric(selected_row[cols].values.flatten(), errors='coerce')
    res = {}
    for k, idx in perma_indices.items():
        scores = [vals[i] for i in idx if i < len(vals) and not np.isnan(vals[i])]
        res[k] = float(np.mean(scores)) if scores else 0.0
    return res

def summarize(results):
    avg = float(np.mean(list(results.values())))
    STRONG, GROWTH = 7.0, 5.0
    by_short = {
        'P': results['Positive Emotion'],
        'E': results['Engagement'],
        'R': results['Relationships'],
        'M': results['Meaning'],
        'A': results['Accomplishment'],
    }
    strong = [k for k in perma_short_keys if by_short[k] >= STRONG]
    growth = [k for k in perma_short_keys if by_short[k] < GROWTH]
    middle = [k for k in perma_short_keys if GROWTH <= by_short[k] < STRONG]

    def ja(k): return full_labels[k].split('ー')[-1].split('（')[0]
    def jlist(lst): return lst[0] if len(lst)==1 else "、".join(lst[:-1])+" と "+lst[-1] if lst else ""

    # 基準を冒頭に移動
    lines = [
        "**基準：7点以上＝強み、5〜7点＝一定の満足、5点未満＝改善余地**",
        f"**総合評価**：平均 {avg:.1f} 点。"
    ]
    if strong: lines.append(f"あなたは **{jlist([ja(s) for s in strong])}** が強みです。")
    if middle: lines.append(f"**{jlist([ja(m) for m in middle])}** は一定の満足が見られます。")
    if growth: lines.append(f"**{jlist([ja(g) for g in growth])}** は改善の余地があります。")
    return {"summary_text":"\n\n".join(lines), "growth": growth}

def plot_radar(results):
    labels = list(results.keys())
    values = list(results.values())
    values += values[:1]
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    # 🔽 サイズを小さめに変更
    fig, ax = plt.subplots(figsize=(5.5, 5.5), subplot_kw=dict(polar=True))
    for i in range(len(labels)):
        ax.plot([angles[i], angles[i+1]], [values[i], values[i+1]], 
                color=colors[i], linewidth=3)
    ax.fill(angles, values, alpha=0.10, color="#888")
    ax.set_thetagrids(np.degrees(angles[:-1]), ['P','E','R','M','A'],
                      fontsize=int(14*FONT_SCALE), fontweight='bold')
    ax.set_ylim(0, 10)
    ax.set_rticks([2,4,6,8,10])
    fig.tight_layout()
    st.pyplot(fig)


# =========================
# ここから2ページ目にする（CSSで改ページ）
# =========================
st.markdown('<div style="page-break-before:always"></div>', unsafe_allow_html=True)


# =========================
# 本体
# =========================
st.markdown('<div class="main-wrap">', unsafe_allow_html=True)
st.title("PERMAプロファイル")
st.caption("※ 本ツールはスクリーニングであり医療的診断ではありません。")

uploaded = st.file_uploader("Excelファイル（.xlsx）をアップロードしてください（左端の列にID、6_1〜の列にスコア）", type="xlsx")

if uploaded:
    try:
        df = pd.read_excel(uploaded)
        id_list = df.iloc[:, 0].dropna().astype(str).tolist()
        sid = st.selectbox("IDを選んでください", options=id_list, index=0)
        selected_row = df[df.iloc[:, 0].astype(str) == sid]
        if selected_row.empty:
            st.warning("選択されたIDに該当する行がありません。")
        else:
            results = compute_results(selected_row)
            summary = summarize(results)

            # ---------- ページ1：レーダー + 各要素 ----------
            st.markdown('<div class="page-1">', unsafe_allow_html=True)

            # レーダー
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><h3>レーダーチャート</h3></div>', unsafe_allow_html=True)
            plot_radar(results)
            st.markdown('</div>', unsafe_allow_html=True)

            # 各要素
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><h3>各要素の説明</h3></div>', unsafe_allow_html=True)
            # 2列にして圧縮（印刷時 720px 幅想定で改行を抑える）
            colA, colB = st.columns(2)
            items = list(perma_short_keys)
            left_items, right_items = items[:3], items[3:]
            with colA:
                for k in left_items:
                    st.markdown(f"**{full_labels[k]}**：{descriptions[k]}")
            with colB:
                for k in right_items:
                    st.markdown(f"**{full_labels[k]}**：{descriptions[k]}")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)  # /page-1
            st.markdown('<div class="force-break"></div>', unsafe_allow_html=True)  # 改ページ強制

            # ---------- ページ2：まとめ + おすすめ + メモ ----------
            st.markdown('<div class="page-2">', unsafe_allow_html=True)

            # 結果のまとめ（←基準は冒頭に移動済み）
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><h3>結果のまとめコメント</h3></div>', unsafe_allow_html=True)
            st.markdown(summary["summary_text"])
            st.markdown('</div>', unsafe_allow_html=True)

            # あなたに合わせたおすすめ行動（改善余地のみ表示、なければ各2件）
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><h3>あなたに合わせたおすすめ行動</h3></div>', unsafe_allow_html=True)
            growth_keys = summary["growth"]
            if growth_keys:
                for k in growth_keys:
                    st.markdown(f"**{full_labels[k]}**")
                    # 長文化を避けるため最大2件に圧縮
                    for t in tips[k][:2]:
                        st.markdown(f"- {t}")
            else:
                st.markdown("大きな偏りは見られません。維持と予防のために、以下の活動も役立ちます。")
                for k in perma_short_keys:
                    st.markdown(f"**{full_labels[k]}**")
                    for t in tips[k][:1]:
                        st.markdown(f"- {t}")
            st.markdown('</div>', unsafe_allow_html=True)

            # 大切なこと（短文化）
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><h3>この結果を受け取るうえで大切なこと</h3></div>', unsafe_allow_html=True)
            st.markdown(
                "- 結果は“良い/悪い”ではなく **選好や環境** の反映です。\n"
                "- 新しい活動は **小さな一歩** から。（例：1日5分の散歩）\n"
                "- 本ツールは **スクリーニング** であり診断ではありません。つらさが続く場合は専門職へご相談ください。"
            )
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)  # /page-2

    except Exception as e:
        st.error(f"データ読み込み時にエラーが発生しました：{e}")
else:
    st.info("まずはExcel（.xlsx）をアップロードしてください。左端の列がID、6_1〜の列にスコアが並ぶ形式を想定しています。")

st.markdown('</div>', unsafe_allow_html=True)
