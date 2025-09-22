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
    'E': '集中して取り組む(Engagement)',
    'R': '人間関係(Relationship)',
    'M': '意味づけ(Meaning)',
    'A': '達成感(Accomplishment)'
}
descriptions = {
    'P': '楽しい気持ちや感謝の気持ちを感じる時間',
    'E': '何かに集中して取り組んでいる時間',
    'R': '他人との関係やつながりを感じる時間',
    'M': '人生の意味や目的を感じている時間',
    'A': '達成感や満足感を得られている時間'
}
tips = {
    'P': ['大切な人と過ごす', '趣味や創造的活動', '音楽を聴く', '感謝を日々振り返る　など'],
    'E': ['夢中になれる活動に参加', '今に集中する練習', '自然の中で観察', '自分の強みを活かす　など'],
    'R': ['教室やグループに参加', '相手に質問して関係を深める', '昔の知人に連絡する　など'],
    'M': ['意義ある団体や活動に参加', '情熱を他者のために使う', '創作活動で意味を見出す　など'],
    'A': ['SMARTな目標を立てる', '成功体験を振り返る', '成果を祝う など']
}
colors = ['red', 'orange', 'green', 'blue', 'purple']  # レーダー用の色

# =========================
# タイトル・導入
# =========================
st.title("あなたのPERMAプロファイル")
st.markdown("### PERMA：じぶんらしく生きるための5つの要素")
st.markdown("以下の図は、あなたが現在の生活でどの種類の幸せな時間をどの程度過ごせているかを表したものです。")

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
        labels = perma_short_keys

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        for i in range(len(perma_short_keys)):
            ax.plot([angles[i], angles[i+1]], [values[i], values[i+1]], color=colors[i], linewidth=3)
        ax.plot(angles, values, color='gray', alpha=0.2)
        ax.fill(angles, values, alpha=0.1)
        ax.set_thetagrids(np.degrees(angles[:-1]), labels, fontsize=16)
        ax.set_ylim(0, 10)
        st.pyplot(fig)

        # =========================
        # 結果のまとめコメント（レーダー直下）
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

        # 判定
        key_map = {
            'Positive Emotion': 'P',
            'Engagement': 'E',
            'Relationships': 'R',
            'Meaning': 'M',
            'Accomplishment': 'A'
        }
        strong_keys = [key_map[k] for k, v in results.items() if v >= STRONG_THR]
        growth_keys = [key_map[k] for k, v in results.items() if v < GROWTH_THR]
        middle_keys = [key_map[k] for k, v in results.items() if GROWTH_THR <= v < STRONG_THR]

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

        # --- 5要素の意味（短い引用つき） ---
        # 引用は Butler & Kern (2016) の本文から25語未満で抜粋
        domain_quote = {
            'P': '"the value of positive emotion across a range of life outcomes"',
            'E': '"an extreme level of psychological engagement that involves intense concentration, absorption, and focus"',
            'R': '"Social relationships are fundamental to life."',
            'M': '"having direction in life, connecting to something larger than oneself"',
            'A': '"working toward and reaching goals, mastery, and efficacy to complete tasks"'
        }

        # 高齢者にも平易なPERMA説明
        perma_plain = (
            "PERMAは、しあわせを支える5つの要素（P=楽しい気持ち、E=集中して打ち込む時間、"
            "R=人とのつながり、M=生きがい・意味、A=達成感）をバランスよく見ていく考え方です。"
            "点数は診断ではなく“今の状態の目安”として役立てます。"
        )

        # Butler & Kern (2016) の短い引用（25語未満）
        perma_profiler_line = (
            "研究では、結果は“領域ごとのプロフィールとして”示すことが推奨されています "
            "（Butler & Kern, 2016: \"Scores are reported visually as a profile across domains.\"）。"
        )

        # コメント本文の構築
        st.subheader("結果のまとめコメント")

        # 5要素の意味（引用つき）を最初に提示
        intro_lines = []
        intro_lines.append("**PERMAの5要素（意味と短い引用）**")
        for k in perma_short_keys:
            intro_lines.append(
                f"- **{k} – {full_labels[k]}**：{descriptions[k]} "
                f"— {domain_quote[k]}（Butler & Kern, 2016）"
            )
        st.markdown("\n".join(intro_lines))

        # 個別サマリー本体
        summary_lines = []
        summary_lines.append(perma_plain)
        summary_lines.append(f"**総合**：平均 **{avg_score:.1f} 点**（ばらつき {std_score:.1f}）。{balance_comment}")

        if strong_keys:
            summary_lines.append(
                f"**あなたの強み**：{_jp_list(strong_labels)}。"
                "うまくいっている習慣をそのまま続けましょう。"
            )
        if middle_keys:
            summary_lines.append(
                f"**安定している領域**：{_jp_list(middle_labels)}。"
                "無理のない範囲で少しずつ時間や頻度を増やすと、全体の底上げになります。"
            )
        if growth_keys:
            summary_lines.append(
                f"**これから育てたい領域**：{_jp_list(growth_labels)}。"
                "下に、今日から取り入れやすい行動例を挙げます。"
            )

        # PERMA-Profiler の説明・出典
        summary_lines.append(
            "> 参考：PERMA-Profiler は、PERMAの5領域を手短に測る尺度で、"
            "多面的なウェルビーイングの変化を丁寧に捉えることを目的としています。"
        )
        summary_lines.append(perma_profiler_line)
        summary_lines.append(
            "出典：Butler, J., & Kern, M. L. (2016). *The PERMA-Profiler: A brief multidimensional measure of flourishing*. "
            "International Journal of Wellbeing, 6(3), 1–48. doi:10.5502/ijw.v6i3.526"
        )
        st.markdown("\n\n".join(summary_lines))

        # 伸びしろに応じた具体的ヒント（各領域2つ）
        if growth_keys:
            st.markdown("#### あなたに合わせたおすすめ行動（各領域）")
            for k in perma_short_keys:
                if k in growth_keys:
                    st.markdown(f"- **{full_labels[k]}**： " + " / ".join(tips[k][:2]))

        # =========================
        # 各構成要素の説明
        # =========================
        st.subheader("各要素の説明")
        for key in perma_short_keys:
            st.markdown(f"**{key} - {full_labels[key]}**：{descriptions[key]}")

        # =========================
        # 活動のヒント（全体）
        # =========================
        st.subheader("☺あなたらしさを育むための活動の例")
        # 注意：低スコア抽出は results.values() の順序に依存しないよう再計算
        value_by_short = {
            'P': results['Positive Emotion'],
            'E': results['Engagement'],
            'R': results['Relationships'],
            'M': results['Meaning'],
            'A': results['Accomplishment'],
        }
        low_keys = [k for k in perma_short_keys if value_by_short[k] < 5]

        if low_keys:
            for key in low_keys:
                st.markdown(f"#### {key}：{full_labels[key]}")
                for tip in tips[key]:
                    st.markdown(f"- {tip}")
        else:
            st.markdown("すべての項目がバランスよく育っています。")
            st.markdown("これからもあなたらしく過ごしていくために、以下のような活動が役立ちます。")
            for key in perma_short_keys:
                st.markdown(f"#### {key}：{full_labels[key]}")
                for tip in tips[key]:
                    st.markdown(f"- {tip}")

        st.markdown("---")
        st.markdown("作成：認知症介護研究・研修大府センター　わらトレスタッフ")

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")

