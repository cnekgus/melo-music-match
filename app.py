"""melo — music taste matching student project."""
import csv
import os
import sqlite3
from pathlib import Path

import streamlit as st
from matching import compare, feature_sets

ROOT = Path(__file__).resolve().parent
with (ROOT / 'songs.csv').open(encoding='utf-8-sig', newline='') as f:
    SONGS = list(csv.DictReader(f))
SONG_BY_ID = {s['id']: s for s in SONGS}

st.set_page_config(page_title='melo | Find your music people', page_icon='🎧', layout='centered')
st.markdown('''<style>
.stApp {background:#101522;color:#f5f7fb} .block-container{max-width:830px;padding-top:1.7rem}
h1,h2,h3{letter-spacing:-.04em} .hero{padding:24px 25px;border-radius:24px;background:linear-gradient(125deg,#1b2a35,#172033);border:1px solid #354451;margin-bottom:22px}
.brand{font-size:35px;font-weight:900;color:#a9f1ce}.sub{color:#b7c4d2;font-size:13px;letter-spacing:2px}
[data-testid="stMetric"]{border:1px solid #354451;border-radius:15px;padding:12px;background:#1c2532}
div.stButton>button[kind="primary"]{background:#a9f1ce;color:#10201b;border:0;border-radius:12px;font-weight:800}
</style>''',unsafe_allow_html=True)

# Streamlit Community Cloud persistent storage should use Supabase.
# SQLite is for a single-computer demonstration only.
@st.cache_resource
def db():
    path = os.environ.get('MELO_DB', str(ROOT / 'melo_demo.sqlite3'))
    con = sqlite3.connect(path, check_same_thread=False)
    con.execute('CREATE TABLE IF NOT EXISTS submissions (nickname TEXT PRIMARY KEY, song_ids TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
    con.execute('CREATE TABLE IF NOT EXISTS contact_requests (sender TEXT NOT NULL, receiver TEXT NOT NULL, status TEXT DEFAULT "pending", PRIMARY KEY(sender,receiver))')
    con.commit()
    return con

def supabase_client():
    try:
        from supabase import create_client
        cfg=st.secrets['supabase']
        return create_client(cfg['url'],cfg['key'])
    except (KeyError, FileNotFoundError, AttributeError):
        return None

client=supabase_client()

def rows():
    if client:
        return client.table('submissions').select('nickname,song_ids').execute().data or []
    data=db().execute('SELECT nickname,song_ids FROM submissions').fetchall()
    return [{'nickname':n,'song_ids':ids.split('|')} for n,ids in data]

def save(nickname,ids):
    if client:
        chosen=[SONG_BY_ID[x] for x in ids]
        client.table('submissions').insert({'nickname':nickname,'song_ids':ids,'genres':sorted({s['genre'] for s in chosen}),'moods':sorted({s['mood'] for s in chosen})}).execute()
    else:
        db().execute('INSERT INTO submissions(nickname,song_ids) VALUES (?,?)',(nickname,'|'.join(ids)))
        db().commit()

st.markdown('<div class="hero"><div class="brand">melo ♫</div><div class="sub">FIND YOUR MUSIC PEOPLE</div><h2>너의 취향을 들려줘.</h2><p>좋아하는 노래로 연결되는 우리 학교 음악 친구들</p></div>',unsafe_allow_html=True)
if client is None:
    st.info('🧪 현재 로컬 체험 모드입니다. 같은 컴퓨터에서는 데이터가 저장됩니다. 여러 휴대폰에서 함께 사용하려면 Supabase 연결 후 온라인 배포가 필요합니다.')

survey,match,math_tab=st.tabs(['🎵 취향 등록','💚 친구 찾기','📐 수학 원리'])
with survey:
    st.subheader('01 · 나의 취향 등록')
    nickname=st.text_input('익명 닉네임 (실명 사용하지 않기)',max_chars=20,placeholder='예: mintwave')
    genres=['전체']+sorted({s['category'] for s in SONGS})
    category=st.selectbox('장르',genres)
    query=st.text_input('노래 검색',placeholder='제목 또는 가수 이름')
    if 'picked' not in st.session_state: st.session_state.picked=[]
    shown=[s for s in SONGS if (category=='전체' or s['category']==category) and (not query or query.casefold() in (s['title']+' '+s['artist']).casefold())]
    st.caption(f'전체 {len(SONGS)}곡 · 검색 결과 {len(shown)}곡 · 5~15곡 선택')
    page_count=max(1,(len(shown)+24)//25)
    page=st.number_input('페이지',min_value=1,max_value=page_count,value=1,step=1)
    for s in shown[(page-1)*25:page*25]:
        sid=s['id']
        checked=st.checkbox(f"{s['title']} — {s['artist']}",value=sid in st.session_state.picked,key='song_'+sid)
        if checked and sid not in st.session_state.picked: st.session_state.picked.append(sid)
        if not checked and sid in st.session_state.picked: st.session_state.picked.remove(sid)
    st.markdown(f'**선택한 곡: {len(st.session_state.picked)} / 15**')
    if st.session_state.picked:
        for sid in st.session_state.picked:
            s=SONG_BY_ID[sid]
            st.caption(f"• {s['title']} — {s['artist']}")
        if st.button('선택 초기화'):
            st.session_state.picked=[]
            for s in SONGS: st.session_state.pop('song_'+s['id'],None)
            st.rerun()
    if st.button('내 음악 취향 등록하기 →',type='primary',use_container_width=True):
        if len(nickname.strip())<2: st.error('닉네임을 2글자 이상 입력해 주세요.')
        elif not 5<=len(st.session_state.picked)<=15: st.error('노래를 5~15곡 선택해 주세요.')
        else:
            try:
                save(nickname.strip(),st.session_state.picked)
                st.success('등록 완료! 💚 친구 찾기 탭에서 확인해 보세요.')
            except Exception:
                st.error('등록 실패: 이미 존재하는 닉네임이거나 데이터베이스 연결에 문제가 있습니다.')

with match:
    st.subheader('02 · 음악 취향이 닮은 친구')
    try: people=rows()
    except Exception: people=[];st.error('저장된 참여자 정보를 읽지 못했습니다.')
    if len(people)<2:
        st.info('매칭하려면 최소 2명의 참여자가 등록해야 해요.')
    else:
        who=st.selectbox('내 닉네임 선택',[p['nickname'] for p in people])
        threshold=st.slider('최소 매칭 유사도',0,100,30,5)
        me=next(p for p in people if p['nickname']==who)
        a=feature_sets(me['song_ids'],SONGS)
        candidates=[]
        for p in people:
            if p['nickname']==who:continue
            result=compare(a,feature_sets(p['song_ids'],SONGS))
            candidates.append((p['nickname'],result))
        candidates.sort(key=lambda x:x[1]['score'],reverse=True)
        visible=[x for x in candidates if x[1]['score']*100>=threshold]
        if not visible:st.info('이 기준을 넘는 친구가 없어요. 유사도 기준을 낮춰보세요.')
        for rank,(name,result) in enumerate(visible,1):
            with st.container(border=True):
                st.markdown(f'### {rank}. 🎧 {name}')
                st.metric('취향 유사도',f"{result['score']*100:.1f}%")
                st.progress(result['score'])
                common=result['common']
                st.write('**공통 노래:** '+(', '.join(SONG_BY_ID[i]['title'] for i in common['songs'] if i in SONG_BY_ID) or '없음'))
                st.write('**공통 장르:** '+(', '.join(common['genres']) or '없음'))
                st.write('**공통 분위기:** '+(', '.join(common['moods']) or '없음'))
                with st.expander('교집합·합집합 계산 보기'):
                    b=feature_sets(next(p['song_ids'] for p in people if p['nickname']==name),SONGS)
                    for k,label in [('songs','노래'),('genres','장르'),('moods','분위기'),('tempos','템포')]:
                        st.write(f"{label}: |A∩B|={len(a[k]&b[k])}, |A∪B|={len(a[k]|b[k])}, J={result['parts'][k]:.3f}")
                    st.write('총점 = 0.35×노래 + 0.25×장르 + 0.25×분위기 + 0.15×템포')
                    st.write(f"명제 '유사도 ≥ {threshold}%' → 참")
                if client is None:
                    if st.button(f'{name}에게 연결 요청하기',key='req_'+name):
                        db().execute('INSERT OR IGNORE INTO contact_requests(sender,receiver) VALUES (?,?)',(who,name));db().commit()
                        st.success('연결 요청을 보냈어요. 상대방이 수락해야 연결됩니다.')
        if client is None:
            st.divider()
            st.subheader('💌 받은 연결 요청 (로컬 체험)')
            requests=db().execute('SELECT sender,status FROM contact_requests WHERE receiver=?',(who,)).fetchall()
            if not requests:st.caption('아직 받은 요청이 없어요.')
            for sender,status in requests:
                c1,c2=st.columns([3,2]);c1.write(f'{sender} · {"수락됨" if status=="accepted" else "대기 중"}')
                if status=='pending' and c2.button('수락',key='accept_'+sender):
                    db().execute('UPDATE contact_requests SET status="accepted" WHERE sender=? AND receiver=?',(sender,who));db().commit();st.rerun()
            st.caption('연락처를 공개하지 않는 익명 연결 시연입니다. 실제 채팅·신원 확인 기능은 아직 없습니다.')
        else:
            st.caption('온라인 모드의 연결 요청 기능은 인증·권한 정책 구현 후 활성화됩니다.')

with math_tab:
    st.subheader('집합과 명제로 만든 매칭 알고리즘')
    st.latex(r'J(A,B)=\frac{|A\cap B|}{|A\cup B|')
    st.write('선택한 노래들의 장르·분위기·템포를 각각 집합으로 바꾼 뒤 자카드 유사도를 계산합니다.')
    st.latex(r'S=0.35J_{song}+0.25J_{genre}+0.25J_{mood}+0.15J_{tempo}')
    st.write('매칭 조건은 명제 P: S ≥ 설정한 기준값으로 정의합니다.')
    st.warning('노래별 분위기·템포는 초기 수작업 분류이며, 실제 음원 분석 AI의 결과가 아닙니다. 실험 전 검수가 필요합니다.')
    st.caption('동일 닉네임 중복 방지 수준의 시범 앱입니다. 실제 학생 대상 공개 전에는 사용자 인증, 동의 및 개인정보 보호 설정을 추가해야 합니다.')
