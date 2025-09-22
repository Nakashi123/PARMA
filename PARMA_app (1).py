# -*- coding: utf-8 -*-
import io
import base64
import datetime as _dt

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# =========================
# 基本設定（レイアウト & フォント）
# =========================
st.set_page_config(page_title="PERMAプロファイル", layout="centered")

# 見やすさ（高齢者向け：大きめ）
BASE_FONT_PX   = 20
H1_REM, H2_REM, H3_REM = 2.4, 2.0, 1.7
LINE_HEIGHT    = 1.9
WIDGET_REM     = 1.2
CARD_RADIUS_PX = 14
CARD_PAD_REM   = 1.0

FONT_SCALE = 1.25
plt.rcParams.update({
    "font.size": int(14 * FONT_SCALE),
    "axes.titlesize": int(18 * FONT_SCALE),
    "axes.labelsize": int(16 * FONT_SCALE),
    "xtick.labelsize": int(14 * FONT_SCALE),
    "ytick.labelsize": int(14 * FONT_SCALE),
    "legend.fontsize": int(14 * FONT_SCALE),
    "font.sans-serif": [
        "Yu Gothic UI","Hiragino Kaku Gothic ProN","Meiryo",
        "Noto Sans JP","Noto Sans CJK JP","Helvetica","Arial","DejaVu Sans"
    ],
    "axes.unicode_minus": False,
})

# 全体CSS（印刷最適化つき）
st.markdown(f"""
<style>
/* 共通文字 */
html, body, [class*="css"] {{
  font-size: {BASE_FONT_PX}px !important;
  line-height: {LINE_HEIGHT} !important;
  font-family: "Yu Gothic UI","Hiragino Kaku Gothic ProN","Meiryo",
               "Noto Sans JP","Noto Sans CJK JP","Helvetica","Arial",sans-serif !important;
  color: #111 !important;
}}
h1 {{ font-size: {H1_REM}rem !important; font-weight: 800; }}
h2 {{ font-size: {H2_REM}rem !important; font-weight: 700; }}
h3 {{ font-size: {H3_REM}rem !important; font-weight: 700; }}
.section-card {{
  background:#fff; border:1px solid #e6e6e6; border-radius:{CARD_RADIUS_PX}px;
  padding:{CARD_PAD_REM}rem {CARD_PAD_REM+0.3}rem; margin:0.75rem 0 1rem 0;
  box-shadow:0 2px 8px rgba(0,0,0,.06);
}}
.section-title {{ border-bottom:2px solid #f0f0f0; padding-bottom:.25rem; margin-bottom:.6rem; }}
.stSelectbox label, .stFileUploader label, .stRadio label, .stCheckbox label {{ font-size:{WIDGET_REM}rem !important; }}
div[data-baseweb="select"] * {{ font-size:{WIDGET_REM}rem !important; }}
input, textarea {{ font-size:{WIDGET_REM}rem !important; }}

/* 用紙幅を意識した中央寄せ */
.main-wrap {{ max-width: 980px; margin: 0 auto; }}

/* 印刷最適化：A4縦、UIを隠す */
@media print {{
  @page {{ size: A4; margin: 12mm; }}
  header, footer,
  .stApp [data-testid="stToolbar"],
  .stApp [data-testid="stDecoration"],
  .stApp [data-testid="stStatusWidget"],
  .stApp [data-testid="stSidebar"],
  .stApp [data-testid="collapsedControl"] {{ display: none !important; }}
  .stApp {{ padding: 0 !important; }}
  .no-print {{ display: none !important; }}
}}
</style>
""", unsafe_allow_html=True)

# =========================
# 定義
# =========================
perma_indices = {
    'Positive Emotion': [0, 1, 2],
    'Engagement'      : [3, 4, 5],
    'Relationships'   : [6, 7, 8],
    'Meaning'         : [9,10,11],
    'Accomplishment'  : [12,13,14],
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
    'P': ['感謝を込めた手紙を書く','毎日、その日にあった「良かったこと」を三つ書く。','最近うまくいった出来事を思い出す'],
    'E': ['自分の得意なことを行う','自分の強みを書く','呼吸に集中して心を落ち着ける'],
    'R': ['日常で小さな親切を行う','周囲の人に大いに喜びを伝える'],
    'M': ['自分の価値や目的に合った目標を立てる','困難を振り返る','得られた新しい機会や意味を考える'],
    'A': ['小さな習慣を積み重ねる','失敗も学びととらえる','はっきりとした目標を決める'],
}
colors = ['#D81B60','#E65100','#2E7D32','#1E88E5','#6A1B9A']  # 高コントラスト

# =========================
# ユーティリティ
# =========================
def ja_only(label: str) -> str:
    base = label.split('（')[0]
    return base.split('ー')[-1].strip()

def jp_list(items):
    if not items: return ""
    return items[0] if len(items)==1 else "、".join(items[:-1]) + " と " + items[-1]

def compute_results(selected_row: pd.DataFrame):
    score_columns = [c for c in selected_row.columns if str(c).startswith("6_")]
    scores_raw = selected_row[score_columns].values.flatten()
    scores = pd.to_numeric(scores_raw, errors='coerce')
    results = {}
    for k, idxs in perma_indices.items():
        vals = [scores[i] for i in idxs if i < len(scores) and not np.isnan(scores[i])]
        results[k] = float(np.mean(vals)) if len(vals) else 0.0
    return results

def summarize(results):
    avg = float(np.mean(list(results.values())))
    STRONG_THR, GROWTH_THR = 7.0, 5.0
    by_short = {
        'P': results['Positive Emotion'],
        'E': results['Engagement'],
        'R': results['Relationships'],
        'M': results['Meaning'],
        'A': results['Accomplishment'],
    }
    strong = [k for k in perma_short_keys if by_short[k] >= STRONG_THR]
    growth = [k for k in perma_short_keys if by_short[k] <  GROWTH_THR]
    middle = [k for k in perma_short_keys if GROWTH_THR <= by_short[k] < STRONG_THR]

    strong_labels = [ja_only(full_labels[s]) for s in strong]
    growth_labels = [ja_only(full_labels[s]) for s in growth]
    middle_labels = [ja_only(full_labels[s]) for s in middle]

    lines = [f"**総合評価**：平均 {avg:.1f} 点。"]
    if strong:
        lines.append(
            "判定は、各要素の平均が **7点以上=強み**、**5〜7点=一定の満足**、**5点未満=改善余地** としています。"
            f"本結果によると、あなたは **{jp_list(strong_labels)}** が比較的しっかり育まれています。"
        )
    if middle:
        lines.append(
            f"**{jp_list(middle_labels)}** は日常の中で一定の満足があり、おおむね安定しています。"
            "無理のない範囲で関連する時間や機会を少し増やすと、全体の底上げにつながります。"
        )
    if growth:
        lines.append(
            f"一方で、**{jp_list(growth_labels)}** はやや弱めかもしれません。"
            "もし「この要素をもっと育てたい」「関わる機会を増やしたい」と感じるなら、"
            "下の活動例を取り入れてみましょう。"
        )
    return {"summary_text": "\n\n".join(lines), "growth": growth}

def plot_radar(results):
    labels = list(results.keys())
    values = list(results.values())
    values += values[:1]
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8.2, 8.2), subplot_kw=dict(polar=True))
    for i in range(len(labels)):
        ax.plot([angles[i], angles[i+1]], [values[i], values[i+1]], color=colors[i], linewidth=4)
    ax.plot(angles, values, color="#444", alpha=0.35, linewidth=2)
    ax.fill(angles, values, alpha=0.10, color="#888")
    ax.set_thetagrids(np.degrees(angles[:-1]), ['P','E','R','M','A'],
                      fontsize=int(18*FONT_SCALE), fontweight='bold')
    ax.set_ylim(0, 10)
    ax.set_rticks([2,4,6,8,10])
    ax.tick_params(axis='y', labelsize=int(14*FONT_SCALE))
    ax.grid(alpha=0.25, linewidth=1.2)
    fig.tight_layout()
    st.pyplot(fig)

def make_radar_png_base64(results):
    labels = list(results.keys())
    values = list(results.values())
    values += values[:1]
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]
    fig, ax = plt.subplots(figsize=(6.8, 6.8), subplot_kw=dict(polar=True), dpi=180)
    for i in range(len(labels)):
        ax.plot([angles[i], angles[i+1]], [values[i], values[i+1]], color=colors[i], linewidth=3)
    ax.plot(angles, values, color="#444", alpha=0.35, linewidth=1.6)
    ax.fill(angles, values, alpha=0.10, color="#888")
    ax.set_thetagrids(np.degrees(angles[:-1]), ['P','E','R','M','A'],
                      fontsize=int(16*FONT_SCALE), fontweight='bold')
    ax.set_ylim(0, 10)
    ax.set_rticks([2,4,6,8,10])
    ax.tick_params(axis='y', labelsize=int(12*FONT_SCALE))
    ax.grid(alpha=0.25, linewidth=1.0)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64}"

# =========================
# 1ページに全表示（アップロード→ID選択→結果）
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
            # 計算
            results = compute_results(selected_row)
            summary = summarize(results)

            # ========== レーダーチャート ==========
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><h3>レーダーチャート</h3></div>', unsafe_allow_html=True)
            plot_radar(results)
            st.markdown('</div>', unsafe_allow_html=True)

            # ========== スコア一覧 ==========
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><h3>スコア一覧</h3></div>', unsafe_allow_html=True)
            mapping = [('P','Positive Emotion'),('E','Engagement'),('R','Relationships'),('M','Meaning'),('A','Accomplishment')]
            cols = st.columns([2,1])
            for short, key in mapping:
                label = full_labels[short].split('（')[0]
                cols[0].markdown(f"・{label}")
                cols[1].markdown(f"<div style='text-align:right;font-weight:700'>{results.get(key,0.0):.1f}</div>", unsafe_allow_html=True)
            avg = float(np.mean(list(results.values())))
            st.markdown("<hr style='margin:8px 0 6px 0;border:none;border-top:2px solid #ddd'>", unsafe_allow_html=True)
            cols = st.columns([2,1])
            cols[0].markdown("平均")
            cols[1].markdown(f"<div style='text-align:right;font-weight:800'>{avg:.1f}</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # ========== 各要素の説明 ==========
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><h3>各要素の説明</h3></div>', unsafe_allow_html=True)
            for k in perma_short_keys:
                st.markdown(f"**{full_labels[k]}**：{descriptions[k]}")
            st.markdown('</div>', unsafe_allow_html=True)

            # ========== まとめコメント ==========
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><h3>結果のまとめコメント</h3></div>', unsafe_allow_html=True)
            st.markdown(summary["summary_text"])
            st.markdown('</div>', unsafe_allow_html=True)

            # ========== あなたに合わせたおすすめ行動 ==========
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><h3>あなたに合わせたおすすめ行動</h3></div>', unsafe_allow_html=True)
            growth_keys = summary["growth"]
            if growth_keys:
                st.markdown("伸ばしたい・機会を増やしたい領域に合わせた例です。")
                for k in perma_short_keys:
                    if k in growth_keys:
                        st.markdown(f"**{full_labels[k]}**")
                        for tip in tips[k][:3]:
                            st.markdown(f"- {tip}")
            else:
                st.markdown("現在は大きな偏りは見られません。維持と予防のために、次の活動も役立ちます。")
                for k in perma_short_keys:
                    st.markdown(f"**{full_labels[k]}**")
                    for tip in tips[k][:2]:
                        st.markdown(f"- {tip}")
            st.markdown('</div>', unsafe_allow_html=True)

            # ========== スタッフ向けメモ ==========
            with st.expander("この結果を受け取るうえで大切なこと", expanded=True):
                st.markdown(
                    "- この結果は“良い/悪い”ではなく **選好と環境** の反映として扱い、ご自身の生活史・価値観に照らして解釈します。\n"
                    "- 活動を新たに取り入れるときは、まず日課化しやすい **最小行動** から行いましょう。（例：1日5分の散歩 / 感謝の手紙3文 など）。\n"
                    "- 本ツールは **スクリーニング** であり医療的診断ではありません。心身の不調が続く場合は専門職へご相談を。"
                )

            # ========== 最後：印刷（ブラウザ印刷→PDF保存可） ==========
            st.markdown("---")
            c1, c2 = st.columns([1,2])
            with c1:
                if st.button("🖨️ このページを印刷（PDF保存も可）", type="primary", help="ブラウザの印刷ダイアログを開きます"):
                    st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

            with c2:
                # 参考：印刷時の見栄えヒントを表示（印刷では非表示）
                st.markdown(
                    "<div class='no-print' style='color:#555'>"
                    "印刷設定：余白は「最小」、ヘッダー/フッターはOFF、背景グラフィックONがきれいです。"
                    "</div>", unsafe_allow_html=True
                )

    except Exception as e:
        st.error(f"データ読み込み時にエラーが発生しました：{e}")
else:
    st.info("まずはExcel（.xlsx）をアップロードしてください。左端の列がID、6_1〜の列にスコアが並ぶ形式を想定しています。")

st.markdown('</div>', unsafe_allow_html=True)
