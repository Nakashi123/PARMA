import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

# --- タイトルと説明 ---
st.title('🌸 PERMA: じぶんらしく生きるための5つの要素')
st.markdown("""
### 🧭 この図は、あなたが現在の生活で **どの種類の幸せな時間をどの程度過ごせているか** を表したものです。
5つの視点から、あなたの「じぶんらしさ」を振り返ってみましょう。
""")

# --- PERMA分類（各指標に該当する質問番号） ---
perma_indices = {
    'Positive Emotion': [0, 1, 2],
    'Engagement': [3, 4, 5],
    'Relationships': [6, 7, 8],
    'Meaning': [9, 10, 11],
    'Accomplishment': [12, 13, 14]
}

# --- ラベル略称と説明 ---
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

# --- スコア入力 ---
st.subheader('✏️ 23の質問にスコア（0〜10）で答えてください')
scores = []
for i in range(23):
    score = st.slider(f'Q{i+1}', 0.0, 10.0, 5.0, step=0.1, key=f'q{i+1}')
    scores.append(score)

# --- スコア集計 ---
scores = np.array(scores)
results = {key: scores[idxs].mean() for key, idxs in perma_indices.items()}

# --- レーダーチャート描画 ---
labels = list(short_labels.values())
values = list(results.values())
values += values[:1]
angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
angles += angles[:1]

fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
ax.plot(angles, values, linewidth=2, linestyle='solid')
ax.fill(angles, values, alpha=0.25)
ax.set_thetagrids(np.degrees(angles[:-1]), labels, fontsize=18)
ax.set_ylim(0, 10)

st.pyplot(fig)

# --- ダウンロードボタン ---
img_buffer = BytesIO()
fig.savefig(img_buffer, format='png')
img_buffer.seek(0)
st.download_button(
    label='📥 レーダーチャート画像をダウンロード',
    data=img_buffer,
    file_name='perma_chart.png',
    mime='image/png'
)

# --- 各項目の説明 ---
st.subheader("📖 各要素の説明と育て方")

growth_tips = {
    'Positive Emotion': [
        "大切な人と過ごす",
        "感謝を日々振り返る",
        "音楽や趣味を楽しむ"
    ],
    'Engagement': [
        "時間を忘れる活動に取り組む",
        "今に集中する練習をする",
        "自分の強みを活かす"
    ],
    'Relationships': [
        "人とのつながりを大切にする",
        "興味のあるグループに参加する",
        "昔の知り合いに連絡を取る"
    ],
    'Meaning': [
        "意義ある活動に参加する",
        "他者への貢献を意識する",
        "新しい体験や創作活動を行う"
    ],
    'Accomplishment': [
        "達成できそうな目標を立てる",
        "過去の成功体験を振り返る",
        "成果を自分らしく祝う"
    ]
}

for key in results:
    score = results[key]
    st.markdown(f"### {short_labels[key]} ({key})")
    st.markdown(f"**説明：** {descriptions[key]}")
    if score < 10.0:
        st.markdown("🌱 **育て方のヒント：**")
        for tip in growth_tips[key]:
            st.markdown(f"- {tip}")
        # --- 音声読み上げボタン（Webブラウザ用） ---
        explanation = f"{short_labels[key]}、{key}。{descriptions[key]}"
        st.components.v1.html(f"""
        <button onclick="var msg = new SpeechSynthesisUtterance('{explanation}'); 
                          msg.lang = 'ja-JP'; 
                          window.speechSynthesis.speak(msg);">
          🔊 {short_labels[key]} の説明を聞く
        </button>
        """, height=50)

# --- フッター ---
st.markdown("---")
st.caption("作成協力: あなたのウェルビーイングを応援するプロジェクト")
