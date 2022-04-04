# 림펫 ( Limn pet )

- Limn = to draw or paint on a surface
- 반려동물의 사진을 그림 또는 카툰 형식의 캐릭터로 변환하여 제공하는 것
- 변환된 캐릭터를 커스터마이징 굿즈로 구매하는 것
  - 림펫에서 캐릭터화를 시킨 후 커스터마이징 굿즈를 제작하는 사업자와 연결시켜주는 방법
  - 이후 앱 이용을 통해 중개가 잘 이루어지면, 림펫 자체적으로 굿즈 제각하여 판매


## TEAM

- 김한주 - Leader
- 성연재- Co-Leader
- 송종호
- 정영훈
- 김민지

### Goal

- 가족중 하나인 나의 반려동물만을 위한 카툰/그림 형식의 캐릭터 생성 
- 생성된 캐릭터를 SNS에 공유하여 소셜네트워크에 나의 가족인 반려동물 소개
-  높은 비용과 오랜 제작기간이 필요한 수작업 반려동물 굿즈의 문제점을 해결
  - 전문가의 작업이 필요했던 반려동물 캐릭터화 또는 그림을 자동하여 비용과 시간을 절약
  - 생성된 이미지를 커스터마이징 굿즈 제작 업체에 제공하여 손쉽게 나만의 굿즈 구매
-  반려동물과 커스터마이징 업체 중개를 통해 **반려동물 관련 새로운 시장 및 문화를 형성하고자 함** 

---

#### 1st. iteration

- goal 1

  - 반려견 사진 카툰화

    - 사진입력/제거 기능 구현
    - CartoonGAN 모델 이용하려 사진을 Cartoon화
    - return 이미지를 웹과 앱상에 post

    

- goal 2

  - 소셜 네트워크 기능 
    - 댓글 기능 추가
    - 피드백 수용
    - SNS 공유기능 추가

- goal 3

  - 웹, 앱 배포



#### 2nd. iteration

- goal 1
  - segmentation 추가
    - 배경을 제외한 반려동물 사진만 캐릭터화
    - UX/UI 개선
    - 모델 개선
- goal 2 
  - 앱/웹 배포를 통해 얻은 feedback 추가



#### 3rd. iteration

- goal 1
  - 캐릭터화된 사진을 굿즈 구매로 연결
    - 카테고리 별로 사업자 구분
      - 사업자 정보 제공
    - 사진을 굿즈 사업자에게 전달
      - 굿즈 제작 및 구매

- goal 2 
  - 앱/웹 배포를 통해 얻은 feedback 추가

---

### 구현 방법

#### 웹

- Docker을 기반으로한 groomide를 이용한 웹/앱 구현.

  - 웹/앱 사진 입력, 삭제기능 

    - codepen 사용하여 아주 기본적인 template 가져오기
      - HTML/CSS/Javascript 수정하여 완전히 다른 디자인과 UX/UI 변경

  - 댓글창 구현

    - DISQUS를 이용한 댓글기능 구현 ( Backend 안해도됨) 

      - SNS 공유, 움짤(gif), 이미지 첨부, 텍스트 꾸미기 기능, 좋아요, 싫어요, 대댓글 기능 등 엄청나게 다양한 기능 추가
      - SEO에도 도움됨( 검색엔진 최적화)

    - AddThis로 공유하기 버튼 따로 만들기

      - SNS마다 API연결 안해도 됨

  - Github와 Deploy 서비스 Netlify 연동하기
  - 도메인 설정
    - 도메인 구입
      - Freenom에서 무료로 도메인 얻기
        - 사용하고 싶은 도메인 이름 입력 후 원하는 도메인 이름 선택
        - .com은 유료로 만원정도 함
        - 무료도 있음
          - 기간 최대 12개월
          - 임시메일 이용하여 사용
    - Services > My Domains 복사 > netfliy로 가서 변경
    - check DNS configureation에서 설정
      - A 타입으로 설정
    - freenom으로 이동 후 > manage domain > Manage Freedom DNS > type 지정 후 연결 ( tareget에 IP 주소 입력)
      - www.을 추가해서 해도 됨
  - 검색엔진 최적화 SEO
    - robots.txt, sitemap.xml 추가
  - favicon generator ( 인터넷 창에 뜨는 이미지)
    - 원하는 이미지 선택 후 

---



#### 앱

- ReatNative를 이용해서 앱 만들기

  - Webview 이용하기
    - 인터넷 화면을 앱에 띄우는 기술
- 환경설정

  - React-Native & Expo 개발 환경 설정 

    - Node.js, Expo, React Native = 구름 IDE로 해결
      - container에서 React Native 선택 후 생성
  - Android & iOS 앱 코딩
  
    - React Native를 도와주는 Expo(테스트와 배포)를 이용
      - expo react web view 검색 > inastallation (terminal)> Usage (App.js) 대체 > 저장
      - expo 어플 다운뒤 QR 찍어서 직접 확인가능
    - - 
  - 앱 마켓 출시 준비

    - 출시를 위한 설정(아이콘이나 스플래시 이미지) , APK 파일 제작

      - App.json

        - 앱 이름설정

        - 앱 아이콘과 스플래쉬 이미지 변경

        - Expo에서 규격 확인 후 변경
    - Install Expo CLI를 이용
    
      - terminal에서 npm install > .expo 폴더 삭제
    - configure app.json
      - app.json에 추가
      - package 이름 변경
    - 카메라 접근 허용
      - expo permissions
        - installation( terminal)
      - app.json 필요한 권한만 추가
    - Run Build
    - APK 다운 > 무시하고 설치

- 앱 배포하기
  - google store 
    - 한번만 내면 됨
  - one store
    - 네이버
  - Applaunchpad
    - 앱 스크린 샷 (다양함)
