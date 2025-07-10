import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- ページ設定 ---
st.set_page_config(page_title="PERMAプロファイラー", layout="centered")

# --- タイトル・説明 ---
st.title('PERMA: じぶんらしく生きるための5つの要素')
st.markdown("以下の図は、あなたが**現在の生活でどの種類の幸せな時間をどの程度過ごせているか**を表したものです。")

# --- 点数入力 ---
st.subheader('23の質問に、今の気持ちを 0〜10 の中から選んでください')

scores = []
cols = st.columns(1)
for i in range(23):
    with cols[0]:
        score = st.radio(
            f"Q{i+1}", 
            options=list(range(11)), 
            horizontal=True, 
            key=f"q{i+1}"
        )
        scores.append(score)

scores = np.array(scores)

# --- PERMA分類インデックス ---
perma_indices = {
    'Positive Emotion': [0, 1, 2],
    'Engagement': [3, 4, 5],
    'Relationships': [6, 7, 8],
    'Meaning': [9, 10, 11],
    'Accomplishment': [12, 13, 14]
}

# --- 各スコア計算 ---
results = {k: scores[idxs].mean() for k, idxs in perma_indices.items()}

# --- ラベルと説明 ---
labels = ['P', 'E', 'R', 'M', 'A']
full_labels = {
    'P': 'Positive Emotion',
    'E': 'Engagement',
    'R': 'Relationships',
    'M': 'Meaning',
    'A': 'Accomplishment'
}

descriptions = {
    'P': 'うれしい、たのしい、にっこりする気持ちのこと',
    'E': '何かに夢中になったり、いきいきと取りくむこと',
    'R': '人とのつながり、支えあいのこと',
    'M': 'だれかの役になっていると感じること',
    'A': '何かをやりとげたり、自分の成長を感じること'
}

tips = {
    'P': ['・大切な人と過ごす', '・感謝を日々振り返る', '・音楽や趣味を楽しむ'],
    'E': ['・夢中になれる活動を見つける', '・今に集中する練習をする', '・自然の中で感覚に集中'],
    'R': ['・教室や集まりに参加する', '・昔の知人に連絡をとる', '・知人と会話してつながる'],
    'M': ['・意義ある活動に参加する', '・人のために力を活かす', '・新しいことに挑戦する'],
    'A': ['・小さな目標を立てる', '・成功体験を思い出す', '・努力を自分らしく祝う']
}

# --- レーダーチャート ---
values = [results[full_labels[l]] for l in labels]
values += values[:1]
angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
angles += angles[:1]

fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
ax.plot(angles, values, linewidth=2)
ax.fill(angles, values, alpha=0.25)
ax.set_thetagrids(np.degrees(angles[:-1]), labels, fontsize=16)
ax.set_ylim(0, 10)
ax.set_title("PERMA figure", size=18, pad=20)

st.pyplot(fig)

# --- やさしい説明 ---
st.subheader("5つの要素の意味")
for key in labels:
    st.markdown(f"**{key} ({full_labels[key]})**: {descriptions[key]}")

# --- 育て方ヒント（満点未満のみ表示）---
st.subheader("あなたに合ったヒント")
for key in labels:
    if results[full_labels[key]] < 10:
        st.markdown(f"### {key} ({full_labels[key]}) を育てるヒント")
        for tip in tips[key]:
            st.markdown(f"- {tip}")

# --- フッター ---
st.markdown("---")
st.markdown("作成：認知症介護研究・研修大府センター　わらトレスタッフ")
