# Foos OBS Scoreboard

## Setup
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

## Integrate to OBS
```bash
Install URL Source plugin
https://github.com/royshil/obs-urlsource/releases

Add new source: URL Source

Change the URL to:
http://127.0.0.1:8765/state

Click on Setup Data Source
Set Method to GET

Set Output Parsing Options
 - Parsing Type: JSON
 - JSON Path (example): $.score.timeouts_right_string

Set your Render Width based on the maximum width of the source

Open the webapp control site in your browser: http://127.0.0.1:8765/control
Enjoy your live score setup for your tournament! :)
```