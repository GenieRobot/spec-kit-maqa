# MAQA Trello Changelog

## 0.1.0 — 2026-03-26

Initial release.

- Setup command: reads Trello board via API and generates trello-config.yml
- Coordinator integration: auto-detected by MAQA coordinator when config + TRELLO_API_KEY present
- Real-time checklist ticking: feature agent ticks items via curl as each is completed
