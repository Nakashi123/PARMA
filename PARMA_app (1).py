# -*- coding: utf-8 -*-
import io, base64
import streamlit as st
import pandas as pd, numpy as np
import matplotlib.pyplot as plt

# =========================
# 基本設定（高齢期にやさしい視認性）
# =========================
st.set_page_config(page_title="PERMAプロファイル", layout="centered")

BASE_FONT_PX = 20              # 大きめの基本文字
H1_REM, H2_REM, H3_REM = 2.4, 2.0, 1.7
LINE_HEIGHT = 1.95             # 行間を広く
CARD_RADIUS_PX, CARD_PAD_REM = 14, 1.0
FONT_SCALE = 1.2               # Matplotlibの文字も拡大

plt.rcParams.update({
    "font.size": int(13 * FONT_SCALE),
    "axes.titlesize": int(17 * FONT_SCALE),
    "axes.labelsize": int(15 * FONT_SCALE),
    "xtick.labelsize": int(13 * FONT_SCALE),
    "ytick.labelsize": int(13 * FONT_SCALE),
    "legend.fontsize": int(13 * FONT_SCALE),
    "font.sans-serif": [
        "BIZ UDPGothic", "Yu Gothic UI","Hiragino Kaku Gothic ProN","Meiryo",
        "Noto Sans JP","Helvetica","Arial","DejaVu Sans"
    ],
    "axes.unicode_minus": False,
})

# =========================
# CSS（高コントラスト＋印刷最適化）
# =========================
st.markdown(f"""
<style>
html, body, [class*="css"] {{
  font-size:{BASE_FONT_PX}px !important;
  line-height:{LINE_HEIGHT} !important;
  font-family:"BIZ UDPGothic","Yu Gothic UI","Hiragino Kaku Gothic ProN","Meiryo","Noto Sans JP",sans-serif !important;
  color:#0b0b0b !important; background:#fafafa !important;
}}
h1 {{ font-size:{H1_REM}rem !important; font-weight:800; margin:0 0 .4rem 0; letter-spacing:.02em; }}
h2 {{ font-size:{H2_REM}rem !重要; font-weight:750; margin:.3rem 0 .5rem 0; }}
h3 {{ font-size:{H3_REM}rem !important; font-weight:700; margin:.2rem 0 .55rem 0; }}

.main-wrap {{ max-width: 900px; margin: 0 auto; }}

.section-card {{
  background:#fff; border:2px solid #e3e3e3; border-radius:{CARD_RADIUS_PX}px;
  padding:{CARD_PAD_REM}rem {CARD_PAD_REM+0.3}rem; margin:.75rem 0 1rem 0;
  box-shadow:0 2px 8px rgba(0,0,0,.06);
  page-break-inside: avoid; break-inside: avoid;
}}
.section-title {{ border-bottom:3px solid #f2f2f2; padding-bottom:.35rem; margin-bottom:.55rem; }}
.badge {{ display:inline-block; padding:.06rem .5rem; border-radius:999px; font-size:.86rem; font-weight:700; background:#efefef; }}

.page-1, .page-2 {{ page-break-inside: avoid; break-inside: avoid; }}
.force-break {{ break-after: page; page-break-after: always; height: 0 !important; margin: 0 !important; padding: 0 !important; }}

@media print {{
  @page {{ size: A4; margin: 12mm; }}
  html, body {{ zoom: 1; }}
  body, [class*="css"] {{ font-size: 17px !important; line-height: 1.6 !important; }}
  h1 {{ font-size: 2.0rem !important; }}
  h2 {{ font-size: 1.7rem !important; }}
  h3 {{ font-size: 1.45rem !important; }}
  .main-wrap {{ max-width: 760px; }}
  .section-card {{ margin: .55rem 0 .75rem 0; padding: .75rem .9rem; }}
  .stApp [data-testid="stToolbar"], .stApp [data-testid="stDecoration"],
  .stApp [data-testid="stStatusWidget"], .stApp [data-testid="stSidebar"],
  .stApp [data-testid="collapsedControl"] {{ display: none !important; }}
  .stApp {{ padding: 0 !important; }}
}}
</style>
""", unsafe_allow_html=True)

# =========================
# PERMA定義（あなたの質問紙の順に完全対応）
# =========================
# 6_1〜6_23 が以下の順で入っている前提：
# M1(6_1), A1(6_2), E1(6_3), H1(6_4), P1(6_5), R1(6_6), N1(6_7), A2(6_8), M2(6_9), P2(6_10), E2(6_11), Lon(6_12),
# H2(6_13), N2(6_14), R2(6_15), A3(6_16), M3(6_17), H3(6_18), R3(6_19), N3(6_20), E3(6_21), P3/Content(6_22), Hap(6_23)

# 0始まりインデックスに変換
perma_indices = {
    'Positive Emotion': [4, 9, 21],   # 6_5, 6_10, 6_22
    'Engagement':       [2, 10, 20],  # 6_3, 6_11, 6_21
    'Relationships':    [5, 14, 18],  # 6_6, 6_15, 6_19
    'Meaning':          [0, 8, 16],   # 6_1, 6_9, 6_17
    'Accomplishment':   [1, 7, 15],   # 6_2, 6_8, 6_16
}

# 補助指標（参考）
extra_indices = {
    'Negative Emotion': [6, 13, 19],  # 6_7, 6_14, 6_20
    'Health':           [3, 12, 17],  # 6_4, 6_13, 6_18
    'Loneliness':       [11],         # 6_12（単一項目）
    'Happiness':        [22],         # 6_23（全体幸福）
}

perma_short_keys = ['P','E','R','M','A']
full_labels = {
    'P':'Pー前向きな気持ち（Positive Emotion）',
    'E':'Eー集中して取り組むこと（Engagement）',
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

# アクセシブル配色（色弱配慮・高コントラスト）
COLORS = {
    'P': '#1f77b4',   # 青
    'E': '#2ca02c',   # 緑
    'R': '#ff7f0e',   # オレンジ
    'M': '#9467bd',   # 紫
    'A': '#d62728',   # 赤
    'FILL': '#777777' # レーダー塗り
}

# =========================
# ユーティリティ
# =========================
def compute_domain_avg(vals, idx_list):
    scores = [vals[i] for i in idx_list if i < len(vals) and not np.isnan(vals[i])]
    return float(np.mean(scores)) if scores else np.nan

def compute_results(selected_row: pd.DataFrame):
    cols = [c for c in selected_row.columns if str(c).startswith("6_")]
    vals = pd.to_numeric(selected_row[cols].values.flatten(), errors='coerce')

    # PERMA各領域
    perma_scores = {k: compute_domain_avg(vals, idx) for k, idx in perma_indices.items()}

    # 補助指標
    extras = {k: compute_domain_avg(vals, idx) for k, idx in extra_indices.items()}

    # Overall wellbeing（主要15項目＋Happinessの平均）
    main15_idx = sorted(sum(perma_indices.values(), []))  # PERMA 15項目
    if not np.isnan(extras.get('Happiness', np.nan)):
        overall_items = main15_idx + extra_indices['Happiness']
    else:
        overall_items = main15_idx
    overall = compute_domain_avg(vals, overall_items)

    return perma_scores, extras, overall

def summarize(perma_scores):
    avg = float(np.nanmean(list(perma_scores.values())))
    STRONG, GROWTH = 7.0, 5.0
    by_short = {
        'P': perma_scores['Positive Emotion'],
        'E': perma_scores['Engagement'],
        'R': perma_scores['Relationships'],
        'M': perma_scores['Meaning'],
        'A': perma_scores['Accomplishment'],
    }
    strong = [k for k in ['P','E','R','M','A'] if not np.isnan(by_short[k]) and by_short[k] >= STRONG]
    growth = [k for k in ['P','E','R','M','A'] if not np.isnan(by_short[k]) and by_short[k] < GROWTH]
    middle = [k for k in ['P','E','R','M','A'] if not np.isnan(by_short[k]) and GROWTH <= by_short[k] < STRONG]

    def ja(k): return {'P':'前向きな気持ち','E':'集中して取り組むこと','R':'人間関係','M':'意味づけ','A':'達成感'}[k]
    def jlist(lst):
        return lst[0] if len(lst)==1 else "、".join(lst[:-1])+" と "+lst[-1] if lst else ""

    lines = [
        "**基準：7点以上＝強み、5〜7点＝一定の満足、5点未満＝改善余地**",
        f"**総合評価（PERMA平均）**：{avg:.1f} 点。"
    ]
    if strong: lines.append(f"あなたは **{jlist([ja(s) for s in strong])}** が強みです。")
    if middle: lines.append(f"**{jlist([ja(m) for m in middle])}** は一定の満足が見られます。")
    if growth: lines.append(f"**{jlist([ja(g) for g in growth])}** は改善の余地があります。")

    return {"summary_text": "\n\n".join(lines), "growth": growth}

def plot_radar(perma_scores):
    labels = list(perma_scores.keys())
    values = list(perma_scores.values())
    values += values[:1]
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(3.2, 3.2), subplot_kw=dict(polar=True), dpi=220)
    ring_colors = [COLORS['P'], COLORS['E'], COLORS['R'], COLORS['M'], COLORS['A']]

    for i in range(len(labels)):
        ax.plot([angles[i], angles[i+1]], [values[i], values[i+1]], color=ring_colors[i], linewidth=2.4)
    ax.fill(angles, values, alpha=0.12, color=COLORS['FILL'])

    ax.set_thetagrids(np.degrees(angles[:-1]), ['P','E','R','M','A'],
                      fontsize=max(11, int(12*FONT_SCALE)), fontweight='bold')
    ax.set_ylim(0, 10)
    ax.set_rticks([2, 6, 10])
    ax.tick_params(axis='y', labelsize=max(10, int(11*FONT_SCALE)))
    ax.grid(alpha=0.32, linewidth=1.0)
    fig.tight_layout(pad=0.25)
    st.pyplot(fig, use_container_width=False)

# =========================
# 補助指標カード（中立表示：数値＋バーのみ）
# =========================
EXTRA_LABELS = {
    'Negative Emotion': 'こころのつらさ（不安・怒り・悲しみ）',
    'Health': 'からだの調子',
    'Loneliness': 'ひとりぼっち感',
    'Happiness': 'しあわせ感（全体）',
}

def render_extra_cards(extras: dict, overall: float, show_extras: bool = True):
    if not show_extras:
        return
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title"><h3>補助指標（スコア表示）</h3></div>', unsafe_allow_html=True)
    # 括弧書きの注釈
    st.markdown(
        '<div style="font-size:0.95rem; color:#555; margin-top:-.25rem;">'
        '(0〜10の自己評価スコアを表示します)'
        '</div>',
        unsafe_allow_html=True
    )

    cols = st.columns(2)
    order = ['Health', 'Happiness', 'Negative Emotion', 'Loneliness']
    for i, key in enumerate(order):
        with cols[i % 2]:
            val = extras.get(key, np.nan)
            label = EXTRA_LABELS[key]
            # バー（■□）を中立色で表示
            if np.isnan(val):
                score_txt = '—'
                bar = '□' * 10
            else:
                score_txt = f'{val:.1f}'
                filled = int(round(val))
                bar = '■' * filled + '□' * (10 - filled if filled <= 10 else 0)

            st.markdown(
                f"<div style='border:1px solid #eee;border-radius:12px;padding:.7rem .8rem;margin:.35rem 0;'>"
                f"<div style='font-weight:800'>{label}</div>"
                f"<div style='font-size:1.12rem;margin:.25rem 0;'>スコア："
                f"<span style='font-weight:800'>{score_txt}</span> / 10</div>"
                f"<div style='font-family:monospace;letter-spacing:.05em;color:#333'>{bar}</div>"
                f"</div>", unsafe_allow_html=True
            )

    if not np.isnan(overall):
        st.markdown("<hr style='opacity:.2'>", unsafe_allow_html=True)
        st.markdown(f"**しあわせ感（総合）**：**{overall:.1f} / 10**（PERMA15＋全体幸福）")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# 本体
# =========================
st.markdown('<div class="main-wrap">', unsafe_allow_html=True)
st.title("PERMAプロファイル")
st.caption("※ 本ツールはスクリーニングであり医療的診断ではありません。大きめの文字と高コントラストで見やすくしています。")

uploaded = st.file_uploader("Excelファイル（.xlsx）をアップロードしてください（左端の列にID、6_1〜6_23の順でスコア）", type="xlsx")
show_extras = st.checkbox("補助指標（健康・しあわせ・こころのつらさ・ひとりぼっち感）を表示する", value=True)

if uploaded:
    try:
        df = pd.read_excel(uploaded)
        id_list = df.iloc[:, 0].dropna().astype(str).tolist()
        sid = st.selectbox("IDを選んでください", options=id_list, index=0)
        selected_row = df[df.iloc[:, 0].astype(str) == sid]

        if selected_row.empty:
            st.warning("選択されたIDに該当する行がありません。")
        else:
            perma_scores, extras, overall = compute_results(selected_row)
            summary = summarize(perma_scores)

            # ---------- ページ切り替え ----------
            st.markdown('<div class="force-break"></div>', unsafe_allow_html=True)

            # ---------- ページ1 ----------
            st.markdown('<div class="page-1">', unsafe_allow_html=True)

            # レーダーチャート + 説明
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><h3>レーダーチャート</h3></div>', unsafe_allow_html=True)
            col1, col2 = st.columns([2, 3])
            with col1:
                plot_radar(perma_scores)
            with col2:
                st.markdown(
                    "この図は、しあわせを支える5つの要素（PERMA）の自己評価です。  \n"
                    "点数が高いほどその要素が生活のなかで満たされていることを示し、  \n"
                    "どこが強みで、どこに伸びしろがあるかが一目でわかります。"
                )
                # 括弧書きの注釈（ツールチップを使わない）
                st.markdown(
                    '<div style="font-size:0.95rem; color:#555; margin-top:.2rem;">'
                    '(0〜10で評価。平均7以上は強みの目安です)'
                    '</div>',
                    unsafe_allow_html=True
                )
            st.markdown('</div>', unsafe_allow_html=True)

            # 各要素の説明
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><h3>各要素の説明</h3></div>', unsafe_allow_html=True)
            colA, colB = st.columns(2)
            with colA:
                for k in ['P', 'E', 'R']:
                    st.markdown(f"<span class='badge'>{k}</span> **{full_labels[k]}**：{descriptions[k]}", unsafe_allow_html=True)
            with colB:
                for k in ['M', 'A']:
                    st.markdown(f"<span class='badge'>{k}</span> **{full_labels[k]}**：{descriptions[k]}", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)  # /page-1

            # ---------- ページ2 ----------
            st.markdown('<div class="force-break"></div>', unsafe_allow_html=True)
            st.markdown('<div class="page-2">', unsafe_allow_html=True)

            # 結果まとめ
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><h3>結果のまとめ</h3></div>', unsafe_allow_html=True)
            st.markdown(summary["summary_text"])

            # 追加の数値（任意表示）
            with st.expander("スコア一覧（0〜10）"):
                perma_df = pd.DataFrame({k:[round(v,1) if not np.isnan(v) else None] for k,v in perma_scores.items()})
                st.dataframe(perma_df, use_container_width=True)
                if show_extras:
                    extras_df = pd.DataFrame({k:[round(v,1) if not np.isnan(v) else None] for k,v in extras.items()})
                    st.dataframe(extras_df, use_container_width=True)
                if not np.isnan(overall):
                    st.markdown(f"**Overall wellbeing**（主要15＋全体幸福の平均）：**{overall:.1f}** 点")
            st.markdown('</div>', unsafe_allow_html=True)
# =========================
# PERMAスコア（シンプル表示）
# =========================
st.subheader("PERMAスコア")
st.write("（0〜10で評価。平均7以上は強みの目安です）")

st.write(f"前向きな気持ち（Positive Emotion）: {perma_scores['Positive Emotion']:.2f}")
st.write(f"熱中（Engagement）: {perma_scores['Engagement']:.2f}")
st.write(f"人間関係（Relationships）: {perma_scores['Relationships']:.2f}")
st.write(f"意味や目的（Meaning）: {perma_scores['Meaning']:.2f}")
st.write(f"達成（Accomplishment）: {perma_scores['Accomplishment']:.2f}")

# =========================
# 補助指標（シンプル表示）
# =========================
st.subheader("補助指標")
st.write("（健康・しあわせは高いほど良い ／ こころのつらさ・ひとりぼっち感は低いほど良い）")

st.write(f"健康: {extras['Health']:.2f}")
st.write(f"しあわせ: {extras['Happiness']:.2f}")
st.write(f"こころのつらさ: {extras['Negative Emotion']:.2f}")
st.write(f"ひとりぼっち感: {extras['Loneliness']:.2f}")

            # 補助指標（中立表示）
            render_extra_cards(extras, overall, show_extras)

            # あなたにおすすめな活動（2列レイアウト）
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><h3>あなたにおすすめな活動</h3></div>', unsafe_allow_html=True)
            if summary["growth"]:
                col1, col2 = st.columns(2)
                cols = [col1, col2]
                for i, k in enumerate(summary["growth"]):
                    with cols[i % 2]:
                        st.markdown(f"**{full_labels[k]}**")
                        for t in tips[k][:2]:
                            st.markdown(f"- {t}")
            else:
                st.markdown("大きな偏りは見られません。維持と予防のために、以下の活動も役立ちます。")
                col1, col2 = st.columns(2)
                cols = [col1, col2]
                for i, k in enumerate(perma_short_keys):
                    with cols[i % 2]:
                        st.markdown(f"**{full_labels[k]}**")
                        for t in tips[k][:1]:
                            st.markdown(f"- {t}")
            st.markdown('</div>', unsafe_allow_html=True)

            # この結果を受け取るうえで大切なこと
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
    st.info("まずはExcel（.xlsx）をアップロードしてください。左端の列がID、6_1〜6_23の順にスコアが並ぶ形式を想定しています。")

st.markdown('</div>', unsafe_allow_html=True)
