
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- PERMA分類（例：各要素の該当インデックス）---
perma_indices = {
    'Positive Emotion': [0, 1, 2],
    'Engagement': [3, 4, 5],
    'Relationships': [6, 7, 8],
    'Meaning': [9, 10, 11],
    'Accomplishment': [12, 13, 14]
}

st.title('あなたのPERMAプロファイル')

# --- 入力 ---
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

# --- レーダーチャート用データ ---
labels = list(results.keys())
values = list(results.values())
values += values[:1]  # 閉じる

# --- レーダーチャート描画 ---
angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
angles += angles[:1]

fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
ax.plot(angles, values, linewidth=2, linestyle='solid')
ax.fill(angles, values, alpha=0.3)
ax.set_thetagrids(np.degrees(angles[:-1]), labels)
ax.set_ylim(0, 10)

st.pyplot(fig)

# --- やさしい解説 ---
st.subheader("それぞれの意味（やさしい説明）")
descriptions = {
    'Positive Emotion': 'うれしい、たのしい、にっこりする気持ちのことです。',
    'Engagement': '何かに夢中になったり、いきいきと取りくむことです。',
    'Relationships': '人とのつながり、支えあいのことです。',
    'Meaning': 'じぶんのいみや、だれかのためになっているかんじのことです。',
    'Accomplishment': 'やりとげたことや、自分の成長を感じることです。'
}
for k, v in descriptions.items():
    st.markdown(f"**{k}**: {v}")
