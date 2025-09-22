# -*- coding: utf-8 -*-
import os
import io
import base64
import datetime as _dt

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from textwrap import shorten
from string import Template

# PDF生成用
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont




# =========================
# 基本設定
# =========================
st.set_page_config(page_title="PERMAプロファイル", layout="centered")

# アクセシビリティ（大きめ文字＆行間）
BASE_FONT_PX   = 20
H1_REM, H2_REM, H3_REM = 2.2, 1.8, 1.5
LINE_HEIGHT    = 1.8
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

st.markdown(f"""
<style>
html, body, [class*="css"] {{
  font-size: {BASE_FONT_PX}px !important;
  line-height: {LINE_HEIGHT} !important;
  font-family: "Yu Gothic UI","Hiragino Kaku Gothic ProN","Meiryo",
               "Noto Sans JP","Noto Sans CJK JP","Helvetica","Arial",sans-serif !important;
  color: #111 !important;
}}
h1 {{ font-size: {H1_REM}rem !important; font-weight: 800; }}
h2 {{ font-size: {H2_REM}rem !important; font-weight: 700; }}
h3 {{ font-size: {H3_REM}rem !重要; font-weight: 700; }}
.section-card {{
  background:#fff; border:1px solid #e6e6e6; border-radius:{CARD_RADIUS_PX}px;
  padding:{CARD_PAD_REM}rem {CARD_PAD_REM+0.3}rem; margin:0.75rem 0 1rem 0;
  box-shadow:0 2px 8px rgba(0,0,0,.06);
}}
.section-title {{ border-bottom:2px solid #f0f0f0; padding-bottom:.25rem; margin-bottom:.6rem; }}
.stSelectbox label, .stFileUploader label, .stRadio label, .stCheckbox label {{ font-size:{WIDGET_REM}rem !important; }}
div[data-baseweb="select"] * {{ font-size:{WIDGET_REM}rem !important; }}
input, textarea {{ font-size:{WIDGET_REM}rem !important; }}
</style>
""", unsafe_allow_html=True)

# =========================
# 定義
# =========================
perma_indices = {
    # 6_1〜6_23 から各3項目想定（不足時は自動で除外）
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
    if not items:
        return ""
    return items[0] if len(items) == 1 else "、".join(items[:-1]) + " と " + items[-1]

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
    std = float(np.std(list(results.values())))

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

    balance = ""  # 予備（文面そのまま）

    strong_labels = [ja_only(full_labels[s]) for s in strong]
    growth_labels = [ja_only(full_labels[s]) for s in growth]
    middle_labels = [ja_only(full_labels[s]) for s in middle]

    lines = [f"**総合評価**：平均 {avg:.1f} 点。{balance}"]
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

    return {
        "avg": avg,
        "std": std,
        "by_short": by_short,
        "strong": strong,
        "growth": growth,
        "middle": middle,
        "summary_text": "\n\n".join(lines)
    }

def plot_radar(results):
    labels = list(results.keys())
    values = list(results.values())
    values += values[:1]  # close loop

    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(7.8, 7.8), subplot_kw=dict(polar=True))
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

# =========================
# ページ状態
# =========================
if "page" not in st.session_state:
    st.session_state.page = 1
if "df" not in st.session_state:
    st.session_state.df = None
if "selected_id" not in st.session_state:
    st.session_state.selected_id = None
if "results" not in st.session_state:
    st.session_state.results = None
if "summary" not in st.session_state:
    st.session_state.summary = None
if "last_sid" not in st.session_state:
    st.session_state.last_sid = None

# =========================
# ページ1：データ入力（アップロード & ID）
# =========================
if st.session_state.page == 1:
    st.header("データ入力（スタッフ用）")
    uploaded = st.file_uploader("Excelファイル（.xlsx）をアップロードしてください", type="xlsx")
    if uploaded:
        try:
            st.session_state.df = pd.read_excel(uploaded)
            st.success("データ読み込み成功！")
            id_list = st.session_state.df.iloc[:, 0].dropna().astype(str).tolist()
            st.session_state.selected_id = st.selectbox("IDを選んでください", options=id_list)
            if st.button("次へ ▶"):
                if st.session_state.selected_id:
                    st.session_state.page = 2
                    st.rerun()
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

# =========================
# 準備（以降のページで共通使用）
# =========================
if st.session_state.page >= 2:
    df = st.session_state.df
    sid = st.session_state.selected_id
    if df is None or sid is None:
        st.warning("最初のページでデータを読み込み、IDを選択してください。")
        st.stop()
    selected_row = df[df.iloc[:, 0].astype(str) == sid]
    if selected_row.empty:
        st.warning("選択されたIDに該当する行がありません。")
        st.stop()
    if (st.session_state.results is None) or (st.session_state.summary is None) or (st.session_state.last_sid != sid):
        st.session_state.results = compute_results(selected_row)
        st.session_state.summary = summarize(st.session_state.results)
        st.session_state.last_sid = sid

# =========================
# ページ2：タイトル＋レーダーチャート（1ページ）
# =========================
if st.session_state.page == 2:
    st.title("あなたのPERMAプロファイル")
    st.markdown("### PERMA：しあわせを支える5つの要素")
    st.markdown("この図は、あなたが現在の生活でどの種類のしあわせな時間をどの程度過ごせているかを表しています。")

    plot_radar(st.session_state.results)

    cols = st.columns(2)
    with cols[0]:
        if st.button("◀ 戻る"):
            st.session_state.page = 1
            st.rerun()
    with cols[1]:
        if st.button("次へ ▶"):
            st.session_state.page = 3
            st.rerun()

# =========================
# ページ3：各要素の説明（1ページ）
# =========================
elif st.session_state.page == 3:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title"><h3>各要素の説明</h3></div>', unsafe_allow_html=True)
    for k in perma_short_keys:
        st.markdown(f"**{full_labels[k]}**：{descriptions[k]}")
    st.markdown('</div>', unsafe_allow_html=True)

    cols = st.columns(2)
    with cols[0]:
        if st.button("◀ 戻る"):
            st.session_state.page = 2
            st.rerun()
    with cols[1]:
        if st.button("次へ ▶"):
            st.session_state.page = 4
            st.rerun()

# =========================
# ページ4：まとめコメント（1ページ）
# =========================
elif st.session_state.page == 4:
    st.subheader("結果のまとめコメント")
    st.markdown(st.session_state.summary["summary_text"])

    cols = st.columns(2)
    with cols[0]:
        if st.button("◀ 戻る"):
            st.session_state.page = 3
            st.rerun()
    with cols[1]:
        if st.button("次へ ▶"):
            st.session_state.page = 5
            st.rerun()

# =========================
# ページ5：あなたに合わせたおすすめ行動（1ページ）
# =========================
elif st.session_state.page == 5:
    st.subheader("あなたに合わせたおすすめ行動（各領域）")

    growth_keys = st.session_state.summary["growth"]
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

    cols = st.columns(2)
    with cols[0]:
        if st.button("◀ 戻る"):
            st.session_state.page = 4
            st.rerun()
    with cols[1]:
        if st.button("次へ ▶"):
            st.session_state.page = 6
            st.rerun()

# =========================
# ページ6：スタッフ向けメモ（1ページ）
# =========================
elif st.session_state.page == 6:
    with st.expander("この結果を受け取るうえで大切なこと", expanded=True):
        st.markdown("""
- この結果は“良い/悪い”ではなく **選好と環境** の反映として扱い、ご自身の生活史・価値観に照らして解釈します。
- 活動を新たに取り入れるときは、まず日課化しやすい **最小行動** から行いましょう。（例：1日5分の散歩/感謝の手紙3文 など）。
- 本ツールは **スクリーニング** であり医療的診断ではありません。心身の不調が続く場合は専門職へご相談を。
""")

    st.markdown("---")
    st.markdown("作成：認知症介護研究・研修大府センター　わらトレスタッフ")

    cols = st.columns(2)
    with cols[0]:
        if st.button("◀ 戻る"):
            st.session_state.page = 5
            st.rerun()
    with cols[1]:
        if st.button("最初に戻る ⟳"):
            st.session_state.page = 1
            st.session_state.df = None
            st.session_state.selected_id = None
            st.session_state.results = None
            st.session_state.summary = None
            st.rerun()

# ===== ここから：結果の保存／PDF出力 =====

def make_radar_png_base64(results):
    labels = list(results.keys())
    values = list(results.values())
    values += values[:1]
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6.5, 6.5), subplot_kw=dict(polar=True), dpi=180)
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

def make_scores_table_html(results):
    rows = []
    mapping = [('P','Positive Emotion'),('E','Engagement'),('R','Relationships'),('M','Meaning'),('A','Accomplishment')]
    for short, key in mapping:
        label = full_labels[short].split('（')[0]
        val = results.get(key, 0.0)
        rows.append(f"<tr><td>{label}</td><td style='text-align:right;font-weight:700'>{val:.1f}</td></tr>")
    avg = float(np.mean(list(results.values())))
    rows.append("<tr><td style='border-top:2px solid #ddd'>平均</td><td style='text-align:right;font-weight:800;border-top:2px solid #ddd'>%.1f</td></tr>" % avg)
    table = "<table style='width:100%; border-collapse:collapse; font-size:12pt;'><thead><tr><th style='text-align:left'>領域</th><th style='text-align:right'>スコア(0-10)</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>"
    return table

def make_tips_html(summary):
    growth = summary.get('growth', [])
    if not growth:
        return "<p>現在は大きな偏りは見られません。維持のため、日常に小さな取り組みを続けましょう。</p>"
    blocks = []
    for k in perma_short_keys:
        if k in growth and k in tips:
            tip_items = ''.join([f"<li>{shorten(t, width=36, placeholder='…')}</li>" for t in tips[k][:3]])
            blocks.append(f"<div class='tip'><div class='tip-h'>{full_labels[k]}</div><ul>{tip_items}</ul></div>")
    return "".join(blocks)

def _register_jp_font(uploaded_font_bytes: bytes | None = None) -> str:
    """
    日本語表示用フォントをReportLabに登録してフォント名を返す。
    フォントがない場合はHelveticaを返す（※日本語は豆腐になるがPDF生成は動く）。
    """
    try:
        # 1) アップロードフォントがあればそれを使う
        if uploaded_font_bytes:
            tmp_path = os.path.join(os.getcwd(), "jpfont.ttf")
            with open(tmp_path, "wb") as f:
                f.write(uploaded_font_bytes)
            pdfmetrics.registerFont(TTFont("JP", tmp_path))
            return "JP"

        # 2) よくある日本語フォントを探して登録（手元OSに依存）
        candidates = [
            # Windows
            r"C:\Windows\Fonts\meiryo.ttc",
            r"C:\Windows\Fonts\meiryob.ttf",
            r"C:\Windows\Fonts\YuGothM.ttc",
            r"C:\Windows\Fonts\yugothib.ttf",
            # macOS
            "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
            "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
            # Linuxなど
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/ipafont-gothic/ipagp.ttf",
            "/usr/share/fonts/truetype/ipaexfont-gothic/ipaexg.ttf",
        ]
        for p in candidates:
            if os.path.exists(p):
                try:
                    pdfmetrics.registerFont(TTFont("JP", p))
                    return "JP"
                except Exception:
                    continue
    except Exception:
        pass
    return "Helvetica"  # フォールバック（日本語は表示不可）

def build_perma_pdf_bytes(results, summary, tips_dict, sid: str, today: str, radar_png_b64: str,
                          page_mode: str = "1page", uploaded_font_bytes: bytes | None = None) -> bytes:
    """
    A4（縦）1枚 または 2枚でPERMA結果PDFを生成してbytesを返す。
    """
    # フォント準備
    font_name = _register_jp_font(uploaded_font_bytes)

    # キャンバス作成
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    W, H = A4  # pt

    def header_footer():
        c.setFont(font_name, 10)
        c.setFillGray(0.4)
        c.drawRightString(W - 15*mm, 12*mm, "※ 本資料はスクリーニング結果です。医療的診断ではありません。")
        c.setFillGray(0)

    # 共通：タイトル・メタ
    def draw_title_block():
        c.setFont(font_name, 20)
        c.drawString(15*mm, H - 20*mm, "PERMAプロファイル")
        c.setFont(font_name, 11)
        c.setFillGray(0.4)
        c.drawString(15*mm, H - 27*mm, f"ID: {sid} ／ 日付: {today}")
        c.setFillGray(0)

    # レーダー画像
    radar_data = base64.b64decode(radar_png_b64.split(",")[-1])
    radar_img = ImageReader(io.BytesIO(radar_data))

    # 表の準備
    mapping = [('P','Positive Emotion'),('E','Engagement'),('R','Relationships'),('M','Meaning'),('A','Accomplishment')]
    table_rows = []
    for short, key in mapping:
        label = full_labels[short].split('（')[0]
        val = results.get(key, 0.0)
        table_rows.append((label, f"{val:.1f}"))
    avg = float(np.mean(list(results.values())))
    table_rows.append(("平均", f"{avg:.1f}"))

    # まとめ／推奨
    summary_text = summary.get("summary_text", "")
    recommend_blocks = []
    growth = summary.get("growth", [])
    if growth:
        for k in perma_short_keys:
            if k in growth and k in tips_dict:
                items = tips_dict[k][:3]
                recommend_blocks.append((full_labels[k], items))
    else:
        for k in perma_short_keys:
            items = tips_dict[k][:2]
            recommend_blocks.append((full_labels[k], items))

    # 折返し
    def _wrap_text(text, max_chars=36):
        lines = []
        t = text.replace("\r", "")
        while len(t) > max_chars:
            lines.append(t[:max_chars])
            t = t[max_chars:]
        if t:
            lines.append(t)
        return lines

    # ---- 1ページ描画 ----
    def draw_page1():
        draw_title_block()

        # 左：レーダー（だいたい正方で）
        img_size = 85 * mm
        c.drawImage(
            radar_img,
            15*mm, H - 20*mm - img_size - 8*mm,
            width=img_size, height=img_size,
            preserveAspectRatio=True, mask='auto'
        )

        # 右：スコア表＋まとめ
        x0 = 15*mm + img_size + 12*mm
        y0 = H - 28*mm
        c.setFont(font_name, 14)
        c.drawString(x0, y0, "スコア一覧")
        y = y0 - 6*mm
        c.setFont(font_name, 11.5)
        for label, val in table_rows:
            c.drawString(x0, y, f"・{label}")
            c.drawRightString(x0 + 70*mm, y, val)
            y -= 6*mm

        # まとめ
        y -= 6*mm
        c.setFont(font_name, 14)
        c.drawString(x0, y, "まとめ")
        y -= 6*mm
        c.setFont(font_name, 10.8)
        for para in summary_text.split("\n"):
            for line in _wrap_text(para, max_chars=36):
                if y < 30*mm:  # 下余白
                    return y, False  # 次ページに続く
                c.drawString(x0, y, line)
                y -= 5.2*mm
        return y, True

    # ---- 2ページでおすすめ行動 ----
    def draw_page2():
        c.setFont(font_name, 14)
        c.drawString(15*mm, H - 20*mm, "あなたに合わせたおすすめ行動")
        y = H - 27*mm
        c.setFont(font_name, 11.5)
        for title, items in recommend_blocks:
            if y < 30*mm:
                c.showPage()
                header_footer()
                c.setFont(font_name, 11.5)
                y = H - 20*mm
            c.drawString(15*mm, y, f"● {title}")
            y -= 6*mm
            c.setFont(font_name, 10.8)
            for it in items:
                for line in _wrap_text(f"・{it}", max_chars=42):
                    if y < 30*mm:
                        c.showPage()
                        header_footer()
                        c.setFont(font_name, 10.8)
                        y = H - 20*mm
                    c.drawString(19*mm, y, line)
                    y -= 5.2*mm

    # ページ描画
    header_footer()
    y, done = draw_page1()
    if page_mode == "2pages" or not done:
        c.showPage()
        header_footer()
        draw_page2()

    c.save()
    buf.seek(0)
    return buf.getvalue()


# ===== ここから：1枚PDF生成（集約版） =====

def _wrap_text(text: str, max_chars: int) -> list[str]:
    """超シンプルな折返し（日本語も固定幅で切る）。"""
    text = (text or "").replace("\r", "")
    lines = []
    while len(text) > max_chars:
        lines.append(text[:max_chars])
        text = text[max_chars:]
    if text:
        lines.append(text)
    return lines

def build_perma_pdf_onepage(results, summary, tips_dict, sid: str, today: str, radar_png_b64: str,
                             uploaded_font_bytes: bytes | None = None) -> bytes:
    """
    A4縦1枚に集約（高齢者向け：大きい文字・行間広め・日本語フォント埋め込み）
    """
    font_name = _register_jp_font(uploaded_font_bytes)

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    W, H = A4
    L, R, T, B = 15*mm, 15*mm, 18*mm, 15*mm  # 余白

    # ヘッダー（大きめ）
    c.setFont(font_name, 24)
    c.drawString(L, H - T, "PERMAプロファイル")
    c.setFont(font_name, 12)
    c.setFillGray(0.4)
    c.drawString(L, H - T - 8*mm, f"ID: {sid}    日付: {today}")
    c.setFillGray(0)

    # レーダー（やや大きめ）
    radar_data = base64.b64decode(radar_png_b64.split(",")[-1])
    radar_img = ImageReader(io.BytesIO(radar_data))
    chart_size = 95*mm
    chart_x = L
    chart_y = H - T - 8*mm - chart_size - 4*mm
    c.drawImage(radar_img, chart_x, chart_y, width=chart_size, height=chart_size,
                preserveAspectRatio=True, mask='auto')

    # 右側：スコア＋まとめ（大きい文字＆行間）
    right_x = chart_x + chart_size + 12*mm
    right_w = W - R - right_x
    y = H - T - 4*mm

    # スコア一覧
    c.setFont(font_name, 16); c.drawString(right_x, y, "スコア一覧")
    y -= 7*mm
    c.setFont(font_name, 14)
    mapping = [('P','Positive Emotion'),('E','Engagement'),('R','Relationships'),('M','Meaning'),('A','Accomplishment')]
    for short, key in mapping:
        label = full_labels[short].split('（')[0]
        val = results.get(key, 0.0)
        c.drawString(right_x, y, f"・{label}")
        c.drawRightString(right_x + right_w, y, f"{val:.1f}")
        y -= 6.5*mm
    avg = float(np.mean(list(results.values())))
    c.line(right_x, y+2.8*mm, right_x + right_w, y+2.8*mm)
    c.setFont(font_name, 15)
    c.drawString(right_x, y, "平均")
    c.drawRightString(right_x + right_w, y, f"{avg:.1f}")
    y -= 8*mm

    # まとめ（本文14pt・行間広め）
    c.setFont(font_name, 16); c.drawString(right_x, y, "まとめ")
    y -= 7*mm
    c.setFont(font_name, 14)
    summary_text = summary.get("summary_text", "")
    def _wrap(text, n=34):
        text = (text or "").replace("\r", "")
        out = []
        while len(text) > n:
            out.append(text[:n]); text = text[n:]
        if text: out.append(text)
        return out
    for para in summary_text.split("\n"):
        for line in _wrap(para, n=34):
            if y < chart_y:
                break
            c.drawString(right_x, y, line)
            y -= 6.4*mm

    # 下段：おすすめ行動（本文14pt、2カラム）
    lower_y_top = chart_y - 8*mm
    c.setFont(font_name, 16); c.drawString(L, lower_y_top, "あなたに合わせたおすすめ行動")
    y2 = lower_y_top - 7*mm
    growth = summary.get("growth", [])
    blocks = []
    if growth:
        for k in perma_short_keys:
            if k in growth and k in tips_dict:
                blocks.append((full_labels[k], tips_dict[k][:3]))
    else:
        for k in perma_short_keys:
            blocks.append((full_labels[k], tips_dict[k][:2]))

    col_w = (W - L - R - 8*mm) / 2.0
    col_x = [L, L + col_w + 8*mm]
    col_y = [y2, y2]
    c.setFont(font_name, 14)
    def wrap2(t, n=38):
        t = (t or "").replace("\r", "")
        out = []
        while len(t) > n:
            out.append(t[:n]); t = t[n:]
        if t: out.append(t)
        return out

    for title, items in blocks:
        idx = 0 if col_y[0] > col_y[1] else 1
        x = col_x[idx]; yy = col_y[idx]
        c.setFont(font_name, 14)
        c.drawString(x, yy, f"● {title}")
        yy -= 6.2*mm
        c.setFont(font_name, 14)
        for it in items:
            for line in wrap2(f"・{it}", n=36):
                if yy < B + 18*mm:
                    break
                c.drawString(x + 3*mm, yy, line)
                yy -= 6.0*mm
        yy -= 3.0*mm
        col_y[idx] = yy

    # スタッフ注意（1行〜2行・14pt）
    foot_y = min(col_y[0], col_y[1]) - 5*mm
    if foot_y > B + 14*mm:
        c.setFont(font_name, 13)
        note = ("※ この結果は“良い/悪い”ではなく選好と環境の反映として扱います。"
                "新しい活動は最小行動から。これはスクリーニングであり診断ではありません。")
        for line in wrap2(note, n=64):
            if foot_y < B + 12*mm: break
            c.drawString(L, foot_y, line); foot_y -= 6.0*mm

    # フッター
    c.setFont(font_name, 10)
    c.setFillGray(0.45)
    c.drawRightString(W - R, B + 6*mm, "© 認知症介護研究・研修大府センター　わらトレスタッフ / 診断ではありません")
    c.setFillGray(0)

    c.save()
    buf.seek(0)
    return buf.getvalue()
