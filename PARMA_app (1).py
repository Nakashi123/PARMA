import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

# --- フォント設定（日本語対応）---
matplotlib.rcParams['font.family'] = 'IPAPGothic'

# --- PERMA分類と説明 ---
perma_indices = {
    'Positive Emotion': [0, 1, 2],
    'Engagement': [3, 4, 5],
    'Relationships': [6, 7, 8],
    'Meaning': [9, 10, 11],
    'Accomplishment': [12, 13, 14]
}

short_labels = {
    'Positive Emotion': 'P',
    'Engagement': 'E',
    'Relationships': 'R',
    'Meaning': 'M',
    'Accomplishment': 'A'
}

descriptions = {
    'Positive Emotion': 'うれしい、たのしい、にっこりする気持ちのこと',
    'Engagement': '何かに夢中になったり、いきいきと取りくむこと',
    'Relationships': '人とのつながり、支えあいのこと',
    'Meaning': 'だれかの役になっていると感じること',
    'Accomplishment': '何かをやりとげたり、自分の成長を感じること'
}

tips = {
    'Positive Emotion': [
        '大切な人と過ごす時間をつくる',
        '毎日の中で感謝できることを探す',
        '好きな音楽を聞いたり、趣味を楽しむ'
    ],
    'Engagement': [
        '夢中になれる活動を見つける',
        'いまに集中する練習をする',
        '自然や芸術に触れる'
    ],
    'Relationships': [
        '誰かに声をかけてみる',
        '教室や集まりに参加する',
        '久しぶりの人に連絡してみる'
    ],
    'Meaning': [
        '人のためになる活動に関わる',
        'ボランティアや地域活動に参加する',
        '自分の好きなことを誰かのために活かす'
    ],
    'Accomplishment': [
        '小さな目標を立てて達成する',
        'できたことを振り返ってみる',
        '「よくがんばった」と声をかける'
    ]
}

# --- タイトルと冒頭説明 ---
st.title('あなたのPERMAプロファイル（しあわせのかたち）')
st.markdown("""
### PARMA：じぶんらしく生きるための5つのしあわせ

この図は、**あなたが今の生活でどんな「しあわせな時間」をどれくらい過ごせているか**を表しています。  
5つのしあわせ（PERMA）のバランスを、じぶんらしくふりかえってみましょう。
""")

# --- 入力欄 ---
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

# --- レーダーチャートデータ ---
labels = [short_labels[k] for k in results.keys()]
values = list(results.values())
values += values[:1]

angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
angles += angles[:1]

# --- チャート描画 ---
fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
ax.plot(angles, values, linewidth=2, linestyle='solid')
ax.fill(angles, values, alpha=0.3)
ax.set_thetagrids(np.degrees(angles[:-1]), labels, fontsize=16)
ax.set_ylim(0, 10)
st.pyplot(fig)

# --- 各要素のやさしい解説 ---
st.subheader('それぞれの「しあわせ」の意味')
for key in results.keys():
    st.markdown(f"**{short_labels[key]} ({key})**：{descriptions[key]}")

# --- 改善のヒント（満点でない要素のみ表示） ---
st.subheader('よりよい「しあわせ」のためのヒント')
for key, score in results.items():
    if score < 10:
        st.markdown(f"### {short_labels[key]} ({key})：{descriptions[key]}")
        for tip in tips[key]:
            st.markdown(f"- {tip}")
