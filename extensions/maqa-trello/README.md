# MAQA Trello Integration

> Trello board integration for the [MAQA](https://github.com/GenieRobot/spec-kit-maqa-ext) spec-kit extension.

Replaces local `.maqa/state.json` tracking with a live Trello board. Feature agents tick checklist items in real-time as each task completes.

## Prerequisites

- MAQA extension installed (`specify ext add maqa`)
- Trello API key and token:
  - Get key: https://trello.com/app-key
  - Generate token from that page
  - Set in environment: `TRELLO_API_KEY` and `TRELLO_TOKEN`

## Setup

```bash
# Install
specify ext add maqa-trello

# Configure
/speckit.maqa-trello.setup
```

The setup command reads your Trello board via the API and writes the list IDs to `maqa-trello/trello-config.yml`.

## How it works

The MAQA coordinator auto-detects Trello when:
1. `maqa-trello/trello-config.yml` exists in the project root, AND
2. `TRELLO_API_KEY` environment variable is set

When both conditions are met, the coordinator:
- Reads card state from the Trello board (Backlog → To Do → In Progress → In Review → Done)
- Moves cards between lists as features progress
- Feature agents tick checklist items in real-time as each task completes

Without Trello, the coordinator tracks state in `.maqa/state.json`.

## Board structure

The integration expects these lists (setup command creates them if missing):

| List | Meaning |
|---|---|
| Backlog | Planned but not yet scheduled |
| To Do | Ready to implement |
| In Progress | Being implemented by feature agent |
| In Review | Feature complete, awaiting human review |
| Done | Merged and closed |

## License

MIT
