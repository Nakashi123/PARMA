import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os  


# =========================
# アプリ設定
# =========================
st.set_page_config(page_title="PERMAプロファイル", layout="centered")

# ===== アクセシビリティ設定（必要なら数値を調整） =====
BASE_FONT_PX = 20          # 文章の基準サイズ（px）
H1_REM = 2.1               # 見出しサイズ倍率（rem）
H2_REM = 1.7
H3_REM = 1.4
LINE_HEIGHT = 1.75         # 行間
WIDGET_REM = 1.2           # セレクトボックス等の文字拡大
CARD_PADDING_REM = 1.0     # カード内余白
CARD_RADIUS_PX = 14

# Matplotlibのフォント/サイズ（日本語優先フォントを並べる）
FONT_SCALE = 1.25  # 図中の文字拡大倍率
plt.rcParams.update({
    "font.size": int(14 * FONT_SCALE),
    "axes.titlesize": int(18 * FONT_SCALE),
    "axes.labelsize": int(16 * FONT_SCALE),
    "xtick.labelsize": int(14 * FONT_SCALE),
    "ytick.labelsize": int(14 * FONT_SCALE),
    "legend.fontsize": int(14 * FONT_SCALE),
    "font.sans-serif": [
        "Yu Gothic UI", "Hiragino Kaku Gothic ProN", "Meiryo",
        "Noto Sans CJK JP", "Noto Sans JP", "Helvetica", "Arial", "DejaVu Sans"
    ],
    "axes.unicode_minus": False,
})

# ===== 大きめフォントと余白のCSS（高コントラスト） =====
st.markdown(f"""
<style>
html, body, [class*="css"] {{
  font-size: {BASE_FONT_PX}px !important;
  line-height: {LINE_HEIGHT} !important;
  font-family: "Yu Gothic UI","Hiragino Kaku Gothic ProN","Meiryo",
               "Noto Sans JP","Noto Sans CJK JP","Helvetica","Arial",sans-serif !important;
  color: #111 !important;
}}
h1 {{ font-size: {H1_REM}rem !important; font-weight: 800 !important; letter-spacing: .02em; }}
h2 {{ font-size: {H2_REM}rem !important; font-weight: 700 !important; }}
h3 {{ font-size: {H3_REM}rem !important; font-weight: 700 !important; }}

p, li, label, span, div, th, td {{ font-weight: 500; }}
small {{ font-size: 0.95rem !important; }}

.block-container {{ padding-top: 1.5rem; padding-bottom: 2rem; }}

.stSelectbox label, .stFileUploader label, .stRadio label, .stCheckbox label {{
  font-size: {WIDGET_REM}rem !important;
}}
div[data-baseweb="select"] * {{
  font-size: {WIDGET_REM}rem !important;
}}
input, textarea {{ font-size: {WIDGET_REM}rem !important; }}

.section-card {{
  background: #fff; border: 1px solid #e6e6e6; border-radius: {CARD_RADIUS_PX}px;
  padding: {CARD_PADDING_REM}rem {CARD_PADDING_REM+0.3}rem; margin: 0.75rem 0 1rem 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}}
/* 箇条書きの行間を広めに */
.section-card ul {{ line-height: {LINE_HEIGHT+0.1}; }}
/* リンクは下線で識別しやすく */
a {{ text-decoration: underline; }}
/* セクション見出しの下に薄い区切り線 */
.section-title {{ border-bottom: 2px solid #f0f0f0; padding-bottom: .25rem; margin-bottom: .6rem; }}
</style>
""", unsafe_allow_html=True)

# =========================
# データ・定義
# =========================
perma_indices = {
    'Positive Emotion': [0, 1, 2],
    'Engagement': [3, 4, 5],
    'Relationships': [6, 7, 8],
    'Meaning': [9, 10, 11],
    'Accomplishment': [12, 13, 14]
}

perma_short_keys = ['P', 'E', 'R', 'M', 'A']
full_labels = {
    'P': 'Pー前向きな気持ち（Positive Emotion）',
    'E': 'Eー集中して取り組む（Engagement）',
    'R': 'Rー人間関係（Relationships）',
    'M': 'Mー意味づけ（Meaning）',
    'A': 'Aー達成感（Accomplishment）'
}
descriptions = {
    'P': '楽しい気持ちや感謝、安心感など、気分の明るさや心のゆとりが感じられること。',
    'E': '物事に没頭し、時間を忘れて集中している感覚があること。',
    'R': '家族や友人、地域とのつながりを感じ、支え合えていること。',
    'M': '自分の人生に目的や価値を見いだし、「自分にとって大切なこと」に沿って生きていること。',
    'A': '目標に向かって取り組み、できた・やり遂げたという手応えがあること。'
}
tips = {
    'P': ['大切な人と過ごす', '趣味や創造的活動', '好きな音楽を聴く', '感謝を日々振り返る'],
    'E': ['夢中になれる作業時間を10〜15分だけ確保', '今に集中する呼吸法', '自然の中を観察しながら歩く', '自分の強みが活きる課題を選ぶ'],
    'R': ['地域のサークルや教室に参加', '相手に質問して話を深める', '昔の知人に近況連絡をする'],
    'M': ['意義を感じる活動に関わる', '情熱を誰かの役に立つ形にする', '小さな創作・記録で意味を言語化'],
    'A': ['小さなSMART目標を1つ設定', '最近の成功を振り返る', 'できたことを小さく祝う']
}

# 各要素のイラスト画像（ローカルファイル or 画像URL）
illustrations = {
    'P': 'assets/perma_P.png',  # 前向きな気持ち
    'E': 'assets/perma_E.png',  # 集中して取り組む
    'R': 'assets/perma_R.png',  # 人間関係
    'M': 'assets/perma_M.png',  # 意味づけ
    'A': 'assets/perma_A.png',  # 達成感
}

# 高コントラストの色（色弱にも配慮して彩度高め）
colors = ['#D81B60', '#E65100', '#2E7D32', '#1E88E5', '#6A1B9A']

# =========================
# タイトル
# =========================
st.title("あなたのPERMAプロファイル")
st.markdown("### PERMA：しあわせを支える5つの要素")
st.markdown("この図は、あなたが現在の生活でどの種類のしあわせな時間をどの程度過ごせているかを表しています。")

# =========================
# ファイルアップロード
# =========================
uploaded_file = st.file_uploader("Excelファイル（.xlsx）をアップロードしてください", type="xlsx")

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("データ読み込み成功！")

        # ID選択
        id_list = df.iloc[:, 0].dropna().astype(str).tolist()
        selected_id = st.selectbox("IDを選んでください", options=id_list)
        selected_row = df[df.iloc[:, 0].astype(str) == selected_id]
        if selected_row.empty:
            st.warning("選択されたIDに該当する行がありません。")
            st.stop()

        # スコア抽出（列名が "6_1"〜"6_23" を想定）
        score_columns = [col for col in df.columns if str(col).startswith("6_")]
        scores_raw = selected_row[score_columns].values.flatten()
        scores = pd.to_numeric(scores_raw, errors='coerce')

        if len(scores) < 23:
            st.error("6_1〜6_23 のスコアが不足しています。")
            st.stop()

        # =========================
        # PERMAスコア計算（5領域の平均）
        # =========================
        results = {}
        for key, idxs in perma_indices.items():
            valid_scores = [scores[i] for i in idxs if not np.isnan(scores[i])]
            results[key] = float(np.mean(valid_scores)) if valid_scores else 0.0

        value_by_short = {
            'P': results['Positive Emotion'],
            'E': results['Engagement'],
            'R': results['Relationships'],
            'M': results['Meaning'],
            'A': results['Accomplishment'],
        }

        # =========================
        # レーダーチャート（大きめ＆読みやすく）
        # =========================
        values = list(results.values())
        values += values[:1]
        angles = np.linspace(0, 2 * np.pi, len(perma_short_keys), endpoint=False).tolist()
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(7.8, 7.8), subplot_kw=dict(polar=True))
        for i in range(len(perma_short_keys)):
            ax.plot([angles[i], angles[i+1]], [values[i], values[i+1]], color=colors[i], linewidth=4)
        ax.plot(angles, values, color='#444', alpha=0.3, linewidth=2)
        ax.fill(angles, values, alpha=0.10, color='#888')

        # 方位ラベルを大きく・太め
        ax.set_thetagrids(np.degrees(angles[:-1]), perma_short_keys, fontsize=int(18 * FONT_SCALE), fontweight='bold')
        ax.set_ylim(0, 10)
        # 目盛りを明確に
        ax.set_rticks([2, 4, 6, 8, 10])
        ax.tick_params(axis='y', labelsize=int(14 * FONT_SCALE))
        ax.grid(alpha=0.25, linewidth=1.2)

        st.pyplot(fig)

        # =========================
        # 1) 各要素の説明（レーダー直下／カード表示）
        # =========================
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title"><h3>各要素の説明</h3></div>', unsafe_allow_html=True)
        for key in perma_short_keys:
            st.markdown(f"**{full_labels[key]}**：{descriptions[key]}")
        st.markdown('</div>', unsafe_allow_html=True)

                # =========================
        # 2) 結果のまとめコメント（日本語のみ）
        # =========================
        def _jp_list(items):
            if not items:
                return ""
            return items[0] if len(items)==1 else "、".join(items[:-1]) + " と " + items[-1]

        def _ja_only(label: str) -> str:
            base = label.split('（')[0]          # 'Pー前向きな気持ち'
            return base.split('ー')[-1].strip()  # '前向きな気持ち'

        avg_score = float(np.mean(list(results.values())))
        std_score = float(np.std(list(results.values())))

        STRONG_THR = 7.0
        GROWTH_THR = 5.0

        value_by_short = {
            'P': results['Positive Emotion'],
            'E': results['Engagement'],
            'R': results['Relationships'],
            'M': results['Meaning'],
            'A': results['Accomplishment'],
        }
        strong_keys = [k for k in perma_short_keys if value_by_short[k] >= STRONG_THR]
        growth_keys = [k for k in perma_short_keys if value_by_short[k] < GROWTH_THR]
        middle_keys = [k for k in perma_short_keys if GROWTH_THR <= value_by_short[k] < STRONG_THR]

        strong_labels = [_ja_only(full_labels[s]) for s in perma_short_keys if s in strong_keys]
        growth_labels = [_ja_only(full_labels[s]) for s in perma_short_keys if s in growth_keys]
        middle_labels = [_ja_only(full_labels[s]) for s in perma_short_keys if s in middle_keys]

        if std_score < 1.0:
            balance_comment = "全体としてバランスよく整っています。"
        elif std_score < 2.0:
            balance_comment = "おおむね良好ですが、いくつか強弱があります。"
        else:
            balance_comment = "要素間の強弱が比較的大きい状態です。"

        st.subheader("結果のまとめコメント")

        summary_lines = []  # ← これが無いと NameError になります
        summary_lines.append(f"**総合評価**：平均 {avg_score:.1f} 点（ばらつき {std_score:.1f}）。{balance_comment}")

        if strong_keys:
            summary_lines.append(
                f"あなたは **{_jp_list(strong_labels)}** に関して、"
                "その要素に沿った時間を比較的しっかり過ごせており、"
                "穏やかさや前向きさ、行動のしやすさが感じられている可能性が高いです。"
            )
        if middle_keys:
            summary_lines.append(
                f"**{_jp_list(middle_labels)}** は日常の中で一定の満足があり、おおむね安定しています。"
                "無理のない範囲で関連する時間や機会を少し増やすと、全体の底上げにつながります。"
            )
        if growth_keys:
            summary_lines.append(
                f"一方で、**{_jp_list(growth_labels)}** に関する習慣や体験はやや少ないかもしれません。"
                "もし「この要素をもっと育てたい」「関わる機会を増やしたい」と感じるなら、"
                "下の活動例を取り入れてみることをおすすめします。"
            )

        st.markdown("\n\n".join(summary_lines))

        # =========================
        # 3) 活動例（各領域）※ここも try: の内側！
        # =========================
        st.subheader("あなたに合わせたおすすめ行動（各領域）")

        # （イラストを使う場合は illustrations と os を先頭で定義しておく）
        def _render_activity_block(k: str, items: list):
            left, right = st.columns([3, 2])
            with left:
                st.markdown(f"**{_ja_only(full_labels[k])}**")
                for tip in items:
                    st.markdown(f"- {tip}")
            # 右カラムに画像を出すならここで st.image(...)
            # 例:
            # with right:
            #     img_path = illustrations.get(k)
            #     if img_path and (img_path.startswith("http") or os.path.isfile(img_path)):
            #         st.image(img_path, caption=_ja_only(full_labels[k]), use_column_width=True)

        if growth_keys:
            for k in perma_short_keys:
                if k in growth_keys:
                    _render_activity_block(k, tips[k][:3])
        else:
            st.markdown("現在は大きな偏りは見られません。維持と予防のために、次のような活動も役立ちます。")
            for k in perma_short_keys:
                _render_activity_block(k, tips[k][:2])

        # =========================
        # スタッフ向けメモ（折りたたみ）
        # =========================
        with st.expander("（スタッフ向け）評価メモと伝え方のコツ"):
            st.markdown(
                "- 点数は“良い/悪い”ではなく**選好と環境**の反映として扱い、生活史・価値観に照らして解釈。\n"
                "- 活動を新たに取り入れるときは、まず日課化しやすい**最小行動**から（例：1日5分の散歩/感謝メモ）。\n"
                "- 本ツールは**スクリーニング**であり医療的診断ではありません。心身の不調が続く場合は専門職へ。"
            )
