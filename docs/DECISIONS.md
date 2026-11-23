# Govlens 결정 목록

중요 결정의 상태·ADR 링크와 짧은 결정을 관리한다. ADR 번호는 DEC 번호를 따른다(`DEC-0024` ↔ `ADR-0024`).

상태가 따로 적히지 않은 ADR(0001–0017, 0024, 0026)은 팀 프로젝트 기간에 채택돼 구현에 반영된 결정이므로 `Accepted`로 본다. 이후 대체된 결정은 아래 표의 상태를 따른다.

## 중요 결정 · ADR 목록

| 결정 ID | 결정 | 상태 | ADR | 대체 관계 |
| --- | --- | --- | --- | --- |
| `DEC-0001` | Repository and delivery workflow | Partially Superseded | [ADR-0001](adr/ADR-0001-repository-and-delivery.md) | 브랜치·진행 관리 부분 → DEC-0028 |
| `DEC-0002` | AI evaluation boundary | Accepted | [ADR-0002](adr/ADR-0002-ai-evaluation-boundary.md) | — |
| `DEC-0003` | Continuous scoring with reliability-triggered anchors | Superseded | [ADR-0003](adr/ADR-0003-scoring-reliability.md) | 연속 점수·Anchor 전환 → DEC-0024 (2026-09-05) |
| `DEC-0004` | Policy knowledge architecture without RAG | Accepted | [ADR-0004](adr/ADR-0004-policy-knowledge-architecture.md) | — |
| `DEC-0005` | Serverless workflow execution | Partially Superseded | [ADR-0005](adr/ADR-0005-serverless-workflow-execution.md) | Worker의 LangGraph subgraph 부분 → DEC-0029 |
| `DEC-0006` | Persistence and artifact storage boundary | Accepted | [ADR-0006](adr/ADR-0006-persistence-and-artifact-storage.md) | — |
| `DEC-0007` | Approved deployment boundary | Accepted | [ADR-0007](adr/ADR-0007-approved-deployment-boundary.md) | — |
| `DEC-0008` | Customer deployment topology | Accepted | [ADR-0008](adr/ADR-0008-customer-deployment-topology.md) | — |
| `DEC-0009` | M0 contract fixtures and deployment binding | Accepted | [ADR-0009](adr/ADR-0009-m0-contract-fixtures.md) | — |
| `DEC-0010` | M0 platform foundation and Job ownership | Accepted | [ADR-0010](adr/ADR-0010-m0-platform-foundation.md) | — |
| `DEC-0011` | IaC·Actual 상태·Drift 평가 관점 분리 | Accepted | [ADR-0011](adr/ADR-0011-iac-actual-drift-assessment.md) | — |
| `DEC-0012` | Natural-language orchestration and role-specific model profiles | Accepted | [ADR-0012](adr/ADR-0012-natural-language-orchestration-and-model-profiles.md) | — |
| `DEC-0013` | SQS-resumable Worker execution | Accepted | [ADR-0013](adr/ADR-0013-sqs-resumable-worker-execution.md) | — |
| `DEC-0014` | Artifact access audit and tenant runtime isolation | Accepted | [ADR-0014](adr/ADR-0014-artifact-audit-and-tenant-isolation.md) | — |
| `DEC-0015` | Customer policy ingestion and approval boundary | Accepted | [ADR-0015](adr/ADR-0015-customer-policy-ingestion.md) | — |
| `DEC-0016` | C derives M1 Findings and Readiness from immutable evaluation results | Accepted | [ADR-0016](adr/ADR-0016-m1-finding-readiness-projection.md) | — |
| `DEC-0017` | B decides what may be remediated automatically, and what a human must judge | Accepted | [ADR-0017](adr/ADR-0017-remediation-scope-and-exceptions.md) | — |
| `DEC-0018` | Remediation 정책 판정 소비와 C-owned Worker 오케스트레이션 | Accepted | [ADR-0018](adr/ADR-0018-remediation-consumption-contract.md) | — |
| `DEC-0019` | 승인 배포 실행 경계 (plan/apply 재현성과 트리거 소유권) | Accepted | [ADR-0019](adr/ADR-0019-approved-deployment-execution-boundary.md) | — |
| `DEC-0020` | Post-Deploy Verification과 before/after 비교 경계 | Accepted | [ADR-0020](adr/ADR-0020-post-deploy-verification-and-comparison.md) | — |
| `DEC-0021` | Demo와 Release readiness gate | Accepted | [ADR-0021](adr/ADR-0021-demo-and-release-readiness-gate.md) | — |
| `DEC-0022` | M4 Golden customer-runtime observation handoff | Accepted | [ADR-0022](adr/ADR-0022-m4-golden-customer-runtime-observations.md) | — |
| `DEC-0023` | 정책 문서에서 승인된 Rule까지의 Authoring 경계 | Accepted | [ADR-0023](adr/ADR-0023-policy-to-rule-authoring.md) | — |
| `DEC-0024` | 사실·해석·모름 — 평가 경계를 의미로 긋는다 | Accepted | [ADR-0024](adr/ADR-0024-scoring-boundary-by-meaning.md) | — |
| `DEC-0025` | 추출하지 못한 단위는 보이는 미완료로 남는다 | Rejected (철회 2026-09-05) | [ADR-0025](adr/ADR-0025-visible-incompleteness-in-authoring.md) | — |
| `DEC-0026` | ISMS-P는 고객이 올리지 않는다 — 운영자 기준선으로 게시한다 | Accepted | [ADR-0026](adr/ADR-0026-isms-p-as-operator-baseline.md) | — |
| `DEC-0027` | 평가 대상 revision은 배포 시점의 고정 commit이 아니라 branch HEAD를 따른다 | Accepted | [ADR-0027](adr/ADR-0027-assessment-revision-follows-branch-head.md) | — |

상태 값: `Proposed`, `Accepted`, `Partially Superseded`, `Superseded`, `Rejected`.

## 짧은 결정

각 항목은 결정일·상태와 결정·핵심 이유를 1~2줄로 남긴다.

<a id="dec-0028"></a>
### DEC-0028 · 개인 프로젝트 전환: `main` + 작업 브랜치 PR

- 결정일: 2026-11-23 · 상태: Accepted · 대체: DEC-0001(ADR-0001)의 브랜치·진행 관리 부분
- 결정·이유: 혼자 운영하므로 `dev` 통합 브랜치와 Owner 승인·`.ai/` 규칙을 없애고, `type/kebab-case` 작업 브랜치에서 `main`으로 PR을 열어 CI 통과 후 병합한다. 진행 관리는 `docs/TASKS.md`·`docs/PROGRESS.md`로 옮긴다. Monorepo + 별도 Customer IaC Repository 구조는 유지한다.

<a id="dec-0029"></a>
### DEC-0029 · Worker는 LangGraph 없이 일반 Python으로 유지한다

- 결정일: 2026-11-23 · 상태: Accepted · 대체: DEC-0005(ADR-0005)의 "Worker = LangGraph subgraph" 부분 · 검토: [제안서](proposals/LANGGRAPH-REMEDIATION-WORKER.md)
- 결정·이유: LangGraph는 자연어 진입점인 Parent Orchestrator에만 쓴다. Assessment·Remediation·Deployment Worker는 SQS + DynamoDB checkpoint의 일반 Python(ADR-0013)으로 둔다. Remediation의 생성·검증·재요청 반복은 이미 코드에 있고 검증 단계를 늘릴 계획이 없어, 옮겨도 동작 이득 없이 의존성·Layer 크기만 늘기 때문이다.

<a id="dec-0030"></a>
### DEC-0030 · 개인 sandbox는 단일 AWS 계정, Foundation 유지·고객 workload는 매일 삭제

- 결정일: 2026-11-23 · 상태: Accepted
- 결정·이유: 비용 때문에 플랫폼(bootstrap·Foundation)과 고객 쪽(onboarding·workload)을 개인 AWS 계정 하나에 둔다(팀 기간 sandbox와 같은 구성, 이전 팀 계정은 쓰지 않는다). Foundation은 유휴 비용이 거의 없고 이름 고정 `Retain` 리소스(DynamoDB·S3·Cognito·CloudTrail) 때문에 재생성이 실패하므로 유지하고, 비용이 드는 customer-demo workload(EC2·RDS·ALB)만 작업일마다 `terraform apply`/`destroy`한다. 계정 정리 가능성에 대비해 고객 배포 경로(`m1-customer-bootstrap` → Foundation → 고객 onboarding)를 그대로 재실행하는 bootstrap을 두고, 모든 리소스에 공통 태그 `Owner`·`Project`·`Layer`(`bootstrap`|`foundation`|`customer-onboarding`|`customer-workload`)를 붙인다. 계정 ID·`Owner` 값은 공개 저장소에 두지 않고 배포 파라미터·GitHub Variable로 주입한다.

## 기록·변경 규칙

- 사용자와의 핵심 약속, 되돌리기 큰 비용이 드는 선택, 보안·데이터 경계, 결론만으로는 오해하기 쉬운 중요한 절충은 ADR로 남긴다. 여러 구성 요소에 영향을 주거나 논의가 길었다는 사실만으로 ADR을 만들지 않는다.
- 기존 방향 안의 세부 방식이며 변경 시 데이터 이전·사용자 약속 변경이 필요 없고 결정과 이유를 두 문장으로 설명할 수 있으면 이 파일에 짧게 남긴다. 현행 제품 정책의 상세는 PRD, 구현 계약의 상세는 DESIGN 또는 관련 상세 설계로 연결한다.
- 짧은 결정은 ID·결정일·상태와 결정·핵심 이유를 1~2줄로 기록한다. 승인 대화 전문·대안별 분석·영향·검증 현황을 항목마다 반복하지 않는다. 영향이 커지면 ADR로 옮겨 링크를 남긴다.
- ADR이 있는 결정은 목록에 ID·제목·상태·ADR 링크·대체 관계만 관리하고 결론 식별에 필요한 요약만 허용한다. 같은 결정을 별도 본문에 장문으로 다시 기록하지 않는다. ADR로 이관한 기존 본문 앵커는 짧은 링크로 보존한다.
- ADR에는 결정 당시 배경·선택·이유·대안·절충과 승인 범위를 식별하는 핵심 조건을 남긴다. 전체 제품 정책·API/DB 명세·작업 수용 기준을 복사하거나 최신 검증 결과를 계속 누적하지 않는다. 검증 항목·재검토 조건은 결정의 위험을 설명하는 범위에 두고 실제 결과는 worklog로 연결한다.
- 승인 후 구현 진척만으로 과거 ADR의 판단·대안·당시 미확인 사실을 다시 쓰지 않는다. 후속 결정과 대체 범위를 연결하고 상태를 갱신한다. 오탈자·잘못된 링크 수정과 의미를 보존하는 문서 이관은 정책 변경과 구분한다.
- 중요한 새 결정·기존 결정 변경은 대안과 영향을 논의하고 명시적 동의 후 Accepted로 기록한다. 미확정안은 `docs/proposals/`에 둔다. 정책 변경 시 이전/후속 결정과 상태를 연결하고 영향받는 기준 문서를 갱신한다.
- 문서 축약·이관은 정책 대체와 구분한다. ID·상태·대체 관계와 중요한 위험 수용 근거를 보존하고 기존 링크를 새 위치로 연결한다.

새 ADR은 결정일·상태·동의 근거, 배경, 결정과 이유, 핵심 대안·단점, 미검증 가정·재검토 조건, 대체 관계를 필요한 만큼 작성한다. 비용·일정·사용자 경험·데이터·운영 영향은 실제로 관련 있는 내용만 적는다.
