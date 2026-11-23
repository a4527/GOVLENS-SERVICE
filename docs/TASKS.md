# Govlens 작업 목록

상태 표기: `TODO`, `IN PROGRESS`, `DONE`, `BLOCKED`, `CANCELLED`. 요구사항은 [PRD](PRD.md)에 정의한다. 수용 기준은 확인할 동작·경계 중심으로 적고 요구사항·설계 상세는 복사하지 않는다.

2026-11-23 이전 팀 프로젝트 기간의 마일스톤(M0–M4)·역할별 진행 기록은 [archive/PROGRESS-team-2026.md](archive/PROGRESS-team-2026.md)에 원문으로 보존한다. 아래 항목은 그 문서의 Current "다음"·Next·Blocked 중 아직 열려 있는 것을 개인 프로젝트 기준으로 옮긴 것이다.

## 설계와 결정

| ID | 우선순위 | 상태 | 작업 / 완료 기준 |
| --- | --- | --- | --- |
| D-01 | P0 | DONE | 개인 프로젝트 전환 결정 기록. [DEC-0028](DECISIONS.md#dec-0028) Accepted, ADR-0001 대체 범위 표시 |

## 기능 구현

| ID | 우선순위 | 상태 | 작업 / 완료 기준 |
| --- | --- | --- | --- |
| F-01 | P1 | TODO | EC2/RDS/ALB Golden Case 추가. 확장한 9 Rule(EC2 3·RDS 4·ALB 2)이 IAC/AWS_ACTUAL/DRIFT 관점 Case를 갖고 rubric 반복 평가로 품질 게이트를 통과한다. fixture만 늘리는 것은 근거가 아니다 ([ADR-0021](adr/ADR-0021-demo-and-release-readiness-gate.md), [ADR-0022](adr/ADR-0022-m4-golden-customer-runtime-observations.md)) |
| F-02 | P2 | TODO | IAC INITIAL 좌표의 결정적 판정. HCL parser/projection 계층을 두고 Catalog 술어로 판정해 모델 호출을 줄인다. 판정 출처(`decided_by: CODE`)가 결과에 남는다 ([ADR-0024](adr/ADR-0024-scoring-boundary-by-meaning.md)) |
| F-03 | P2 | TODO | Frontend Admin 감사 이력 화면. `GET /audit-events`를 조회해 표시한다 ([API](design/API.md)) |
| F-04 | P2 | TODO | Frontend 관측·비용 화면. `GET /deployments/{id}/observability`를 조회해 표시한다 ([API](design/API.md)) |

## 검증과 운영

| ID | 우선순위 | 상태 | 작업 / 완료 기준 |
| --- | --- | --- | --- |
| V-01 | P0 | DONE | 로컬 개발 환경과 기준선. `.venv`(uv) + CI 동일 명령으로 ruff·unittest 4종·frontend build·gitleaks 통과 ([worklog](worklogs/2026-11-23.md)) |
| V-02 | P0 | TODO | 잔존 AWS 리소스·비용 점검. sandbox 계정의 Foundation 스택과 customer-demo의 의도적 비준수 리소스(퍼블릭 RDS 등)가 남아 있는지 확인하고, 유지/삭제를 결정한다 |
| V-03 | P1 | TODO | GitHub 설정 재확인. 개인 계정(a4527) 저장소의 Environment·Required reviewers·Secret·OIDC Role·GitHub App 설치가 현재 저장소를 가리킨다 ([CUSTOMER_SANDBOX_ONBOARDING](sandbox/CUSTOMER_SANDBOX_ONBOARDING.md)) |
| V-04 | P1 | TODO | 고객 read Role 권한 반영. S3 `GetBucketPolicy`/`GetBucketOwnershipControls`/`GetBucketLogging`, EC2 `DescribeSubnets`가 배포된 read Role에 있다 ([M1-SANDBOX-INTEGRATION](sandbox/M1-SANDBOX-INTEGRATION.md)). V-03 이후 |
| V-05 | P1 | TODO | 폐루프 라이브 E2E. Assessment → Finding → Remediation PR → plan → 승인 → apply(2026-09-07 dispatch `ref` 수정 포함) → Post-Deploy Verification이 실제 sandbox에서 완주한다 ([M4-DEMO-RUNBOOK](demo/M4-DEMO-RUNBOOK.md)). V-03·V-04 이후 |
| V-06 | P1 | TODO | 점수 경계 라이브 회귀 측정. `evaluations/data/score-boundary-20260905.md` §3 절차를 자격 증명 환경에서 실행하고 CODE/MODEL 판정별 정확도·일치율을 기록한다 |
| V-07 | P2 | TODO | M4 Golden release gate 실측. Post-Deploy 18 Case × 5 run observation bundle로 `scripts/evaluate_m4_golden_release_gate.py` sanitized report를 만든다 ([M4-GOLDEN-RELEASE-GATE](evaluations/M4-GOLDEN-RELEASE-GATE.md)). V-05 이후 |
| V-08 | P2 | TODO | Frontend 테스트. `apps/frontend`에 test 스크립트가 없다. 최소 smoke test를 추가하고 `frontend-checks.yml`에서 실행한다 |

## 선행 관계

- V-03 → V-04 → V-05 → V-07
- V-02는 다른 라이브 작업 전에 먼저 확인한다(비용·공개 저장소 노출).
