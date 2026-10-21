# melo — 음악 취향 매칭 웹 앱

이 프로젝트는 Streamlit(화면) + Supabase(온라인 데이터베이스)를 사용하는 시범 앱입니다.
배포하면 휴대폰 브라우저에서 링크로 접속할 수 있습니다.

## 파일
- `app.py`: 웹 앱 코드
- `requirements.txt`: 설치할 파이썬 패키지
- `supabase_setup.sql`: 온라인 데이터베이스 테이블과 권한 설정

## 1. 노래 목록 바꾸기
`app.py` 맨 위의 `SONGS` 목록을 실제 노래로 바꾸세요.
각 노래는 `id`, `title`, `artist`, `genre`, `mood`를 가져야 합니다.
- `id`: 노래마다 고유한 영문 ID (예: `song_001`)
- `genre`: 발라드, 팝, R&B 등
- `mood`: 잔잔함, 밝음, 감성적 등
한 번 설문이 저장된 뒤에는 기존 노래 ID를 바꾸지 않는 편이 좋습니다.

## 2. Supabase 설정
1. https://supabase.com 에서 프로젝트를 만듭니다.
2. 대시보드의 SQL Editor를 엽니다.
3. `supabase_setup.sql`의 내용을 붙여 넣고 실행합니다.
4. 프로젝트의 Connect/API 설정에서 Project URL과 Publishable key를 찾습니다.
   - 새 프로젝트에서는 `sb_publishable_...` 형태의 Publishable key를 사용할 수 있습니다.
   - `service_role` 또는 `sb_secret_...` 키는 절대 사용하지 마세요.
5. 아래 값은 Streamlit Cloud의 App settings → Secrets에 넣습니다.

```toml
[supabase]
url = "https://YOUR_PROJECT.supabase.co"
key = "YOUR_SUPABASE_PUBLISHABLE_KEY"
```

## 3. GitHub에 업로드
1. GitHub 계정으로 새 저장소(repository)를 만듭니다.
2. `app.py`, `requirements.txt`, `supabase_setup.sql`, `README.md`를 업로드합니다.
3. Supabase 키를 GitHub 파일에 넣지 마세요.

## 4. Streamlit Community Cloud 배포
1. https://share.streamlit.io 에서 GitHub로 로그인합니다.
2. Create app을 선택하고 방금 만든 저장소와 `app.py`를 지정합니다.
3. Advanced settings 또는 Secrets 설정에 위 TOML 값을 입력합니다.
4. Deploy를 누르면 공유 가능한 `streamlit.app` 링크가 생성됩니다.

## 중요: 개인정보와 공개 범위
이 데모는 로그인 없이 사용하며 닉네임과 선택한 노래/장르/분위기를 참여자끼리 읽을 수 있게 설계되어 있습니다. 누구나 닉네임을 선점할 수 있고, 중복 닉네임은 거부됩니다. 친구들의 동의를 받고 익명 닉네임만 사용하세요. 실명, 연락처, 학교/학급 등 개인정보는 입력하지 마세요. 실제 서비스로 운영하려면 인증과 더 엄격한 데이터 접근 정책이 필요합니다.

## 수학 탐구
자카드 유사도 `|A ∩ B| / |A ∪ B|`를 노래 집합, 장르 집합, 분위기 집합에 각각 적용합니다.
최종 점수는 공통 노래 50%, 장르 30%, 분위기 20%로 계산합니다. 이 가중치는 탐구용 선택이므로 다른 비율과 결과를 비교할 수 있습니다.


## v4 목록 업데이트
- `songs.csv`: 325곡(학생 직접 선정 50곡, 추가 후보 275곡). 해외 팝은 직접 선정 10곡만 유지.
- `source` 열로 학생 선정곡 구분. 노래 제목/가수/분류를 수업 전에 검수할 것.
- 장르/분위기/템포는 임시 태그로 실제 오디오 분석 결과가 아님.
- 앱에서는 검색/장르 필터/30곡 단위 페이지를 지원하며 5~15곡을 선택.
- 기존 Supabase 테이블을 사용했다면 기존 check 제약조건을 5~15로 수정해야 함. SQL 파일을 재실행하는 것만으로 기존 check가 변경되지는 않음.
