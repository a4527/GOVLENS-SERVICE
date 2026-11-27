#!/usr/bin/env bash
# Re-runnable single-account sandbox bootstrap (DEC-0030, TASKS V-11).
#
# Replays the customer deployment path in order, skipping what already exists:
#   platform    m1-customer-bootstrap stack (OIDC provider, deploy/CFN roles, Lambda code bucket)
#   foundation  dispatches the protected deploy-m0-foundation workflow (never deploys locally)
#   customer    customer-demo workload policy + customer-onboarding stack
#               (state backend, Plan/Apply OIDC roles, cross-account read role, External ID)
#   status      prints the stack outputs needed for GitHub Environments and Secrets
#   recover-foundation
#               sandbox only: deletes a broken foundation stack and the retained, fixed-name
#               resources it leaves behind (metadata table, artifact/audit buckets, CloudTrail
#               trail, Cognito user pool) so the foundation phase can create them again.
#               DESTROYS sandbox data: assessment history, artifacts, audit logs, users.
#               A customer environment recovers by CloudFormation import instead.
#
# Every stack gets the common tags Owner/Project/Layer. Values that identify the account or
# owner come from the environment, never from this public repository.
#
# Required environment:
#   EXPECTED_AWS_ACCOUNT_ID  12-digit account the current credentials must belong to
#   OWNER_TAG                value of the Owner tag
#   SERVICE_REPOSITORY       owner/name of the platform repository (OIDC subject for deploys)
#   WORKLOAD_REPOSITORY      owner/name of the customer Terraform repository (customer phase)
#   SANDBOX_BUCKET_NAME      the customer-demo sandbox bucket name (customer phase)
# Optional environment:
#   PROJECT_NAME (govlens), PLATFORM_ENVIRONMENT (sandbox), AWS_REGION (us-east-1),
#   CUSTOMER_DEMO_DIR (../customer-demo relative to the repository root),
#   ARTIFACT_ENVIRONMENT (customer-sandbox-artifact), DEPLOY_ENVIRONMENT (customer-sandbox-deploy)
#
# Usage: scripts/sandbox-bootstrap.sh <platform|foundation|customer|status|recover-foundation> [--yes]
#   Without --yes each stack change is shown as a change set preview and needs confirmation.
#   recover-foundation always asks for the typed resource prefix, even with --yes.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
CFN="${ROOT}/infrastructure/cloudformation"

PROJECT_NAME=${PROJECT_NAME:-govlens}
PLATFORM_ENVIRONMENT=${PLATFORM_ENVIRONMENT:-sandbox}
AWS_REGION=${AWS_REGION:-us-east-1}
CUSTOMER_DEMO_DIR=${CUSTOMER_DEMO_DIR:-${ROOT}/../customer-demo}
ARTIFACT_ENVIRONMENT=${ARTIFACT_ENVIRONMENT:-customer-sandbox-artifact}
DEPLOY_ENVIRONMENT=${DEPLOY_ENVIRONMENT:-customer-sandbox-deploy}
export AWS_REGION AWS_DEFAULT_REGION="${AWS_REGION}"

PREFIX="${PROJECT_NAME}-${PLATFORM_ENVIRONMENT}"
BOOTSTRAP_STACK="${PREFIX}-bootstrap"
FOUNDATION_STACK="${PREFIX}-foundation"
WORKLOAD_POLICY_STACK="${PREFIX}-workload-policy"
ONBOARDING_STACK="${PREFIX}-customer-onboarding"

ASSUME_YES=false

die() { echo "error: $*" >&2; exit 1; }
need() { [[ -n "${!1:-}" ]] || die "$1 is required"; }

check_account() {
  need EXPECTED_AWS_ACCOUNT_ID
  need OWNER_TAG
  [[ "${EXPECTED_AWS_ACCOUNT_ID}" =~ ^[0-9]{12}$ ]] || die "EXPECTED_AWS_ACCOUNT_ID must be 12 digits"
  [[ "${OWNER_TAG}" =~ ^[A-Za-z0-9._@+-]{1,128}$ ]] || die "OWNER_TAG has unsupported characters"
  local actual
  actual=$(aws sts get-caller-identity --query Account --output text)
  [[ "${actual}" == "${EXPECTED_AWS_ACCOUNT_ID}" ]] || die "credentials belong to a different account"
}

tags() { echo "Owner=${OWNER_TAG}" "Project=${PROJECT_NAME}" "Layer=$1"; }

# A stack left in REVIEW_IN_PROGRESS by an aborted preview has no resources yet; treat it as
# absent so a re-run still detects reusable resources (e.g. an existing OIDC provider).
stack_exists() {
  local status
  status=$(aws cloudformation describe-stacks --stack-name "$1" \
    --query 'Stacks[0].StackStatus' --output text 2>/dev/null) || return 1
  [[ "${status}" != REVIEW_IN_PROGRESS ]]
}

# Prints the resource changes of the newest change set of a stack.
show_change_set() {
  local change_set
  change_set=$(aws cloudformation list-change-sets --stack-name "$1" \
    --query 'reverse(sort_by(Summaries, &CreationTime))[0].ChangeSetId' --output text)
  [[ -n "${change_set}" && "${change_set}" != None ]] || return 0
  aws cloudformation describe-change-set --change-set-name "${change_set}" \
    --query 'Changes[].ResourceChange.[Action, LogicalResourceId, ResourceType, Replacement]' \
    --output table
}

output() {
  aws cloudformation describe-stacks --stack-name "$1" \
    --query "Stacks[0].Outputs[?OutputKey=='$2'].OutputValue | [0]" --output text
}

# deploy <stack> <template> <layer> <param=value>...
# Creates a change set, shows it, and executes it after confirmation. No-op when unchanged.
deploy() {
  local stack=$1 template=$2 layer=$3
  shift 3
  local -a args=(--stack-name "${stack}" --template-file "${template}"
    --capabilities CAPABILITY_NAMED_IAM --tags $(tags "${layer}")
    --no-fail-on-empty-changeset)
  (($# > 0)) && args+=(--parameter-overrides "$@")
  if [[ "${ASSUME_YES}" != true ]]; then
    aws cloudformation deploy "${args[@]}" --no-execute-changeset
    show_change_set "${stack}"
    read -r -p "Execute the change set above for ${stack}? [y/N] " answer
    [[ "${answer}" == y ]] || die "aborted by user"
  fi
  aws cloudformation deploy "${args[@]}"
}

phase_platform() {
  need SERVICE_REPOSITORY
  local provider_arn="arn:aws:iam::${EXPECTED_AWS_ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"
  local existing_provider=""
  if ! stack_exists "${BOOTSTRAP_STACK}" &&
    aws iam get-open-id-connect-provider --open-id-connect-provider-arn "${provider_arn}" >/dev/null 2>&1; then
    existing_provider=${provider_arn}
  fi
  local code_bucket="${PREFIX}-lambda-code-${EXPECTED_AWS_ACCOUNT_ID}"
  local -a params=(
    "ProjectName=${PROJECT_NAME}"
    "PlatformEnvironment=${PLATFORM_ENVIRONMENT}"
    "FoundationStackName=${FOUNDATION_STACK}"
    "GitHubOidcSubjectPrefix=repo:${SERVICE_REPOSITORY}"
    "ArtifactPreparationEnvironment=${ARTIFACT_ENVIRONMENT}"
    "DeploymentApprovalEnvironment=${DEPLOY_ENVIRONMENT}"
    "ExistingGitHubOidcProviderArn=${existing_provider}"
  )
  # A retained Lambda code bucket without its stack (partial account cleanup) cannot be
  # re-created; the roles-only variant reuses it.
  if ! stack_exists "${BOOTSTRAP_STACK}" && aws s3api head-bucket --bucket "${code_bucket}" \
    --expected-bucket-owner "${EXPECTED_AWS_ACCOUNT_ID}" >/dev/null 2>&1; then
    [[ -n "${existing_provider}" ]] || die "code bucket exists but the OIDC provider does not; create the provider first"
    deploy "${BOOTSTRAP_STACK}" "${CFN}/m1-customer-bootstrap-roles.yaml" bootstrap \
      "${params[@]}" "ExistingLambdaCodeBucketName=${code_bucket}"
  else
    deploy "${BOOTSTRAP_STACK}" "${CFN}/m1-customer-bootstrap.yaml" bootstrap "${params[@]}"
  fi
}

phase_foundation() {
  need SERVICE_REPOSITORY
  stack_exists "${BOOTSTRAP_STACK}" || die "run the platform phase first"
  local deploy_role exec_role code_bucket
  deploy_role=$(output "${BOOTSTRAP_STACK}" GitHubActionsDeploymentRoleArn)
  exec_role=$(output "${BOOTSTRAP_STACK}" FoundationExecutionRoleArn)
  code_bucket=$(output "${BOOTSTRAP_STACK}" LambdaCodeBucketName)
  if [[ "${code_bucket}" == None || -z "${code_bucket}" ]]; then
    code_bucket="${PREFIX}-lambda-code-${EXPECTED_AWS_ACCOUNT_ID}"
  fi
  local scope=${ASSESSMENT_SCOPE_JSON:-}
  [[ -n "${scope}" ]] || scope='{}'
  local -a cmd=(gh workflow run deploy-m0-foundation.yml -R "${SERVICE_REPOSITORY}" --ref main
    -f "stack_name=${FOUNDATION_STACK}" -f "project_name=${PROJECT_NAME}"
    -f "environment=${ARTIFACT_ENVIRONMENT}" -f "stack_environment=${PLATFORM_ENVIRONMENT}"
    -f "artifact_approval_environment=${DEPLOY_ENVIRONMENT}" -f "aws_region=${AWS_REGION}"
    -f "role_to_assume=${deploy_role}" -f "cloudformation_execution_role_arn=${exec_role}"
    -f "lambda_code_s3_bucket=${code_bucket}"
    -f "assessment_scope_json=${scope}")
  echo "The foundation is deployed only through the protected workflow (two Environment approvals)."
  if [[ "${ASSUME_YES}" != true ]]; then
    read -r -p "Dispatch deploy-m0-foundation.yml to ${SERVICE_REPOSITORY}? [y/N] " answer
    [[ "${answer}" == y ]] || die "aborted by user"
  fi
  "${cmd[@]}"
}

phase_customer() {
  need WORKLOAD_REPOSITORY
  need SANDBOX_BUCKET_NAME
  stack_exists "${BOOTSTRAP_STACK}" || die "run the platform phase first"
  local worker_role="arn:aws:iam::${EXPECTED_AWS_ACCOUNT_ID}:role/${PREFIX}-workflow-runtime"
  aws iam get-role --role-name "${PREFIX}-workflow-runtime" >/dev/null 2>&1 ||
    die "foundation Worker role ${PREFIX}-workflow-runtime not found; deploy the foundation first"
  local provider_arn
  provider_arn=$(output "${BOOTSTRAP_STACK}" GitHubOidcProviderArn)
  # The roles-only bootstrap variant has no provider output; the provider ARN is fixed per account.
  if [[ "${provider_arn}" == None || -z "${provider_arn}" ]]; then
    provider_arn="arn:aws:iam::${EXPECTED_AWS_ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"
  fi
  [[ -f "${CUSTOMER_DEMO_DIR}/onboarding/workload-policy.yaml" ]] ||
    die "workload policy template not found under CUSTOMER_DEMO_DIR"

  deploy "${WORKLOAD_POLICY_STACK}" "${CUSTOMER_DEMO_DIR}/onboarding/workload-policy.yaml" \
    customer-onboarding \
    "ProjectName=${PROJECT_NAME}" "PlatformEnvironment=${PLATFORM_ENVIRONMENT}" \
    "SandboxBucketName=${SANDBOX_BUCKET_NAME}" "ApprovedRegion=${AWS_REGION}"
  local plan_policy apply_policy
  plan_policy=$(output "${WORKLOAD_POLICY_STACK}" PlanPolicyArn)
  apply_policy=$(output "${WORKLOAD_POLICY_STACK}" ApplyPolicyArn)

  deploy "${ONBOARDING_STACK}" "${CFN}/customer-onboarding.yaml" customer-onboarding \
    "ProjectName=${PROJECT_NAME}" "PlatformEnvironment=${PLATFORM_ENVIRONMENT}" \
    "GitHubOidcProviderArn=${provider_arn}" \
    "WorkloadRepositorySubjectPrefix=repo:${WORKLOAD_REPOSITORY}" \
    "PlatformWorkerRoleArn=${worker_role}" \
    "PlanWorkloadPolicyArns=${plan_policy}" \
    "ApplyWorkloadPolicyArns=${plan_policy},${apply_policy}"
}

phase_status() {
  local stack
  for stack in "${BOOTSTRAP_STACK}" "${FOUNDATION_STACK}" "${WORKLOAD_POLICY_STACK}" "${ONBOARDING_STACK}"; do
    echo "== ${stack}"
    if stack_exists "${stack}"; then
      aws cloudformation describe-stacks --stack-name "${stack}" \
        --query "Stacks[0].[StackStatus, Outputs[].[OutputKey, OutputValue]]" --output text
    else
      echo "(not deployed)"
    fi
  done
}

# Deletes every object version and delete marker, then the bucket.
empty_and_delete_bucket() {
  local bucket=$1 page
  while :; do
    page=$(aws s3api list-object-versions --bucket "${bucket}" --max-items 1000 \
      --expected-bucket-owner "${EXPECTED_AWS_ACCOUNT_ID}" --output json |
      jq -c '{Objects: ([(.Versions // [])[], (.DeleteMarkers // [])[]]
        | map({Key, VersionId})), Quiet: true}')
    [[ $(jq '.Objects | length' <<<"${page}") -eq 0 ]] && break
    aws s3api delete-objects --bucket "${bucket}" --delete "${page}" \
      --expected-bucket-owner "${EXPECTED_AWS_ACCOUNT_ID}" >/dev/null
  done
  aws s3api delete-bucket --bucket "${bucket}" --expected-bucket-owner "${EXPECTED_AWS_ACCOUNT_ID}"
}

phase_recover_foundation() {
  [[ "${PLATFORM_ENVIRONMENT}" == sandbox ]] ||
    die "recover-foundation runs only for PLATFORM_ENVIRONMENT=sandbox; recover customers by import"

  # Names are fixed by m0-foundation.yaml (ProjectName-Environment-<component>).
  local table="${PREFIX}-metadata"
  local artifact_bucket="${PREFIX}-artifacts-${EXPECTED_AWS_ACCOUNT_ID}"
  local audit_bucket="${PREFIX}-audit-${EXPECTED_AWS_ACCOUNT_ID}"
  local trail="${PREFIX}-artifact-access"
  local pool_name="${PREFIX}-users"

  local stack_status="(none)"
  if stack_exists "${FOUNDATION_STACK}"; then
    stack_status=$(aws cloudformation describe-stacks --stack-name "${FOUNDATION_STACK}" \
      --query 'Stacks[0].StackStatus' --output text)
  fi

  local -a found=()
  aws dynamodb describe-table --table-name "${table}" >/dev/null 2>&1 && found+=("table ${table}")
  local bucket
  for bucket in "${artifact_bucket}" "${audit_bucket}"; do
    aws s3api head-bucket --bucket "${bucket}" --expected-bucket-owner "${EXPECTED_AWS_ACCOUNT_ID}" \
      >/dev/null 2>&1 && found+=("bucket ${bucket}")
  done
  aws cloudtrail get-trail --name "${trail}" >/dev/null 2>&1 && found+=("trail ${trail}")
  local pool_ids
  pool_ids=$(aws cognito-idp list-user-pools --max-results 60 --output json |
    jq -r --arg name "${pool_name}" '.UserPools[] | select(.Name == $name) | .Id')
  local pool
  for pool in ${pool_ids}; do found+=("user-pool ${pool} (${pool_name})"); done

  echo "Foundation stack ${FOUNDATION_STACK}: ${stack_status}"
  if ((${#found[@]} == 0)); then
    echo "No retained foundation resources found."
  else
    echo "Retained foundation resources that will be DELETED with all their data:"
    printf '  - %s\n' "${found[@]}"
  fi
  [[ "${stack_status}" == "(none)" && ${#found[@]} -eq 0 ]] && return 0
  # A complete stack that still owns all five retained resources is healthy: recovery would
  # only destroy data. Externally deleted resources make the count lower.
  if [[ "${stack_status}" =~ ^(CREATE|UPDATE)_COMPLETE$ && ${#found[@]} -eq 5 &&
    "${FORCE_RECOVER:-}" != 1 ]]; then
    die "the foundation looks healthy; set FORCE_RECOVER=1 to delete and recreate it anyway"
  fi

  read -r -p "Type ${PREFIX} to delete the stack and the resources above: " answer
  [[ "${answer}" == "${PREFIX}" ]] || die "aborted by user"

  if [[ "${stack_status}" != "(none)" ]]; then
    # Retained resources survive this; the loop below removes them.
    aws cloudformation delete-stack --stack-name "${FOUNDATION_STACK}"
    aws cloudformation wait stack-delete-complete --stack-name "${FOUNDATION_STACK}"
  fi
  local item
  for item in "${found[@]}"; do
    case "${item}" in
      "trail "*) aws cloudtrail delete-trail --name "${trail}" ;;
    esac
  done
  for item in "${found[@]}"; do
    case "${item}" in
      "bucket "*) empty_and_delete_bucket "${item#bucket }" ;;
      "table "*)
        aws dynamodb update-table --table-name "${table}" --no-deletion-protection-enabled >/dev/null
        aws dynamodb delete-table --table-name "${table}" >/dev/null
        aws dynamodb wait table-not-exists --table-name "${table}"
        ;;
      "user-pool "*)
        pool=${item#user-pool }
        pool=${pool%% *}
        local domain
        domain=$(aws cognito-idp describe-user-pool --user-pool-id "${pool}" \
          --query 'UserPool.Domain' --output text)
        if [[ -n "${domain}" && "${domain}" != None ]]; then
          aws cognito-idp delete-user-pool-domain --user-pool-id "${pool}" --domain "${domain}"
        fi
        aws cognito-idp delete-user-pool --user-pool-id "${pool}"
        ;;
    esac
  done
  echo "Recovered. Run the foundation phase to deploy it again, then re-create the admin user."
}

main() {
  local phase=${1:-}
  [[ "${2:-}" == --yes ]] && ASSUME_YES=true
  case "${phase}" in
    platform | foundation | customer | status | recover-foundation) ;;
    *) sed -n '2,33p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 2 ;;
  esac
  check_account
  "phase_${phase//-/_}"
}

main "$@"
