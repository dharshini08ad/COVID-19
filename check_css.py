"""CSS health check: brace balance, unintended nesting, and class coverage."""
import re
import pathlib

CSS_PATH = pathlib.Path("static/css/style.css")
TEMPLATE_DIR = pathlib.Path("templates/hms")

with open(CSS_PATH, encoding="utf-8") as f:
    raw = f.read()

# Strip comments so they don't count
css = re.sub(r"/\*.*?\*/", "", raw, flags=re.S)

opens = css.count("{")
closes = css.count("}")
print(f"open braces : {opens}")
print(f"close braces: {closes}")
print(f"balance     : {'OK' if opens == closes else 'BROKEN (diff %d)' % (opens - closes)}")

# Find rules whose selector is nested inside another STYLE rule (unintended).
# Rules inside @media/@supports blocks are legitimate, so we track a stack of
# open blocks and only flag a rule when its immediate parent is a style rule.
lines = raw.splitlines()
depth = 0
block_stack = []  # (depth_after_open, is_atrule)
suspects = []
for i, line in enumerate(lines, 1):
    stripped = re.sub(r"/\*.*?\*/", "", line).strip()
    is_selector = stripped.endswith("{") and not stripped.startswith("@")
    parent_is_atrule = True  # top-level is fine
    for open_depth, is_at in block_stack:
        if open_depth == depth:  # innermost block currently open
            parent_is_atrule = is_at
    if is_selector and depth > 0 and not parent_is_atrule:
        suspects.append((i, stripped))
    for ch in stripped:
        if ch == "{":
            depth += 1
            block_stack.append((depth, stripped.startswith("@")))
        elif ch == "}":
            depth -= 1
            if block_stack:
                block_stack.pop()
    if depth < 0:
        print(f"NEGATIVE DEPTH at line {i}: {stripped!r}")
        break

if suspects:
    print(f"\n{len(suspects)} rule(s) nested inside another style rule:")
    for ln, txt in suspects[:15]:
        print(f"  line {ln}: {txt}")
else:
    print("\nNo unintended nested rules found.")

print(f"final depth: {depth} ({'OK' if depth == 0 else 'UNCLOSED BLOCKS'})")

# ---------- Class coverage: every class used in templates should be styled ----------
defined = set(re.findall(r"\.([a-zA-Z_][\w-]*)", css))

# Bootstrap utilities / icon font we rely on — covered by CDN or local fallbacks
whitelist = {
    # bootstrap utilities (local fallbacks exist in style.css)
    "d-none", "d-md-flex", "d-md-block", "d-lg-none", "w-100", "mt-2",
    "table-responsive",
    # bootstrap-icons font classes
    "bi", "bi-arrow-down-right", "bi-arrow-left", "bi-arrow-right",
    "bi-arrow-up-right", "bi-arrow-up-right-circle", "bi-bed", "bi-bell",
    "bi-box-arrow-in-right", "bi-box-arrow-left", "bi-briefcase",
    "bi-calendar-plus", "bi-calendar2-check", "bi-check2",
    "bi-check2-circle", "bi-circle-fill", "bi-clipboard2-pulse", "bi-clock",
    "bi-clock-history", "bi-cylinder", "bi-database", "bi-download",
    "bi-envelope", "bi-eye", "bi-fan", "bi-file-earmark-bar-graph",
    "bi-file-earmark-medical", "bi-funnel", "bi-graph-up-arrow",
    "bi-grid-1x2", "bi-hdd-rack-fill", "bi-heart-pulse-fill", "bi-hospital",
    "bi-info-circle", "bi-list", "bi-lock", "bi-pencil", "bi-people",
    "bi-people-fill", "bi-person", "bi-person-badge", "bi-person-check",
    "bi-person-fill", "bi-person-plus", "bi-search", "bi-speedometer2",
    "bi-telephone", "bi-virus", "bi-x-lg",
    # semantic hooks: styled via their sibling .bento-card/.bento-grid classes
    "bento-charts", "bento-lower", "bento-bigdata", "bed-card",
    "bed-overview-card", "occupancy-card", "patient-hero", "table-card",
}

used = set()
for tpl in TEMPLATE_DIR.glob("*.html"):
    text = tpl.read_text(encoding="utf-8")
    # remove Django template expressions so only literal HTML classes remain
    text = re.sub(r"\{%.*?%\}", " ", text, flags=re.S)
    text = re.sub(r"\{\{.*?\}\}", " ", text, flags=re.S)
    for m in re.finditer(r'class="([^"]*)"', text):
        for cls in m.group(1).split():
            if re.fullmatch(r"[a-z][a-z0-9-]*", cls):
                used.add(cls)

missing = sorted(c for c in used if c not in defined and c not in whitelist)
print(f"\nclasses used in templates : {len(used)}")
print(f"classes styled in CSS     : {len(defined)}")
if missing:
    print(f"{len(missing)} class(es) used but not styled:")
    for c in missing:
        print(f"  .{c}")
else:
    print("coverage: every template class is styled.")

