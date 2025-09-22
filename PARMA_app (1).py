
# --- ID選択が終わったら改ページ ---
st.markdown('<div class="force-break"></div>', unsafe_allow_html=True)

if selected_row.empty:
    st.warning("選択されたIDに該当する行がありません。")
else:
    results = compute_results(selected_row)
    summary = summarize(results)

    # ================= ページ2 =================
    st.markdown('<div class="page-2">', unsafe_allow_html=True)

    # レーダーチャート + 説明
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title"><h3>レーダーチャート</h3></div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 3])
    with col1:
        plot_radar(results)
    with col2:
        st.markdown(
            "この図は、しあわせを支える5つの要素（PERMA）の自己評価です。  \n"
            "点数が高いほどその要素が生活のなかで満たされていることを示し、  \n"
            "どこが強みで、どこに伸びしろがあるかが一目でわかります。"
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # 各要素の説明
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title"><h3>各要素の説明</h3></div>', unsafe_allow_html=True)
    colA, colB = st.columns(2)
    with colA:
        for k in ['P', 'E', 'R']:
            st.markdown(f"**{full_labels[k]}**：{descriptions[k]}")
    with colB:
        for k in ['M', 'A']:
            st.markdown(f"**{full_labels[k]}**：{descriptions[k]}")
    st.markdown('</div>', unsafe_allow_html=True)

    # === 改ページ ===
    st.markdown('<div class="force-break"></div>', unsafe_allow_html=True)

    # ================= ページ3 =================
    st.markdown('<div class="page-3">', unsafe_allow_html=True)

    # 結果のまとめ
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title"><h3>結果のまとめ</h3></div>', unsafe_allow_html=True)
    st.markdown(summary["summary_text"])
    st.markdown('</div>', unsafe_allow_html=True)

    # あなたにおすすめな活動
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title"><h3>あなたにおすすめな活動</h3></div>', unsafe_allow_html=True)
    if summary["growth"]:
        for k in summary["growth"]:
            st.markdown(f"**{full_labels[k]}**")
            for t in tips[k][:2]:
                st.markdown(f"- {t}")
    else:
        st.markdown("大きな偏りは見られません。維持と予防のために、以下の活動も役立ちます。")
        for k in perma_short_keys:
            st.markdown(f"**{full_labels[k]}**")
            for t in tips[k][:1]:
                st.markdown(f"- {t}")
    st.markdown('</div>', unsafe_allow_html=True)

    # この結果を受け取るうえで大切なこと
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title"><h3>この結果を受け取るうえで大切なこと</h3></div>', unsafe_allow_html=True)
    st.markdown(
        "- 結果は“良い/悪い”ではなく **選好や環境** の反映です。\n"
        "- 新しい活動は **小さな一歩** から。（例：1日5分の散歩）\n"
        "- 本ツールは **スクリーニング** であり診断ではありません。つらさが続く場合は専門職へご相談ください。"
    )
    st.markdown('</div>', unsafe_allow_html=True)
