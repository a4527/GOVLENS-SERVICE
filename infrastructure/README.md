# Infrastructure

CloudFormation packaging, IAM definitions, and deployment parameters for the customer-deployed platform.

## Customer-operated M1 bootstrap

`cloudformation/m1-customer-bootstrap.yaml` is the one-time stack a customer
administrator runs in the target sandbox account before any repository workflow
can access it. It creates a private, versioned Lambda-code bucket, a GitHub
Actions OIDC deployment role, and a CloudFormation execution role. The GitHub
role trusts only the two exact protected Environment subjects supplied to the
bootstrap and can upload only `lambda/m0/*`, manage the one declared foundation
stack, and pass only the execution role to CloudFormation. It has no customer
workload, Secrets Manager, Bedrock, or `sts:AssumeRole` permission.

The bootstrap supports an existing account-level GitHub OIDC provider through
`ExistingGitHubOidcProviderArn`; otherwise it creates one. A customer must run
this stack with its own approved administrator path. It is not run by a local
Agent session or by the repository workflow it enables. Its outputs are the
only AWS identifiers needed by `Deploy M0 Foundation`; see
`docs/sandbox/M1-SANDBOX-INTEGRATION.md` for the complete M1 sequence.

## Customer onboarding and sandbox bootstrap

`cloudformation/customer-onboarding.yaml` turns the manual checklist in
`docs/sandbox/CUSTOMER_SANDBOX_ONBOARDING.md` into one customer-operated stack per Terraform
workload repository: a retained, versioned, TLS-only state bucket and lock table, Plan and Apply
OIDC roles that each trust one exact protected Environment subject, and the cross-account read
role that the platform Worker assumes with a generated External ID (stored in Secrets Manager).
It grants no workload permissions: the customer attaches its own managed policies through
`PlanWorkloadPolicyArns`/`ApplyWorkloadPolicyArns` (the demo repository ships
`onboarding/workload-policy.yaml`). The Worker role must exist first, so deploy it after the
foundation.

`scripts/sandbox-bootstrap.sh` replays the whole path for the single-account sandbox (DEC-0030):
`platform` (bootstrap stack), `foundation` (dispatches the protected workflow; never deploys
locally), `customer` (workload policy + onboarding), and `status`. Each step previews a change set
and asks before executing, tags every stack with `Owner`/`Project`/`Layer`, and takes account and
owner values from the environment.

If the account was cleaned and the foundation stack is gone or broken, its fixed-name retained
resources (metadata table, artifact and audit buckets, CloudTrail trail, Cognito user pool) block a
new deploy. `scripts/sandbox-bootstrap.sh recover-foundation` lists them and, after the typed
resource prefix, deletes the stack and those resources with all their data. It runs only for
`PLATFORM_ENVIRONMENT=sandbox` and refuses a healthy stack unless `FORCE_RECOVER=1`. A customer
environment must not use it: recover there by CloudFormation resource import so audit logs and
assessment history survive.

## M0 foundation contract

The first stack accepts `ProjectName` and `Environment`; it normally derives physical names as
`<project>-<env>-<component>`. The globally named artifact bucket is the explicit exception and
uses `<project>-<env>-artifacts-<account-id>`. The stack creates one metadata DynamoDB table and
one private artifact S3 bucket. The table has on-demand capacity, encryption, point-in-time recovery,
the `expires_at` TTL attribute, and `GSI1`–`GSI3` from `docs/design/DATABASE.md`.

The stack must retain data by default. It must not create customer-workload write permissions:
Agent Runtime and AWS Resource Tool roles are read-only, and Terraform write permissions stay
on the separately approved GitHub Actions OIDC Apply path.

`cloudformation/m0-foundation.yaml` implements the M0 resource skeleton: metadata table,
private versioned artifact bucket, Assessment/Remediation/Deployment queues with DLQs,
Cognito User Pool/client, HTTP API JWT authorizer, Job API Lambda, EventBridge-scheduled Outbox
sweeper Lambda, and Assessment SQS Worker Lambda. The worker is deliberately restricted to the
packaged synthetic S3 Fixture in M0. The HTTP API uses its `$default` stage with auto deployment,
and the User Pool is retained on stack deletion or replacement. `LambdaCodeS3Bucket`,
`LambdaCodeS3Key`, and `LambdaCodeS3ObjectVersion` must identify the exact versioned ZIP built by
`scripts/package-m0-lambda.sh`; the package-validation and deployment workflows pin Python 3.12,
Git attributes normalize text files under `apps/`, `packages/`, and `fixtures/` to LF, and the
script writes sorted entries with fixed metadata for a deterministic hash. It verifies application
imports and the required `fixtures/m0/` files inside the same Python process without an early-exit
shell pipeline. `.github/workflows/deploy-m0-foundation.yml` is the approval-gated
manual GitHub Actions OIDC path. Its preparation job validates the expected AWS account against the
role ARN, STS identity, and artifact-bucket owner; computes the ZIP SHA-256; and conditionally creates
or verifies the matching commit-qualified object version. A second, distinct protected Environment
then requires reviewers to approve that exact commit/key/hash/Version ID before the deployment job
revalidates and pins it in every Lambda resource. Both Environments must be configured with required
reviewers and the same `EXPECTED_AWS_ACCOUNT_ID`. No stack is deployed from a local developer or Agent
session. `AssessmentScopeJson` is a fail-closed, customer-scoped M0 selector map and must be supplied
by the deployment workflow.

Frontend releases use the separate `.github/workflows/deploy-frontend.yml` workflow. It builds
the Vite SPA at an immutable commit, records the archive and `index.html` SHA-256 values, and pauses
at the protected deployment Environment before assuming a frontend-only OIDC role. That role can
write only the configured private SPA bucket and invalidate only the configured CloudFront
distribution; it cannot mutate the foundation stack, API, Cognito, DynamoDB, or runtime roles.
The foundation deploy creates this role only when the protected Environment supplies both
`FRONTEND_SPA_BUCKET_NAME` and `FRONTEND_DISTRIBUTION_ID`. `OIDC_SUBJECT_PREFIX` must carry the
same name-based or immutable-ID subject prefix used by the customer bootstrap role.
`OWNER_TAG` is the non-secret value of the `Owner` stack tag; the deploy job rejects an empty value
and tags the stack with `Owner`, `Project`, and `Layer=foundation` (DEC-0030).

For M1 sandbox frontend testing, the stack also creates Cognito `Admin`/`User` groups and a
Hosted UI domain with Authorization Code OAuth enabled. The customer-operated local-user
handoff and PKCE frontend test are documented in `docs/sandbox/M1-AUTH-FRONTEND-TEST.md`; no user
password is a CloudFormation parameter or repository value.

## Storage hardening and validation

The canonical YAML template protects the metadata table with deletion protection, SSE, PITR,
TTL, and retained replacement/deletion behavior. The account-qualified artifact bucket enables
AES256 encryption, versioning, bucket-owner-enforced ownership, all public-access blocks, and a
retained bucket policy that denies non-TLS requests to the bucket and its objects. Both storage
resources carry Project, Environment, and Component tags.

Artifact bucket object reads and writes are recorded by a retained single-region CloudTrail trail
with log-file validation. The trail selects only `AWS::S3::Object` data events under the artifact
bucket and delivers them to a separate retained, versioned, encrypted, private audit bucket. The
audit destination is deliberately excluded from the data selector to avoid recursive event
collection. CloudTrail data events add event-based cost and retain object-key metadata; sensitive
material must not be embedded in artifact object keys. The customer deployment role must permit
creation and update of the CloudTrail trail and audit destination, and a customer-approved sandbox
run must verify a controlled artifact Get/Put produces a delivered, validated trail record.

M0 Assessment Workers use packaged synthetic fixtures and receive no ArtifactBucket permission.
Before a Worker accesses customer artifacts, its runtime identity must be tenant-scoped as defined
in `docs/adr/ADR-0014-artifact-audit-and-tenant-isolation.md`; a shared `customers/*` role
is not an acceptable tenant isolation boundary.

The stack exposes metadata table and artifact bucket names and ARNs for runtime injection and
least-privilege integrations. `ProjectName` and `Environment` constraints, including the
account-qualified S3 naming exception, are documented in `parameters/README.md` and
`docs/design/NAMING.md`. The non-deploying approval-input checklist and controlled sandbox CloudTrail
acceptance procedure are in `parameters/m0-foundation-sandbox-deployment-runbook.md`; they must be
completed through the protected GitHub Actions path, not from a local developer or Agent session.

Run the same offline CloudFormation validation used by CI without deploying:

```bash
cfn-lint --non-zero-exit-code error \
  infrastructure/cloudformation/m0-foundation.yaml \
  infrastructure/cloudformation/m1-customer-bootstrap.yaml
```
