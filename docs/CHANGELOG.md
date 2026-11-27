# Govlens 변경 이력

사용자에게 의미 있는 제품 요구사항과 프로젝트 문서·구조의 변경을 날짜별로 기록한다.

## 2026-11-27

- 배포 이름을 Govlens 서비스는 `platform`, 평가 대상은 `workload`로 나누고 마일스톤 번호를 뺐다. GitHub Environment는 `platform-artifact`·`platform-deploy`·`workload-plan`·`workload-apply`, 배포 변수는 `ASSESSMENT_*`, 템플릿은 `platform-bootstrap`·`platform-foundation`·`workload-onboarding`이다([DEC-0031](DECISIONS.md#dec-0031)). 운영 문서는 `docs/sandbox/PLATFORM_DEPLOYMENT.md`·`WORKLOAD_ONBOARDING.md`, `docs/demo/DEMO-*.md`, `docs/evaluations/GOLDEN-RELEASE-GATE.md`로 옮겼다.

## 2026-11-23

- 개인 sandbox를 단일 AWS 계정으로 운영하기로 했다. Foundation은 유지하고 customer-demo workload만 작업일마다 만들고 지운다. 모든 리소스에 공통 태그 `Owner`·`Project`·`Layer`를 붙인다([DEC-0030](DECISIONS.md#dec-0030)).
- Worker는 LangGraph 없이 일반 Python으로 유지하기로 하고 아키텍처 문서를 구현에 맞췄다([DEC-0029](DECISIONS.md#dec-0029)). LangGraph는 자연어 진입점에만 쓴다.
- 문서 구조와 비밀값 검사 훅을 초기화했다.
- 개인 프로젝트로 전환했다. `dev` 브랜치를 없애고 작업 브랜치 → `main` PR로 CI 규칙을 바꿨다([DEC-0028](DECISIONS.md#dec-0028)).
- 상세 설계는 `docs/design/`, sandbox·데모 런북은 `docs/sandbox/`·`docs/demo/`로 묶었다.
- ADR을 `docs/adr/`로 옮기고 결정 목록(`DECISIONS.md`)을 만들었다. 팀 진행 기록은 `docs/archive/`에 보존하고 남은 일은 `TASKS.md`로 옮겼다.
