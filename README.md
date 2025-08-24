# Crash Game Monitor

A Python script that monitors crash games and records the final crash values.

## Setup

1. Clone this repository
2. Install requirements: `pip install -r requirements.txt`
3. Set the GAME_URL environment variable to your crash game URL
4. Run the script: `python crash_monitor.py`

## Deployment to Render.com

1. Fork this repository to your GitHub account
2. Connect your GitHub account to Render.com
3. Create a new Web Service on Render
4. Connect your repository
5. Set the GAME_URL environment variable in Render dashboard
6. Deploy!

The script will run continuously and save crash values to `crash_results.txt`.
