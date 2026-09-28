# CLAUDE.md

이 파일은 Claude(와 사람)가 이 저장소에서 작업할 때 먼저 읽는 안내서예요.

## 이 앱은 뭐예요?

**물마시기 체크** — 하루에 물을 얼마나 마셨는지 기록하는 작은 웹앱이에요.

- 정해진 시간(기본 10:00, 11:30, 14:00, 16:00, 18:00)마다 "한 잔"을 체크해요.
- 하루 목표량(기본 1500ml)을 채우면 달력에 표시되고, 며칠 연속 달성했는지(🔥)도 보여줘요.
- 이메일로 로그인하면 기록이 클라우드(Firebase)에 저장돼서 다른 기기에서도 똑같이 보여요.
- 정해진 시간에 휴대폰/브라우저로 푸시 알림(💧)이 와요.

빌드 도구, 프레임워크, `package.json`이 **없어요**. 그냥 HTML 파일 하나와 몇 개의 보조 파일이 전부예요.

## 파일 구성

| 파일 | 하는 일 |
|---|---|
| `index.html` | 앱 전체. 화면(HTML), 디자인(CSS), 동작(JavaScript)이 모두 이 한 파일에 들어 있어요. |
| `firebase-messaging-sw.js` | 서비스 워커. 앱이 꺼져 있을 때도 푸시 알림을 받아서 띄워줘요. |
| `send_push.py` | 푸시 알림을 실제로 보내는 파이썬 스크립트. |
| `.github/workflows/water-push.yml` | GitHub Actions가 정해진 시간마다 `send_push.py`를 실행하게 하는 설정. |

## 실행해 보기

빌드 과정이 없어서, 아무 정적 웹서버로 폴더를 열면 돼요.

```bash
python3 -m http.server 8000
# 브라우저에서 http://localhost:8000 열기
```

- 파일을 더블클릭(`file://`)으로 열면 서비스 워커와 푸시 알림이 동작하지 않아요. 꼭 서버로 열어주세요.
- 테스트 코드나 린터는 없어요. 바꾼 뒤에는 브라우저에서 직접 눌러보며 확인해요.

## `index.html` 안의 구조

`index.html`은 900줄 정도지만, 앞부분의 아주 긴 줄 두 개는 아이콘 이미지(base64)예요. 읽을 때 이 줄은 건너뛰세요(`cut -c1-200 index.html`처럼 잘라 보면 편해요).

순서대로 이렇게 되어 있어요:

1. **`<style>`** — CSS. 색은 `:root`의 변수(`--blue`, `--ink` 등)로 정해져 있고, 다크 모드용 색도 따로 있어요.
2. **`<body>`** — 로그인 창, 날짜 이동 버튼, 진행률 카드(컵 그림 + 막대), 잔 목록, 달력, 계정 바.
3. **`<script>`** — 앱 동작:
   - Firebase 설정과 초기화 (`firebaseConfig`, `VAPID_KEY`)
   - `setupPushNotifications()` — 알림 권한 요청 후 기기 토큰을 Firestore에 저장
   - 설정/데이터 불러오기·저장 (`loadSettings`, `loadData`, `saveData`, `pushToCloud`)
   - `getDayObj()` — 하루치 기록을 꺼내고, 옛날 형식이면 새 형식으로 바꿔줌
   - `computeStreak()` — 연속 달성 일수 계산
   - `renderMain()` — 선택한 날의 잔 목록과 진행률을 그림
   - `renderCalendar()` — 한 달 달력을 그림
   - 로그인/회원가입/비밀번호 재설정, 실시간 동기화 (`startCloudSync`, `applyRemoteSnapshot`)

화면을 바꾸는 방식은 단순해요: 데이터를 고치고 → `saveData(data)` → `renderMain()`과 `renderCalendar()`를 다시 불러서 전체를 새로 그려요. 새 기능을 넣을 때도 이 흐름을 따라 주세요.

## 데이터는 어떻게 생겼어요?

### 브라우저 저장소 (localStorage)
- `water-tracker-data-v2` — 날짜별 기록
- `water-tracker-settings-v1` — 설정 (`{ slotTimes, goalMl }`)

### 날짜별 기록 모양
키는 `"2026-09-28"` 같은 날짜 문자열이에요.

```js
{
  "2026-09-28": {
    slots:     [355, 0, 500, 0, 0],   // 정해진 시간별로 마신 양(ml). 0이면 안 마심
    slotTimes: ["10:00","11:30","14:00","16:00","18:00"], // 그날의 시간표
    extras:    [{ id: "x...", time: "15:10", ml: 240 }],  // "+ 잔 추가"로 넣은 것
    hidden:    [3],                   // 그날 건너뛴 칸의 번호
    goal:      1500                   // 그날의 목표량
  }
}
```

- 아주 옛날 기록은 그냥 숫자 배열(`[355, 0, ...]`)일 수 있어요. `getDayObj()`와 `totalForKey()`가 이걸 처리하니까, 이 호환 코드를 지우지 마세요.
- 시간표와 목표는 **날마다 따로** 저장돼요. 어떤 날의 시간을 바꿔도 다른 날엔 영향이 없어요.
- 새로 만들어지는 날은 항상 `DEFAULT_SLOT_TIMES`에서 시작해요. (오늘의 목표를 바꾸면 `settings.goalMl`이 바뀌어서 앞으로의 새 날짜 목표에는 반영돼요.)

### 클라우드 (Firestore)
- 문서 위치: `users/{로그인한 사람의 uid}`
- 들어 있는 것: `data`(위의 날짜별 기록 전체), `settings`, `fcmTokens`(푸시 받을 기기 토큰 목록)
- 저장할 때마다 문서 전체의 `data`를 통째로 덮어써요 (`set(..., {merge:true})`).

### 동기화할 때 조심할 점
- `applyingRemote` — 클라우드에서 받은 내용을 적용하는 중에는 다시 클라우드로 올리지 않게 막는 표시예요. 없으면 무한 반복이 생겨요.
- 사용자가 입력칸에 타이핑 중이면 클라우드 변경을 바로 적용하지 않고 `pendingRemoteApply`에 미뤄뒀다가, 입력이 끝나면 적용해요.

## 푸시 알림은 어떻게 가요?

1. 사용자가 로그인하면 `setupPushNotifications()`가 기기 토큰을 받아 `users/{uid}.fcmTokens`에 저장해요.
2. GitHub Actions(`water-push.yml`)가 cron 일정에 맞춰 `send_push.py`를 실행해요.
3. `send_push.py`는 모든 사용자의 토큰을 모아서 알림을 보내요. 알림 제목은 어떤 cron으로 실행됐는지에 따라 💧 개수가 달라요.
4. 브라우저에서는 `firebase-messaging-sw.js`가 알림을 띄워줘요.

알아둘 것:
- **cron 시간은 UTC 기준**이에요. 한국 시간(KST)은 여기에 9시간을 더하면 돼요. (예: `0 1 * * 1-5` = 평일 오전 10시)
- 알림 시간을 바꾸려면 `water-push.yml`의 cron **과** `send_push.py`의 `messages_map` 키를 **똑같이** 바꿔야 해요. 하나만 바꾸면 기본 문구("물 마실 시간이에요 (테스트)")가 나가요.
- 앱 안의 기본 시간표(`DEFAULT_SLOT_TIMES`)와 알림 시간은 자동으로 연결되어 있지 않아요. 시간을 바꿀 땐 `index.html`의 `DEFAULT_SLOT_TIMES`와 알림 시간(cron, `messages_map`)을 함께 맞춰주세요. (이미 기록이 있는 날은 그날 저장된 시간표를 그대로 써요.)
- GitHub Actions 탭에서 "Run workflow"를 누르면 바로 테스트 알림을 보낼 수 있어요 (`workflow_dispatch`).
- 서버 쪽 비밀 키는 저장소 Secret `FIREBASE_SERVICE_ACCOUNT`에 있어요. 코드에 직접 넣지 마세요.
- 서비스 워커에서 `showNotification`을 직접 부르지 마세요. Firebase가 이미 한 번 띄워주기 때문에 알림이 두 번 떠요.

## Firebase 설정값

- `index.html`과 `firebase-messaging-sw.js` **두 곳에** 같은 `firebaseConfig`가 들어 있어요. 바꿀 땐 둘 다 바꿔주세요.
- 이 `apiKey`, `VAPID_KEY`는 웹앱용 공개 값이라 코드에 있어도 괜찮아요. (서비스 계정 키는 공개하면 안 돼요.)
- Firebase 라이브러리는 CDN(`gstatic.com`)에서 버전 `10.12.2`의 compat 버전을 불러와요. 버전을 올릴 땐 `index.html`과 서비스 워커 양쪽을 맞춰주세요.

## 코드 작성 규칙

- 화면 글자와 코드 주석은 **한국어**로, 친근한 말투("~해요")로 써요.
- 스타일은 기존 코드처럼: 2칸 들여쓰기, 짧은 함수, `document.getElementById`로 요소 찾기, 라이브러리 없는 순수 JavaScript.
- 모바일(아이폰 홈 화면에 추가해서 쓰는 것)을 먼저 생각해요. 화면 최대 너비는 440px이에요.
- 새 색을 쓸 땐 CSS 변수로 만들고, 다크 모드 값도 같이 넣어주세요.
- 저장 형식을 바꾸면 기존 사용자 데이터가 깨질 수 있어요. 옛날 형식도 읽을 수 있게 `getDayObj()`에 변환 코드를 추가하는 식으로 해주세요.
