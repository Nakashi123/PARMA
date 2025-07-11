import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ✅ 手動IDリスト
manual_ids = [1, 3, 4, 5, 11, 15, 18, 19, 3659, 2896, 3089, 3336,
              3129, 3713, 3264, 3015, 3786, 3104, 3443, 3003,
              3788, 3646, 15, 3, 5, 19, 11, 2005]

# ✅ ファイルアップロード
uploaded_file = st.file_uploader("Excelファイルをアップロードしてください", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, header=0)
    excel_ids = df.iloc[:, 0].dropna().astype(int).tolist()
    combined_ids = sorted(set(excel_ids + manual_ids))
    selected_id = st.selectbox("IDを選んでください", options=combined_ids)
    st.write(f"選択されたID: {selected_id}")
    selected_row = df[df.iloc[:, 0] == selected_id]
    st.write("選択されたIDのデータ:", selected_row)

   # PERMAの5つの要素と説明つきラベル
labels = [
    "Positive Emotion（楽しい気持ち）",
    "Engagement（集中して没頭する）",
    "Relationships（人とのつながり）",
    "Meaning（人生の意味・目的）",
    "Accomplishment（達成感）"
]

# 対応するスコア列を抽出（あなたの列名に応じて変更）
scores = selected_row[["PE", "EN", "RE", "ME", "AC"]].values.flatten().tolist()
scores += scores[:1]  # 円を閉じる

# ラベルと同じ数だけ角度を作る
angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
angles += angles[:1]

# 描画
fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
ax.plot(angles, scores, linewidth=2, linestyle='solid')
ax.fill(angles, scores, alpha=0.3)

# ✅ 日本語つきのラベルを使う
ax.set_thetagrids(np.degrees(angles[:-1]), labels)
ax.set_title("PERMAレーダーチャート（やさしい説明つき）", fontsize=16)
st.pyplot(fig)

