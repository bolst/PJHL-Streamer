# PJHL Streamer

This is a script for downloading on-demand streams for PJHL games. All one needs is a game ID (which can be easily found on [https://pjhltv.ca/](https://pjhltv.ca/)) and a PJHL TV account (which is free).

For example, [https://pjhltv.ca/watch/13725](https://pjhltv.ca/watch/13725) has a game ID `13725`.

### Usage
1. Clone this repo `git clone https://github.com/bolst/PJHL-Streamer.git`
1. `cd` into `PJHL-Streamer`
1. Install dependencies `pip install -r requirements.txt`
1. Enter your PJHL TV account credentials in `UserCredentials.json`
1. Find your desired game ID and enter it in `GetStream.py`
1. Run with `python GetStream.py` and wait for the script to finish