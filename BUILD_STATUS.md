# BUILD_STATUS
| Area | Status | Notes |
|---|---|---|
| Project audit | COMPLETE | Defects found and fixed: symptom lost before the report, technical wording, generic 3-step guidance, no rule for a silent router, contradictory evidence classed as "possible", demo retest repeated the same result |
| Plain-language rewrite | COMPLETE | All app text, check names, results, report. README updated. Technical names kept as secondary labels |
| Technical glossary | COMPLETE | `plain.GLOSSARY` shown in "What does this mean?" on Results and Guided fix; check help text is visible, not tooltip-only |
| Scenario-specific guidance | COMPLETE | 6 flows tied to diagnosis keys, 3-5 steps each, with purpose, look-for, if-ok, if-not, alternative path, final retest |
| Windows navigation | IN PROGRESS | Windows 11/10 paths written from knowledge, NOT checked on a real PC. Menu names may differ |
| UI/UX improvements | IN PROGRESS | Results in the requested order, labels, progress, 5 answer options with real behaviour. Not viewed in a real browser; no accessibility audit tool run |
| Diagnostic correctness | COMPLETE | Rules unit-tested incl. gateway silence and conflicts |
| Retesting | COMPLETE | Before/after comparison; demo "pretend the fix worked" is labelled simulated |
| Reports | COMPLETE | Plain summary + technical section; marks simulated vs real; no env vars or keys |
| Demo Mode | COMPLETE | Offline, labelled, cleared on mode switch |
| Automated tests | COMPLETE | See final run in the reply |
| Startup verification | IN PROGRESS | Streamlit AppTest only (Linux). Not run on Windows or in a browser |
| Known limitations | COMPLETE | Ping may be blocked; point-in-time results; `ipconfig`/`route print` parsing untested on Windows; AI wording untested with a real key; "skip" and "didn't help" are recorded but don't branch to a different flow |

## AI assistant (Ollama Cloud)
| Item | Status | Notes |
|---|---|---|
| `netsathi/ai_client.py` | COMPLETE | POST https://ollama.com/api/chat, Bearer key, `stream:false`, answer from `message.content` (checked against docs.ollama.com/api/index) |
| Ask NetSathi chat view | COMPLETE | Chat input, spinner, clear chat, privacy note, missing-key help, friendly errors, history capped |
| Redaction | COMPLETE | IPv4, IPv6, MAC, hostnames, Windows user path, local user/computer name. Test targets (1.1.1.1, 8.8.8.8, example.com) kept |
| Removed defect | COMPLETE | Old `ai_explanation()` sent data automatically on the Results page and used the wrong provider. Removed |
| Mocked tests | COMPLETE | Request build, parsing, 401/403/429/404/5xx, timeouts, network, malformed/empty, limits, redaction, chat UI, engine isolation |
| Real Ollama call | NOT STARTED | No API key was available. The integration has NOT been tested against the live service |
| Default model `gemma4:31b` | IN PROGRESS | Taken from Ollama's docs example. Availability on your account is unchecked. Change with NETSATHI_MODEL |
| Browser / Windows check | NOT STARTED | Only Linux AppTest and a headless startup check |
