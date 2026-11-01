# NetSathi
NetSathi helps you find out why your internet isn't working. It runs a few safe tests, explains the result in plain words, and shows you where to click to fix it. It never changes your settings.

## Features
Dashboard with symptom picker; live diagnostic session; results with a connection-path diagram; one-step-at-a-time guided fix; retest with comparison; JSON report; Demo Mode (simulated, offline); optional AI wording.

## Architecture
`app.py` (UI) -> `netsathi/diagnostics.py` (real checks) -> `netsathi/engine.py` (deterministic rules) -> `guidance.py` (manual steps) -> `explain.py` (wording only, never changes findings) -> `reporting.py` (JSON). `demo.py` holds synthetic scenarios.

## Install and run (Windows PowerShell)
    cd NetSathi
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    python -m streamlit run app.py
If activation is blocked: `Set-ExecutionPolicy -Scope Process Bypass`. Needs Python 3.11+.

## How to use it
Live Diagnosis: Dashboard -> pick a problem -> Start diagnosis -> View results -> Guided fix -> Retest -> Report.
Demo Mode: sidebar -> Demo Mode -> pick a scenario -> Start diagnosis. Switching mode clears the session.

## Tests
    python -m pytest -q

## Optional AI assistant (Ask NetSathi)
Ask questions in plain English on the "Ask NetSathi" page. It uses the Ollama Cloud API and is completely optional.
1. Create a key at https://ollama.com/settings/keys.
2. Copy `.env.example` to `.env` (PowerShell: `Copy-Item .env.example .env`) and put your key after `OLLAMA_API_KEY=`.
3. Optional: set `NETSATHI_MODEL` to another cloud model (list: https://ollama.com/api/tags).
4. Restart NetSathi.

AI answers explain and suggest. They are not test results. NetSathi's tests and rules decide the diagnosis, and the AI never runs commands. Nothing is sent until you press Enter on a question. Questions and (if ticked) a short summary of your results go to Ollama's cloud service, after IP addresses, MAC addresses, website names and your user/computer name are hidden. The key stays in `.env`, which Git ignores.

## Privacy and safety
Read-only checks, bounded timeouts, argument-list subprocesses, no admin rights, no history kept on disk. Reports contain check results and the OS name only.

## Known limits
Ping can be blocked by firewalls. Results are point-in-time. The public resolver test is one UDP query to 1.1.1.1 only. No traceroute (routing check is a table summary). Fonts load from Google Fonts with system fallbacks. Windows parsing of `ipconfig`/`route print` is untested by the author's sandbox (Linux).
