# Cloud Governance & Compliance Agent

> AWS와 Terraform 환경을 정책·ISMS-P 기준으로 평가하고, **Finding → Remediation → 승인된 Apply → 재평가**까지 폐루프로 연결하는 Customer-Deployed 거버넌스 플랫폼

<p>
  <img alt="status" src="https://img.shields.io/badge/status-MVP-blue">
  <img alt="python" src="https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white">
  <img alt="react" src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black">
  <img alt="aws" src="https://img.shields.io/badge/AWS-Serverless-FF9900?logo=amazonaws&logoColor=white">
  <img alt="terraform" src="https://img.shields.io/badge/Terraform-IaC-7B42BC?logo=terraform&logoColor=white">
  <img alt="license" src="https://img.shields.io/badge/license-Internal-lightgrey">
</p>

---

## 이 프로젝트는 무엇인가

Terraform 기반 IaC, 실제 AWS 상태, 그리고 사내 정책·ISMS-P 요구사항을 **함께** 평가하는 플랫폼입니다. 단순히 규칙을 나열하는 것이 아니라, 실제 AWS 환경에서 아래 폐루프를 완주하는 것을 목표로 합니다.

```text
Policy / ISMS-P + Customer IaC + AWS Actual
   → Initial Assessment (IaC 준수 / Actual 준수 / Drift)
   → Finding / Evidence / Readiness Score / Coverage
   → Terraform Remediation → PR → plan
   → Human Approval → GitHub Actions apply → Re-Assessment
```

핵심 가치는 **AI 평가의 정확성·일관성·근거 추적성**을 검증하면서, 사람의 승인 없이는 어떤 인프라 변경도 일어나지 않는 안전한 경계를 지키는 데 있습니다.

### 설계 원칙

- **Customer-Deployed** — 플랫폼은 고객 AWS 계정(`us-east-1`)에 배포됩니다.
- **AWS + Terraform 집중** — 대상 리소스는 EC2, RDS, ALB, S3.
- **AI는 경계 안에서만 판단** — 적용할 Rule은 승인된 Profile이, Severity는 승인된 Rule이 정합니다. AI는 허용된 범위 안에서 판정(status), 0–100 점수, Rationale, 허용된 Evidence 부분집합만 선택합니다.
- **사실은 코드가, 판단만 모델이** — 권한·범위·스키마·Evidence 검증·Coverage 계산은 결정적 코드가 담당합니다.
- **사람 승인이 있어야 변경** — 고객 워크로드 변경은 Human Approval 뒤 GitHub Actions가 수행합니다.
- **MVP 범위** — RAG, Vector DB, Bedrock Knowledge Base는 사용하지 않습니다.

---

## 아키텍처 개요

```text
React SPA (S3 + CloudFront)
  → Cognito (JWT)
  → API Gateway
      ├─ Parent Router Lambda      (LangGraph: 자연어 라우팅 + Policy Q&A, 동기 max 30s)
      ├─ Assessment API  → SQS → Assessment Worker   (Python, DynamoDB checkpoint)
      ├─ Remediation API → SQS → Remediation Worker  (Python, DynamoDB checkpoint)
      └─ Deployment API  → SQS → Deployment Worker    (Python, DynamoDB checkpoint)

AI / Tools : Bedrock 역할별 Model Profile, Policy Context, AWS Resource Tool(RO), GitHub App
State      : DynamoDB (Job / checkpoint / metadata)
Artifact   : S3 (policy 원본 / IaC·AWS snapshot / report / patch / plan)
Deploy     : GitHub App + GitHub Actions(OIDC) CI / plan / approved apply
             → EventBridge → Deployment Queue
```

- **명시적 UI/API 요청**은 해당 Workflow로 직접 진입합니다.
- **자연어 요청**만 Parent Orchestrator가 의도·후보 Scope를 해석해 적절한 Workflow로 라우팅합니다.
- 상태의 정본은 DynamoDB와 S3이며, SQS는 전달 수단입니다.

자세한 내용은 [기술 설계 문서](docs/DESIGN.md)를 참고하세요.

---

## 기술 스택

| 영역 | 사용 기술 |
| --- | --- |
| Frontend | React 19, TypeScript, Vite |
| Backend | Python 3.12+, AWS Lambda |
| AI / Orchestration | Amazon Bedrock, LangGraph |
| Storage | DynamoDB, Amazon S3 |
| Auth / Edge | Cognito, API Gateway, CloudFront |
| Async | SQS (+ DLQ), EventBridge |
| IaC / Deploy | Terraform, CloudFormation, GitHub Actions (OIDC) |
| Quality | Ruff, unittest, cfn-lint, Gitleaks |

---

## 평가 모델

- **평가 단위**: `Resource × Rule`
- **관점**: `IAC`, `AWS_ACTUAL`, `DRIFT`
- **상태**: `PASS`, `FAIL`, `MANUAL_REVIEW`, `INSUFFICIENT_EVIDENCE`, `OUT_OF_SCOPE`, `EXECUTION_ERROR`
- **점수**: 결과별 점수는 판정의 재진술(PASS 100, FAIL 0, 판정이 아닌 상태 0)이고, Readiness는 판정된 결과만 severity로 가중 평균합니다. 사실이 명확한 항목은 코드가 결정적으로 판정하고, 해석이 필요한 항목만 모델이 판단합니다.
- **Readiness Score**: 공식 인증 점수가 아닌 `ISMS-P Readiness Score`이며, Coverage는 AI가 아니라 코드가 기계적으로 계산합니다.
- Evidence는 정책 원문 위치 또는 content hash를 참조해 추적성을 유지합니다.

---

## 프로젝트 구조

```text
GOVLENS-SERVICE/
├── apps/
│   ├── backend/        # 기능별 Lambda (auth, jobs, assessment, policy, remediation, deployment)
│   └── frontend/       # React SPA 콘솔
├── agent/              # LangGraph Parent Orchestrator, Resource/GitHub Tool
├── packages/           # 공용 Contract, 도메인 스키마
├── infrastructure/     # CloudFormation, IAM, 파라미터
├── ci/                 # Terraform plan/apply template
├── fixtures/           # 개발용 seed (rules 등)
├── docs/               # PRD, DESIGN, API, CONTRACTS, DATABASE, ADR
├── tests/              # unit / contract / integration / security
└── scripts/            # 운영·측정 스크립트
```

---

## 시작하기

### 사전 요구사항

- Python 3.12 이상
- Node.js 24 (Frontend, CI 기준 24.14.0)

### Backend (Python) 부트스트랩

```bash
uv venv .venv   # 시스템 Python에 ensurepip이 있으면 python3 -m venv .venv 도 가능
uv pip install --python .venv/bin/python -r requirements-dev.txt -r apps/backend/requirements.txt

# 린트
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
```

테스트 명령은 아래 [테스트 · CI](#테스트--ci)를 참고하세요.

### 비밀값과 커밋 전 검사

`.env`는 로컬 전용이며 Git에서 제외합니다. 변수 이름과 안전한 예시는 [.env.example](.env.example)을 따릅니다.

[Gitleaks](https://github.com/gitleaks/gitleaks#installing)를 설치하거나 실행 파일을 `.tools/gitleaks`에 둡니다. Gitleaks가 없으면 커밋과 push가 차단됩니다. 저장소를 받은 뒤 한 번 훅을 켭니다.

```bash
git config --local core.hooksPath .githooks
```

커밋 훅은 민감한 파일명과 스테이징된 비밀값을, push 훅은 추적 중인 민감 파일명과 Git 전체 이력을 검사합니다. 과거 이력의 확인된 오탐은 `.gitleaksignore`에 이유와 함께 등록합니다. GitHub에서는 pull request마다 `.github/workflows/secret-scan.yml`이 같은 검사를 실행합니다.

### Frontend

```bash
cd apps/frontend
npm install
npm run dev      # 개발 서버
npm run build    # 프로덕션 빌드
```

환경 변수는 [`.env.example`](.env.example)을 참고하세요. 실제 값(토큰·시크릿)은 커밋하지 않습니다.

---

## 문서

| 문서 | 내용 |
| --- | --- |
| [PRD](docs/PRD.md) | 제품 가치, 사용자, MVP 범위, 평가 의미 |
| [DESIGN](docs/DESIGN.md) | 아키텍처, AWS, 보안, 워크플로, 관측성 |
| [API](docs/design/API.md) | HTTP API와 오류 형식 |
| [CONTRACTS](docs/design/CONTRACTS.md) | 도메인 / structured-output 스키마 |
| [DATABASE](docs/design/DATABASE.md) | DynamoDB / S3 Artifact 모델과 접근 패턴 |
| [design/](docs/design/) | 위 상세 설계와 정책 수집 경계, 이름 규칙, C4 다이어그램 |
| [sandbox/](docs/sandbox/) · [demo/](docs/demo/) | 고객 sandbox 연동 절차와 데모 실행 런북 |
| [evaluations/](docs/evaluations/) | 평가 품질 측정, 모델 선택, release gate |
| [DECISIONS](docs/DECISIONS.md) · [adr/](docs/adr/) | 결정 목록과 장기 기술 결정(ADR)의 이유 |
| [TASKS](docs/TASKS.md) · [PROGRESS](docs/PROGRESS.md) | 남은 작업과 현재 진행 상태 |
| [CHANGELOG](docs/CHANGELOG.md) · [worklogs/](docs/worklogs/) | 변경 이력과 날짜별 작업·검증 기록 |
| [CONTRIBUTING](CONTRIBUTING.md) | 브랜치, PR, 커밋, 릴리스 게이트 |

작업별로 어떤 문서를 읽고 어디에 기록하는지는 [AGENTS.md](AGENTS.md)의 문서 책임 표가 기준입니다. 팀 프로젝트 기간(~2026-09)의 진행 기록은 [docs/archive/](docs/archive/)에 보존합니다.

---

## API 개요

모든 요청·응답은 버전 관리되는 `packages/contracts/` 스키마를 따릅니다. 인증은 Cognito access-token JWT이며, Backend는 Role과 Customer / Repository / AWS Account Scope를 fail-closed로 검증합니다. `customer_id`, Job ID, status, timestamp 같은 값은 클라이언트가 보낼 수 없고 서버가 verified JWT와 상태에서 결정합니다. 장시간 작업은 `202 Accepted` + `job_id`로 응답합니다.

### 평가 · 작업

| Method | Path | 용도 |
| --- | --- | --- |
| `POST` | `/assessments` | Assessment Job 생성 (승인된 `repository_id`, `policy_profile_id` 지정) |
| `GET` | `/jobs/{jobId}` | Job 상태·결과 조회 |
| `GET` | `/assessments/{assessmentId}` | 결과, Findings, Coverage, Readiness Score 조회 |
| `POST` | `/orchestrate` | 자연어 메시지를 Policy Q&A 답변 또는 워크플로 제안으로 라우팅 |

### 조치 (Remediation)

| Method | Path | 용도 |
| --- | --- | --- |
| `POST` | `/findings/{findingId}/remediations` | 정책 판정 후 Remediation 시작 또는 non-action 보고 |
| `GET` | `/remediations/{remediationId}` | 조치 상태·결과·PR 조회 |
| `POST` | `/remediation-exceptions` | Admin이 만료 필수 예외 승인·등록 |

### 배포 (Deployment)

| Method | Path | 용도 |
| --- | --- | --- |
| `POST` | `/remediations/{remediationId}/deployments` | 승인된 IaC commit으로 Deployment 생성 |
| `GET` | `/deployments/{deploymentId}` | plan 요약, readiness, 승인·진행 상태 조회 |
| `POST` | `/deployments/{deploymentId}/approve` | `commit_sha`·`plan_hash` 재검증 후 승인 |
| `POST` | `/deployments/{deploymentId}/reject` | 배포 거절 (Admin) |
| `GET` | `/deployments/{deploymentId}/verification` | Post-Deploy before/after 비교 조회 |

### 정책 수집 · 관리

| Method | Path | 용도 |
| --- | --- | --- |
| `POST` | `/policy-sources/uploads` | 정책 문서 업로드 세션 생성 |
| `POST` | `/policy-sources/{sourceId}/versions/{version}/process` | 검증·파싱·정규화 실행 |
| `POST` | `/policy-sources/{sourceId}/versions/{version}/candidates` | Rule 후보 추출 요청 |
| `POST` | `/policy-sources/{sourceId}/versions/{version}/approve` | 검토된 Rule version 승인 |
| `POST` | `/policy-profiles` | 승인된 Rule로 versioned Policy Profile 게시 |
| `GET` | `/scope` | 호출자 customer의 assessment scope 대상 조회 |
| `GET` `POST` `DELETE` | `/admin/users` | Admin 전용 사용자 관리 |
| `GET` | `/audit-events` | Admin 전용 감사 이력 조회 |

전체 목록·요청/응답 형식·페이지네이션·오류 규약은 [docs/design/API.md](docs/design/API.md)를 참고하세요.

### 오류 형식

```json
{
  "error": {
    "code": "SCOPE_DENIED",
    "message": "The requested resource is outside the approved scope"
  }
}
```

초기 오류 코드: `UNAUTHORIZED`, `SCOPE_DENIED`, `VALIDATION_ERROR`, `NOT_FOUND`, `CONFLICT`, `EXECUTION_ERROR`.

---

## 평가 워크플로 상세

Assessment는 하나의 이벤트가 아니라 단계로 나뉩니다.

1. **Initial Assessment** — 같은 Terraform 관리 대상에 대해 세 관점을 구분해 평가합니다.
   - `IAC` — 승인 commit의 Terraform 본문 기준 준수 여부
   - `AWS_ACTUAL` — 읽기 전용으로 조회한 실제 AWS 상태 기준 준수 여부
   - `DRIFT` — 위 두 판정의 불일치 (코드가 결정적으로 계산, Readiness 점수에서는 제외)
   - `MANUAL` — 자동 평가할 수 없는 통제는 사람 검토 대상으로 남김

2. **Remediation** — IaC가 안전하지 않으면 원하는 안전한 상태로 Terraform Patch와 PR을 만듭니다. IaC는 이미 안전하고 Actual만 drift된 경우엔 Patch 없이 현재 commit을 동기화 대상으로 삼습니다. 안전한 조치를 만들 수 없으면 `MANUAL_REVIEW`.

3. **Deployment Readiness Validation** — refresh된 Terraform Plan으로 현재 AWS 상태에 안전하게 적용 가능한지 검증합니다. 이 단계는 배포를 막거나 재수정을 요구할 수 있지만 직접 변경하지 않습니다.

4. **Human Approval → Apply** — 승인된 `commit_sha`·`plan_hash`를 apply 직전 재검증한 뒤 GitHub Actions가 적용합니다.

5. **Post-Deploy Verification** — apply 뒤 실제 AWS에 반영됐는지 확인하고 Actual/Drift를 재평가합니다. 원 Assessment를 덮어쓰지 않고 같은 Profile version·Model Profile·rubric으로 실행한 **새 Assessment**로 기록하며, 해소 여부·점수 변화는 AI 판정이 아니라 두 결과의 결정적 비교입니다.

---

## 핵심 개념

| 용어 | 의미 |
| --- | --- |
| **Policy Profile** | 승인된 Rule version 묶음. Assessment 생성 시점에 판본이 고정됩니다. |
| **Rule** | 하나의 통제 항목. 적용 관점(`evaluation_type`)과 Severity를 정의합니다. |
| **Finding** | `FAIL` / `MANUAL_REVIEW` / `INSUFFICIENT_EVIDENCE` 결과에서 만든 actionable projection. |
| **Evidence** | 판정 근거. 정책 원문 위치(`{source_id}@{version}#{locator}`) 또는 `aws:` read locator를 참조. |
| **Readiness Score** | 판정된 좌표(PASS=100, FAIL=0)의 Severity 가중 준수율. 공식 인증 점수가 아닙니다. |
| **Coverage** | `Resource × Rule × Perspective` 평가 계획의 실행률. AI가 아니라 코드가 계산합니다. |
| **decided_by** | 각 결과의 판정 출처 (`CODE` 또는 `MODEL`). 사실은 코드가, 해석은 모델이 판단합니다. |

---

## 테스트 · CI

테스트는 계층별로 나뉩니다.

```bash
for layer in unit contract integration security; do
  .venv/bin/python -m unittest discover --start-directory tests/$layer --pattern 'test_*.py'
done
```

| 계층 | 검증 대상 |
| --- | --- |
| `unit` | 개별 모듈·함수 |
| `contract` | `packages/contracts/` 스키마와 wire shape |
| `integration` | 여러 컴포넌트 결합 |
| `security` | IAM·route allow-list·scope 경계 회귀 |

`main` 대상 PR마다 GitHub Actions 워크플로(`.github/workflows/`)가 Python 검사, CloudFormation lint, frontend 빌드, Lambda 패키지, secret scan, PR source gate를 실행합니다. 모든 PR은 secret scan과 source gate를 통과해야 합니다.

---

## 개발 규칙

1인 개인 프로젝트로 운영합니다([DEC-0028](docs/DECISIONS.md#dec-0028)).

- `main`에서 `feature/`·`fix/`·`docs/`·`refactor/`·`test/`·`chore/` 작업 브랜치를 만들고 `main`으로 PR을 열어 CI 통과 후 병합합니다. 상세는 [CONTRIBUTING](CONTRIBUTING.md).
- 정책 원문은 저장소에 커밋하지 않습니다. 저장소에는 Rule 정의와 `SourceReference` locator만 둡니다.
- AWS Resource Tool은 읽기 전용입니다. 실제 인프라 변경은 승인된 `commit_sha`·`plan_hash` 검증 뒤 Human Approval과 GitHub Actions를 통해서만 수행합니다.
- 영역 경계를 넘는 API·Schema 변경은 `packages/contracts/`와 Contract Test를 같은 변경에서 갱신합니다.

### 구성 요소 영역

코드와 ADR은 팀 프로젝트 기간의 역할 이름(A–D)을 영역 이름으로 그대로 씁니다.

| 영역 | 책임 |
| --- | --- |
| **A — Platform/Backend** | 플랫폼 기반, 사용자, API, durable workflow state |
| **B — Policy/Governance Boundary** | 정책 문서 형식, Rule Registry/Profile/Context, remediation 허용 범위 |
| **C — AI Evaluation & Agent Orchestration** | Assessment/Remediation Agent, 평가 품질·evidence orchestration |
| **D — Integration & Deployment Execution** | GitHub/AWS Tool, Terraform Plan/Apply, Deployment Worker |

---

## 보안 경계

- AI와 Tool은 Customer / AWS Account / Repository / Policy Profile Scope 밖으로 접근할 수 없습니다.
- 고객 워크로드 변경은 사람 승인 뒤에만, GitHub Actions를 통해서만 이뤄집니다.
- 민감한 Prompt·정책 원문·IaC 전체는 로그에서 마스킹하거나 제외합니다.
- 모든 PR은 secret scan과 source gate를 통과해야 합니다.
