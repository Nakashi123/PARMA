import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 日本語フォント指定（文字化け防止）
plt.rcParams['font.family'] = 'IPAexGothic'

# PERMAインデックス定義
perma_indices = {
    'Positive Emotion': [0, 1, 2],
    'Engagement': [3, 4, 5],
    'Relationships': [6, 7, 8],
    'Meaning': [9, 10, 11],
    'Accomplishment': [12, 13, 14]
}

# ラベルとヒント
labels = ['P', 'E', 'R', 'M', 'A']
full_labels = {
    'P': 'Positive Emotion',
    'E': 'Engagement',
    'R': 'Relationships',
    'M': 'Meaning',
    'A': 'Accomplishment'
}
tips = {
    'P': ['大切な人と過ごす', '趣味や創造的活動', '音楽を聴く', '感謝を日々振り返る'],
    'E': ['夢中になれる活動に参加', '今に集中する練習', '自然の中で観察', '自分の強みを活かす'],
    'R': ['教室やグループに参加', '相手に質問して関係を深める', '昔の知人に連絡する'],
    'M': ['意義ある団体や活動に参加', '情熱を他者のために使う', '創作活動で意味を見出す'],
    'A': ['SMARTな目標を立てる', '成功体験を振り返る', '成果を祝う']
}

# --- タイトル ---
st.title("あなたのPERMAプロファイル")
st.markdown("### PERMA：じぶんらしく生きるための5つの要素")
st.markdown("以下の図は、あなたが現在の生活でどの種類の幸せな時間をどの程度過ごせているかを表したものです。")

# --- ファイルアップロード ---
uploaded_file = st.file_uploader("Excelファイル（.xlsx）をアップロードしてください", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("データ読み込み成功！")

    # IDの選択
    ids = df.index.tolist()
    selected_index = st.selectbox("IDを選んでください", options=ids)
    row = df.iloc[selected_index]

    # スコア抽出（6_1〜6_23）
    scores = row.filter(like="6_").values[:23]
    scores = np.array(scores, dtype=float)

    # 各PERMAスコア計算
    results = {}
    for key, idxs in perma_indices.items():
        results[key] = scores[idxs].mean()

    # --- レーダーチャート ---
    perma_labels = list(results.keys())
    values = list(results.values())
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, len(perma_labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angles, values, linewidth=2, linestyle='solid')
    ax.fill(angles, values, alpha=0.3)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels, fontsize=16)
    ax.set_ylim(0, 10)
    st.pyplot(fig)

    # --- あなたに合ったヒント ---
    perma_short_keys = ['P', 'E', 'R', 'M', 'A']
    low_keys = [k for k in perma_short_keys if results[full_labels[k]] < 5]

    st.subheader("あなたに合ったヒント")
    if low_keys:
        for key in low_keys:
            st.markdown(f"### {key} ({full_labels[key]}) を育てるヒント")
            for tip in tips[key]:
                st.markdown(f"- {tip}")
    else:
        st.markdown("あなたは十分あなたらしく過ごせているようです。")
        st.markdown("ここに、さらに豊かに過ごすためのヒントを載せておきます。")
        for key in perma_short_keys:
            st.markdown(f"### {key} ({full_labels[key]})")
            st.markdown(", ".join(tips[key]))

    # --- フッター ---
    st.markdown("---")
    st.markdown("作成：認知症介護研究・研修大府センター　わらトレスタッフ")
