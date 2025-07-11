import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 日本語フォント指定
plt.rcParams['font.family'] = 'IPAexGothic'

# PERMAインデックス定義（6_1〜6_23 に対応）
perma_indices = {
    'Positive Emotion': [0, 1, 2],
    'Engagement': [3, 4, 5],
    'Relationships': [6, 7, 8],
    'Meaning': [9, 10, 11],
    'Accomplishment': [12, 13, 14]
}

# 表示用ラベルとヒント
perma_short_keys = ['P', 'E', 'R', 'M', 'A']
full_labels = {
    'P': 'Positive Emotion',
    'E': 'Engagement',
    'R': 'Relationships',
    'M': 'Meaning',
    'A': 'Accomplishment'
}
label_names = {
    'P': 'P（楽しい気持ち）',
    'E': 'E（集中して没頭する）',
    'R': 'R（人とのつながり）',
    'M': 'M（人生の意味・目的）',
    'A': 'A（達成感）'
}
tips = {
    'P': ['大切な人と過ごす', '趣味や創造的活動', '音楽を聴く', '感謝を日々振り返る'],
    'E': ['夢中になれる活動に参加', '今に集中する練習', '自然の中で観察', '自分の強みを活かす'],
    'R': ['教室やグループに参加', '相手に質問して関係を深める', '昔の知人に連絡する'],
    'M': ['意義ある団体や活動に参加', '情熱を他者のために使う', '創作活動で意味を見出す'],
    'A': ['SMARTな目標を立てる', '成功体験を振り返る', '成果を祝う']
}

# --- UI ---
st.title("あなたのPERMAプロファイル")
st.markdown("### PERMA：じぶんらしく生きるための5つの要素")
st.markdown("以下の図は、あなたが現在の生活でどの種類の幸せな時間をどの程度過ごせているかを表したものです。")

# --- ファイルアップロード ---
uploaded_file = st.file_uploader("Excelファイル（.xlsx）をアップロードしてください", type="xlsx")

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("データ読み込み成功！")

        # IDリスト（1列目をIDとみなす）
        id_list = df.iloc[:, 0].dropna().astype(str).tolist()
        selected_id = st.selectbox("IDを選んでください", options=id_list)

        # 選択された行を取得
        selected_row = df[df.iloc[:, 0].astype(str) == selected_id]
        if selected_row.empty:
            st.warning("選択されたIDに該当する行がありません。")
            st.stop()

        # スコア抽出（6_1〜6_23）
        score_columns = [col for col in df.columns if str(col).startswith("6_")]
        scores_raw = selected_row[score_columns].values.flatten()

        # 数値化と欠損処理
        scores = pd.to_numeric(scores_raw, errors='coerce')
        if len(scores) < 23:
            st.error("6_1〜6_23 のスコアが不足しています。")
            st.stop()

        # PERMAスコア計算
        results = {}
        for key, idxs in perma_indices.items():
            selected_scores = [scores[i] for i in idxs if not np.isnan(scores[i])]
            results[key] = np.mean(selected_scores) if selected_scores else 0

        # --- レーダーチャート ---
        values = list(results.values())
        values += values[:1]
        angles = np.linspace(0, 2 * np.pi, len(perma_short_keys), endpoint=False).tolist()
        angles += angles[:1]
        labels = [label_names[k] for k in perma_short_keys]

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.plot(angles, values, linewidth=2, linestyle='solid')
        ax.fill(angles, values, alpha=0.3)
        ax.set_thetagrids(np.degrees(angles[:-1]), labels, fontsize=14)
        ax.set_ylim(0, 10)
        st.pyplot(fig)

        # --- ヒント表示 ---
        st.subheader("あなたに合ったヒント")
        low_keys = [k for k in perma_short_keys if results[full_labels[k]] < 5]

        if low_keys:
            for key in low_keys:
                st.markdown(f"### {label_names[key]} を育てるヒント")
                for tip in tips[key]:
                    st.markdown(f"- {tip}")
        else:
            st.markdown("あなたは十分あなたらしく過ごせているようです。")
            st.markdown("ここに、さらに豊かに過ごすためのヒントを載せておきます。")
            for key in perma_short_keys:
                st.markdown(f"### {label_names[key]}")
                st.markdown(", ".join(tips[key]))

        # --- フッター ---
        st.markdown("---")
        st.markdown("作成：認知症介護研究・研修大府センター　わらトレスタッフ")

    except Exception as e:
        st.error(f"データ処理中にエラーが発生しました：{e}")
