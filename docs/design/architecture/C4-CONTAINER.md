# C4 Container

- React SPA: S3 + CloudFront 정적 호스팅
- Cognito: 사용자 인증 및 JWT 발급
- API Gateway + API Lambda: JWT/RBAC, Domain API, Job/Outbox orchestration. 모든 라우트를 Lambda
  하나(`ApiRuntimeFunction`)가 처리하며 `/orchestrate`의 LangGraph Parent도 이 함수 안에서 실행된다.
  Outbox Sweeper Lambda가 EventBridge 스케줄로 미전송 `WorkflowTask`를 재전송한다.
- LangGraph + Bedrock: 자연어 Orchestrator와 Policy Q&A를 함께 맡는 Parent. Assessment,
  Remediation, Deployment Worker는 LangGraph를 쓰지 않는다([DEC-0029](../../DECISIONS.md#dec-0029)).
  각 역할은 Golden Dataset으로 승인된 Model Profile을 사용한다.
- SQS + Worker Lambda: Assessment, Remediation, Deployment Queue별 resumable Task 실행;
  DynamoDB checkpoint에서 재개하고 3분 전 checkpoint 후 재큐잉. C는 Assessment/Remediation
  Agent와 Worker orchestration을 소유하고, Remediation Worker는 stored `RemediationDecision`으로
  injected D Patch/Sync port만 호출한다. D는 live GitHub/Terraform adapter와 Deployment Worker를 소유한다.
- EventBridge: GitHub Actions OIDC의 Apply 완료 Event(`terraform-apply-completed`)를 Apply
  Completion Lambda로 전달하고, 이 Lambda가 검증 좌표를 예약한 뒤 Deployment Queue에
  `APPLY_COMPLETED`를 보낸다. Plan은 Deployment Worker가 dispatch하고 run 완료를 폴링한다. Event는
  신호이며 상태 정본이 아니다. D Deployment Worker가 `run_id`로 Actions run을 다시 읽어 workflow,
  repository, `ref`, conclusion, plan artifact digest를 대조한 뒤에만 상태를 전이한다
  (ADR-0019, `Accepted`)
- Terraform state (M3 계획): 고객 bootstrap stack이 만드는 별도 S3 state bucket과 DynamoDB lock
  table. state key는 `(repository_id, workspace)`로 분리하고(workspace 이름은
  `{customer_id}-{repository_id}`), plan 시점 state `lineage`·`serial`을 Deployment record에 기록해
  apply 전 두 값을 함께 재검증한다 (ADR-0019, `Accepted`)
- 고객 repository workflow (M3 계획): plan/apply workflow는 `ci/terraform/` template을 고객 관리자가
  1회 수동 설치한다. GitHub App은 `contents`/`pull_requests` write만 갖고 `workflows: write`는 갖지
  않는다 (ADR-0019, `Accepted`)
- Policy Ingestion: 고객 정책 원본을 customer-scoped S3에 보관하고, Worker Lambda의
  형식 판정·Parser(`apps/backend/policy/ingestion/`, 표준 라이브러리 전용)가 정규화 Artifact를
  만든다. 추출 텍스트는 정규화 Artifact에만 존재하고 Queue/DynamoDB에는 hash만 흐른다.
  `DynamoDbPolicySourceUploadRepository`가 server-issued upload session, exact S3 version
  finalization, normalized Artifact와 customer-scoped ingestion state write를 담당한다. 업로드·
  처리·후보·승인 라우트가 API Lambda에 연결돼 있고, Rule 후보 추출은 전용 Role의 Policy Authoring
  Queue/Worker가 맡는다(ADR-0023, `docs/design/POLICY_INGESTION.md`).
- DynamoDB/S3: 상태·메타데이터 및 Artifact 저장
- CloudWatch/CloudTrail: 운영·감사 관측
- GitHub App/Actions: Customer IaC PR, OIDC plan/apply
