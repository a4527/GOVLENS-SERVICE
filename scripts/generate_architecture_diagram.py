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
W, H = 1540, 1030
add(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="{FONT}">'
)
add("<defs>")
for mid, color in (("arrow", INK), ("arrowRed", "#DC2626")):
    add(
        f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
        f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
        f'fill="{color}"/></marker>'
    )
add("</defs>")
add(f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>')

TOP, BOTTOM = 58, 905
COLS = [
    (15, 205, "#3B82F6", ["1. EDGE & API"]),
    (260, 615, "#7C3AED", ["2. ASYNC WORKFLOW"]),
    (905, 260, "#22A35A", ["3. STATE & TOOLS"]),
    (1195, 330, "#14B8A6", ["4. DEPLOYMENT INTEGRATION", "+ CUSTOMER WORKLOAD"]),
]
for x, w, c, heads in COLS:
    box(x, TOP, w, BOTTOM - TOP, c, sw=2)
    for i, head in enumerate(heads):
        y = 34 + i * 22 - (10 if len(heads) > 1 else 0)
        text(x + w / 2, y, head, size=19, weight=700, fill="#1E3A8A")


def label(cx, y, rows, size=14):
    lines(cx, y, [(r, 500, INK) for r in rows], size=size, gap=size + 4)


# ---------------------------------------------------------------- 1. edge & api
C1 = 117
icon("user", C1, 115)
label(C1, 172, ["Customer User"])
path(f"M{C1},184 L{C1},232")
icon("react", C1, 272)
label(C1, 328, ["React SPA", "(S3 + CloudFront)"])
path(f"M{C1},370 L{C1},420")
icon("cognito", C1, 456)
label(C1, 512, ["Cognito JWT"])
path(f"M{C1},524 L{C1},574")
icon("apigw", C1, 610)
label(C1, 666, ["API Gateway"])
path(f"M{C1},678 L{C1},728")
icon("lambda", C1, 764)
label(C1, 820, ["API Lambda"])

# ---------------------------------------------------------------- 2. async workflow
# parent router (runs inside the API Lambda) + its tools
icon("lambda", 330, 168, 60)
lines(
    372,
    132,
    [
        ("Parent Router", 700, INK),
        ("Natural-language routing", 400, INK),
        ("+ Policy Q&A", 400, INK),
        ("(in API Lambda,", 400, INK),
        ("synchronous, max 30 s)", 400, INK),
    ],
    size=13.5,
    gap=19,
    anchor="start",
)
path("M612,168 L560,168")
path("M612,118 L612,218", marker=None)
path("M612,118 L648,118")
path("M612,218 L648,218")
icon("bedrock", 682, 118, 56)
lines(
    722,
    114,
    [("Policy Context", 700, INK), ("(Read-only)", 400, INK)],
    size=14,
    gap=20,
    anchor="start",
)
icon("bedrock", 682, 218, 56)
lines(
    722, 214, [("Bedrock", 700, INK), ("Model Profiles", 400, INK)], size=14, gap=20, anchor="start"
)
add(
    '<line x1="270" y1="262" x2="865" y2="262" stroke="#A78BFA" stroke-width="1.6" '
    'stroke-dasharray="7 6"/>'
)

LANES = [
    ("POLICY AUTHORING", "#0E7490", "#3B9FB5", "Policy Authoring"),
    ("ASSESSMENT", "#1D4ED8", "#5B8DEF", "Assessment"),
    ("REMEDIATION", "#15803D", "#5DBB78", "Remediation"),
    ("DEPLOYMENT", "#C2410C", "#F0B35B", "Deployment"),
]
LX, LW, LH = 270, 585, 150
QX, WX, DX = 400, 640, 800
lane_cy = []
for i, (name, ink, stroke, short) in enumerate(LANES):
    y = 272 + i * (LH + 6)
    box(LX, y, LW, LH, stroke, r=10, sw=1.6)
    cy = y + 56
    lane_cy.append(cy)
    icon("sqs", QX, cy, 56)
    label(QX, cy + 44, [short, "SQS Standard"], size=13)
    path(f"M{QX + 34},{cy} L{WX - 38},{cy}")
    icon("lambda", WX, cy, 56)
    label(WX, cy + 44, [f"{short}", "Worker Lambda"], size=13)
    icon("dlq", DX, cy - 4, 44)
    label(DX, cy + 38, ["DLQ"], size=13)
    red_y = cy - 36
    path(
        f"M{QX},{cy - 30} L{QX},{red_y} L{DX - 34},{red_y}",
        stroke="#DC2626",
        dash="4 3",
        marker="arrowRed",
        sw=1.4,
    )
    text((QX + DX) / 2, red_y - 6, "after 3 retryable failures only", size=12, fill="#DC2626")
    text(LX + LW / 2, y + LH - 9, name, size=14, weight=700, fill=ink)

# API Lambda -> queues
BUS1 = 240
path(f"M{C1 + 36},764 L{BUS1},764", marker=None)
path(f"M{BUS1},{lane_cy[0]} L{BUS1},{lane_cy[3]}", marker=None)
for cy in lane_cy:
    path(f"M{BUS1},{cy} L{QX - 32},{cy}")

# ---------------------------------------------------------------- 3. state & tools
C3 = 1035
BUS2 = 885
for cy in lane_cy:
    path(f"M{LX + LW},{cy} L{BUS2},{cy}", marker=None)
path(f"M{BUS2},160 L{BUS2},{lane_cy[3]}", marker=None)
icon("dynamodb", C3, 250, 68)
label(C3, 306, ["DynamoDB", "(Job + checkpoint", "+ metadata)"])
icon("s3", C3, 450, 68)
label(C3, 506, ["S3", "(snapshots, reports,", "patches, plans)"])
icon("tool", C3, 660, 60)
label(C3, 712, ["AWS Resource Tool", "(Read-only)"])
for ty, half in ((250, 36), (450, 36), (660, 32)):
    path(f"M{BUS2},{ty} L{C3 - half - 4},{ty}")
path(f"M{C3},746 L{C3},768")
box(925, 772, 220, 118, "#9CA3AF", dash="7 5", r=10, sw=1.5)
label(C3, 794, ["Customer Workload", "(Read-only)"], size=13.5)
for j, (k, lab) in enumerate((("ec2", "EC2"), ("rds", "RDS"), ("alb", "ALB"), ("s3s", "S3"))):
    x = 958 + j * 51
    icon(k, x, 848, 32)
    text(x, 882, lab, size=12, weight=500)

# workers -> GitHub (PR, plan/apply dispatch)
path(f"M{BUS2},160 L1236,160")

# ---------------------------------------------------------------- 4. deployment integration
C4 = 1360
CW = 244
for cy, kind, title, sub in (
    (160, "github", "GitHub App", None),
    (262, "repo", "Customer", "Terraform Repository"),
    (370, "actions", "GitHub Actions", "CI / Plan / approved Apply"),
):
    box(C4 - CW / 2, cy - 34, CW, 68, "#9CA3AF", fill="#FFFFFF", r=8, sw=1.5)
    icon(kind, C4 - CW / 2 + 34, cy, 42)
    tx = C4 - CW / 2 + 66
    if sub:
        text(tx, cy - 4, title, size=14, weight=700, anchor="start")
        text(tx, cy + 14, sub, size=11.5, fill=INK, anchor="start")
    else:
        text(tx, cy + 5, title, size=14, weight=700, anchor="start")
path(f"M{C4},194 L{C4},226")
path(f"M{C4},296 L{C4},334")
path(f"M{C4 - 30},404 L{C4 - 30},468")
lines(
    C4 - 22,
    432,
    [("Apply completion", 400, INK), ("event", 400, INK)],
    size=12.5,
    gap=16,
    anchor="start",
)
icon("eventbridge", C4 - 30, 500, 54)
label(C4 - 30, 546, ["Amazon EventBridge"], size=13.5)
path(f"M{C4 - 30},556 L{C4 - 30},584")
icon("lambda", C4 - 30, 616, 54)
label(C4 - 30, 662, ["Apply Completion Lambda"], size=13.5)

# Apply Completion -> Deployment SQS
ROUTE = 927
path(
    f"M{C4 - 58},616 L1180,616 L1180,{ROUTE} L330,{ROUTE} L330,{lane_cy[3] + 16} "
    f"L{QX - 32},{lane_cy[3] + 16}"
)
text(760, ROUTE - 6, "Apply completed → Deployment SQS", size=12.5, fill=INK)

# approved apply -> customer workload
path(f"M{C4 + CW / 2},370 L1508,370 L1508,700 L{C4 + 60},700 L{C4 + 60},728")
lines(1500, 690, [("Approved Apply", 500, INK)], size=13, anchor="end")
box(1225, 732, 270, 158, "#9CA3AF", dash="7 5", r=10, sw=1.5)
label(C4, 760, ["Customer Workload", "(Write access)"], size=13.5)
for j, (k, lab) in enumerate((("ec2", "EC2"), ("rds", "RDS"), ("alb", "ALB"), ("s3s", "S3"))):
    x = 1270 + j * 60
    icon(k, x, 830, 36)
    text(x, 868, lab, size=12, weight=500)

# ---------------------------------------------------------------- legend
LY = 948
box(15, LY, 960, 66, "#D1D5DB", fill="#FFFFFF", r=10, sw=1.2)
path(f"M38,{LY + 33} L82,{LY + 33}")
lines(
    94,
    LY + 29,
    [("Synchronous", 400, INK), ("(HTTP)", 400, INK)],
    size=12.5,
    gap=16,
    anchor="start",
)
path(f"M220,{LY + 33} L264,{LY + 33}")
lines(
    276,
    LY + 29,
    [("Asynchronous", 400, INK), ("(Message/Events)", 400, INK)],
    size=12.5,
    gap=16,
    anchor="start",
)
path(f"M430,{LY + 33} L474,{LY + 33}", stroke="#DC2626", dash="4 3", marker="arrowRed")
lines(
    486,
    LY + 29,
    [("DLQ (after 3 retryable", 400, INK), ("failures only)", 400, INK)],
    size=12.5,
    gap=16,
    anchor="start",
)
box(660, LY + 18, 40, 30, "#9CA3AF", dash="6 4", r=6, sw=1.3)
text(712, LY + 38, "Read-only access", size=12.5, anchor="start")
box(840, LY + 18, 40, 30, "#9CA3AF", dash="6 4", r=6, sw=1.3)
text(892, LY + 38, "Write access", size=12.5, anchor="start")

add("</svg>")
DEFAULT = Path(__file__).resolve().parents[1] / "docs/design/architecture/architecture.svg"
target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
target.write_text("\n".join(out) + "\n", encoding="utf-8")
