# Foos OBS Scoreboard

## Setup
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

## Setup OBS WebSocket
```python
# IN OBS click: Tools → WebSocket Server Settings
# Turn ON the Enable WebSocket server option
# Set up a password

# In python backend you can connect easily with for e.g.:
import obsws_python as obs

HOST = "127.0.0.1"
PORT = 4455
PASSWORD = "your_password"

with obs.ReqClient(host=HOST, port=PORT, password=PASSWORD, timeout=5) as cl:
    status = cl.get_replay_buffer_status()
    print(status)

# or in this project just change the password in app/obs_action_utils.py
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