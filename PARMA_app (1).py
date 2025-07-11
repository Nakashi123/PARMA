import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# PERMAインデックス（6_1〜6_23を5要素に分ける）
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
    'P': 'Positive Emotion',
    'E': 'Engagement',
    'R': 'Relationships',
    'M': 'Meaning',
    'A': 'Accomplishment'
}
descriptions = {
    'P': '楽しい気持ちや感謝の気持ちを感じる時間',
    'E': '何かに集中して取り組んでいる時間',
    'R': '他人との関係やつながりを感じる時間',
    'M': '人生の意味や目的を感じている時間',
    'A': '達成感や満足感を得られている時間'
}
tips = {
    'P': ['大切な人と過ごす', '趣味や創造的活動', '音楽を聴く', '感謝を日々振り返る'],
    'E': ['夢中になれる活動に参加', '今に集中する練習', '自然の中で観察', '自分の強みを活かす'],
    'R': ['教室やグループに参加', '相手に質問して関係を深める', '昔の知人に連絡する'],
    'M': ['意義ある団体や活動に参加', '情熱を他者のために使う', '創作活動で意味を見出す'],
    'A': ['SMARTな目標を立てる', '成功体験を振り返る', '成果を祝う']
}
colors = ['red', 'orange', 'green', 'blue', 'purple']

# --- タイトル・導入 ---
st.title("あなたのPERMAプロファイル")
st.markdown("### PERMA：じぶんらしく生きるための5つの要素")
st.markdown("以下の図は、あなたが現在の生活でどの種類の幸せな時間をどの程度過ごせているかを表したものです。")

# --- ファイルアップロード ---
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

        # スコア抽出
        score_columns = [col for col in df.columns if str(col).startswith("6_")]
        scores_raw = selected_row[score_columns].values.flatten()
        scores = pd.to_numeric(scores_raw, errors='coerce')

        if len(scores) < 23:
            st.error("6_1〜6_23 のスコアが不足しています。")
            st.stop()

        # PERMAスコア計算
        results = {}
        for key, idxs in perma_indices.items():
            valid_scores = [scores[i] for i in idxs if not np.isnan(scores[i])]
            results[key] = np.mean(valid_scores) if valid_scores else 0

        # --- レーダーチャート（色分け）---
        values = list(results.values())
        values += values[:1]
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

        # --- 各構成要素の説明 ---
        st.subheader("各要素の説明")
        for key in perma_short_keys:
            st.markdown(f"**{key} - {full_labels[key]}**：{descriptions[key]}")

        # --- 活動のヒントセクション ---
        st.subheader("☺あなたらしさを育むための活動の例")
        low_keys = [k for k, v in zip(perma_short_keys, results.values()) if v < 5]

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
