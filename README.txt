Ai-Builder 에 파이썬 앱을 만든다.
파이썬 3.11.9 64비트이다.
pyside6을 이용한다.
pyside6 의 designer 로 직접 수정할 수 있도록 ui 파일을 만들고 이것을 컨버트해서 py 파일 만들고 이것을 메인쓰레드에서 호출 하는 방식으로 해라.
뷰는 메인, 설정 2개다.

코드 폴더의 기본형태는
sigma_agent 참고해라.
src/conf/nnconf/nnconfig.py, nnlogger.py 이것은 똑같이 넣어라.

sigma_agent 에서 build.bat 로 한번에 빌드하는것처럼 Ai-Builder 에도 동일하게 해라.

sigma_agent 를 참고하되, 가장 글로벌 표준에 부합하는 폴더 구조로 해라.

==========================


설정 뷰
시그마차트 API
검색하기
검색하기를 클릭하면 해당 대역 아이피의 x.x.x.0~x.x.x.255 에 health 체크해서 응답하는 서버 ip를 이 프로젝트에 저장한다.
다음번에 이 프로그램 실행시 최초에 이 ip가 있으면 헬스체크한다.
연결이 끊겨있으면 설정뷰, 메인뷰 모두 "연결끊김" 아이콘을 보여줘라.
API 키 : [   ] 저장 아이콘
저장을 클릭하면 해당 api로 뭔가 던져서 응답이 정상이면 "정상" 이라고 표시하고 응답이 정상이 아니면 api 키 값이 올바르지 않습니다.
보여줘라.

제미나이
제미나인 구글 AI Studio로 이동하기(https://aistudio.google.com/api-keys?hl=ko)
API 키  :  [    ] [저장] 아이콘


GTP
OpenAI AI플랫폼 이동하기(https://platform.openai.com/settings/organization/api-keys) 
SECRET KEY : [    ] 저장 아이콘

==========================

메인뷰
날짜 선택 필드 [목록조회]
목록조회를 클릭하면 해당일의 진료를 한 환자의 목록을 sigma_server api(이하 ) 로 가져온다.
조회한 목록을 리스트로 보여준다.

목록중의 하나를 클릭하고 [조회] 를 클릭하면 
오른쪽에 encounter.plain_note 를 보여줘라.



프롬프트
프롬프트의 제목, 내용, 날짜를 저장하는 것을 만들거다.
제목들을 리스트로 보여주고 그것을 클릭하면 오른쪽에 내용이 나온다.
"신규"를 클릭하면 "제목" "내용"을 새로 만들기해서 저장 가능하고
기존 프롬프트를 선택 후 "수정" 을 클릭하면 "내용" 부분을 수정 가능하게 하고
"삭제"를 클릭하면 "삭제할까요?"물어보고 삭제하게 해라.
"순서"를 내가 원하는 순서대로 정렬할 수 있게 해라.
이 부분은 파이썬 puside6 ui의 가장 글로벌 표준 방식으로 해라.
순서를 마우스 드래그로 해도 되고, 버튼으로 위, 아래 이동하게 해도 된다.

선택한 AI Agent 가 콤보박스로 선택할 수 있게 하고, 제미나이와 GTP 중에서 api 키가 있는 것만 콤보박스로 나오게 해라.
콤보박스 선택을 변경하면 다음번에 다시 실행했을 때 동일한 것이 선택되어 있게 해당 부분 즉시 저장해라.

encounter.plain_note 가 있는 상태에서 [Enhance] 버튼을 클릭하면
AI 에이전트를 선택하고, AI API 키가 있고, sigma api 키가 있고, sigma_server 헬쓰가 정상인지 확인 후
정상이면 plain_note 를 프롬프트를 이용해서 api 한 후 결과를 텍스트박스에 보여줘라.
[시그마차트에 저장] 을 클릭하면 sigma api 의 EncounterExternalData.external_data 에 그 결과를 저장해라.


===================
아래 링크에서 open ai 프롬프트 api 연결하는 설명서 있다.
https://developers.openai.com/api/docs/quickstart

https://developers.openai.com/api/docs/guides/latest-model#prompting-guidance


====================

여기까지 개발할거다. 이것을 개발하기 위한 문서를 아주 꼼꼼하게 만들어라. 잘 모르겠는 부분은 물어봐라.