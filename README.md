# apt-alarm :: 관심 부동산 알람

slack 메시지로 관심있는 아파트 단지의 매물 정보를 받아볼 수 있는 프로그램입니다.
슬랙 계정이 필요합니다.

## 실행

1. download [chromedriver](https://chromedriver.chromium.org/downloads) for scraping
   - check version
   - put it in apt-alarm/driver/
2. mongodb 설치
3. docker 실행
   ```
   $ bash /docker/build_and_run_docker.sh
   ```
4. webrowser 접속
   home : http://localhost:8000/
   1. 정확한 '동'명 검색
      ex.
      - 서초구 양재동
      - 영통구 하동
   2. 동네별 아파트 단지 중 알림을 원하는 단지 입력
   3. mypage에서 알림 취소 / 조건 설정
5. crontab 설정
   - 매일 설정한 시간에 알림 원하는 단지의 정보 제공
   - 새로운 매물 정보는 1시간에 1번 알림
   - [크론탭 설정 방법](documents/crontab.md) 참고
