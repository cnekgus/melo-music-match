# melo 웹앱 실행 안내

## 로컬 실행 (PC)
1. Python 3.10 이상 설치
2. 이 폴더에서 `pip install -r requirements.txt`
3. `streamlit run app.py`
4. 브라우저에 표시된 주소로 접속

Supabase 없이 실행하면 로컬 SQLite 체험 모드가 활성화됩니다. 이 데이터는 실행하는 컴퓨터에 저장되며, 여러 사람이 각자의 휴대폰으로 함께 접속하는 공개 서비스가 아닙니다.

## 학생들과 함께 쓰는 온라인 앱
1. Supabase 프로젝트를 만들고 `supabase_setup.sql`을 실행합니다.
2. Streamlit Community Cloud에 GitHub 저장소를 배포합니다.
3. 앱의 Secrets에 다음을 등록합니다.

```
[supabase]
url = "https://YOUR_PROJECT.supabase.co"
key = "YOUR_ANON_KEY"
```

4. 온라인 데이터 저장과 매칭 기능이 동작합니다. **온라인 연결 요청은 현재 비활성화**되어 있습니다. 실제 연락 기능은 인증과 요청 수락, 접근 제어를 추가한 뒤 사용하세요.

## 주의
- 학생 실명, 연락처, 비밀번호는 입력받지 않습니다.
- 학생 대상 설문 전 참여 동의와 데이터 공개 범위를 안내하세요.
- 노래 특징은 초기 분류이므로 조사 전에 검수하세요.
