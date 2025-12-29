# -*- coding: utf-8 -*-
import streamlit as stあいう
import pandas as pd, numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="わらトレ　心の健康チェック", layout="centered")

plt.rcParams.update({
    "font.sans-serif": ["BIZ UDPGothic","Meiryo","Noto Sans JP"],
    "axes.unicode_minus": False,
    "font.size": 12,
})

# ------------ カラー設定 ------------
colors = {
    "P": "#F28B82",
    "E": "#FDD663",
    "R": "#81C995",
    "M": "#AECBFA",
    "A": "#F9AB00",
}
theme = {
    "bg": "#FAFAFA",
    "bar_bg": "#EEF2FB",
    "accent": "#4E73DF",
    "text": "#222",
}

# ------------ CSS ------------
st.markdown(f"""
<style>
.underline {{
  font-weight:bold;
  border-bottom:3px solid;
  padding-bottom:2px;
}}
</style>
""", unsafe_allow_html=True)

# ------------ PERMA定義 ------------
full_labels = {
    'P':'前向きな気持ち',
    'E':'集中して取り組むこと',
    'R':'人とのつながり',
    'M':'生きがいや目的',
    'A':'達成感',
}
descriptions = {
    'P':'楽しい気持ちや安心感、感謝など前向きな感情の豊かさを示します。',
    'E':'物事に没頭したり夢中になって取り組める状態を示します。',
    'R':'支え合えるつながりや信頼関係を感じられている状態です。',
    'M':'人生に目的や価値を感じて生きている状態です。',
    'A':'努力し、達成感や成長を感じられている状態です。',
}
tips = {
    'P':['感謝を書き出す','今日の良かったことを振り返る'],
    'E':['小さな挑戦を設定する','得意なことを活かす'],
    'R':['感謝を伝える','小さな親切をする'],
    'M':['大切にしている価値を書き出す','経験から学びを見つける'],
    'A':['小さな目標を作る','失敗を学びと捉える'],
}

# ------------ 質問項目位置 ------------
perma_indices = {
    'P':[4,9,21],
    'E':[2,10,20],
    'R':[5,14,18],
    'M':[0,8,16],
    'A':[1,7,15],
}
extra_indices = {
    'こころのつらさ':[6,13,19],
    'からだの調子':[3,12,17],
    'ひとりぼっち感':[11],
    'しあわせ感':[22],
}

# ------------ 計算 ------------
def compute_domain_avg(vals, idx):
    s = [vals[i] for i in idx if not np.isnan(vals[i])]
    return float(np.mean(s)) if s else np.nan

def compute_results(row):
    cols=[c for c in row.columns if str(c).startswith("6_")]
    vals=pd.to_numeric(row[cols].values.flatten(),errors="coerce")
    perma={k:compute_domain_avg(vals,v) for k,v in perma_indices.items()}
    extras={k:compute_domain_avg(vals,v) for k,v in extra_indices.items()}
    return perma,extras

# ------------ 表示用 ------------
def plot_hist(perma):
    labels=list(perma.keys())
    values=list(perma.values())
    fig,ax=plt.subplots(figsize=(4.5,3),dpi=160)
    ax.bar(labels,values,color=[colors[k] for k in labels])
    ax.set_ylim(0,10)
    st.pyplot(fig)

def score_label(v):
    if np.isnan(v): return "未回答"
    s=int(round(v))
    if s>=7: return f"{s}点（強み）"
    if s>=4: return f"{s}点（おおむね良好）"
    return f"{s}点（サポートが必要）"

# ------------ アプリ ------------
st.title("わらトレ　心の健康チェック")

# ======= 追加：わかりやすい説明 =======
st.info("""
このチェックは、ポジティブ心理学者 **Martin Seligman** が提唱した  
**PERMAモデル** に基づいて、心の健康や満たされている度合いを測定するものです。

PERMAは  
**前向きな気持ち・集中・つながり・意味・達成感**  
の5要素で構成されており、

> ネガティブな状態がないこと＝幸せ  
ではなく  
> 心が満たされ、前向きに生きられている状態（Flourishing）

をとらえます。

この結果は診断ではなく、  
**あなたの今の状態を理解し、より良く生きるヒントを得るためのツール**です。
""")

uploaded = st.file_uploader("Excelファイルをアップロード", type="xlsx")
if not uploaded: st.stop()

df=pd.read_excel(uploaded)
sid=st.selectbox("IDを選択",df.iloc[:,0].astype(str))
row=df[df.iloc[:,0].astype(str)==sid]

perma,extras=compute_results(row)

# ------ グラフ ------
st.header("PERMAスコアまとめ")
plot_hist(perma)

# ------ スコア表示（補助指標含む） ------
st.markdown("### あなたのスコア")
for k in perma:
    st.markdown(
        f"<span class='underline' style='border-color:{colors[k]};'>{full_labels[k]}</span>：{score_label(perma[k])}",
        unsafe_allow_html=True
    )

st.write("---")

st.markdown("#### 心の状態に関連する指標（参考）")
for k,v in extras.items():
    st.write(f"{k}：{score_label(v)}")

# ------ 行動提案 & 強み ------
weak=[k for k,v in perma.items() if not np.isnan(v) and v<=5]
strong=[k for k,v in perma.items() if not np.isnan(v) and v>=7]

if strong:
    st.subheader("あなたの強み（満たされている要素）")
    for k in strong:
        st.write(f"✔ {full_labels[k]}")

if weak:
    st.subheader("あなたにおすすめな行動")
    for k in weak:
        st.write(f"**{full_labels[k]}**")
        for t in tips[k]:
            st.write(f"- {t}")
