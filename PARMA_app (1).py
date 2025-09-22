import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# =========================
# 設定・定義
# =========================
st.set_page_config(page_title="PERMAプロファイル", layout="centered")

# PERMAインデックス（6_1〜6_23のうち、各領域3項目ぶんを集計）
perma_indices = {
    'Positive Emotion': [0, 1, 2],
    'Engagement': [3, 4, 5],
    'Relationships': [6, 7, 8],
    'Meaning': [9, 10, 11],
    'Accomplishment': [12, 13, 14]
}

# ラベル・ヒント設定
perma_short_keys = ['P', 'E', 'R', 'M', 'A']
full_labels = {
    'P': '前向きな気持ち（Positive Emotion）',
    'E': '集中して取り組む（Engagement）',
    'R': '人間関係（Relationships）',
    'M': '意味づけ（Meaning）',
    'A': '達成感（Accomplishment）'
}
# 日本語での要素説明（英語は出さない）
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
colors = ['red', 'orange', 'green', 'blue', 'purple']  # レーダー用の色

# =========================
# タイトル・導入
# =========================
st.title("あなたのPERMAプロファイル")
st.markdown("### PERMA：しあわせを支える5つの要素")
st.markdown("以下の図は、あなたが現在の生活でどの種類のしあわせな時間をどの程度過ごせているかを表しています。")

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

        # =========================
        # レーダーチャート
        # =========================
        values = list(results.values())
        values += values[:1]  # 円を閉じる
        angles = np.linspace(0, 2 * np.pi, len(perma_short_keys), endpoint=False).tolist()
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        for i in range(len(perma_short_keys)):
            ax.plot([angles[i], angles[i+1]], [values[i], values[i+1]], color=colors[i], linewidth=3)
        ax.plot(angles, values, color='gray', alpha=0.2)
        ax.fill(angles, values, alpha=0.1)
        ax.set_thetagrids(np.degrees(angles[:-1]), perma_short_keys, fontsize=16)
        ax.set_ylim(0, 10)
        st.pyplot(fig)

        # =========================
        # 結果のまとめコメント（レーダー直下・日本語のみ）
        # =========================
        def _jp_list(items):
            """日本語の自然な列挙（最後は「と」）"""
            if not items:
                return ""
            if len(items) == 1:
                return items[0]
            return "、".join(items[:-1]) + " と " + items[-1]

        # 数値の要約
        avg_score = float(np.mean(list(results.values())))
        std_score = float(np.std(list(results.values())))

        # 閾値（必要に応じて調整可能）
        STRONG_THR = 7.0      # 強み
        GROWTH_THR = 5.0      # これから育てたい領域

        # 判定用マップと値
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

        strong_labels = [full_labels[s] for s in perma_short_keys if s in strong_keys]
        growth_labels = [full_labels[s] for s in perma_short_keys if s in growth_keys]
        middle_labels = [full_labels[s] for s in perma_short_keys if s in middle_keys]

        # バランス評価コメント
        if std_score < 1.0:
            balance_comment = "全体としてバランスよく整っています。"
        elif std_score < 2.0:
            balance_comment = "おおむね良好ですが、いくつか強弱があります。"
        else:
            balance_comment = "要素間の強弱が比較的大きい状態です。"

        # --- 5要素の意味（日本語のみ、冒頭で簡潔に） ---
        st.subheader("結果のまとめコメント")
        intro_lines = []
        intro_lines.append("**PERMAの5要素（意味）**")
        for k in perma_short_keys:
            intro_lines.append(f"- **{full_labels[k]}**：{descriptions[k]}")
        st.markdown("\n".join(intro_lines))

        # --- 個別サマリー（体験・習慣ベースの日本語） ---
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
                f"**{_jp_list(middle_labels)}** は日常の中で一定の満足があり、"
                "おおむね安定しています。無理のない範囲で、関連する時間や機会を少し増やすと、"
                "全体の底上げにつながります。"
            )
        if growth_keys:
            summary_lines.append(
                f"一方で、**{_jp_list(growth_labels)}** に関する習慣や体験はやや少ないかもしれません。"
                "もし「この要素をもっと育てたい」「関わる機会を増やしたい」と感じるなら、"
                "以下の活動を取り入れてみることをおすすめします。"
            )

        st.markdown("\n\n".join(summary_lines))

        # 伸びしろに応じた具体的ヒント（各領域2つ）
        if growth_keys:
            st.markdown("#### あなたに合わせたおすすめ行動（各領域）")
            for k in perma_short_keys:
                if k in growth_keys:
                    st.markdown(f"- **{full_labels[k]}**： " + " / ".join(tips[k][:2]))

        # =========================
        # 各構成要素の説明（再掲）
        # =========================
        st.subheader("各要素の説明")
        for key in perma_short_keys:
            st.markdown(f"**{full_labels[key]}**：{descriptions[key]}")

        # =========================
        # 活動のヒント（全体）
        # =========================
        st.subheader("☺ あなたらしさを育むための活動の例")
        low_keys = [k for k in perma_short_keys if value_by_short[k] < 5]

        if low_keys:
            for key in low_keys:
                st.markdown(f"#### {full_labels[key]}")
                for tip in tips[key]:
                    st.markdown(f"- {tip}")
        else:
            st.markdown("すべての項目がバランスよく育っています。")
            st.markdown("これからもあなたらしく過ごしていくために、以下のような活動が役立ちます。")
            for key in perma_short_keys:
                st.markdown(f"#### {full_labels[key]}")
                for tip in tips[key]:
                    st.markdown(f"- {tip}")

        

        st.markdown("---")
        st.markdown("作成：認知症介護研究・研修大府センター　わらトレスタッフ")

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
