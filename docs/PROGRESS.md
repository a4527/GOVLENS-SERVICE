# Govlens 진행 현황

마지막 갱신: 2026-11-23 · 개인 프로젝트 전환, 단일 계정 sandbox 결정(DEC-0030), 공통 태그 코드 반영(V-10)

현재 단계: MVP 폐루프(평가 → Finding → 조치 PR → plan → 사람 승인 → apply → 재평가)의 코드는 모두 들어가 있고 fixture·단위·통합 테스트로 검증된다. 실제 sandbox에서는 Initial Assessment와 조치 patch 생성까지 완주했고(2026-09-03), 승인 뒤 apply dispatch의 422 원인을 고친 상태(2026-09-07)에서 팀 작업이 멈췄다. 라이브 apply·Post-Deploy Verification은 아직 확인되지 않았다.

## 현재 작업 상태

| 작업 | 상태 | 확인된 범위와 다음 단계 |
| --- | --- | --- |
| 개인 프로젝트 전환 (D-01, V-01) | DONE | `main` + 작업 브랜치 PR로 CI 규칙 변경, 문서 구조 재편, 기준선 테스트 통과. [worklog](worklogs/2026-11-23.md) |
| 운영 계정 결정 (V-02) | DONE | 팀 sandbox 계정은 접근 불가, 개인 계정 하나에 플랫폼·고객을 함께 두고 Foundation은 유지·workload는 매일 삭제([DEC-0030](DECISIONS.md#dec-0030)) |
| 개인 계정 sandbox 구성 (V-10, V-11, V-03, V-12) | IN PROGRESS | 공통 태그·재실행 가능한 bootstrap(코드 반영, 라이브 확인은 V-03) → GitHub Environment·Secret 재구성 → workload teardown 절차. a4527 저장소에는 아직 Secret·Variable·Environment가 없다 |
| 폐루프 라이브 E2E (V-04, V-05) | TODO | read Role 권한 반영 후 apply·Post-Deploy Verification 완주 |
| 품질 근거 확장 (F-01, V-06, V-07) | TODO | EC2/RDS/ALB Golden Case, 점수 경계 라이브 측정, M4 release gate 실측 |
| 관측 구현 (O-01–O-05) | TODO | 현재는 Artifact CloudTrail과 정책 추출 DLQ 알람 1개뿐. 구조화 로그·핵심 알람부터 |

작업 상태의 기준은 [TASKS](TASKS.md)다.

## 합의와 미정 범위

- 브랜치·진행 관리 방식: [DEC-0028](DECISIONS.md#dec-0028).
- sandbox 운영: 단일 개인 AWS 계정, 공통 태그 `Owner`·`Project`·`Layer`([DEC-0030](DECISIONS.md#dec-0030)).
- Worker 실행 방식: LangGraph는 Parent에만, Worker는 일반 Python([DEC-0029](DECISIONS.md#dec-0029)).
- 제품 범위·평가 의미는 [PRD](PRD.md), 구조는 [DESIGN](DESIGN.md), 결정은 [DECISIONS](DECISIONS.md)를 따른다.
- IaC 관점 INITIAL 판정은 HCL parser 계층이 생길 때까지 모델이 판단한다(F-02).

## 검증 상태

- 2026-11-23 로컬 기준선: ruff lint/format 통과, unittest unit 1595(skip 1)·contract 248·integration 23·security 119 모두 통과, frontend build 통과, gitleaks 전체 기록 오탐 4건(`.gitleaksignore`로 등록).
- 라이브(AWS/GitHub/Bedrock) 검증은 2026-09-07 이후 실행하지 않았다.

상세 검증 결과는 날짜별 [worklog](worklogs/)를 연결한다.
