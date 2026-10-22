"""MELODY: responsive retro pixel music-match app (Streamlit)."""
import csv
import html
import os
import sqlite3
import hashlib
import secrets
import time
import threading
from pathlib import Path

import streamlit as st
from matching import compare, feature_sets

ROOT = Path(__file__).resolve().parent
with (ROOT / "songs.csv").open(encoding="utf-8-sig", newline="") as fh:
    SONGS = list(csv.DictReader(fh))
BY_ID = {song["id"]: song for song in SONGS}
CATEGORIES = ["전체"] + sorted({s["category"] for s in SONGS})

st.set_page_config(page_title="MELODY ♫ | Find Your Music Mate", page_icon="💗", layout="centered", initial_sidebar_state="collapsed")
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Gowun+Dodum:wght@400;700&display=swap');
:root{--ink:#1b205e;--violet:#6554bb;--pink:#ff84d7;--paper:#f9edff;--shadow:#4a3e99}
html,body,[class*="css"],.stApp{font-family:'Gowun Dodum',sans-serif!important}
.stApp{background:radial-gradient(circle at 20% 15%,#ffd3fa70,transparent 28%),radial-gradient(circle at 80% 85%,#a6d9ff66,transparent 36%),linear-gradient(160deg,#545fca 0%,#9790e8 44%,#e4b7f9 100%);color:var(--ink)}
.stApp::before{content:"";position:fixed;inset:0;pointer-events:none;opacity:.22;background-image:linear-gradient(#ffffff65 1px,transparent 1px),linear-gradient(90deg,#ffffff65 1px,transparent 1px);background-size:35px 35px}
header[data-testid="stHeader"]{background:transparent}
.block-container{max-width:720px!important;padding:1rem 1rem 4rem!important;position:relative;z-index:1}
[data-testid="stSidebar"],#MainMenu,footer{display:none!important}
h1,h2,h3,p,span,label,[data-testid="stMarkdownContainer"]{color:var(--ink)}
.game-shell{background:#343a91;border:4px solid #f5ccff;outline:3px solid #4b438d;box-shadow:8px 8px 0 #403778; padding:14px; margin:9px 3px 19px;color:white;position:relative}
.game-shell:before{content:'✦　✧　　　✦　　　　✧　✦';display:block;text-align:center;color:#fff0a9;font-size:18px;letter-spacing:8px}
.pixel{font-family:'Press Start 2P','Gowun Dodum',sans-serif!important;text-shadow:3px 3px 0 #483c9e}
.brand{font-size:clamp(30px,8vw,62px);line-height:1.5;color:#ff9ee5;text-align:center;-webkit-text-stroke:1px #fff;overflow-wrap:anywhere}
.game-sub{color:#e4dfff;text-align:center;font-weight:700;letter-spacing:1px;margin:8px 0 16px}
.tiny-top{display:flex;justify-content:space-between;gap:8px;color:#fff1c7;font-size:11px;font-weight:900;letter-spacing:1px}
.hearts{color:#ff92ce;letter-spacing:3px;font-size:19px}
.game-title{font-size:clamp(16px,4vw,24px);text-align:center;color:#ffc5f2;font-weight:900;margin:8px 0 14px;text-shadow:2px 2px #27216b}
.clouds{text-align:center;font-size:24px;color:#ffdcfb;letter-spacing:9px;margin-top:14px}
.panel{background:linear-gradient(180deg,#fff7ff,#efdcff);border:3px solid #fff;outline:2px solid #6554bb;box-shadow:5px 5px 0 #544b9d;padding:18px;margin:10px 4px 19px}
.panel-title{text-align:center;font-weight:900;color:#37318b;font-size:20px;margin-bottom:10px}
.panel-sub{text-align:center;font-size:13px;color:#675ba6}
.step{color:#fff4b6;font-size:12px;font-weight:900;letter-spacing:2px;margin:4px 0 10px}
[data-testid="stWidgetLabel"] p{font-weight:900;color:#322d83!important}
[data-testid="stTextInput"] input{background:#fff7ff!important;color:#27235e!important;border:2px solid #8c77d5!important;border-radius:2px!important;min-height:48px}
.stButton>button{background:#e5dbff;color:#27235e;border:2px solid #544a9e;border-radius:2px;box-shadow:3px 3px 0 #6d5fba;min-height:43px;font-weight:900;transition:transform .08s;white-space:normal;overflow-wrap:anywhere}
.stButton>button:hover{background:#ffd3f2;color:#211d64;border-color:#43378e;transform:translateY(-1px)}
.stButton>button[kind="primary"]{background:linear-gradient(180deg,#ffb3ee,#fa82d5);color:#251d65;border:3px solid #54408e;box-shadow:4px 4px 0 #5548a5;min-height:55px;font-size:16px}
.stButton>button:disabled{opacity:.4}
[data-testid="stCheckbox"]{background:#fff7ff;border:2px solid #ded0fb;margin:4px 0;padding:7px 9px}
[data-testid="stCheckbox"] label p{font-size:14px!important;font-weight:800}
[data-testid="stCheckbox"] [data-testid="stCheckboxLabel"]{min-width:0}
[data-testid="stAlert"]{background:#fff0ff;color:#40358d;border:2px solid #aa9ae2;border-radius:2px}
[data-testid="stProgress"]>div{background:#e1d3ff}
[data-testid="stProgress"] [role="progressbar"]{background:#ff80cc}
[data-testid="stExpander"]{background:#fff8ff;border:2px solid #c7b5f2}
[data-testid="stSelectbox"]>div>div{background:#fff8ff;color:#352c83}
[data-testid="stCaptionContainer"] p{color:#493c88!important}
.match-row{display:flex;align-items:center;gap:12px;background:#fff2ff;border:2px solid #c2aaf1;padding:12px;margin:9px 0;min-width:0}
.rank{font-size:24px;min-width:32px;text-align:center}.match-name{font-weight:900;flex:1;overflow-wrap:anywhere}.match-score{font-size:20px;color:#d940a1;font-weight:900}
.score-big{font-size:42px;font-weight:900;color:#dc4aaf;text-align:center}
.note{font-size:12px;color:#4c428f;line-height:1.7}
@media(max-width:600px){.block-container{padding:.65rem .6rem 3rem!important}.game-shell{padding:11px 9px;box-shadow:4px 4px 0 #403778;margin:5px 3px 15px}.panel{padding:12px 9px;box-shadow:3px 3px 0 #544b9d}.brand{font-size:clamp(29px,9vw,48px)}.stButton>button{font-size:12px;min-height:42px;padding:6px 4px}.stButton>button[kind="primary"]{font-size:14px}.hearts{font-size:14px}.tiny-top{font-size:9px}.clouds{font-size:16px}.match-row{gap:7px;padding:9px 6px}.rank{font-size:17px;min-width:24px}.match-score{font-size:16px}}
</style>""", unsafe_allow_html=True)

@st.cache_resource
def local_db():
    con = sqlite3.connect(os.environ.get("MELO_DB", str(ROOT / "melody_demo.sqlite3")), check_same_thread=False)
    con.execute('CREATE TABLE IF NOT EXISTS submissions (nickname TEXT PRIMARY KEY, song_ids TEXT NOT NULL, delete_hash TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
    cols = {row[1] for row in con.execute("PRAGMA table_info(submissions)").fetchall()}
    if "delete_hash" not in cols:
        con.execute('ALTER TABLE submissions ADD COLUMN delete_hash TEXT')
    con.commit()
    return con

@st.cache_resource
def online_client():
    from supabase import create_client
    conf = st.secrets["supabase"]
    # Only use the *server-side* secret key from Streamlit Secrets.
    # The publishable key can no longer read/write submissions after hardening.
    return create_client(conf["url"], conf["service_key"])

try:
    conf = st.secrets.get("supabase")
except (FileNotFoundError, KeyError):
    conf = None

if conf and not conf.get("service_key"):
    st.error("🔐 보안 업그레이드 설정 중이야. Streamlit Secrets에 [supabase] service_key를 추가해 줘! 기존 key 값은 유지해도 돼.")
    st.stop()
try:
    CLIENT = online_client() if conf else None
except Exception:
    st.error("🔐 Supabase 서버 연결 설정을 확인해 줘. service_key는 이 채팅이나 GitHub에 공유하지 마!")
    st.stop()

@st.cache_resource
def activity_log():
    return {"lock":threading.Lock(), "events":{}}

def allowed_submission():
    # Basic server-side friction; not bot-proof, especially across restarts/replicas.
    state=activity_log()
    with state["lock"]:
        now=time.time()
        session=st.session_state.session_nonce
        times=[v for v in state["events"].get(session,[]) if now-v<3600]
        if times and now-times[-1]<30:
            return False, "연속 등록은 30초 뒤에 다시 시도해 줘!"
        if len(times)>=3:
            return False, "한 시간에 최대 3번만 등록할 수 있어. 잠시 뒤 다시 시도해 줘!"
        state["events"][session]=times+[now]
    return True, ""

def hash_code(code):
    return hashlib.sha256(code.strip().encode("utf-8")).hexdigest()

def load_people():
    if CLIENT:
        # Results are computed server-side; anonymous Supabase API roles cannot read this table.
        return CLIENT.table("submissions").select("nickname,song_ids").order("created_at",desc=True).limit(1000).execute().data or []
    records = local_db().execute("SELECT nickname,song_ids FROM submissions").fetchall()
    return [{"nickname": name, "song_ids": ids.split("|")} for name, ids in records]

def save_profile(name, song_ids):
    delete_code=secrets.token_urlsafe(18)
    token_hash=hash_code(delete_code)
    if CLIENT:
        selected=[BY_ID[sid] for sid in song_ids]
        CLIENT.table("submissions").insert({"nickname":name,"song_ids":song_ids,"genres":sorted({s["genre"] for s in selected}),"moods":sorted({s["mood"] for s in selected}),"delete_token_hash":token_hash}).execute()
    else:
        local_db().execute("INSERT INTO submissions(nickname,song_ids,delete_hash) VALUES (?,?,?)",(name,"|".join(song_ids),token_hash))
        local_db().commit()
    return delete_code

def delete_profile(name, code):
    if not name or not code:return False
    wanted_hash=hash_code(code)
    if CLIENT:
        result=CLIENT.table("submissions").delete().eq("nickname",name.strip()).eq("delete_token_hash",wanted_hash).execute()
        return bool(result.data)
    db=local_db()
    row=db.execute("SELECT 1 FROM submissions WHERE nickname=? AND delete_hash=?",(name.strip(),wanted_hash)).fetchone()
    if row:
        db.execute("DELETE FROM submissions WHERE nickname=? AND delete_hash=?",(name.strip(),wanted_hash))
        db.commit()
    return bool(row)

def go(stage):
    st.session_state.stage = stage
    st.rerun()

def banner(level, title, subtitle=""):
    st.markdown(f'''<div class="game-shell"><div class="tiny-top"><span>{html.escape(level)}</span><span class="hearts">♥ ♥ ♥</span></div><div class="game-title">{html.escape(title)}</div><div class="game-sub">{html.escape(subtitle)}</div><div class="clouds">☁ ✦ ♫ ✦ ☁</div></div>''',unsafe_allow_html=True)

def card(title, sub=""):
    st.markdown(f'<div class="panel"><div class="panel-title">{html.escape(title)}</div><div class="panel-sub">{html.escape(sub)}</div></div>',unsafe_allow_html=True)

for key, default in [("stage","start"),("identity",""),("picked",[]),("category","전체"),("page",1),("detail",None),("delete_code",""),("session_nonce",secrets.token_hex(12))]:
    if key not in st.session_state:
        st.session_state[key] = default

if st.session_state.stage == "start":
    st.markdown('''<div class="game-shell"><div class="tiny-top"><span>HI-SCORE<br>20261022</span><span class="hearts">♥ ♥ ♥</span></div><div style="text-align:center;margin:25px 0 0;font-size:33px">🎧 ✦ 🎵</div><div class="brand pixel">MELODY ♫</div><div class="game-sub">FIND YOUR MUSIC MATE !</div><div class="clouds">☁ ♡ ☁ ♫ ☁</div></div>''',unsafe_allow_html=True)
    if st.button("▶ START GAME", type="primary", use_container_width=True):go("profile")
    st.caption("♫ 좋아하는 노래로 나와 취향이 닮은 친구를 찾아봐!")
    with st.expander("🔐 내 참여 기록 삭제하기"):
        st.caption("등록할 때 받은 삭제 코드를 사용하면 내 음악 취향 기록을 삭제할 수 있어.")
        del_name=st.text_input("등록했던 닉네임 또는 인스타 아이디",key="delete_name",max_chars=20)
        del_code=st.text_input("삭제 코드",key="delete_input",type="password")
        if st.button("내 기록 삭제",key="delete_btn",use_container_width=True):
            try:
                if delete_profile(del_name,del_code):st.success("내 기록이 삭제됐어! 🎉")
                else:st.warning("일치하는 기록이 없어. 닉네임과 삭제 코드를 확인해 줘.")
            except Exception:st.error("삭제에 실패했어. 앱 관리자에게 문의해 줘.")
    st.stop()

if st.session_state.stage == "profile":
    banner("LEVEL 01 · PLAYER PROFILE","PLAYER PROFILE","♡ 너를 뭐라고 부를까? ♡")
    card("닉네임 또는 인스타그램 아이디", "다른 친구들에게 표시될 이름을 입력해 줘!")
    name=st.text_input("인스타 아이디 또는 닉네임", value=st.session_state.identity, max_chars=20, placeholder="예: @music_lover 또는 music_lover")
    st.caption("닉네임만 입력해도 돼! 인스타 아이디가 아니면 매칭된 친구가 연락하기 어려울 수 있어.")
    st.info("🔐 참여 안내: 입력한 닉네임 또는 인스타 아이디, 선택한 노래와 음악 취향이 다른 참여자에게 매칭 목적으로 표시돼. 연락처·실명·비밀번호는 입력하지 마! 기록은 발급받는 삭제 코드로 지울 수 있어.")
    consent=st.checkbox("내 입력 정보가 다른 참여자에게 표시되는 것에 동의해.",key="consent")
    if st.button("NEXT LEVEL ➜",type="primary",use_container_width=True):
        if len(name.strip())<2:st.warning("2글자 이상 입력해 줘!")
        elif not consent:st.warning("참여 안내를 확인하고 동의해 줘!")
        else:st.session_state.identity=name.strip();go("songs")
    if st.button("← BACK",use_container_width=True):go("start")
    st.stop()

if st.session_state.stage == "songs":
    banner("LEVEL 02 · MUSIC SELECT","MUSIC SELECT","좋아하는 노래를 5~15곡 골라줘!")
    st.markdown(f'<div class="step">♪ PLAYER: {html.escape(st.session_state.identity)}　　♥ {len(st.session_state.picked)}/15</div>',unsafe_allow_html=True)
    # Category buttons are intentionally short and responsive.
    cat_names=CATEGORIES
    for start_idx in range(0,len(cat_names),3):
        chunk=cat_names[start_idx:start_idx+3]
        cols=st.columns(len(chunk))
        for col, cat in zip(cols,chunk):
            with col:
                if st.button(("♥ " if cat==st.session_state.category else "")+cat,key="genre_"+cat,use_container_width=True):
                    st.session_state.category=cat;st.session_state.page=1;st.rerun()
    filtered=[s for s in SONGS if st.session_state.category=="전체" or s["category"]==st.session_state.category]
    pages=max(1,(len(filtered)+9)//10)
    st.session_state.page=min(st.session_state.page,pages)
    page=st.session_state.page
    st.markdown(f'<div class="panel-title">♫ SONG LIST · {html.escape(st.session_state.category)} <span style="font-size:13px">({len(filtered)}곡)</span></div>',unsafe_allow_html=True)
    for i,song in enumerate(filtered[(page-1)*10:page*10],(page-1)*10+1):
        sid=song["id"]
        selected=sid in st.session_state.picked
        label=f'{i:02d}.  {song["title"]} — {song["artist"]}'
        # No direct post-widget session_state mutation; this avoids Streamlit widget state errors.
        checked=st.checkbox(label,value=selected,key=f"choose_{sid}_{'yes' if selected else 'no'}")
        if checked!=selected:
            if checked:
                if len(st.session_state.picked)>=15:
                    st.warning("최대 15곡까지 선택할 수 있어!")
                else:st.session_state.picked.append(sid)
            else:st.session_state.picked.remove(sid)
            st.rerun()
    st.caption(f"PAGE {page} / {pages}")
    window_start=max(1,min(page-2,pages-4))
    window=list(range(window_start,min(pages,window_start+4)+1))
    cols=st.columns(len(window)+2)
    if cols[0].button("◀",key="page_prev",disabled=page==1):st.session_state.page=page-1;st.rerun()
    for col,num in zip(cols[1:-1],window):
        if col.button(str(num),key=f"page_num_{num}",type="primary" if num==page else "secondary"):
            st.session_state.page=num;st.rerun()
    if cols[-1].button("▶",key="page_next",disabled=page==pages):st.session_state.page=page+1;st.rerun()
    with st.expander(f"💗 MY PLAYLIST · {len(st.session_state.picked)}/15",expanded=False):
        if not st.session_state.picked:st.caption("아직 선택한 노래가 없어!")
        for sid in st.session_state.picked:
            s=BY_ID[sid];st.write(f"♫ {s['title']} — {s['artist']}")
        if st.button("선택 초기화",key="reset_songs"):
            st.session_state.picked=[];st.rerun()
    if st.button("♫ 나와 맞는 친구 찾기 ➜",type="primary",use_container_width=True):
        if not 5<=len(st.session_state.picked)<=15:
            st.warning("노래를 5~15곡 선택해야 해!")
        else:
            try:
                ok,why=allowed_submission()
                if not ok:
                    st.warning(why)
                else:
                    st.session_state.delete_code=save_profile(st.session_state.identity,st.session_state.picked)
                    go("saved")
            except Exception as err:
                # Show only non-sensitive diagnostics. Never render the raw exception,
                # because it can contain account data or API URLs.
                error_type = type(err).__name__
                status = getattr(err, "code", None)
                st.error(f"저장 실패 · 오류 종류: {error_type}" + (f" · 코드: {status}" if status is not None and str(status).isalnum() else ""))
                st.caption("이 문구만 캡처해서 보내줘. API 키와 개인정보는 보내지 마!")
                if error_type in ("APIError", "PostgrestException"):
                    st.info("DB 요청이 거절됐어. 연결 키의 종류, 테이블 권한 또는 중복 닉네임을 확인해야 해.")
    if st.button("← 프로필로",use_container_width=True):go("profile")
    st.stop()


if st.session_state.stage == "saved":
    banner("SAVE COMPLETE","PROFILE SAVED!","💗 너의 음악 취향이 저장됐어!")
    st.success("등록 완료! 아래 삭제 코드를 꼭 보관해 줘.")
    st.warning("🔐 삭제 코드는 이 화면을 벗어나면 다시 발급받을 수 없어. 다른 친구에게 보여주지 마!")
    st.code(st.session_state.delete_code,language=None)
    st.caption("나중에 메인 화면의 '내 참여 기록 삭제하기'에서 닉네임과 이 코드로 삭제할 수 있어.")
    if st.button("코드 저장했어! ♥ 친구 TOP 10 보기 →",type="primary",use_container_width=True):
        st.session_state.delete_code=""
        go("results")
    st.stop()

if st.session_state.stage in ("results","detail"):
    try:
        people=load_people()
        me=next((p for p in people if p["nickname"]==st.session_state.identity),None)
    except Exception:
        people=[];me=None;st.error("친구 목록을 불러오지 못했어. 잠시 후 다시 시도해 줘!")
    if me:
        features=feature_sets(me["song_ids"],SONGS)
        ranked=[]
        for person in people:
            if person["nickname"]==me["nickname"]:continue
            result=compare(features,feature_sets(person["song_ids"],SONGS))
            ranked.append((person["nickname"],result))
        ranked.sort(key=lambda item:item[1]["score"],reverse=True)
    else:ranked=[]

    if st.session_state.stage=="results":
        banner("RESULT · LEVEL 03","MUSIC MATE TOP 10","너와 음악 취향이 비슷한 친구들이야!")
        if not CLIENT:st.info("🧪 지금은 로컬 체험 모드야. 다른 휴대폰 친구와 매칭하려면 Supabase 연결이 필요해!")
        if not me:st.warning("먼저 노래를 등록해 줘!")
        elif not ranked:st.info("아직 다른 참가자가 없어! 친구들이 노래를 등록하면 여기에 순위가 나와.")
        for idx,(name,result) in enumerate(ranked[:10],1):
            symbol="👑" if idx==1 else ("🥈" if idx==2 else ("🥉" if idx==3 else "♫"))
            st.markdown(f'<div class="match-row"><div class="rank">{symbol}</div><div class="match-name">{idx}위　{html.escape(name)}</div><div class="match-score">♥ {result["score"]*100:.0f}%</div></div>',unsafe_allow_html=True)
            if st.button(f"{idx}위 {name} · 공통 노래 보기 →",key=f"detail_{idx}",use_container_width=True):
                st.session_state.detail=name;go("detail")
        if st.button("♫ 다시 노래 선택하기",use_container_width=True):go("songs")
        st.caption("🔐 참여 기록을 지우고 싶다면 처음 화면의 '내 참여 기록 삭제하기'를 눌러 줘.")
        if st.button("⌂ 처음으로",use_container_width=True):
            st.session_state.identity="";st.session_state.picked=[];go("start")
        with st.expander("🎮 HOW IT WORKS · 집합과 명제"):
            st.latex(r"J(A,B)=\frac{|A\cap B|}{|A\cup B|}")
            st.write("선택한 노래·장르·분위기·템포 집합의 교집합과 합집합으로 자카드 유사도를 계산해. 노래 35%, 장르 25%, 분위기 25%, 템포 15%를 반영해!")
        st.stop()

    if st.session_state.stage=="detail":
        name=st.session_state.detail
        found=next(((n,r) for n,r in ranked if n==name),None)
        banner("MATCH DETAIL","OUR MUSIC MATCH","공통 취향을 확인해 봐!")
        if found:
            _,result=found
            st.markdown(f'<div class="panel"><div class="panel-title">♥ {html.escape(name)}</div><div class="score-big">{result["score"]*100:.0f}%</div><div class="panel-sub">음악 취향 유사도</div></div>',unsafe_allow_html=True)
            st.progress(min(1.,max(0.,result["score"])))
            common=result["common"]
            st.subheader("💗 우리의 공통 노래")
            song_ids=common["songs"]
            if song_ids:
                for sid in song_ids:
                    if sid in BY_ID:st.markdown(f"♫ **{BY_ID[sid]['title']}** — {BY_ID[sid]['artist']}")
            else:st.info("같이 선택한 노래는 아직 없지만 장르나 분위기가 비슷할 수 있어!")
            st.write("**🎧 공통 장르:** "+(", ".join(common["genres"]) or "없음"))
            st.write("**✨ 공통 분위기:** "+(", ".join(common["moods"]) or "없음"))
            with st.expander("집합 계산 자세히 보기"):
                other=next(p for p in people if p["nickname"]==name)
                their=feature_sets(other["song_ids"],SONGS)
                for key,label in [("songs","노래"),("genres","장르"),("moods","분위기"),("tempos","템포")]:
                    st.write(f"{label}: 교집합 {len(features[key]&their[key])}개 / 합집합 {len(features[key]|their[key])}개 / J={result['parts'][key]:.3f}")
            st.caption("표시된 아이디가 실제 인스타 계정인지 검증하지는 않아. 개인정보를 주고받을 때는 주의해 줘!")
        else:st.warning("선택한 친구를 찾을 수 없어.")
        if st.button("← 친구 순위표로 돌아가기",type="primary",use_container_width=True):go("results")
        st.stop()
