import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- PERMA分類（各要素の該当インデックス） ---
perma_indices = {
    'Positive Emotion': [0, 1, 2],
    'Engagement': [3, 4, 5],
    'Relationships': [6, 7, 8],
    'Meaning': [9, 10, 11],
    'Accomplishment': [12, 13, 14]
}

st.title('あなたのPERMAプロファイル')

# --- スコア入力 ---
st.subheader('23の質問にスコア（0〜10）で答えてください')
scores = []
for i in range(23):
    score = st.slider(f'Q{i+1}', 0.0, 10.0, 5.0, step=0.1)
    scores.append(score)

# --- スコア計算 ---
scores = np.array(scores)
results = {}
for key, idxs in perma_indices.items():
    results[key] = scores[idxs].mean()

# --- ラベルとやさしい説明 ---
short_labels = {
    'Positive Emotion': 'P (Positive Emotion)',
    'Engagement': 'E (Engagement)',
    'Relationships': 'R (Relationships)',
    'Meaning': 'M (Meaning)',
    'Accomplishment': 'A (Accomplishment)'
}

descriptions = {
    'Positive Emotion': 'P: うれしい、たのしい、にっこりする気持ちのこと',
    'Engagement': 'E: 何かに夢中になったり、いきいきと取りくむこと',
    'Relationships': 'R: 人とのつながり、支えあいのこと',
    'Meaning': 'M: だれかの役になっていると感じること',
    'Accomplishment': 'A: 何かをやりとげたり、自分の成長を感じること'
}

# --- レーダーチャートデータ作成 ---
labels = [short_labels[k] for k in results.keys()]
values = list(results.values())
values += values[:1]  # 閉じるために最初の値を追加

angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
angles += angles[:1]

# --- レーダーチャート描画 ---
fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
ax.plot(angles, values, linewidth=2, linestyle='solid')
ax.fill(angles, values, alpha=0.3)
ax.set_thetagrids(np.degrees(angles[:-1]), labels)
ax.set_ylim(0, 10)

st.pyplot(fig)

# --- やさしい説明を下に表示 ---
st.subheader("それぞれの意味（やさしい説明）")
for k in results.keys():
    st.markdown(f"**{short_labels[k]}**: {descriptions[k]}")
