# apt-alarm :: 관심 부동산 알람

slack 메시지로 관심있는 아파트 단지의 매물 정보를 받아볼 수 있는 프로그램입니다.
슬랙 계정과 채널이 필요합니다.

## 실행

1. docker 실행
   - docker-compose.yaml 에 YOUR_CHANNEL, YOUR_TOKEN을 자신의 정보로 입력
   - docker build & run
   ```
   $ docker-compose up --build
   ```
2. webrowser 접속
   home : http://localhost:8000/

   1. 정확한 '동'명 검색
      ex.
      - 서초구 양재동
      - 영통구 하동
   2. 동네별 아파트 단지 중 알림을 원하는 단지 추가
      ![](documents/img/home.png)

   3. mypage에서 알림 취소 / 조건 설정(#TODO)
      ![](documents/img/mypage.png)

3. crontab 설정

   - 매일 설정한 시간에 알림 원하는 단지의 정보 제공
   - 새로운 매물 정보는 1시간에 1번 알림
   - [크론탭 설정 방법](documents/crontab.md) 참고
     ![](documents/img/slack.png)

4. api docs 확인가능
   swagger : http://localhost:8000/docs#/
   ![](documents/img/swagger.png)
