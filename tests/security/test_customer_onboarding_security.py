"""Semantic security checks for the customer-operated onboarding template (TASKS V-11)."""

import unittest
from pathlib import Path

import yaml
from yaml.nodes import MappingNode, ScalarNode, SequenceNode

TEMPLATE_PATH = Path(__file__).parents[2] / "infrastructure/cloudformation/customer-onboarding.yaml"

#: The Actual read adapters' reads (docs/sandbox/M1-SANDBOX-INTEGRATION.md). Nothing more.
READ_ROLE_ACTIONS = {
    "s3:ListAllMyBuckets",
    "s3:GetBucketPublicAccessBlock",
    "s3:GetEncryptionConfiguration",
    "s3:GetBucketPolicyStatus",
    "s3:GetBucketPolicy",
    "s3:GetBucketOwnershipControls",
    "s3:GetBucketLogging",
    "ec2:DescribeInstances",
    "ec2:DescribeVolumes",
    "ec2:DescribeSecurityGroups",
    "ec2:DescribeSubnets",
    "rds:DescribeDBInstances",
    "elasticloadbalancing:DescribeLoadBalancers",
    "elasticloadbalancing:DescribeListeners",
    "elasticloadbalancing:DescribeLoadBalancerAttributes",
}


def _construct_intrinsic(loader: yaml.SafeLoader, suffix: str, node: yaml.Node) -> object:
    if isinstance(node, ScalarNode):
        value: object = loader.construct_scalar(node)
    elif isinstance(node, SequenceNode):
        value = loader.construct_sequence(node)
    elif isinstance(node, MappingNode):
        value = loader.construct_mapping(node)
    else:
        raise TypeError(f"Unsupported CloudFormation node: {type(node).__name__}")
    return {suffix: value}


class _Loader(yaml.SafeLoader):
    """Keeps intrinsic names ({"Ref": ...}) without changing the shared SafeLoader."""


_Loader.add_multi_constructor("!", _construct_intrinsic)


def _template() -> dict[str, object]:
    loaded = yaml.load(TEMPLATE_PATH.read_text(encoding="utf-8"), Loader=_Loader)  # noqa: S506
    if not isinstance(loaded, dict):
        raise TypeError("CloudFormation template must be a mapping")
    return loaded


def _actions(role: dict) -> set[str]:
    return {
        action
        for policy in role["Properties"].get("Policies", [])
        for statement in policy["PolicyDocument"]["Statement"]
        for action in (
            [statement["Action"]] if isinstance(statement["Action"], str) else statement["Action"]
        )
    }


class CustomerOnboardingSecurityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.resources = _template()["Resources"]

    def test_state_backend_is_private_versioned_tls_only_and_retained(self) -> None:
        bucket = self.resources["TerraformStateBucket"]
        self.assertEqual(bucket["DeletionPolicy"], "Retain")
        self.assertEqual(bucket["UpdateReplacePolicy"], "Retain")
        properties = bucket["Properties"]
        self.assertEqual(properties["VersioningConfiguration"]["Status"], "Enabled")
        self.assertEqual(
            properties["OwnershipControls"]["Rules"][0]["ObjectOwnership"], "BucketOwnerEnforced"
        )
        self.assertTrue(all(properties["PublicAccessBlockConfiguration"].values()))
        self.assertEqual(len(properties["PublicAccessBlockConfiguration"]), 4)
        statement = self.resources["TerraformStateBucketPolicy"]["Properties"]["PolicyDocument"][
            "Statement"
        ][0]
        self.assertEqual(statement["Effect"], "Deny")
        self.assertEqual(statement["Condition"], {"Bool": {"aws:SecureTransport": "false"}})
        self.assertEqual(self.resources["TerraformLockTable"]["DeletionPolicy"], "Retain")

    def test_oidc_roles_trust_one_exact_environment_subject_each(self) -> None:
        for logical_id, environment in (
            ("TerraformPlanRole", "PlanEnvironment"),
            ("TerraformApplyRole", "ApplyEnvironment"),
        ):
            with self.subTest(role=logical_id):
                statements = self.resources[logical_id]["Properties"]["AssumeRolePolicyDocument"][
                    "Statement"
                ]
                self.assertEqual(len(statements), 1)
                condition = statements[0]["Condition"]["StringEquals"]
                self.assertEqual(
                    condition["token.actions.githubusercontent.com:aud"], "sts.amazonaws.com"
                )
                self.assertEqual(
                    condition["token.actions.githubusercontent.com:sub"],
                    {"Sub": f"${{WorkloadRepositorySubjectPrefix}}:environment:${{{environment}}}"},
                )
                self.assertNotIn("StringLike", statements[0]["Condition"])

    def test_plan_role_cannot_write_state_and_neither_role_has_broad_inline_grants(self) -> None:
        plan = _actions(self.resources["TerraformPlanRole"])
        apply = _actions(self.resources["TerraformApplyRole"])
        self.assertNotIn("s3:PutObject", plan)
        self.assertIn("s3:PutObject", apply)
        for actions in (plan, apply):
            self.assertFalse(any(action.endswith("*") for action in actions))
            self.assertFalse(any(action.startswith("iam:") for action in actions))

    def test_template_never_attaches_administrator_access(self) -> None:
        self.assertNotIn("AdministratorAccess", TEMPLATE_PATH.read_text(encoding="utf-8"))

    def test_read_role_trusts_only_the_worker_with_external_id_and_only_reads(self) -> None:
        role = self.resources["CustomerReadRole"]
        statements = role["Properties"]["AssumeRolePolicyDocument"]["Statement"]
        self.assertEqual(len(statements), 1)
        self.assertEqual(statements[0]["Principal"], {"AWS": {"Ref": "PlatformWorkerRoleArn"}})
        self.assertEqual(statements[0]["Action"], "sts:AssumeRole")
        self.assertIn("sts:ExternalId", statements[0]["Condition"]["StringEquals"])
        self.assertEqual(_actions(role), READ_ROLE_ACTIONS)

    def test_external_id_secret_has_no_fixed_name(self) -> None:
        secret = self.resources["ReadRoleExternalIdSecret"]["Properties"]
        self.assertNotIn("Name", secret)
        self.assertIn("GenerateSecretString", secret)


if __name__ == "__main__":
    unittest.main()
