import pandas as pd
import requests, json
from plotly.offline import init_notebook_mode, iplot
import plotly.graph_objects as go

BE_URL = "https://www.blockedge.app"
BE_URL = "https://127.0.0.1:5000"

timeout = 60 * 1000
headers = {'accept': 'application/json', 'content-type': 'application/json'}

def get(url:str) -> dict:
    res = requests.get(url=url, timeout=timeout, headers=headers, verify=False)
    if res.status_code == 200:
        rj = json.loads(res.json())
        res.close()
        if rj.get('error'):
            print(rj)
            return dict()

        return rj

    res.close()
    return dict()

def search_query(query:str, page:int=1) -> dict:
    return get(f'{BE_URL}/search/waves/{query}/{page}')

query = 'get:transactions,timestamp'
res = search_query(query)
if res:
    table = res['results']['get_res']['recs']
    headers = res['results']['get_res']['attrs']
    df = pd.DataFrame(table, columns=headers)
    print(df.head(10))
else:
    df = pd.DataFrame()
    print ('something wrong')

if not df.empty:
    agg_dict = {
        'timestamp': 'first',
        'transactionCount': 'sum'
    }
    df['timestamp'] = pd.to_timedelta(df['timestamp'], 'ms')
    df = df.set_index(df['timestamp']).resample('M', label='left', closed='left').agg(agg_dict)
    df['date'] = pd.to_datetime(df['timestamp'], unit='ns').dt.strftime('%Y-%m-%d')

    init_notebook_mode(connected=True)
    data = [go.Bar(x=df.date, y=df.transactionCount)]
    iplot(data, filename='jupyter-basic_bar')