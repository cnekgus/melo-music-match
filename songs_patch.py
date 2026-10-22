if st.session_state.stage == "songs":
    banner("LEVEL 02 · MUSIC SELECT", "MUSIC SELECT", "좋아하는 노래를 5~15곡 골라줘!")
    st.markdown(
        f'<div class="step">♪ PLAYER: {html.escape(st.session_state.identity)}　♥ {len(st.session_state.picked)}/15</div>',
        unsafe_allow_html=True,
    )

    # One selectbox replaces many small category buttons on mobile.
    category_index = CATEGORIES.index(st.session_state.category) if st.session_state.category in CATEGORIES else 0
    chosen_category = st.selectbox("🎵 장르 선택", CATEGORIES, index=category_index, key="category_selector")
    if chosen_category != st.session_state.category:
        st.session_state.category = chosen_category
        st.session_state.page = 1
        st.rerun()

    filtered = [
        song for song in SONGS
        if st.session_state.category == "전체" or song["category"] == st.session_state.category
    ]
    pages = max(1, (len(filtered) + 9) // 10)
    st.session_state.page = max(1, min(st.session_state.page, pages))
    page = st.session_state.page
    st.markdown(
        f'<div class="panel-title">♫ SONG LIST · {html.escape(st.session_state.category)} '
        f'<span style="font-size:13px">({len(filtered)}곡)</span></div>',
        unsafe_allow_html=True,
    )

    def on_song_change(song_id, widget_key):
        picked = st.session_state.picked.copy()
        checked = st.session_state[widget_key]
        if checked and song_id not in picked:
            if len(picked) < 15:
                picked.append(song_id)
            else:
                st.session_state[widget_key] = False
                st.session_state.song_limit_notice = True
        elif not checked and song_id in picked:
            picked.remove(song_id)
        st.session_state.picked = picked

    st.session_state.setdefault("song_limit_notice", False)
    for i, song in enumerate(filtered[(page - 1) * 10:page * 10], (page - 1) * 10 + 1):
        sid = song["id"]
        widget_key = f"song_{sid}"
        # Persist widget values even when songs are on other pages.
        if widget_key not in st.session_state:
            st.session_state[widget_key] = sid in st.session_state.picked
        st.checkbox(
            f'{i:02d}. {song["title"]} — {song["artist"]}',
            key=widget_key,
            on_change=on_song_change,
            args=(sid, widget_key),
        )

    if st.session_state.song_limit_notice:
        st.warning("최대 15곡까지 선택할 수 있어!")
        st.session_state.song_limit_notice = False

    # Only three pagination controls: never 7 columns on mobile.
    left, middle, right = st.columns([1, 2, 1])
    with left:
        if st.button("◀ 이전", key="page_prev", disabled=page == 1, use_container_width=True):
            st.session_state.page = page - 1
            st.rerun()
    with middle:
        st.markdown(
            f'<p style="text-align:center;font-weight:900;padding-top:10px">PAGE {page} / {pages}</p>',
            unsafe_allow_html=True,
        )
    with right:
        if st.button("다음 ▶", key="page_next", disabled=page == pages, use_container_width=True):
            st.session_state.page = page + 1
            st.rerun()

    with st.expander(f"💗 MY PLAYLIST · {len(st.session_state.picked)}/15", expanded=False):
        if not st.session_state.picked:
            st.caption("아직 선택한 노래가 없어!")
        for sid in st.session_state.picked:
            if sid in BY_ID:
                song = BY_ID[sid]
                st.write(f'♫ {song["title"]} — {song["artist"]}')
        if st.button("선택 초기화", key="reset_songs"):
            st.session_state.picked = []
            for sid in BY_ID:
                widget_key = f"song_{sid}"
                if widget_key in st.session_state:
                    st.session_state[widget_key] = False
            st.rerun()

    if st.button("♫ 나와 맞는 친구 찾기 ➜", type="primary", use_container_width=True):
        if not 5 <= len(st.session_state.picked) <= 15:
            st.warning("노래를 5~15곡 선택해야 해!")
        else:
            try:
                ok, why = allowed_submission()
                if not ok:
                    st.warning(why)
                else:
                    st.session_state.delete_code = save_profile(
                        st.session_state.identity, st.session_state.picked
                    )
                    go("saved")
            except Exception as err:
                error_type = type(err).__name__
                status = getattr(err, "code", None)
                st.error(
                    f"저장 실패 · 오류 종류: {error_type}"
                    + (f" · 코드: {status}" if status is not None and str(status).isalnum() else "")
                )
                st.caption("이 문구만 캡처해서 보내줘. API 키와 개인정보는 보내지 마!")
                if error_type in ("APIError", "PostgrestException"):
                    st.info("DB 요청이 거절됐어. 연결 키의 종류, 테이블 권한 또는 중복 닉네임을 확인해야 해.")
    if st.button("← 프로필로", use_container_width=True):
        go("profile")
    st.stop()

