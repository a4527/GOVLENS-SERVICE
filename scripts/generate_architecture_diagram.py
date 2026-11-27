"""Generate docs/design/architecture/architecture.svg (README architecture diagram).

Icons are simplified glyphs in AWS category colours, not the official AWS icon set.
Keep the diagram in sync with infrastructure/cloudformation/platform-foundation.yaml.

    python scripts/generate_architecture_diagram.py
"""

import sys
from pathlib import Path
from xml.sax.saxutils import escape

W, H = 1640, 1050
FONT = "Inter, 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
INK = "#1F2937"
MUTED = "#4B5563"
out: list[str] = []


def add(s: str) -> None:
    out.append(s)


def text(x, y, s, size=12, weight=400, fill=INK, anchor="middle", italic=False):
    style = ' font-style="italic"' if italic else ""
    add(
        f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
        f'text-anchor="{anchor}"{style}>{escape(s)}</text>'
    )


def lines(x, y, rows, size=12, gap=15, anchor="middle"):
    for i, row in enumerate(rows):
        if isinstance(row, tuple):
            s, weight, fill = row
        else:
            s, weight, fill = row, 400, MUTED
        text(x, y + i * gap, s, size=size, weight=weight, fill=fill, anchor=anchor)


def box(x, y, w, h, stroke, fill="none", dash=None, r=14, sw=2):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    add(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" '
        f'stroke="{stroke}" stroke-width="{sw}"{d}/>'
    )


def path(d, stroke=INK, sw=1.6, dash=None, marker="arrow", fill="none"):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    mk = f' marker-end="url(#{marker})"' if marker else ""
    add(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{da}{mk}/>')


# ---------------------------------------------------------------- icons
COL = {
    "lambda": "#ED7100",
    "sqs": "#E7157B",
    "cognito": "#DD344C",
    "apigw": "#8C4FFF",
    "bedrock": "#01A88D",
    "dynamodb": "#2E73B8",
    "s3": "#7AA116",
    "mgmt": "#E7157B",
    "github": "#24292F",
}


def tile(cx, cy, s, color):
    add(
        f'<rect x="{cx - s / 2}" y="{cy - s / 2}" width="{s}" height="{s}" rx="{s * 0.16}" '
        f'fill="{color}"/>'
    )


def g_open(cx, cy, s):
    # glyph coordinates are drawn in a 0..100 box centred on the tile
    k = s / 100
    add(
        f'<g transform="translate({cx - 50 * k},{cy - 50 * k}) scale({k})" fill="none" '
        f'stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">'
    )


def g_close():
    add("</g>")


def icon(kind, cx, cy, s=64):
    if kind == "user":
        add(
            f'<g fill="none" stroke="{INK}" stroke-width="2.2">'
            f'<circle cx="{cx}" cy="{cy - 14}" r="13"/>'
            f'<path d="M{cx - 26},{cy + 26} C{cx - 26},{cy + 2} {cx + 26},{cy + 2} {cx + 26},{cy + 26}"/>'
            "</g>"
        )
        return
    if kind == "react":
        add('<g fill="none" stroke="#6D4AFF" stroke-width="3">')
        for a in (0, 60, 120):
            add(f'<ellipse cx="{cx}" cy="{cy}" rx="32" ry="12" transform="rotate({a} {cx} {cy})"/>')
        add(f'<circle cx="{cx}" cy="{cy}" r="6" fill="#6D4AFF"/></g>')
        return
    color = {
        "lambda": COL["lambda"],
        "sqs": COL["sqs"],
        "dlq": COL["sqs"],
        "cognito": COL["cognito"],
        "apigw": COL["apigw"],
        "bedrock": COL["bedrock"],
        "dynamodb": COL["dynamodb"],
        "s3": COL["s3"],
        "cloudtrail": COL["mgmt"],
        "eventbridge": COL["mgmt"],
        "tool": COL["mgmt"],
        "github": COL["github"],
        "repo": COL["github"],
        "actions": COL["github"],
        "ec2": COL["lambda"],
        "rds": COL["dynamodb"],
        "alb": COL["apigw"],
        "s3s": COL["s3"],
    }[kind]
    tile(cx, cy, s, color)
    g_open(cx, cy, s)
    if kind == "lambda":
        add('<path d="M30,80 L50,42 M38,22 L48,22 L72,80 L82,80" stroke-width="7"/>')
    elif kind in ("sqs", "dlq"):
        add('<rect x="24" y="32" width="52" height="36" rx="4"/><path d="M24,34 L50,54 L76,34"/>')
        if kind == "dlq":
            add('<path d="M64,62 L80,78 M80,62 L64,78" stroke="#fff"/>')
    elif kind == "cognito":
        add(
            '<circle cx="50" cy="36" r="12"/><path d="M26,76 C26,54 74,54 74,76"/>'
            '<path d="M60,70 L68,78 L82,62" stroke-width="6"/>'
        )
    elif kind == "apigw":
        add('<path d="M40,30 L22,50 L40,70 M60,30 L78,50 L60,70 M55,24 L45,76"/>')
    elif kind == "bedrock":
        add(
            '<circle cx="50" cy="50" r="9"/><circle cx="24" cy="28" r="6"/>'
            '<circle cx="76" cy="28" r="6"/><circle cx="24" cy="72" r="6"/>'
            '<circle cx="76" cy="72" r="6"/>'
            '<path d="M29,32 L43,44 M71,32 L57,44 M29,68 L43,56 M71,68 L57,56"/>'
        )
    elif kind in ("dynamodb", "rds"):
        add(
            '<ellipse cx="50" cy="28" rx="24" ry="8"/>'
            '<path d="M26,28 L26,72 C26,82 74,82 74,72 L74,28"/>'
            '<path d="M26,43 C26,53 74,53 74,43 M26,58 C26,68 74,68 74,58"/>'
        )
        if kind == "dynamodb":
            add('<path d="M58,40 L50,54 L60,54 L52,68" stroke-width="4"/>')
    elif kind in ("s3", "s3s"):
        add(
            '<ellipse cx="50" cy="30" rx="26" ry="8"/>'
            '<path d="M24,30 L32,74 C34,82 66,82 68,74 L76,30"/>'
        )
    elif kind == "cloudtrail":
        add(
            '<path d="M22,30 L60,30 M22,50 L52,50 M22,70 L44,70"/>'
            '<circle cx="66" cy="62" r="12"/><path d="M75,71 L84,80"/>'
        )
    elif kind == "eventbridge":
        add(
            '<circle cx="50" cy="50" r="10"/>'
            '<circle cx="50" cy="18" r="6"/><circle cx="80" cy="64" r="6"/>'
            '<circle cx="20" cy="64" r="6"/>'
            '<path d="M50,24 L50,40 M75,61 L59,54 M25,61 L41,54"/>'
        )
    elif kind == "tool":
        add(
            '<path d="M44,22 L68,34 L68,60 L44,72 L20,60 L20,34 Z M20,34 L44,46 L68,34 M44,46 L44,72"/>'
            '<circle cx="70" cy="68" r="10"/><path d="M77,75 L85,83"/>'
        )
    elif kind == "github":
        # GitHub App: puzzle-ish plug
        add(
            '<rect x="26" y="40" width="48" height="36" rx="5"/>'
            '<path d="M38,40 L38,24 M62,40 L62,24 M50,76 L50,86"/>'
        )
    elif kind == "repo":
        add(
            '<path d="M28,20 L68,20 C72,20 74,22 74,26 L74,80 L34,80 C30,80 28,78 28,74 Z"/>'
            '<path d="M28,70 C28,66 30,64 34,64 L74,64 M40,34 L62,34 M40,46 L56,46"/>'
        )
    elif kind == "actions":
        add(
            '<circle cx="26" cy="28" r="8"/><circle cx="26" cy="72" r="8"/>'
            '<circle cx="70" cy="50" r="8"/>'
            '<path d="M26,36 L26,64 M34,28 C54,28 54,50 62,50 M34,72 C54,72 54,50 62,50"/>'
        )
    elif kind == "ec2":
        add(
            '<rect x="30" y="30" width="40" height="40" rx="3"/>'
            '<path d="M40,30 L40,18 M50,30 L50,18 M60,30 L60,18 M40,70 L40,82 M50,70 L50,82 '
            "M60,70 L60,82 M30,40 L18,40 M30,50 L18,50 M30,60 L18,60 M70,40 L82,40 "
            'M70,50 L82,50 M70,60 L82,60"/>'
        )
    elif kind == "alb":
        add(
            '<circle cx="50" cy="50" r="28"/><circle cx="50" cy="34" r="5"/>'
            '<circle cx="34" cy="62" r="5"/><circle cx="66" cy="62" r="5"/>'
            '<path d="M50,39 L50,50 L34,57 M50,50 L66,57"/>'
        )
    g_close()


def node(kind, cx, cy, label_rows, s=64, gap=15, size=12):
    icon(kind, cx, cy, s)
    lines(cx, cy + s / 2 + 18, label_rows, size=size, gap=gap)


# ---------------------------------------------------------------- canvas
add(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="{FONT}">'
)
add("<defs>")
for mid, color in (
    ("arrow", INK),
    ("arrowRed", "#DC2626"),
    ("arrowTeal", "#0F766E"),
    ("arrowGray", "#6B7280"),
):
    add(
        f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
        f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
        f'fill="{color}"/></marker>'
    )
add("</defs>")
add(f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>')

# column frames + headings
COLS = [
    (20, 230, "#3B82F6", ["1. EDGE & API"]),
    (275, 670, "#7C3AED", ["2. ASYNC WORKFLOW"]),
    (970, 275, "#22A35A", ["3. AI · STATE · ARTIFACTS"]),
    (1270, 350, "#14B8A6", ["4. DEPLOYMENT INTEGRATION", "+ WORKLOAD"]),
]
TOP, BOTTOM = 76, 915
for x, w, c, heads in COLS:
    box(x, TOP, w, BOTTOM - TOP, c, fill="none", sw=2)
    for i, hline in enumerate(heads):
        text(
            x + w / 2,
            34 + i * 22 - (10 if len(heads) > 1 else 0),
            hline,
            size=19,
            weight=700,
            fill="#1E3A8A",
        )

# ---------------------------------------------------------------- column 1
C1 = 135
node("user", C1, 125, [("Customer User", 600, INK)], s=64)
path(f"M{C1},176 L{C1},208")
node("react", C1, 245, [("React SPA", 700, INK), "(S3 + CloudFront)"])
path(f"M{C1},312 L{C1},350")
node("cognito", C1, 388, [("Cognito", 700, INK), "JWT · PreTokenGeneration"])
path(f"M{C1},455 L{C1},493")
node("apigw", C1, 531, [("API Gateway", 700, INK), "HTTP API · JWT authorizer"])
path(f"M{C1},598 L{C1},636")
node(
    "lambda",
    C1,
    674,
    [
        ("API Lambda", 700, INK),
        "single function · all routes",
        "Job + Outbox → WorkflowTask",
        ("/orchestrate →", 600, "#6D28D9"),
        ("LangGraph Parent", 600, "#6D28D9"),
        "NL routing + Policy Q&A",
        "(sync, ≤ 30 s)",
    ],
)

# ---------------------------------------------------------------- column 2
# top section: how work enters the queues
add(
    '<line x1="285" y1="258" x2="935" y2="258" stroke="#A78BFA" stroke-width="1.6" '
    'stroke-dasharray="7 6"/>'
)
icon("eventbridge", 345, 132, 52)
lines(345, 178, [("EventBridge", 600, INK), "rate(1 min)"], size=11, gap=13)
path("M373,132 L428,132", dash="6 4", stroke="#6B7280", marker="arrowGray")
icon("lambda", 462, 132, 56)
lines(462, 180, [("Outbox Sweeper", 700, INK), "Lambda"], size=12, gap=14)
lines(
    520,
    112,
    [
        ("Re-sends undelivered outbox", 400, MUTED),
        ("WorkflowTasks (Assessment ·", 400, MUTED),
        ("Remediation · Deployment)", 400, MUTED),
    ],
    size=11.5,
    gap=15,
    anchor="start",
)
# explanatory card
box(712, 92, 214, 148, "#DDD6FE", fill="#F5F3FF", r=10, sw=1.2)
lines(
    724,
    114,
    [
        ("State lives in DynamoDB + S3", 700, "#4C1D95"),
        "SQS only carries a minimal",
        "WorkflowTask(job_id, revision,",
        "command). Workers reload the",
        "revision-bound checkpoint and",
        "re-queue 3 min before the",
        "15-min Lambda timeout.",
    ],
    size=11,
    gap=15,
    anchor="start",
)

LANES = [
    ("POLICY AUTHORING", "#0E7490", "#ECFEFF", "Policy Authoring", ["dedicated IAM role"]),
    ("ASSESSMENT", "#1D4ED8", "#EFF6FF", "Assessment", ["IaC · Actual · Drift"]),
    ("REMEDIATION", "#15803D", "#F0FDF4", "Remediation", ["Patch / Sync port"]),
    ("DEPLOYMENT", "#C2410C", "#FFF7ED", "Deployment", ["no model call"]),
]
LANE_X, LANE_W, LANE_H = 290, 640, 150
LANE_Y0 = 272
QX, WX, DX = 450, 690, 870
lane_cy = []
for i, (name, color, fill, short, sub) in enumerate(LANES):
    y = LANE_Y0 + i * (LANE_H + 6)
    box(LANE_X, y, LANE_W, LANE_H - 6, color, fill=fill, r=10, sw=1.4)
    cy = y + 72
    lane_cy.append(cy)
    # queue -> worker
    icon("sqs", QX, cy, 58)
    lines(QX, cy + 46, [(f"{short}", 600, INK), "SQS Standard"], size=11.5, gap=14)
    path(f"M{QX + 34},{cy} L{WX - 36},{cy}", dash="6 4")
    icon("lambda", WX, cy, 58)
    lines(WX, cy + 46, [(f"{short} Worker", 600, INK), sub[0]], size=11.5, gap=14)
    # DLQ (SQS redrive after 3 receives)
    icon("dlq", DX, cy - 6, 44)
    text(DX, cy + 32, "DLQ", size=11.5, weight=600)
    dl = cy - 40
    path(
        f"M{QX},{cy - 30} L{QX},{dl} L{DX},{dl} L{DX},{cy - 30}",
        stroke="#DC2626",
        dash="3 3",
        marker="arrowRed",
        sw=1.4,
    )
    if i == 0:
        text(
            LANE_X + LANE_W - 12,
            dl - 6,
            "after 3 failed receives",
            size=10.5,
            fill="#DC2626",
            anchor="end",
        )
    text(LANE_X + 14, y + 20, name, size=13, weight=700, fill=color, anchor="start")

dep_y = LANE_Y0 + 3 * (LANE_H + 6)
text(
    LANE_X + LANE_W - 12,
    dep_y + 13,
    "approval → outbox PLAN_COMPLETED → apply dispatch",
    size=10,
    fill=MUTED,
    anchor="end",
)
text(
    LANE_X + LANE_W - 12,
    dep_y + 25,
    "APPLY_COMPLETED → Post-Deploy verification task → Assessment Queue",
    size=10,
    fill=MUTED,
    anchor="end",
)

# entry bus: API Lambda + Outbox Sweeper -> queues
BUS1 = 270
path(f"M{C1 + 34},{674} L{BUS1},{674}", marker=None, dash="6 4")
path(f"M{BUS1},{lane_cy[0]} L{BUS1},{lane_cy[3]}", marker=None, dash="6 4")
path(f"M462,200 L462,232 L{BUS1},232 L{BUS1},{lane_cy[0]}", marker=None, dash="6 4")
for cy in lane_cy:
    path(f"M{BUS1},{cy} L{QX - 33},{cy}", dash="6 4")

# ---------------------------------------------------------------- column 3
C3 = 1107
BUS2 = 952
node(
    "bedrock",
    C3,
    176,
    [
        ("Amazon Bedrock", 700, INK),
        "role-specific Model Profiles",
        "(Parent · Policy Authoring ·",
        "Assessment · Remediation)",
    ],
    s=60,
)
node(
    "dynamodb",
    C3,
    338,
    [("DynamoDB", 700, INK), "Job · revision-bound checkpoint", "· metadata · outbox"],
    s=60,
)
node(
    "s3",
    C3,
    470,
    [("S3 Artifacts", 700, INK), "policy originals · snapshots", "· reports · patches · plans"],
    s=60,
)
node(
    "cloudtrail",
    C3,
    604,
    [("CloudTrail data events", 700, INK), "+ audit bucket · CloudWatch"],
    s=52,
)
path(
    f"M{C3 + 32},{462} C{C3 + 128},{470} {C3 + 128},{596} {C3 + 30},{604}",
    dash="3 3",
    stroke="#6B7280",
    marker="arrowGray",
    sw=1.3,
)
node(
    "tool",
    C3,
    720,
    [("AWS Resource Tool", 700, INK), "read-only · ExternalId", "(Assessment · Deployment)"],
    s=56,
)
box(990, 814, 235, 94, "#6B7280", dash="7 5", r=10, sw=1.4)
text(C3, 833, "Workload (Read-only)", size=12, weight=700)
for j, (k, lab) in enumerate((("ec2", "EC2"), ("rds", "RDS"), ("alb", "ALB"), ("s3s", "S3"))):
    x = 1025 + j * 55
    icon(k, x, 862, 32)
    text(x, 897, lab, size=11, weight=600)
path(f"M{C3 + 30},{720} L{1210},{720} L{1210},{810}", stroke="#6B7280", marker="arrowGray")

# workers -> state bus
for cy in lane_cy:
    path(f"M{LANE_X + LANE_W},{cy} L{BUS2},{cy}", marker=None)
path(f"M{BUS2},{118} L{BUS2},{lane_cy[3]}", marker=None)
for ty in (176, 338, 470, 720):
    path(f"M{BUS2},{ty} L{C3 - 36},{ty}")
text(976, 300, "API Lambda", size=9.5, fill=MUTED, anchor="start")
text(976, 311, "+ workers", size=9.5, fill=MUTED, anchor="start")

# bus -> GitHub App
path(f"M{BUS2},{118} L{1296},{118}")
text(1110, 100, "Remediation: branch · commit · PR", size=10.5, fill=MUTED)
text(1110, 112, "Deployment: plan / apply dispatch", size=10.5, fill=MUTED)

# ---------------------------------------------------------------- column 4
C4 = 1445
card_w = 244
for cy, kind, title, sub in (
    (118, "github", "GitHub App", "contents · pull_requests"),
    (236, "repo", "Workload Terraform", "Repository"),
    (360, "actions", "GitHub Actions (OIDC)", "CI · Plan · approved Apply"),
):
    box(C4 - card_w / 2, cy - 36, card_w, 72, "#6B7280", fill="#FFFFFF", r=8, sw=1.4)
    icon(kind, C4 - card_w / 2 + 38, cy, 44)
    text(C4 - card_w / 2 + 72, cy - 4, title, size=13, weight=700, anchor="start")
    text(C4 - card_w / 2 + 72, cy + 13, sub, size=11, fill=MUTED, anchor="start")
path(f"M{C4},{154} L{C4},{198}")
path(f"M{C4},{272} L{C4},{322}")
path(f"M{C4 - 40},{396} L{C4 - 40},{462}", dash="6 4")
lines(C4 - 32, 420, ["terraform-apply-", "completed event"], size=10.5, gap=13, anchor="start")
node("eventbridge", C4 - 40, 496, [("Amazon EventBridge", 700, INK)], s=56)
path(f"M{C4 - 40},{548} L{C4 - 40},{586}", dash="6 4")
node("lambda", C4 - 40, 620, [("Apply Completion", 700, INK), "Lambda"], s=56)

# Apply Completion -> Deployment Queue (route under the frames)
ROUTE = 932
path(
    f"M{C4 - 70},{620} L{1252},{620} L{1252},{ROUTE} L{380},{ROUTE} L{380},{lane_cy[3] + 18} L{QX - 32},{lane_cy[3] + 18}",
    dash="6 4",
    sw=1.5,
)
text(860, ROUTE - 5, "APPLY_COMPLETED (run_id re-read by Deployment Worker)", size=10.5, fill=MUTED)

# approved apply -> workload (write)
path(
    f"M{C4 + card_w / 2},{360} L{1600},{360} L{1600},{770} L{C4 + 60},{780} L{C4 + 60},{810}",
    stroke="#0F766E",
    sw=2.4,
    marker="arrowTeal",
)
lines(
    1590,
    688,
    [("approved", 600, "#0F766E"), ("apply only", 600, "#0F766E")],
    size=11,
    gap=13,
    anchor="end",
)
box(1300, 814, 290, 94, "#C2410C", dash="7 5", r=10, sw=1.4)
text(C4, 833, "Workload (Write access)", size=12, weight=700)
for j, (k, lab) in enumerate((("ec2", "EC2"), ("rds", "RDS"), ("alb", "ALB"), ("s3s", "S3"))):
    x = 1355 + j * 60
    icon(k, x, 862, 32)
    text(x, 897, lab, size=11, weight=600)

# ---------------------------------------------------------------- legend
LY = 958
box(20, LY, 1600, 70, "#D1D5DB", fill="#FAFAFA", r=10, sw=1.2)
lx = 50
path(f"M{lx},{LY + 35} L{lx + 50},{LY + 35}")
lines(
    lx + 62,
    LY + 31,
    [("Synchronous", 400, INK), ("(HTTP / SDK call)", 400, INK)],
    size=11.5,
    gap=14,
    anchor="start",
)
lx = 260
path(f"M{lx},{LY + 35} L{lx + 50},{LY + 35}", dash="6 4")
lines(
    lx + 62,
    LY + 31,
    [("Asynchronous", 400, INK), ("(message / event)", 400, INK)],
    size=11.5,
    gap=14,
    anchor="start",
)
lx = 470
path(f"M{lx},{LY + 35} L{lx + 50},{LY + 35}", stroke="#DC2626", dash="3 3", marker="arrowRed")
lines(
    lx + 62,
    LY + 31,
    [("SQS redrive to DLQ", 400, INK), ("(maxReceiveCount 3)", 400, INK)],
    size=11.5,
    gap=14,
    anchor="start",
)
lx = 690
path(f"M{lx},{LY + 35} L{lx + 50},{LY + 35}", stroke="#0F766E", sw=2.4, marker="arrowTeal")
lines(
    lx + 62,
    LY + 31,
    [("Infrastructure write", 400, INK), ("(human-approved apply)", 400, INK)],
    size=11.5,
    gap=14,
    anchor="start",
)
lx = 920
box(lx, LY + 20, 42, 30, "#6B7280", dash="6 4", r=6, sw=1.3)
text(lx + 54, LY + 40, "Read-only access", size=11.5, anchor="start")
lx = 1090
box(lx, LY + 20, 42, 30, "#C2410C", dash="6 4", r=6, sw=1.3)
text(lx + 54, LY + 40, "Write access", size=11.5, anchor="start")
lines(
    1605,
    LY + 28,
    [
        ("Customer AWS account · us-east-1 · backend Lambdas", 400, MUTED),
        ("not attached to the workload VPC", 400, MUTED),
    ],
    size=11,
    gap=14,
    anchor="end",
)

add("</svg>")
DEFAULT = Path(__file__).resolve().parents[1] / "docs/design/architecture/architecture.svg"
target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
target.write_text("\n".join(out) + "\n", encoding="utf-8")
