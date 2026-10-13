# cron-job.org로 물 알림 예약하기

GitHub의 예약 실행(cron)은 몇 시간씩 늦게 시작될 때가 있어요.
그래서 이제는 **cron-job.org**라는 무료 사이트가 정해진 시각에 GitHub에 "지금 알림 보내!" 하고 요청하는 방식으로 바꿨어요.

전체 흐름은 이래요:

```
cron-job.org (정해진 시각) → GitHub API → water-push.yml 실행 → send_push.py → 휴대폰에 💧 알림
```

준비는 세 단계예요.

1. GitHub 토큰 만들기 (cron-job.org가 GitHub에 요청할 때 쓰는 열쇠)
2. Actions 탭에서 수동으로 한 번 테스트하기
3. cron-job.org에 작업 8개 만들기

> ⚠️ **먼저 이 변경이 `main`에 합쳐져(머지) 있어야 해요.**
> GitHub는 `main`에 있는 `water-push.yml`을 보고 `slot` 입력이 있는지 확인해요. 머지 전에 요청하면 `422 Unexpected inputs provided` 오류가 나요.

---

## 1단계. GitHub 토큰 만들기

이 토큰은 **이 저장소 하나에서, 워크플로 실행만** 할 수 있게 권한을 아주 좁게 만들어요.

1. GitHub 오른쪽 위 프로필 사진 → **Settings** 를 눌러요.
2. 왼쪽 메뉴 맨 아래 **Developer settings** → **Personal access tokens** → **Fine-grained tokens** 로 가요.
3. **Generate new token** 을 눌러요.
4. 아래처럼 채워요.
   - **Token name**: `water-cron` (아무 이름이나 괜찮아요)
   - **Expiration**: 원하는 기간 (예: 1년). 만료되면 알림이 멈추니까, 만료일을 달력에 적어두세요.
   - **Repository access**: **Only select repositories** 를 고르고 `yeinariakim/WaterTracker` 하나만 선택해요.
   - **Permissions** → **Repository permissions** 에서 **Actions** 를 **Read and write** 로 바꿔요.
     - 다른 권한은 건드리지 마세요. (`Metadata: Read-only`는 자동으로 들어가는데, 이건 원래 그래요.)
5. **Generate token** 을 누르면 `github_pat_...` 로 시작하는 토큰이 나와요.
   **이 화면에서만 한 번 보여주니까 바로 복사해서 안전한 곳에 적어두세요.**

> 🔒 이 토큰은 비밀번호와 같아요. 저장소 코드나 채팅, 이슈에 붙여넣지 마세요. cron-job.org에만 넣어요.

---

## 2단계. Actions 탭에서 수동 테스트하기

cron-job.org를 설정하기 전에, 알림이 제대로 가는지 먼저 확인해요.

1. GitHub 저장소 → 위쪽 **Actions** 탭으로 가요.
2. 왼쪽에서 **물 마시기 푸시 알림** 을 눌러요.
3. 오른쪽의 **Run workflow** 버튼을 눌러요.
4. Branch는 `main`, **slot** 칸에 `w3` 을 넣고 초록색 **Run workflow** 를 눌러요.
5. 1분쯤 뒤 휴대폰에 **💧💧💧** 알림이 오면 성공이에요.

- slot 칸을 **비워두면** "물 마실 시간이에요 (테스트)" 알림이 와요.
- 실행 기록을 눌러서 **Send FCM push** 단계를 펼치면 `slot='w3' -> 💧💧💧`, `sent OK to ...` 같은 줄이 보여요.

---

## 3단계. cron-job.org에 작업 8개 만들기

### 가입하고 시간대 맞추기

1. https://cron-job.org 에서 무료로 가입하고 로그인해요.
2. 계정 설정(Settings)에서 **Timezone** 을 **Asia/Seoul** 로 바꿔요.
   (작업마다 시간대를 따로 고를 수도 있어요. 어느 쪽이든 **Asia/Seoul** 이면 돼요.)

### 작업 하나 만들기 (예: 평일 10:00 = `w1`)

**Dashboard → Cronjobs → Create cronjob** 을 눌러요.

**Common (기본) 탭**
- **Title**: `물 w1 평일 10:00`
- **URL**:
  ```
  https://api.github.com/repos/yeinariakim/WaterTracker/actions/workflows/water-push.yml/dispatches
  ```
- **Execution schedule**: **Custom** 을 고르고
  - 시(Hours): `10`, 분(Minutes): `0`
  - 요일(Days of week): **월·화·수·목·금** 만 선택
  - 일(Days of month), 월(Months): 전체(Every)

**Advanced (고급) 탭**
- **Time zone**: `Asia/Seoul`
- **Request method**: `POST`
- **Headers**: 아래 3줄을 하나씩 추가해요. (`<토큰>` 자리에 1단계에서 복사한 토큰을 넣어요.)

  | Key | Value |
  |---|---|
  | `Authorization` | `Bearer <토큰>` |
  | `Accept` | `application/vnd.github+json` |
  | `X-GitHub-Api-Version` | `2022-11-28` |

- **Request body**:
  ```json
  {"ref":"main","inputs":{"slot":"w1"}}
  ```

**Create** 로 저장해요.

### 나머지 7개도 똑같이 만들어요

URL, 헤더는 모두 같고 **시각, 요일, 본문의 `slot` 값만** 달라요.
첫 작업을 만든 뒤 목록에서 **복사(Clone)** 하면 편해요.

| 제목 | 시각 (한국 시간) | 요일 | 본문 |
|---|---|---|---|
| 물 w1 평일 10:00 | 10:00 | 월~금 | `{"ref":"main","inputs":{"slot":"w1"}}` |
| 물 w2 평일 11:30 | 11:30 | 월~금 | `{"ref":"main","inputs":{"slot":"w2"}}` |
| 물 w3 평일 14:00 | 14:00 | 월~금 | `{"ref":"main","inputs":{"slot":"w3"}}` |
| 물 w4 평일 16:00 | 16:00 | 월~금 | `{"ref":"main","inputs":{"slot":"w4"}}` |
| 물 w5 평일 18:00 | 18:00 | 월~금 | `{"ref":"main","inputs":{"slot":"w5"}}` |
| 물 e1 주말 11:00 | 11:00 | 토·일 | `{"ref":"main","inputs":{"slot":"e1"}}` |
| 물 e2 주말 14:00 | 14:00 | 토·일 | `{"ref":"main","inputs":{"slot":"e2"}}` |
| 물 e3 주말 17:00 | 17:00 | 토·일 | `{"ref":"main","inputs":{"slot":"e3"}}` |

### 잘 되는지 확인하기

- 작업 목록에서 작업 하나를 골라 **Test run**(또는 실행 버튼)을 눌러봐요.
  - 응답이 **204 No Content** 면 성공이에요. 곧 GitHub Actions 탭에 새 실행이 생기고 알림이 와요.
- 실패했을 때 자주 나오는 응답:

  | 응답 | 이유 |
  |---|---|
  | `401` | 토큰이 틀렸거나 만료됐어요. `Bearer ` 뒤에 띄어쓰기 한 칸이 있는지도 봐주세요. |
  | `403` / `404` | 토큰에 이 저장소나 **Actions: Read and write** 권한이 없어요. |
  | `422` | 본문 모양이 틀렸거나, 아직 `slot` 입력이 `main`에 머지되지 않았어요. |

- 며칠 동안은 cron-job.org의 **History** 와 GitHub **Actions** 탭에서 정해진 시각에 실행됐는지 한 번씩 봐주세요.

---

## 알림 시각을 바꾸고 싶을 때

- **시각만** 바꿀 땐: cron-job.org에서 해당 작업의 시각만 고치면 돼요. 코드는 안 바꿔도 돼요.
- **새 칸을 추가**할 땐: cron-job.org에 작업을 만들고, `send_push.py`의 `messages_map`에 같은 `slot` 이름을 넣어주세요.
  (모르는 이름이면 "물 마실 시간이에요 (테스트)" 문구가 나가요.)
- 앱 안의 기본 시간표(`index.html`의 `DEFAULT_SLOT_TIMES`)와는 자동으로 연결되지 않으니까 함께 맞춰주세요.
