# Contributing

1인 개인 프로젝트 기준이다([DEC-0028](docs/DECISIONS.md#dec-0028)). 문서별 기록 위치는 [AGENTS.md](AGENTS.md)의 문서 책임 표를 따른다.

## Branch and PR

- `main`이 유일한 장기 브랜치다. 작업은 `main`에서 만든 short-lived 브랜치에서 한다.
- 브랜치 이름은 `feature/`, `fix/`, `docs/`, `refactor/`, `test/`, `chore/` 접두사와 kebab-case를 쓴다([NAMING](docs/design/NAMING.md)). `validate-pr-source`가 이 규칙과 같은 저장소 여부를 검사한다.
- `main`으로 PR을 열고 필수 CI가 통과하면 병합한다. PR에는 범위, 검증 결과, Contract/Architecture 영향을 적는다.

## Commit and quality

- Conventional Commits를 사용한다 (`feat`, `fix`, `docs`, `refactor`, `test`, `chore`).
- 기능·Contract·문서·검증 등 하나의 검토 가능한 관심사마다 커밋을 나누고, 각 커밋은 독립적으로 설명하고 되돌릴 수 있게 유지한다.
- 커밋 전에 `.githooks/pre-commit`(민감 파일명 + Gitleaks)을 통과한다. 처음 clone하면 `git config --local core.hooksPath .githooks`를 실행한다.
- Secret, Access Key, Token, 정책 원문은 커밋하지 않는다. 이 저장소는 공개다.

## Change-to-document rule

| Change | Update in the same PR |
| --- | --- |
| 제품 범위·사용자 가치·MVP | `docs/PRD.md` |
| Architecture, AWS, Security, Storage, Deployment | `docs/DESIGN.md`, 필요 시 C4와 결정 기록 |
| Endpoint, Request/Response, Error | `docs/design/API.md`, `packages/contracts/`, Contract Test |
| Domain/AI structured output schema | `docs/design/CONTRACTS.md`, `packages/contracts/`, Contract Test |
| 지속적인 선택과 그 이유 | `docs/DECISIONS.md`, 필요 시 `docs/adr/` |
| Branch/PR/CI 운영 | 이 문서, 필요 시 PR Template |
| 작업 상태·진행 | `docs/TASKS.md`, `docs/PROGRESS.md` |

## Release gate

릴리스(태그)를 만들기 전에 아래 항목을 확인한다. 항목은 ADR-0021이 확정한 게이트다.

- [ ] 데모 폐루프 E2E 실행 기록 (Assessment → Finding → Remediation → PR → plan → 승인 → apply →
      Post-Deploy Verification)
- [ ] Golden Dataset 반복 평가 리포트와 목표(정확도·Evidence·일치율 90% 이상, Score 편차 ±10점)
      대비 결과. 세 관점 중 측정하지 못한 관점이 있으면 통과 근거로 쓰지 않는다
- [ ] 관측·비용 기록: `EXECUTION_ERROR` 0건, DLQ depth 0, Queue age 최대값, checkpoint 재개 횟수,
      plan/apply 실패 0건, 승인 없는 apply 0건, 역할별 Bedrock 호출·토큰·p95 지연, 데모 1회 비용
- [ ] Secret scan과 Python/Frontend/Terraform 검증 결과
- [ ] 문서 Freshness: `docs/PRD.md`, `docs/DESIGN.md`, `docs/design/API.md`, `docs/design/CONTRACTS.md`,
      `docs/design/DATABASE.md`, `docs/design/architecture/`, `docs/adr/`가 구현과 일치하고 `Proposed` 결정이
      남아 있지 않음
- [ ] `docs/TASKS.md`에서 릴리스 범위의 P0·P1 작업이 `DONE`

품질 목표 미달 시 목표를 낮추지 않는다. rubric/prompt/Golden Case를 재고정해 재실행하거나
ADR-0003 절차로 Anchor 전환을 결정한다.
