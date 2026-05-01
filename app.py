# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="わらトレ 心の健康チェック", layout="wide")

colors = {"P": "#F28B82", "E": "#FDD663", "R": "#81C995", "M": "#AECBFA", "A": "#F9AB00"}
extra_colors = {
    "心の健康の総合得点": "#4E73DF",
    "気持ちの様子（いやな気持）": "#E74C3C",
    "からだの調子": "#2ECC71",
    "ひとりぼっち感": "#9B59B6",
    "全体的なしあわせ感": "#F1C40F",
}
full_labels = {"P": "前向きな気持ち", "E": "集中して取り組むこと", "R": "人とのつながり", "M": "生きがいや目的", "A": "達成感"}
descriptions = {
    "P": "楽しい気持ちや安心感、感謝など前向きな感情の豊かさを示します。",
    "E": "物事に没頭したり夢中になって取り組める状態を示します。",
    "R": "支え合えるつながりや信頼関係を感じられている状態です。",
    "M": "人生に目的や価値を感じて生きている状態です。",
    "A": "努力し、達成感や成長を感じられている状態です。",
}
tips = {
    "P": ["感謝の気持ちをメモしてみる", "今日の良かったことを振り返る"],
    "E": ["小さな挑戦を設定する", "得意なことを活かす"],
    "R": ["感謝を伝える", "小さな親切をする"],
    "M": ["大切にしている価値を書き出す", "経験から学びを見つける"],
    "A": ["小さな目標を作る", "失敗を学びと捉える"],
}
action_emojis = {"P": "😊", "E": "🧩", "R": "🤝", "M": "🌱", "A": "🏁"}

perma_indices = {"P": [4, 9, 21], "E": [2, 10, 20], "R": [5, 14, 18], "M": [0, 8, 16], "A": [1, 7, 15]}
extra_indices = {
    "気持ちの様子（いやな気持）": [6, 13, 19],
    "からだの調子": [3, 12, 17],
    "ひとりぼっち感": [11],
    "全体的なしあわせ感": [22],
}

def compute_domain_avg(vals, idx):
    scores = [vals[i] for i in idx if i < len(vals) and not np.isnan(vals[i])]
    return float(np.mean(scores)) if scores else np.nan

def compute_results(row):
    cols = sorted([c for c in row.columns if str(c).startswith("6_")], key=lambda x: int(str(x).split("_")[1]))
    vals = pd.to_numeric(row[cols].values.flatten(), errors="coerce")
    perma = {k: compute_domain_avg(vals, v) for k, v in perma_indices.items()}
    extras = {k: compute_domain_avg(vals, v) for k, v in extra_indices.items()}
    perma_15 = sorted({i for v in perma_indices.values() for i in v})
    extras["心の健康の総合得点"] = compute_domain_avg(vals, perma_15 + [22])
    return perma, extras

def score_html(score):
    return "未回答" if np.isnan(score) else f"<strong>{score:.1f}</strong><span>/10点</span>"

def meter_card(title, score, color, big=False):
    width = 0 if np.isnan(score) else max(0, min(score * 10, 100))
    cls = "score big" if big else "score"
    return f'<div class="card"><div class="card-title">{title}</div><div class="meter"><div class="meter-fill" style="width:{width:.0f}%; background:{color};"></div></div><div class="{cls}">{score_html(score)}</div></div>'

def chart_html(perma_scores):
    items = ""
    for k in ["P", "E", "R", "M", "A"]:
        v = perma_scores.get(k, np.nan)
        h = 0 if np.isnan(v) else v * 4.2
        label = "" if np.isnan(v) else f"{v:.1f}"
        items += f'<div class="chart-item"><div class="chart-score">{label}</div><div class="chart-bar" style="height:{h}mm; background:{colors[k]};"></div><div>{k}</div></div>'
    return f'<div class="chart-box"><div class="chart-title">PERMA</div><div class="bar-chart">{items}</div></div>'

if "ready" not in st.session_state:
    st.session_state.ready = False
if "df" not in st.session_state:
    st.session_state.df = None
if "sid" not in st.session_state:
    st.session_state.sid = None

if not st.session_state.ready:
    st.title("わらトレ　心の健康チェック")
    uploaded = st.file_uploader("Excelファイル（ID列＋6_1〜6_23 の列）をアップロードしてください", type="xlsx")
    if uploaded:
        df = pd.read_excel(uploaded)
        id_list = df.iloc[:, 0].dropna().astype(str).tolist()
        if not id_list:
            st.error("ID列に有効な値がありません。")
        else:
            sid = st.selectbox("IDを選んでください", options=id_list)
            if st.button("このIDで結果を表示"):
                st.session_state.df = df
                st.session_state.sid = sid
                st.session_state.ready = True
                st.rerun()
    st.stop()

df = st.session_state.df
sid = st.session_state.sid
row = df[df.iloc[:, 0].astype(str) == str(sid)]

if row.empty:
    st.warning("選択されたIDが見つかりません。")
    st.session_state.ready = False
    st.rerun()

perma_scores, extras = compute_results(row)
weak_keys = [k for k, v in perma_scores.items() if not np.isnan(v) and v <= 5]
strong_keys = [k for k, v in perma_scores.items() if not np.isnan(v) and v >= 7]

strong_html = "".join([meter_card(f"✓ {full_labels[k]}（{k}）", perma_scores[k], colors[k]) for k in strong_keys])
if not strong_html:
    strong_html = '<div class="note compact">今回は、7点以上の項目はありませんでした。</div>'

action_html = ""
for k in weak_keys:
    items = "".join([f"<li>{t}</li>" for t in tips[k]])
    action_html += f'<div class="action-title">{action_emojis[k]} {full_labels[k]}（{k}）</div><ul class="action-list">{items}</ul>'
if not action_html:
    action_html = '<div class="note compact">今回は、5点以下の項目はありませんでした。</div>'

css = """
<style>
html, body, .stApp {
  background:#f5f6fa;
  color:#222;
  font-family:"BIZ UDPGothic","Meiryo","Noto Sans JP",sans-serif;
}
.block-container {
  max-width:none !important;
  padding:0 !important;
}
.report {
  width:210mm;
  margin:0 auto;
}
.page {
  width:210mm;
  height:297mm;
  box-sizing:border-box;
  background:white;
  padding:8mm 9mm;
  overflow:hidden;
  page-break-after:always;
  break-after:page;
  margin:0 auto 14px auto;
}
.page:last-child {
  page-break-after:auto;
  break-after:auto;
}
.header {
  display:grid;
  grid-template-columns:46mm 1fr 46mm;
  align-items:start;
  margin-bottom:5mm;
}
.title {
  text-align:center;
  font-size:25px;
  font-weight:900;
  padding-top:5mm;
}
.name-box {
  border:2px solid #C9D4EE;
  border-radius:9px;
  padding:8px 11px;
  height:22mm;
  box-sizing:border-box;
}
.name-label {
  font-size:15px;
  font-weight:900;
}
.name-line {
  height:10mm;
  border-bottom:2px solid #8898bf;
}
.section {
  background:#EEF2FB;
  border-left:8px solid #4E73DF;
  border-radius:8px;
  padding:7px 11px;
  font-size:16px;
  font-weight:900;
  margin:8px 0 6px 0;
}
.note {
  border:1px solid #E2E7F2;
  border-radius:9px;
  padding:8px 11px;
  font-size:14px;
  line-height:1.48;
  margin-bottom:6px;
}
.grid-main {
  display:grid;
  grid-template-columns:1fr 50mm;
  gap:8px;
}
.grid-2 {
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:8px;
}
.card {
  border:1px solid #E2E7F2;
  border-radius:9px;
  padding:8px 10px;
  margin-bottom:6px;
}
.card-title {
  font-size:14px;
  font-weight:900;
  margin-bottom:4px;
}
.meter {
  height:11px;
  background:#E4E7ED;
  border-radius:999px;
  overflow:hidden;
}
.meter-fill {
  height:100%;
  border-radius:999px;
}
.score {
  margin-top:4px;
  font-size:12.5px;
}
.score strong {
  font-size:31px;
  font-weight:1000;
  line-height:1;
}
.score.big strong {
  font-size:38px;
}
.chart-box {
  border:1px solid #E2E7F2;
  border-radius:9px;
  padding:9px;
  text-align:center;
}
.chart-title {
  font-size:14px;
  font-weight:900;
  margin-bottom:3px;
}
.bar-chart {
  height:49mm;
  display:flex;
  align-items:end;
  justify-content:space-around;
  border-left:1px solid #999;
  border-bottom:1px solid #999;
  padding:4px 4px 0 4px;
}
.chart-item {
  width:14%;
  font-size:10.5px;
  text-align:center;
}
.chart-score {
  font-size:10.5px;
  font-weight:700;
}
.chart-bar {
  width:100%;
  margin-bottom:2px;
}
.ul-note {
  margin:3px 0 0 1.2em;
  padding:0;
}
.ul-note li {
  margin:2px 0;
}
.page2 {
  padding:8mm 9mm;
}
.page2 .section {
  margin:7px 0 6px 0;
  padding:6px 10px;
  font-size:15.5px;
}
.page2 .card {
  padding:7px 10px;
  margin-bottom:6px;
}
.page2 .card-title {
  font-size:14px;
}
.page2 .score strong {
  font-size:30px;
}
.action-layout {
  display:grid;
  grid-template-columns:1fr 44mm;
  gap:10px;
  align-items:start;
}
.action-title {
  font-size:18px;
  font-weight:900;
  margin:7px 0 2px 0;
}
.action-list {
  margin:0 0 6px 1.25em;
  padding:0;
  font-size:14px;
  line-height:1.38;
}
.illust {
  width:40mm;
  margin-top:8px;
}
.compact {
  font-size:13px;
  line-height:1.38;
  padding:7px 10px;
  margin-bottom:6px;
}
.perma-box {
  border:2px solid #4E73DF;
  border-radius:9px;
  padding:8px 10px;
  font-size:13px;
  line-height:1.38;
  margin-bottom:6px;
}
.perma-highlight {
  color:#4E73DF;
  font-weight:900;
}
.cite {
  font-size:11px;
  line-height:1.28;
}
.footer {
  border-top:2px solid #ddd;
  padding-top:5px;
  margin-top:5px;
  font-size:11px;
  line-height:1.3;
}
@media print {
  @page {
    size:A4 portrait;
    margin:0;
  }
  html, body, .stApp {
    background:white !important;
    margin:0 !important;
    padding:0 !important;
  }
  * {
    -webkit-print-color-adjust:exact !important;
    print-color-adjust:exact !important;
  }
  header, footer,
  [data-testid="stHeader"],
  [data-testid="stToolbar"],
  [data-testid="stDecoration"],
  [data-testid="stStatusWidget"] {
    display:none !important;
  }
  .block-container {
    padding:0 !important;
    margin:0 !important;
  }
  .report {
    width:210mm !important;
    margin:0 !important;
  }
  .page {
    margin:0 !important;
    width:210mm !important;
    height:297mm !important;
    page-break-after:always !important;
    break-after:page !important;
  }
  .page:last-child {
    page-break-after:auto !important;
    break-after:auto !important;
  }
}
</style>
"""

page1 = f"""<div class="page page1">
<div class="header">
<div></div>
<div class="title">わらトレ　心の健康チェック</div>
<div class="name-box"><div class="name-label">氏名</div><div class="name-line"></div></div>
</div>
<div class="note"><b>はじめに（この用紙でわかること）</b><br>この用紙は、心の健康チェックの結果です。今の心の元気さを、0〜10点で確認できます。点数が高いところは「今の強み」、低いところは「これから整えるヒント」としてご覧ください。</div>
<div class="section">1-1. 要素ごとにみた心の状態</div>
<div class="grid-main">
<div class="grid-2">
<div>{meter_card("P：前向きな気持ち", perma_scores.get("P", np.nan), colors["P"])}{meter_card("E：集中して取り組むこと", perma_scores.get("E", np.nan), colors["E"])}{meter_card("R：人とのつながり", perma_scores.get("R", np.nan), colors["R"])}</div>
<div>{meter_card("M：生きがいや目的", perma_scores.get("M", np.nan), colors["M"])}{meter_card("A：達成感", perma_scores.get("A", np.nan), colors["A"])}</div>
</div>
{chart_html(perma_scores)}
</div>
<div class="note"><b>各指標の見方</b><ul class="ul-note"><li><b>P（前向きな気持ち）</b>：{descriptions["P"]}</li><li><b>E（集中して取り組むこと）</b>：{descriptions["E"]}</li><li><b>R（人とのつながり）</b>：{descriptions["R"]}</li><li><b>M（生きがいや目的）</b>：{descriptions["M"]}</li><li><b>A（達成感）</b>：{descriptions["A"]}</li></ul></div>
<div class="section">1-2. こころ・からだの調子</div>
{meter_card("心の健康の総合得点", extras.get("心の健康の総合得点", np.nan), extra_colors["心の健康の総合得点"], True)}
<div class="grid-2">
<div>{meter_card("からだの調子", extras.get("からだの調子", np.nan), extra_colors["からだの調子"])}{meter_card("気持ちの様子（いやな気持）", extras.get("気持ちの様子（いやな気持）", np.nan), extra_colors["気持ちの様子（いやな気持）"])}</div>
<div>{meter_card("全体的なしあわせ感", extras.get("全体的なしあわせ感", np.nan), extra_colors["全体的なしあわせ感"])}{meter_card("ひとりぼっち感", extras.get("ひとりぼっち感", np.nan), extra_colors["ひとりぼっち感"])}</div>
</div>
<div class="note"><b>各指標の意味</b><ul class="ul-note"><li><b>気持ちの様子（いやな気持）</b>：不安になったり、気分が沈んだり、いらいらしたりすることがどのくらいあるかの結果です。</li><li><b>からだの調子</b>：体の調子や元気さについて、ご本人が感じた程度の結果です。</li><li><b>ひとりぼっち感</b>：ひとりぼっちだと感じることがあるかの結果です。</li></ul></div>
</div>"""

page2 = f"""<div class="page page2">
<div class="section">2-1. 満たされている心の健康の要素（強み）</div>
{strong_html}
<div class="section">2-2. これから伸ばせる要素と具体的な行動例</div>
<div class="action-layout">
<div><div class="note compact">点数が低めだったところは、悪い結果ではありません。<br>これから少しずつ整えていける「ヒント」として見てください。</div>{action_html}</div>
<div><img class="illust" src="https://eiyoushi-hutaba.com/wp-content/uploads/2025/01/%E5%85%83%E6%B0%97%E3%81%AA%E3%82%B7%E3%83%8B%E3%82%A2%E3%81%AE%E4%BA%8C%E4%BA%BA%E3%80%80%E9%81%8B%E5%8B%95%E7%89%88.png"></div>
</div>
<div class="section">3. 備考</div>
<div class="perma-box"><b><span class="perma-highlight">このチェックで見ていること</span></b><br>この用紙は、心の元気さを <span class="perma-highlight">5つの面（PERMA）</span> で見る方法をもとにしています。5つの面をそれぞれ見ることで、「どこが保てているか」「どこを整えるとよさそうか」を考えやすくします。</div>
<div class="note compact"><b>① PERMA（5つの面）とは</b><ul class="ul-note"><li><b>P</b>：前向きな気持ち</li><li><b>E</b>：集中して取り組むこと</li><li><b>R</b>：人とのつながり</li><li><b>M</b>：生きがいや目的</li><li><b>A</b>：達成感</li></ul></div>
<div class="note compact"><b>② この尺度（PERMA-Profiler）について</b><ul class="ul-note"><li>PERMAを短い質問で測れるように開発された尺度です。</li><li><b>PERMAの15問</b>に、<b>追加の8問</b>を加えた、合計<b>23問</b>の形式です。</li><li>点数は<b>0〜10点</b>で確認します。</li></ul></div>
<div class="note compact"><b>③ 結果の使い方（おすすめ）</b><ul class="ul-note"><li><b>高いところ</b>：今の強み</li><li><b>低いところ</b>：これから整えるヒント</li><li>くり返して確認し、変化を見ると役立ちます。</li></ul></div>
<div class="note cite compact"><b>引用（根拠）</b><br>Butler, J., &amp; Kern, M. L. (2016). <i>The PERMA-Profiler: A brief multidimensional measure of flourishing</i>. <i>International Journal of Wellbeing</i>, 6(3), 1–48. https://doi.org/10.5502/ijw.v6i3.526</div>
<div class="footer"><b>この評価結果に関するお問い合わせは以下まで</b><br>〈お問い合わせ先〉〒 474-0037　愛知県大府市半月町三丁目294番地<br>☎ 0562-44-5551　研究代表者：李 相侖<br><b>この度は、ご協力ありがとうございました。</b></div>
</div>"""

st.markdown(css + f'<div class="report">{page1}{page2}</div>', unsafe_allow_html=True)
