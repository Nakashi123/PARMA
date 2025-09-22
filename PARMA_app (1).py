import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path

# =========================
# アプリ設定
# =========================
st.set_page_config(page_title="PERMAプロファイル", layout="centered")

# ===== 大きめフォントと余白のCSS（高齢者向け強化版） =====
st.markdown(f"""
<style>
html, body, [class*="css"] {{
  font-size: 24px !important;   /* 全体の基本文字サイズ */
  line-height: 1.9 !important;  /* 行間広め */
  font-family: "Yu Gothic UI","Hiragino Kaku Gothic ProN","Meiryo",
               "Noto Sans JP","Noto Sans CJK JP","Helvetica","Arial",sans-serif !important;
  color: #111 !important;       /* 高コントラスト黒字 */
}}

h1 {{ font-size: 2.6rem !important; font-weight: 800 !important; letter-spacing: .03em; }}
h2 {{ font-size: 2.2rem !important; font-weight: 700 !important; }}
h3 {{ font-size: 1.8rem !important; font-weight: 700 !important; }}

p, li, label, span, div, th, td {{ font-size: 1.25rem !important; font-weight: 600; }}
small {{ font-size: 1.05rem !important; }}

.block-container {{ padding-top: 2rem; padding-bottom: 2.5rem; }}

.stSelectbox label, .stFileUploader label, .stRadio label, .stCheckbox label {{
  font-size: 1.3rem !important;
  font-weight: 600;
}}
div[data-baseweb="select"] * {{
  font-size: 1.3rem !important;
}}
input, textarea {{
  font-size: 1.3rem !important;
}}

.section-card {{
  background: #fff;
  border: 2px solid #e6e6e6;
  border-radius: 18px;
  padding: 1.4rem 1.6rem;
  margin: 1rem 0 1.4rem 0;
  box-shadow: 0 3px 10px rgba(0,0,0,0.08);
}}
.section-card ul {{ line-height: 2; }}
a {{ text-decoration: underline; font-size: 1.25rem !important; }}
.section-title {{
  border-bottom: 3px solid #f0f0f0;
  padding-bottom: .4rem;
  margin-bottom: .8rem;
}}
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


# 高コントラストの色
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
        # PERMAスコア計算
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

        ax.set_thetagrids(np.degrees(angles[:-1]), perma_short_keys, fontsize=int(18 * FONT_SCALE), fontweight='bold')
        ax.set_ylim(0, 10)
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
            return items[0] if len(items) == 1 else "、".join(items[:-1]) + " と " + items[-1]

        def _ja_only(label: str) -> str:
            base = label.split('（')[0]
            return base.split('ー')[-1].strip()

        avg_score = float(np.mean(list(results.values())))
        std_score = float(np.std(list(results.values())))

        STRONG_THR = 7.0
        GROWTH_THR = 5.0

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

        summary_lines = []
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
        # 3) 活動例（各領域）※右側にイラスト表示
        # =========================
        st.subheader("あなたに合わせたおすすめ行動（各領域）")

        def _render_activity_block(k: str, items: list):
            left, right = st.columns([3, 2])
            with left:
                st.markdown(f"**{_ja_only(full_labels[k])}**")
                for tip in items:
                    st.markdown(f"- {tip}")
            with right:
                img_path = illustrations.get(k)
                if img_path and (img_path.startswith("http") or os.path.isfile(img_path)):
                    st.image(img_path, caption=_ja_only(full_labels[k]), use_column_width=True)
                else:
                    st.caption("（画像が見つかりません）")

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
                "- 点数は“良い/悪い”ではなく**選好と環境**の反映として扱い、自分の生活史・価値観に照らして解釈しましょう。\n"
                "- 活動を新たに取り入れる時は、まず日課化しやすい**最小行動**から（例：1日5分の散歩/感謝メモ）。\n"
                "- 本ツールは**スクリーニング**であり医療的診断ではありません。心身の不調が続く場合はご受診を検討してください。"
            )

        st.markdown("---")
        st.markdown("作成：認知症介護研究・研修大府センター　わらトレスタッフ")

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
