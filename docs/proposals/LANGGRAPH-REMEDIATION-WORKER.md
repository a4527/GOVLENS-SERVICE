# 제안: Remediation Worker를 LangGraph 그래프로 옮긴다

- 상태: 미승인 제안 (2026-11-23) · 관련: [ADR-0005](../adr/ADR-0005-serverless-workflow-execution.md), [ADR-0013](../adr/ADR-0013-sqs-resumable-worker-execution.md), TASKS F-07

## 배경

ADR-0005는 Worker를 "LangGraph subgraph"로 적었지만 구현은 일반 Python이다. LangGraph는
Parent Orchestrator(`agent/graphs/parent_graph.py`)만 쓴다. 세 Worker 중 모델이 여러 번 오가는
단계는 Remediation뿐이고, Assessment는 리소스별 분할, Deployment는 모델 없는 이벤트 처리다.

## 현재 Remediation 흐름

```text
RemediationWorker.handle (apps/backend/remediation/worker.py)
  task 검증 → DynamoDB에서 work 재조회(revision 조건) → 저장된 판정 확인
  → BedrockPatchGenerator.generate (bedrock.py)
      ├─ IaC 문서 읽기
      ├─ _bound_changes: for 2회
      │     모델 호출 → 경로 경계 검사 → validate_terraform_changes
      │     실패 사유가 "리소스 블록 누락"이면 빠진 블록 이름을 hint로 다시 묻는다
      └─ patch 인코딩·digest·S3 저장
  → patch 결과 저장 → PR 열기 → PR 결과 저장
```

"생성 → 검증 → 실패하면 이유를 알려 다시 생성" 반복은 이미 `_bound_changes`의 `for` 루프로 있다
(`_PATCH_ATTEMPTS = 2`).

## 제안하는 모양

```text
StateGraph(RemediationState)
  load_work → check_decision → read_iac → generate_patch → validate_patch
                                              ▲                 │
                                              └── 누락 블록 hint ┤ (최대 N회)
                                                                ▼
                                       store_patch → open_pr → store_pr → END
```

- 노드는 지금 함수를 그대로 감싼다. 경계 검사·Contract 검증·revision 조건은 바뀌지 않는다.
- LangGraph checkpointer는 쓰지 않는다. 그래프는 Lambda 한 번 안에서 끝나고, 상태 정본과 재개는
  ADR-0013대로 DynamoDB Job/revision이 맡는다.
- Parent가 쓰는 LangGraph Lambda Layer(`scripts/build-langgraph-layer.sh`)를 Remediation Worker에도 붙인다.
- 기존 `tests/unit`의 Remediation 테스트가 수정 없이 통과해야 한다.

## 얻는 것과 잃는 것

| 얻는 것 | 잃는 것 |
| --- | --- |
| 반복·분기가 코드 구조로 보이고 Parent와 같은 방식이 된다 | 이미 있는 루프를 옮기는 것이라 동작상 새 기능은 없다 |
| 새 검증 단계(예: `terraform validate`, 정적 보안 검사)를 노드 하나로 끼우기 쉽다 | Layer 크기·콜드 스타트 증가, 의존성 하나가 Worker 경로에 들어온다 |
| LangSmith 등으로 노드별 입력·출력·지연을 볼 수 있다(관측 O-03/O-04와 겹침) | 고객 IaC·정책이 외부 추적 서비스로 나가지 않게 따로 막아야 한다 |

## 판단 기준

- 검증 단계를 더 늘릴 계획이 있으면 채택할 가치가 있다.
- 지금 두 번 묻는 루프로 충분하면 채택하지 않고 ADR-0005 문구를 구현에 맞추는 편이 싸다.
