# -*- coding: utf-8 -*-
import io, base64
import streamlit as st
import pandas as pd, numpy as np
import matplotlib.pyplot as plt

# =========================
# 基本設定
# =========================
st.set_page_config(page_title="PERMAプロファイル", layout="centered")

BASE_FONT_PX = 19
H1_REM, H2_REM, H3_REM = 2.2, 1.9, 1.6
LINE_HEIGHT = 1.8
CARD_RADIUS_PX, CARD_PAD_REM = 12, 0.9
FONT_SCALE = 1.1

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
  body, [class*="css"] {{ font-size: 16px !important; line-height: 1.55 !important; }}
  h1 {{ font-size: 1.9rem !important; }}
  h2 {{ font-size: 1.6rem !important; }}
  h3 {{ font-size: 1.3rem !important; }}
  .main-wrap {{ max-width: 720px; }}
  .section-card {{ margin: .45rem 0 .6rem 0; padding: .65rem .75rem; }}
  .stApp [data-testid="stToolbar"],
  .stApp [data-testid="stDecoration"],
  .stApp [data-testid="stStatusWidget"],
  .stApp [data-testid="stSidebar"],
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

colors = ['#D81B60','#E65100','#2E7D32','#1E88E5','#6A1B9A']

# =========================
# ユーティリティ
# =========================
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

    lines = [
        "**基準：7点以上＝強み、5〜7点＝一定の満足、5点未満＝改善余地**",
        f"**総合評価**：平均 {avg:.1f} 点。"
    ]
    if strong: lines.append(f"あなたは **{jlist([ja(s) for s in strong])}** が強みです。")
    if middle: lines.append(f"**{jlist([ja(m) for m in middle])}** は一定の満足が見られます。")
    if growth: lines.append(f"**{jlist([ja(g) for g in growth])}** は改善の余地があります。")
    return {"summary_text":"\n\n".join(lines), "growth": growth}


# --- 高齢期向けの見やすい表示設定 ---
EXTRA_LABELS = {
    'Negative Emotion': 'こころのつらさ（不安・怒り・悲しみ）',
    'Health': 'からだの調子',
    'Loneliness': 'ひとりぼっち感',
    'Happiness': 'しあわせ感（全体）',
}

EXTRA_TIPS = {
    'Negative Emotion': '深呼吸や短い休憩、信頼できる人とのおしゃべりが助けになります。つらさが続くときは専門家へ相談を。',
    'Health': '無理なく体を動かし、睡眠と食事を整えましょう。気になる症状は早めに受診を。',
    'Loneliness': 'あいさつ・電話・短い雑談など、小さなつながりから。地域の「通いの場」もおすすめです。',
    'Happiness': '一日の「よかったこと」を一つ見つけてみましょう。',
}

# しきい値（目安）。Health/Happinessは高いほど良い、Negative Emotion/Lonelinessは低いほど良い。
THRESHOLDS = {
    'good': 7.0,      # 良好の目安
    'watch': 5.0,     # 注意ライン
}

def rate_extra(name: str, value: float):
    """指標の評価（◎/△/！）と簡単コメントを返す。"""
    if np.isnan(value):
        return '―', '未回答', 'neutral'

    high_is_good = name in ['Health', 'Happiness']
    if high_is_good:
        if value >= THRESHOLDS['good']:
            return '◎', '良好です', 'good'
        elif value >= THRESHOLDS['watch']:
            return '△', 'まずまず。様子見', 'watch'
        else:
            return '！', '要注意。無理なく整えましょう', 'alert'
    else:  # Negative Emotion, Loneliness（低いほど良い）
        if value < THRESHOLDS['watch']:
            return '◎', '落ち着いています', 'good'
        elif value < THRESHOLDS['good']:
            return '△', '少し気がかり。休息を', 'watch'
        else:
            return '！', '要注意。支えを得ましょう', 'alert'


def render_extra_cards(extras: dict, overall: float, show_extras: bool = True):
    if not show_extras:
        return
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title"><h3>補助指標（わかりやすい表示）</h3></div>', unsafe_allow_html=True)
    st.caption('※ 数字は0〜10。健康・しあわせは高いほど良い／ こころのつらさ・ひとりぼっち感は低いほど良い。')

    cols = st.columns(2)
    order = ['Health', 'Happiness', 'Negative Emotion', 'Loneliness']
    for i, key in enumerate(order):
        with cols[i % 2]:
            val = extras.get(key, np.nan)
            mark, note, status = rate_extra(key, val)
            label = EXTRA_LABELS[key]
            # バー表示（簡易）
            bar_len = 10 if np.isnan(val) else int(round(val))
            bar = '■' * bar_len + '□' * (10 - bar_len if bar_len <= 10 else 0)
            color = {'good':'#2E7D32', 'watch':'#E65100', 'alert':'#D81B60', 'neutral':'#666'}.get(status, '#666')
            st.markdown(f"<div style='border:1px solid #eee;border-radius:10px;padding:.6rem .7rem;margin:.3rem 0;'>"
                        f"<div style='font-weight:700'>{label}</div>"
                        f"<div style='font-size:1.1rem;margin:.2rem 0;'>スコア：<span style='font-weight:700'>{'' if np.isnan(val) else f'{val:.1f}'}</span> / 10　"
                        f"<span style='color:{color};font-weight:800'>{mark}</span> <span style='color:{color}'>{note}</span></div>"
                        f"<div style='font-family:monospace'>{bar}</div>"
                        f"<div style='color:#555;font-size:.95rem;margin-top:.2rem'>{EXTRA_TIPS[key]}</div>"
                        f"</div>", unsafe_allow_html=True)

    if not np.isnan(overall):
        st.markdown("<hr style='opacity:.2'>", unsafe_allow_html=True)
        st.markdown(f"**しあわせ感（総合）**：**{overall:.1f} / 10**（PERMA15＋全体幸福）")
    st.markdown('</div>', unsafe_allow_html=True)


# =========================
# 本体
# =========================
st.markdown('<div class="main-wrap">', unsafe_allow_html=True)
st.title("PERMAプロファイル")
st.caption("※ 本ツールはスクリーニングであり医療的診断ではありません。")

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
            st.markdown('</div>', unsafe_allow_html=True)

            # 各要素の説明
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><h3>各要素の説明</h3></div>', unsafe_allow_html=True)
            colA, colB = st.columns(2)
            with colA:
                for k in ['P', 'E', 'R']:
                    st.markdown(f"**{full_labels[k]}**：{descriptions[k]}")
            with colB:
                for k in ['M', 'A']:
                    st.markdown(f"**{full_labels[k]}**：{descriptions[k]}")
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

            # 補助指標（見やすい表示）
            render_extra_cards(extras, overall, show_extras)

            # おすすめ活動
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><h3>あなたにおすすめな活動</h3></div>', unsafe_allow_html=True)
            if summary["growth"]:
                for k in summary["growth"]:
                    st.markdown(f"**{full_labels[k]}**")
                    for t in tips[k][:2]:
                        st.markdown(f"- {t}")
            else:
                st.markdown("大きな偏りは見られません。維持と予防のために、以下の活動も役立ちます。")
                for k in perma_short_keys:
                    st.markdown(f"**{full_labels[k]}**")
                    for t in tips[k][:1]:
                        st.markdown(f"- {t}")
            st.markdown('</div>', unsafe_allow_html=True)

            # 大切なこと
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
