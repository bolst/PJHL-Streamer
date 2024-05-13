import requests
import os
import json
from seleniumwire import webdriver 
from selenium.webdriver.common.by import By
import time

# Enter game ID
GameID = 18897

X0 = 21000000
X1 = 24000000
Dx = 500

# cache to remember endpoints already tried
request_cache = {}

request_headers = {}

def fetch_auth_headers(GameID):
    
    username_input = input('PJHL TV Email: ')
    password_input = input('PJHL TV Password: ')
    
    options = webdriver.ChromeOptions()
    options.add_argument('--log-level=3') # to make selenium shut up
    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome(options=options)

    driver.get('https://pjhltv.ca/login')

    username = driver.find_element(By.ID, "email")
    password = driver.find_element(By.ID, "password")

    username.send_keys(username_input)
    password.send_keys(password_input)

    driver.find_element(By.CLASS_NAME, "common-button-pjhl").click()

    time.sleep(5)

    driver.get(f'https://pjhltv.ca/watch/{GameID}')
    
    time.sleep(5)

    headers = {}

    for request in driver.requests:
        if request.response:
            if f'api.htptv.net/player/{GameID}' in request.url:
                s = request.headers
                headers = dict(s)
                break
    
    return headers

def get_watch_url(GameID=GameID) -> str:
    global request_headers
    request_headers = fetch_auth_headers(GameID)
    url = f'https://api.htptv.net/player/{GameID}?customer=6'
    response = requests.get(url=url, headers=request_headers)
    if response.status_code == 200:
        data = response.json()['data']
        if len(data) == 0:
            return ''
        else:
            return data[0]['watch_url']
    else:
        return ''
    
def generate_outfile_name(GameID=GameID) -> str:
    global request_headers
    url = f'https://api.htptv.net/player/{GameID}?customer=6'
    response = requests.get(url=url, headers=request_headers)
    if response.status_code == 200:
        data = response.json()['data']
        if len(data) == 0:
            return 'game.ts'
        else:
            home_abbrv = data[0]['home_team_short']
            away_abbrv = data[0]['away_team_short']
            game_date = data[0]['game_date']
            return f'{home_abbrv}-vs-{away_abbrv}-{game_date}.ts'
    else:
        return 'game.ts'
    
#url = 'https://dumaopej5nmkr.cloudfront.net/htpartners/6630ec29e608923c565d9146/cloud_hls/0_hd_hls/0_hd_2000/'
url = get_watch_url(GameID)
if len(url) == 0:
    print("Couldn't find a URL to try")
    exit(1)
url = url.replace('.m3u8', '/0_hd_2000/')
outfile = generate_outfile_name(GameID)


def construct_url(n:int, debug=False) -> str:
    retval = f'{url}{n}.ts'
    if debug:
        print(retval)
    return retval

# attempt request given a number
def attempt_request(n:int, download=False, debug=False) -> bool:
    str_n = str(n)
    global request_cache
    if str_n not in request_cache:
        r = requests.get(url=construct_url(n,debug=debug))
        request_cache[str_n] = (r.status_code == 200)
        
    return request_cache[str_n]

# finds a valid endpoint between x0 and x1 in steps of dx
# LS = Linear Search
def find_ts_endpoint_LS(x0=X0, x1=X1, dx=Dx, write_file=False, debug=False) -> int:
    N = (x1 - x0) // dx
    for n in range(x0,x1,dx):
        current_iter = (n - x0) // dx
        print(f'{current_iter}/{N}')
        r = attempt_request(n, debug=debug)
        if r:
            print(f'endpoint found at n={n}')
            if write_file:
                with open('endpoint-index.md', 'w+') as f:
                    f.write(str(n))
            return n
    # if fail
    print("Can't find endpoint. Try changing x0,x1,dx")
    return -1

# finds range of ts endpoints
# BS = Binary Search
# REQ is defined below since sometimes the true range of the ts endpoints have "gaps" that don't work
def find_ts_range_BS(n, dx=Dx, debug=False):
    l = n - dx # last iteration failed so n-dx is an invalid endpoint
    r = n + 2500 # usually no more than 2000 ts files, for sure no more than 2500
    def find_lower_bound():
        def REQ(n, tol=2):
            retval = False
            for i in range(0,tol+1):
                retval = attempt_request(n-i) or retval
            return retval
        left = l
        right = n
        while left <= right:
            mid = (left + right) // 2
            if REQ(mid):
                if not REQ(mid-1):
                    return mid
                else:
                    right = mid - 1
            else:
                left = mid + 1
        return -1
    def find_upper_bound():
        def REQ(n, tol=2):
            retval = False
            for i in range(0,tol+1):
                retval = attempt_request(n+i) or retval
            return retval
        left = n
        right = r
        while left <= right:
            mid = (left + right) // 2
            if REQ(mid):
                if not REQ(mid+1):
                    return mid
                else:
                    left = mid + 1
            else:
                right = mid - 1
        return -1
    
    lb = find_lower_bound()
    ub = find_upper_bound()
    return lb,ub

def download_ts(l,r):
    
    # calculate ETA
    req = requests.get(construct_url(l))
    seconds = req.elapsed.total_seconds() * abs(r-l)
    print("ETA: " + "{:.2f}".format(seconds/60) + " min")
    
    if not os.path.exists('ts-files'):
        os.makedirs('ts-files')
    else: # clean ts-files directory
        for f in os.listdir('ts-files'):
            os.remove(f'ts-files/{f}')
        
    for i in range(l,r+1):
        strIndex = str(i-l+1).zfill(4)
        req = requests.get(construct_url(i))
        if req.status_code == 200:
            with open(f'ts-files/in{strIndex}.ts', 'wb+') as f:
                f.write(req.content)
                print(f'Downloaded {i-l+1}/{r-l+1}')
    if os.name == 'nt': #if windows
        os.system(f'copy /b ts-files\\*.ts {outfile}')
    else: #if unix
        os.system(f'cat ts-files/*.ts > {outfile}')
    

def run():
    print(f"Downloading game #{GameID} ({outfile.replace('.ts','').replace('-', ' ')})")
    
    # find one endpoint that works
    print('\nfinding working endpoint...')
    n = find_ts_endpoint_LS(debug=True)
    if n == -1:
        exit(1)
        
    # find range of endpoints containing all ts files
    print('\nfinding endpoint range...')
    l,r = find_ts_range_BS(n, debug=True)
    print(f'found range [{l},{r}]')
    if l == -1 or r == -1:
        exit(1)
    
    # download ts files 
    print('\ndownloading...')
    download_ts(l,r)
    
    exit(0)

if __name__ == '__main__':
    run()
