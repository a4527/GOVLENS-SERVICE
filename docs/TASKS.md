# Govlens 작업 목록

상태 표기: `TODO`, `IN PROGRESS`, `DONE`, `BLOCKED`, `CANCELLED`. 요구사항은 [PRD](PRD.md)에 정의한다. 수용 기준은 확인할 동작·경계 중심으로 적고 요구사항·설계 상세는 복사하지 않는다.

2026-11-23 이전 팀 프로젝트 기간의 마일스톤(M0–M4)·역할별 진행 기록은 [archive/PROGRESS-team-2026.md](archive/PROGRESS-team-2026.md)에 원문으로 보존한다. 아래 항목은 그 문서의 Current "다음"·Next·Blocked 중 아직 열려 있는 것을 개인 프로젝트 기준으로 옮긴 것이다.

## 설계와 결정

| ID | 우선순위 | 상태 | 작업 / 완료 기준 |
| --- | --- | --- | --- |
| D-01 | P0 | DONE | 개인 프로젝트 전환 결정 기록. [DEC-0028](DECISIONS.md#dec-0028) Accepted, ADR-0001 대체 범위 표시 |
| D-02 | P2 | DONE | Worker LangGraph 미도입 결정 기록. [DEC-0029](DECISIONS.md#dec-0029) Accepted, ADR-0005 대체 범위 표시 |

## 기능 구현

| ID | 우선순위 | 상태 | 작업 / 완료 기준 |
| --- | --- | --- | --- |
| F-01 | P1 | TODO | EC2/RDS/ALB Golden Case 추가. 확장한 9 Rule(EC2 3·RDS 4·ALB 2)이 IAC/AWS_ACTUAL/DRIFT 관점 Case를 갖고 rubric 반복 평가로 품질 게이트를 통과한다. fixture만 늘리는 것은 근거가 아니다 ([ADR-0021](adr/ADR-0021-demo-and-release-readiness-gate.md), [ADR-0022](adr/ADR-0022-m4-golden-customer-runtime-observations.md)) |
| F-02 | P2 | TODO | IAC INITIAL 좌표의 결정적 판정. HCL parser/projection 계층을 두고 Catalog 술어로 판정해 모델 호출을 줄인다. 판정 출처(`decided_by: CODE`)가 결과에 남는다 ([ADR-0024](adr/ADR-0024-scoring-boundary-by-meaning.md)) |
| F-03 | P2 | TODO | Frontend Admin 감사 이력 화면. `GET /audit-events`를 조회해 표시한다 ([API](design/API.md)) |
| F-04 | P2 | TODO | Frontend 관측·비용 화면. `GET /deployments/{id}/observability`를 조회해 표시한다 ([API](design/API.md)) |
| F-05 | P2 | TODO | IAM 리소스 평가 추가. ISMS-P 2.5(인증·권한) 기술 통제를 Rule로 만들고 read Role·Resource Tool·Golden Case를 갖춘다. F-01·V-05 이후 |
| F-06 | P3 | TODO | CloudTrail 리소스 평가 추가. ISMS-P 2.9.4(로그·접속기록) 기술 통제를 계정 단위로 평가한다. F-05 이후 |
| F-07 | P2 | DONE | Remediation Worker의 LangGraph 전환 여부 결정. 채택하지 않음([DEC-0029](DECISIONS.md#dec-0029)). README·DESIGN·C4·ADR-0005의 "Worker = LangGraph subgraph" 설명을 구현에 맞췄다 |

## 검증과 운영

| ID | 우선순위 | 상태 | 작업 / 완료 기준 |
| --- | --- | --- | --- |
| V-01 | P0 | DONE | 로컬 개발 환경과 기준선. `.venv`(uv) + CI 동일 명령으로 ruff·unittest 4종·frontend build·gitleaks 통과 ([worklog](worklogs/2026-11-23.md)) |
| V-02 | P0 | DONE | 잔존 AWS 리소스·비용 점검과 운영 계정 결정. 팀 sandbox 계정은 접근할 수 없어 점검 불가(팀 쪽 정리 대상), 개인 계정에는 Govlens 리소스가 없음을 17개 리전에서 확인했다. 단일 계정·Foundation 유지·workload 매일 삭제로 결정([DEC-0030](DECISIONS.md#dec-0030), [worklog](worklogs/2026-11-23.md)) |
| V-03 | P1 | TODO | 개인 계정 sandbox 구성. V-11 bootstrap으로 플랫폼 bootstrap·Foundation·고객 onboarding을 배포하고, a4527 저장소에 Environment(Required reviewers 포함)·Secret·Variable·GitHub App을 새로 만든다. 2026-11-23 확인 시 두 저장소 모두 Secret·Variable·Environment가 없다 ([CUSTOMER_SANDBOX_ONBOARDING](sandbox/CUSTOMER_SANDBOX_ONBOARDING.md)). V-10·V-11 이후 |
| V-04 | P1 | TODO | 고객 read Role 권한 반영(`customer-onboarding.yaml`의 read Role이 아래 권한을 포함하므로 V-11 배포로 충족 예정). S3 `GetBucketPolicy`/`GetBucketOwnershipControls`/`GetBucketLogging`, EC2 `DescribeSubnets`가 배포된 read Role에 있다 ([M1-SANDBOX-INTEGRATION](sandbox/M1-SANDBOX-INTEGRATION.md)). V-03 이후 |
| V-05 | P1 | TODO | 폐루프 라이브 E2E. Assessment → Finding → Remediation PR → plan → 승인 → apply(2026-09-07 dispatch `ref` 수정 포함) → Post-Deploy Verification이 실제 sandbox에서 완주한다 ([M4-DEMO-RUNBOOK](demo/M4-DEMO-RUNBOOK.md)). V-03·V-04 이후 |
| V-06 | P1 | TODO | 점수 경계 라이브 회귀 측정. `evaluations/data/score-boundary-20260905.md` §3 절차를 자격 증명 환경에서 실행하고 CODE/MODEL 판정별 정확도·일치율을 기록한다 |
| V-07 | P2 | TODO | M4 Golden release gate 실측. Post-Deploy 18 Case × 5 run observation bundle로 `scripts/evaluate_m4_golden_release_gate.py` sanitized report를 만든다 ([M4-GOLDEN-RELEASE-GATE](evaluations/M4-GOLDEN-RELEASE-GATE.md)). V-05 이후 |
| V-08 | P2 | TODO | Frontend 테스트. `apps/frontend`에 test 스크립트가 없다. 최소 smoke test를 추가하고 `frontend-checks.yml`에서 실행한다 |
| V-09 | P1 | TODO | 정책 원문 확보. `policies-local/`에 ISMS-P 인증기준(2023-10-31, KISA 공개본)을 두고 `build_isms_p_baseline.py --check`가 통과한다. 사내 체크리스트는 옛 원문을 구해 digest가 맞는지 확인하거나, 새로 작성해 새 version으로 등록하고 16개 Rule의 `source_references`를 갱신한다 |
| V-10 | P1 | IN PROGRESS | 공통 태그. CloudFormation 스택(`--tags`)과 customer-demo `default_tags`가 `Owner`·`Project`·`Layer`를 붙이고, `Owner` 값은 파라미터·GitHub Variable로 받는다(저장소에 값 없음). Tag Editor에서 계층별 조회가 된다 ([DEC-0030](DECISIONS.md#dec-0030)). 2026-11-23 코드 반영(Foundation 워크플로 `--tags`, bootstrap 역할 태그 권한, customer-demo·템플릿 `default_tags`), 라이브 확인은 V-03 배포 때 |
| V-11 | P1 | IN PROGRESS | 재실행 가능한 bootstrap. 빈 계정에서 `m1-customer-bootstrap` → Foundation 배포 → 고객 onboarding(state 버킷·lock 테이블·Plan/Apply/read Role) 순서를 스크립트 하나로 실행하고, 이미 있으면 건너뛴다. 고객 onboarding은 지금 수동 체크리스트이므로 CloudFormation 템플릿으로 만들어 실제 고객 온보딩 키트로도 쓴다. V-10 이후. 2026-11-23 코드 반영(`customer-onboarding.yaml`, customer-demo `onboarding/workload-policy.yaml`, `scripts/sandbox-bootstrap.sh`, 잔존 Foundation 리소스 삭제 `recover-foundation`), 빈 계정 실행 확인은 V-03에서 |
| V-12 | P1 | TODO | customer workload 일일 teardown. customer-demo를 `terraform destroy`로 지워도 state·Foundation·onboarding은 남고, 다음 apply가 같은 비준수 기준선(태그 또는 브랜치로 고정)에서 시작한다. 조치 PR merge 뒤 기준선 복원 절차가 문서화된다 |

## 관측

[DESIGN Observability](DESIGN.md#observability)에 적힌 관측 중 현재 구현은 Artifact 버킷 CloudTrail과 정책 추출 DLQ 알람 1개뿐이다(2026-11-23 확인).

| ID | 우선순위 | 상태 | 작업 / 완료 기준 |
| --- | --- | --- | --- |
| O-01 | P1 | TODO | 구조화 로그와 상관 키. API·Worker Lambda 로그가 JSON이고 `request_id`·`job_id`·`assessment_id`·`rule_id`를 담는다. Prompt·정책 원문·IaC 전체는 로그에 남지 않는다(테스트로 고정). Lambda LogGroup을 CloudFormation으로 만들고 보관 기간을 명시한다 |
| O-02 | P1 | TODO | 핵심 알람. Assessment·Remediation·Deployment DLQ depth, Queue 최고 대기 시간, Worker Lambda 오류·throttle 알람이 있고 SNS로 알린다([ADR-0013](adr/ADR-0013-sqs-resumable-worker-execution.md) Consequences). `cfn-lint`·보안 테스트 통과 |
| O-03 | P2 | TODO | 평가·모델 지표. 역할별 Bedrock 호출 수·입출력 토큰·지연, 판정 분포(`decided_by`별), `EXECUTION_ERROR`, checkpoint 재개 횟수가 CloudWatch 메트릭(EMF)으로 남는다 |
| O-04 | P2 | TODO | 분산 추적. API Gateway·Lambda에 X-Ray를 켜고 Bedrock·GitHub·AWS Resource Tool 호출이 하위 구간으로 보인다. 요청 하나를 API → Queue → Worker까지 따라갈 수 있다 |
| O-05 | P2 | TODO | 데모 관측 live source. `DemoRunMetricsSource`에 CloudWatch·CloudTrail·Cost Explorer 어댑터를 주입해 `GET /deployments/{id}/observability`가 404가 아니라 일곱 항목을 반환한다(값이 없으면 게이트 미충족, fail-closed) ([ADR-0021](adr/ADR-0021-demo-and-release-readiness-gate.md) §3). O-03 이후 |

## 선행 관계

- V-10 → V-11 → V-03 → V-04 → V-05 → V-07, V-12는 V-05 전에 둔다
- O-03 → O-05 → F-04, O-05 → V-07(release gate 관측·비용 기록).
- F-01·V-05 → F-05 → F-06.
