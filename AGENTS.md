# Govlens 에이전트 안내

문서는 `docs/`에 두고 파일명은 대문자와 `.md` 확장자를 사용한다(날짜·측정 기록인 `docs/worklogs/`·`docs/evaluations/data/`는 소문자 예외). `AGENTS.md`·`README.md`·`CLAUDE.md`는 기존 위치에 유지한다.

## 제품 불변식

- AI와 Tool은 Customer, AWS Account, Repository, Policy Profile Scope 밖으로 접근할 수 없다.
- AWS Resource Tool은 읽기 전용이다. 실제 인프라 변경은 승인된 `commit_sha`와 `plan_hash`를 검증한 뒤 Human Approval 및 GitHub Actions를 통해서만 수행한다.
- 정책 원문은 저장소에 커밋하지 않는다. 원문은 로컬 `policies-local/`(Git 제외)에 두고, 저장소에는 Rule 정의와 `SourceReference` locator만 둔다. **이 저장소는 공개다.**
- `policies-local/`과 `fixtures/rules/`는 개발 seed일 뿐 운영용 고객 정책 입력이 아니다. 사용자 정책은 [POLICY_INGESTION.md](docs/design/POLICY_INGESTION.md)의 업로드 → 검증 → 형식별 파싱 → 정규화 → 사람 승인 경계를 통과해야 한다. 지원 형식은 그 문서의 allow-list가 전부이며, 형식을 늘리려면 문서와 Contract를 같은 변경에서 갱신한다.
- 사실은 코드가, 해석만 모델이 판정한다. 근거가 없으면 PASS가 아니라 미판정이다([ADR-0024](docs/adr/ADR-0024-scoring-boundary-by-meaning.md)).
- 실행 가능한 Contract(`packages/contracts/`)와 문서가 충돌하면 Contract를 우선하고 문서를 같은 변경에서 동기화한다.

## 브랜치와 검증

- `main`에서 `type/kebab-case` 작업 브랜치(`feature/`, `fix/`, `docs/`, `refactor/`, `test/`, `chore/`)를 만들고 `main`으로 PR을 열어 CI 통과 후 병합한다. 상세는 [CONTRIBUTING.md](CONTRIBUTING.md).
- 개발 환경: `uv venv .venv && uv pip install --python .venv/bin/python -r requirements-dev.txt -r apps/backend/requirements.txt` (이 머신의 시스템 Python에는 `ensurepip`이 없다).
- Python 변경: `.venv/bin/python -m ruff check .`, `.venv/bin/python -m ruff format --check .`, 관련 `unittest discover -s tests/<unit|contract|integration|security>`.
- Frontend 변경: `apps/frontend`에서 `npm ci && npm run build`.
- Terraform/CloudFormation 변경: `fmt`·`validate`, `cfn-lint`, `tests/security/test_cloudformation_security.py`.
- CI: `python-checks`, `frontend-checks`, `cloudformation-checks`, `m0-lambda-package`, `secret-scan`, `validate-pr-source`(`.github/workflows/`).

<a id="document-ownership"></a>

## 문서별 책임과 중복 방지

필요한 문서만 읽는다. 아래 표에서 작업에 맞는 문서의 관련 절만 연다. 중요도보다 문서가 답하는 질문으로 기록 위치를 정하고, 같은 기능도 제품 약속·선택 이유·구현 방법을 나눠 각 상세를 한 곳에서 관리한다.

| 작업 | 기준 문서 | 목적과 기록할 내용 | 다른 문서로 연결할 내용 |
| --- | --- | --- | --- |
| 제품 동작·정책 설계·변경 | [PRD.md](docs/PRD.md) | **무엇을 제공하고 어떤 조건을 지켜야 하는가.** 사용자 동작·예외, 보관/삭제·권한·비용 등 제품 약속과 제약, 요구사항·목표·미정 항목 | 선택 이유·대안은 결정 기록, API 필드·테이블·잠금 등 구현 방법은 설계로 연결한다. 구현 완료·테스트 결과를 관리하지 않는다. |
| 작업 선택·구현·완료 판정 | [TASKS.md](docs/TASKS.md) | **무슨 작업이 남았고 무엇을 확인해야 완료인가.** 작업 ID·우선순위·의존성·상태와 검증 가능한 수용 기준 | 필요할 때 관련 PRD 절을 읽는다. 요구사항·설계 상세를 복사하지 않고 해당 절과 검증 근거를 연결한다. 수용 기준은 확인할 동작·경계 중심으로 적는다. |
| 현재 진행 상황 확인 | [PROGRESS.md](docs/PROGRESS.md) | **현재 어디까지 진행됐는가.** 구현·검증 범위와 남은 일의 요약 | 작업 상태의 기준은 TASKS, 상세 검증 결과는 worklog로 연결한다. 설계·결정 원문을 반복하지 않는다. |
| 특정 날짜의 작업·검증 확인 | `docs/worklogs/YYYY-MM-DD.md` | **그날 무엇을 했고 어떤 조건에서 무엇을 확인했는가.** 작업·검증 조건과 결과, 한계·문서 대조 결과·트러블슈팅 링크 | 현행 정책·설계의 상세는 해당 기준 문서로 연결한다. |
| 구조·데이터 흐름·API/DB 계약·기술적 가정 확인 | [DESIGN.md](docs/DESIGN.md)와 `docs/design/`의 상세 설계 문서(아래 표) | **요구사항을 어떻게 구현하며 구성 요소가 어떻게 협력하는가.** DESIGN은 전체 구조·경계·핵심 흐름·제약의 진입점. 상세 설계는 아래 표에서 해당 문서만 읽는다. | 제품 정책은 PRD, 선택 이유는 결정 기록으로 연결한다. 상세 문서의 내용을 DESIGN에 다시 쓰지 않는다. 승인된 미구현 설계·현재 구현·미정 사항을 구분하고 날짜별 작업 이력은 넣지 않는다. |
| 기존 결정 확인·변경·기록 | [DECISIONS.md](docs/DECISIONS.md) | **무엇이 언제 승인됐고 어떤 결정이 유효한가.** DEC ID·결정일·상태·대체 관계·ADR 링크와 기록·변경 규칙. 별도 ADR이 없는 작은 결정만 결론·핵심 이유를 짧게 기록 | 해당 ID·연결 ADR·기록 규칙을 읽는다. ADR이 있으면 식별 가능한 요약과 링크만 두고 대안·영향이나 PRD·설계의 상세 계약을 다시 쓰지 않는다. |
| 중요한 선택의 이유·절충 확인 | `docs/adr/`의 해당 ADR ([양식](docs/adr/_TEMPLATE.md)) | **왜 이 선택을 했고 어떤 절충을 승인했는가.** 결정 당시 배경·선택·동의 근거·대안·영향·위험·재검토 조건 | 의미를 식별하는 핵심 조건은 남기되 전체 제품 명세·API/DB 명세·작업 완료 기준·최신 테스트 결과는 복사하지 않는다. 현행 요구사항·설계·검증 근거로 연결한다. |
| 트러블슈팅 선별·작성·재발 확인 | [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | **어떤 문제를 어떻게 진단·해결하고 재발을 확인하는가.** 기록 기준·양식·관련 사례 | 당일 작업·검증 결과는 worklog로 연결한다. |
| 과거 변경 추적 | [CHANGELOG.md](docs/CHANGELOG.md) | **사용자에게 의미 있는 무엇이 바뀌었는가.** 날짜별 변경 요약 | 현재 진행 상태는 PROGRESS, 상세 검증 결과는 worklog, 정책·설계·이유는 각 기준 문서로 연결한다. |
| 프로젝트 소개·실행·설치 확인 | [README.md](README.md) | **무엇을 하는 프로젝트이며 어떻게 설치·실행하는가.** 소개·설치·실행 절차 | 상세 정책·설계는 해당 문서로 연결한다. 실행 절차를 설계에 복사하지 않는다. |
| 미승인 후보 조사·비교 | `docs/proposals/` ([색인](docs/proposals/INDEX.md)) | **무엇을 제안하며 어떤 근거로 비교하는가.** 미승인 후보·조사·비교 과정 | 채택된 제안은 유효한 요구사항·결정·설계로 연결하고 남은 미승인 범위를 표시한다. 과거 후보를 현행 명세처럼 유지하지 않는다. |

### 상세 설계·운영 문서

| 질문 | 문서 |
| --- | --- |
| HTTP API와 오류 형식 | [API.md](docs/design/API.md) |
| Domain/AI structured-output Schema | [CONTRACTS.md](docs/design/CONTRACTS.md)와 `packages/contracts/` (실행 가능한 Contract가 우선) |
| DynamoDB/S3 Artifact 모델과 접근 패턴 | [DATABASE.md](docs/design/DATABASE.md) |
| 사용자 정책 업로드·문서 형식·파싱·승인 경계 | [POLICY_INGESTION.md](docs/design/POLICY_INGESTION.md) |
| System Context/Container (C4) | [architecture/](docs/design/architecture/) |
| 이름 규칙(브랜치·커밋·코드·AWS 리소스) | [NAMING.md](docs/design/NAMING.md) |
| 평가 품질 측정·모델 선택 근거 | [evaluations/](docs/evaluations/), [M4-GOLDEN-RELEASE-GATE.md](docs/evaluations/M4-GOLDEN-RELEASE-GATE.md) |
| 고객 sandbox 연동·배포·인증 확인 | [sandbox/](docs/sandbox/) — 시작은 [CUSTOMER_SANDBOX_ONBOARDING.md](docs/sandbox/CUSTOMER_SANDBOX_ONBOARDING.md), 런타임 연결은 [M1-SANDBOX-INTEGRATION.md](docs/sandbox/M1-SANDBOX-INTEGRATION.md) |
| 데모 실행·데모용 IaC·정책 커버리지 | [demo/](docs/demo/) — 시작은 [M4-DEMO-RUNBOOK.md](docs/demo/M4-DEMO-RUNBOOK.md) |
| 브랜치·PR·커밋·릴리스 게이트 | [CONTRIBUTING.md](CONTRIBUTING.md) |
| 팀 프로젝트 기간 기록(읽기 전용) | [archive/](docs/archive/) — 현행 기준이 아니다. 필요한 내용은 현행 문서로 옮기고 링크한다 |

- **계약의 기준 위치:** 사용자에게 하는 약속(예: “로그인은 마지막 이용 후 30일 유지”)은 PRD, 그것을 어떤 저장/트랜잭션으로 보장하는가는 설계, 왜 이 방식과 절충을 선택했는가는 결정 기록에 둔다. ADR에 조건이 필요하면 결정 당시 핵심 조건으로 짧게 적고 현행 상세는 PRD로 연결한다.
- **허용하는 요약:** 다른 문서에는 이해에 필요한 짧은 요약·ID·링크만 둔다. 같은 정책 표·필드 목록·처리 절차·수용 기준을 여러 문서에 복사하지 않는다. 정확한 스키마·타입은 코드와 연결하고 문서에는 의미·관계·제약을 설명한다. 코드와 설계가 다르면 차이를 표시하며 구현이 승인된 계약을 자동으로 대체하지 않는다.
- **변경 순서:** 승인 여부가 필요한 변경은 아래 논의 절차를 먼저 따른다. 승인 후 바뀐 내용의 기준 문서(제품 약속은 PRD, 구현 계약은 설계)를 갱신하고 결정 기록의 상태·연결, 영향받은 TASK 수용 기준을 맞춘다. PROGRESS·CHANGELOG·worklog에는 각 목적에 맞는 요약·근거를 남긴다. 모든 변경을 모든 문서에 적을 필요는 없다.
- **충돌과 이관:** 최신 파일이라는 이유나 문서 종류만으로 충돌을 덮어쓰지 않는다. 유효한 결정·후속 승인·현재 요구사항과 구현을 대조하고 중요한 계약 충돌은 논의한다. 단순 이관에서는 DEC ID·상태·동의/위험 수용 근거·링크를 보존한다. 기존 ADR의 역사적 판단을 현재 구현에 맞춰 다시 쓰지 않고 후속 결정과 대체 범위를 연결한다.

아키텍처, 주요 기능, 배포 방식, 사용자 데이터 등 영향이 큰 **새 결정**이나 채택된 결정의 변경·충돌은 먼저 논의한다. 관련 기존 결정과 근거를 확인하고, 대안별 장단점 및 비용·일정·사용자 경험·데이터·운영에 대한 영향을 구체적으로 제시한다. 사용자와 결정 이유까지 합의하고 명시적 동의를 받은 뒤에만 해당 결정과 관련 문서·구현을 변경한다. 동의 전에는 충돌하지 않는 조사와 제안서 작성만 진행하며 미확정안을 채택된 결정처럼 기록하지 않는다. 단순한 문구 정리나 기존 결정 안에서의 구현은 이 절차의 대상이 아니다.

문서를 수정할 때는 위 표에서 해당 내용의 기준 문서를 먼저 갱신한다. 요구사항이 바뀌면 관련 작업의 완료 기준을 확인한다. 결정의 ADR 분리 기준·기록 형식·대체 절차는 결정 문서의 기록·변경 규칙을 따른다. 사용자에게 의미 있는 변경은 변경 이력에, 현재 상태는 진행 현황에, 날짜별 작업 결과와 트러블슈팅 링크는 해당 날짜의 worklog에 기록한다. 같은 설명을 여러 파일에 복사하지 않는다.

그날 작업을 마무리할 때는 **그날 바뀐 파일과 직접 연결된 문서만** 대조한다. PRD 요구사항과 해당 TASK의 완료 기준, 승인된 DECISION과 영향받은 문서, TASK 상태와 검증 근거, PROGRESS의 현재 상태, CHANGELOG의 의미 있는 변경을 확인한다. 링크·작업 ID·상태의 불일치도 검사한다. 점검 결과와 남은 불일치는 그날의 worklog에 남긴다. 작업하지 않은 날에는 파일을 만들지 않는다.

외부 자료를 참고할 때는 관찰·추정·미확인을 구분하고 출처와 한계를 남긴다. 구현 완료는 해당 작업의 수용 기준을 확인한 뒤 표시한다. 테스트 환경의 장애 실험과 실제 운영 장애를 구분하며 측정 결과에는 조건과 한계를 남긴다.

커밋 전에는 스테이징된 파일 목록과 diff를 확인하고 `.githooks/pre-commit`의 민감 파일명·Gitleaks 검사를 통과시킨다. `.env`와 실제 키·토큰·개인 키·계정 정보는 추적하지 않는다. 검사 통과만으로 안전을 단정하지 말고, 코드의 비밀값 노출과 사용자 데이터 접근·로그 기록도 검토한다.
