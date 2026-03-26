---
description: "Populate the Trello board from spec-kit specs. Reads specs/*/tasks.md and creates one card per feature in the To Do list with a checklist. Skips features already on the board. Safe to re-run."
---

You are populating a Trello board from spec-kit feature specs. This is safe to re-run — features already on the board are never duplicated.

## Prerequisites check

```bash
[ -n "$TRELLO_API_KEY" ] && [ -n "$TRELLO_TOKEN" ] || { echo "ERROR: TRELLO_API_KEY and TRELLO_TOKEN must be set."; exit 1; }
[ -f "maqa-trello/trello-config.yml" ] || { echo "ERROR: maqa-trello/trello-config.yml not found. Run /speckit.maqa-trello.setup first."; exit 1; }
```

## Step 1 — Read Trello config

```bash
source <(python3 -c "
import re
with open('maqa-trello/trello-config.yml') as f:
    for line in f:
        m = re.match(r'^(\w+):\s*\"?([^\"#\n]+)\"?', line.strip())
        if m and m.group(2).strip():
            print(f'{m.group(1).upper()}={m.group(2).strip()}')
")

BASE="https://api.trello.com/1"
AUTH="key=$TRELLO_API_KEY&token=$TRELLO_TOKEN"
```

## Step 2 — Get existing card names from all active lists

Fetch card names from Backlog, To Do, In Progress, In Review, and Done so we never duplicate:

```bash
EXISTING=$(python3 - <<EOF
import subprocess, json

base = "https://api.trello.com/1"
auth = "key=$TRELLO_API_KEY&token=$TRELLO_TOKEN"

list_ids = [
    "$BACKLOG_LIST_ID", "$TODO_LIST_ID", "$IN_PROGRESS_LIST_ID",
    "$IN_REVIEW_LIST_ID", "$DONE_LIST_ID"
]

names = set()
for lid in list_ids:
    if not lid:
        continue
    result = subprocess.run(
        ["curl", "-s", f"{base}/lists/{lid}/cards?fields=name&{auth}"],
        capture_output=True, text=True
    )
    try:
        for card in json.loads(result.stdout):
            names.add(card["name"].lower().strip())
    except:
        pass

for name in sorted(names):
    print(name)
EOF
)
```

## Step 3 — Discover local specs

Find all specs that have a `tasks.md` (output of `/speckit.tasks`):

```bash
python3 - <<'EOF'
import os, glob

specs = []
for tasks_path in sorted(glob.glob("specs/*/tasks.md")):
    spec_dir = os.path.dirname(tasks_path)
    name = os.path.basename(spec_dir)
    spec_md = os.path.join(spec_dir, "spec.md")
    plan_md = os.path.join(spec_dir, "plan.md")
    specs.append({
        "name": name,
        "tasks_path": tasks_path,
        "has_spec": os.path.exists(spec_md),
        "has_plan": os.path.exists(plan_md),
    })

for s in specs:
    ready = "ready" if s["has_spec"] and s["has_plan"] else "no-plan"
    print(f"{s['name']}|{s['tasks_path']}|{ready}")
EOF
```

Format result as TOON:
```
specs[N]{name,tasks_path,status}:
  001-user-auth,specs/001-user-auth/tasks.md,ready
  002-profile,specs/002-profile/tasks.md,no-plan
```

Skip specs with `status: no-plan` — they have no implementation plan yet.

## Step 4 — For each ready spec not already on the board

For each spec where the name (lowercased) is not in `$EXISTING`:

### 4a — Parse tasks from tasks.md

```bash
SPEC_NAME="001-user-auth"
TASKS_PATH="specs/$SPEC_NAME/tasks.md"

python3 - <<EOF
import re

content = open("$TASKS_PATH").read()

# Extract one-line summary from first heading or first paragraph
title_match = re.search(r'^#\s+(.+)$', content, re.M)
title = title_match.group(1).strip() if title_match else "$SPEC_NAME"

# Extract checklist items: lines starting with - [ ] or numbered tasks
tasks = []
for line in content.split("\n"):
    # Markdown checkbox: - [ ] Task description
    m = re.match(r'^\s*-\s*\[[ x]\]\s*(.+)', line)
    if m:
        tasks.append(m.group(1).strip())
        continue
    # Numbered task: 1. Task description or **1.** Task
    m = re.match(r'^\s*(?:\*\*)?\d+\.(?:\*\*)?\s+(.+)', line)
    if m:
        text = re.sub(r'\*\*', '', m.group(1)).strip()
        if len(text) > 5:
            tasks.append(text)

print("TITLE=" + title)
for t in tasks[:20]:  # cap at 20 checklist items
    print("TASK=" + t)
EOF
```

### 4b — Read dependencies from spec.md (if present)

```bash
python3 - <<EOF
import re
content = open("specs/$SPEC_NAME/spec.md").read() if __import__("os").path.exists("specs/$SPEC_NAME/spec.md") else ""
m = re.search(r'(?:Dep[s]?|Depends on|Dependencies)[:\s]+(.+)', content, re.I)
print(m.group(1).strip() if m else "")
EOF
```

### 4c — Build card description

```
Deps: <dependencies or "none">

<first 200 chars of spec.md summary, if available>
```

### 4d — Create the card in To Do

```bash
CARD_TITLE="<parsed title>"
CARD_DESC="<built description>"

CARD_ID=$(curl -s -X POST "$BASE/cards" \
  --data-urlencode "name=$CARD_TITLE" \
  --data-urlencode "desc=$CARD_DESC" \
  --data "idList=$TODO_LIST_ID&pos=bottom&$AUTH" | \
  python3 -c "import json,sys; print(json.load(sys.stdin)['id'])")

echo "Created card: $CARD_TITLE → $CARD_ID"
```

### 4e — Create checklist on the card

```bash
CHECKLIST_ID=$(curl -s -X POST "$BASE/checklists" \
  --data "idCard=$CARD_ID&name=Tasks&$AUTH" | \
  python3 -c "import json,sys; print(json.load(sys.stdin)['id'])")

# Add each task as a checklist item
for TASK in "${TASKS[@]}"; do
  curl -s -X POST "$BASE/checklists/$CHECKLIST_ID/checkItems" \
    --data-urlencode "name=$TASK" \
    --data "pos=bottom&$AUTH" -o /dev/null
done
```

## Step 5 — Report

After processing all specs, report:

```
populated[N]{name,card_id,tasks}:
  001-user-auth,<id>,5
  002-profile,<id>,3
skipped[M]{name,reason}:
  003-payments,already on board
  004-reports,no plan.md
```

If nothing was created (all already on board or no specs ready): report that clearly and suggest running `/speckit.tasks` first if specs exist but have no tasks.md.
