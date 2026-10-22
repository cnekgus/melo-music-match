# MELODY ♫ — 픽셀 게임 스타일 음악 친구 매칭 앱

## 업데이트 방법 (GitHub + Streamlit)

이 폴더 안의 **파일들 자체**를 GitHub 저장소 `cnekgus/melo-music-match`의 최상위(root)에 업로드하세요. `MELODY_PIXEL_GAME` 폴더 전체를 올리면 `app.py` 경로가 바뀌므로 주의하세요.

필수 파일: `app.py`, `matching.py`, `songs.csv`, `requirements.txt`, `supabase_setup.sql`.

1. GitHub 저장소 → Add file → Upload files.
2. 위 파일들을 선택하여 업로드합니다. 이름이 같은 기존 파일을 교체합니다.
3. Commit changes를 누릅니다.
4. 기존 Streamlit 앱 페이지를 새로고침합니다. 앱 진입점은 `app.py`입니다.

## 화면 구성

START GAME → 닉네임/인스타 아이디 → 장르별 음악 선택(5~15곡, 페이지당 10곡) → **나와 맞는 친구 찾기** → 실제 등록 사용자 기준 TOP 10 → 상세 공통 노래/장르/분위기.

기존 `matching.py`의 자카드 유사도 가중치 계산을 그대로 사용합니다. 테스트용 가짜 친구는 표시하지 않습니다.

## 온라인 데이터베이스

Streamlit Community Cloud → 앱 Settings → Secrets에서 다음 형식으로 연결합니다:

```toml
[supabase]
url = "https://YOUR_PROJECT.supabase.co"
key = "YOUR_PUBLISHABLE_OR_ANON_KEY"
```

Supabase SQL Editor에서 `supabase_setup.sql`을 실행해야 합니다. **서비스 역할 키(service_role)는 절대 넣지 마세요.** 이 프로젝트의 SQL 정책은 교육용 데모이므로 실제 공개 전에 인증, 데이터 삭제, 개인정보 동의 및 접근 제어를 보완하세요. 로그인 없는 공개 닉네임은 다른 사람이 동일한 이름으로 등록을 시도할 수 있으며, 기존 이름 수정은 지원하지 않습니다.

로컬 체험 모드는 서버의 SQLite를 사용하므로 여러 기기의 데이터를 안정적으로 공유하지 못합니다.
