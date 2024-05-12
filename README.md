# PJHL Streamer

This is a script for downloading on-demand streams for PJHL games. All one needs is a game ID (which can be easily found on [https://pjhltv.ca/](https://pjhltv.ca/)) and a PJHL TV account (which is free).

For example, [https://pjhltv.ca/watch/13725](https://pjhltv.ca/watch/13725) has a game ID `13725`.

### Usage
1. Clone this repo `git clone https://github.com/bolst/PJHL-Streamer.git`
1. Move into the repo `cd PJHL-Streamer`
1. Install dependencies `pip install -r requirements.txt`
1. Find your desired game ID and enter it in `GetStream.py`
1. Run with `python GetStream.py`

### If the script fails (try changing x0,x1,dx)
This happens because the search range for API endpoints didn't find any valid ones. You can variate x0,x1,dx but I suggest moving x0 and x1 to scan different ranges. Typically I have found most endpoints lie between 21700000 and 22400000
