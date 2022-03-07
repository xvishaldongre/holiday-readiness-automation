
import pandas as pd
import time
import grequests
from dotenv import load_dotenv
import os

# loading app key and API key from .env file
load_dotenv()
APP_KEY = os.getenv("DATADOG_APP_KEY")
API_KEY = os.getenv("DATADOG_API_KEY")


def get_apps_avalibility(headers, slo_ids, from_, to_):
    '''
    This function will return the avalibility of the slo_ids
    '''
    # params for the request
    params = {
        "interval": "60",
        "group_uptime": "false",
        "no_cache": "false",
        "target": "0",
        "from_ts": str(from_),
        "to_ts": str(to_),
    }

    # create a list of requests
    rs = (grequests.get(
        f"https://app.datadoghq.com/api/v1/slo/{slo_id}/history", headers=headers, params=params) for slo_id in slo_ids)

    # send all requests and wait for all of them to finish
    results = grequests.map(rs)

    def get_aval_res(item):
        # return the avalibility if status code is 200
        if item.status_code == 200:
            item = item.json()
            value = item['data']['overall']['sli_value']
            return round(value, 2)
        else:
            return None

    # get avalibility for each app
    aval = list(map(get_aval_res, results))

    return aval


def get_apps_performance(headers, perf_payload, from_, to_):
    '''
    This function will return the performance of the apps
    '''

    def modify_time(item):
        item["data"][0]["attributes"]["from"] = int(from_)*1000
        item["data"][0]["attributes"]["to"] = int(to_)*1000
        return item

    perf_payload = list(map(modify_time, perf_payload))

    # create a list of requests
    perf_rs = (grequests.post("https://app.datadoghq.com/api/v2/query/scalar",
               headers=headers, json=payload) for payload in perf_payload)

    # send all requests and wait for all of them to finish
    perf_results = grequests.map(perf_rs)
    # print(perf_results)

    def get_perf(item):
        # return performance if iteam status is 200
        if item.status_code == 200:
            item = item.json()
            # print(item)
            # name = item['data']['slo']['name']
            value = item["data"][0]["attributes"]["columns"][0]["values"][0]
            return round(value, 2)
        else:
            return None

    performance = list(map(get_perf, perf_results))
    return performance


def time_range_1h():
    '''
    This function will return the time range for 1 hour
    '''
    now = time.time()
    from_ = now - 3600
    to_ = now
    # convert to epoch time in milliseconds
    return {"from": int(from_), "to": int(to_)}


def genrate_apps_payload(payload_file):
    '''
    Generate the payload for the apps from the csv file
    '''
    print("Genrating payload for applications.")
    df = pd.read_csv(payload_file)
    apps_data = {}
    for index, row in df.iterrows():
        temp = {
            row["name"]: {
                "performance": {
                    "data": [
                        {
                            "type": "scalar_request",
                            "attributes": {
                                "formulas": [
                                    {"formula": "(query1 / (query1 + query2)) * 100"}
                                ],
                                "queries": [
                                    {
                                        "search": {"query": row["query1"]},
                                        "data_source": "logs",
                                        "compute": {"aggregation": "count"},
                                        "name": "query1",
                                        "indexes": ["*"],
                                        "group_by": [],
                                    },
                                    {
                                        "search": {"query": row["query2"]},
                                        "data_source": "logs",
                                        "compute": {"aggregation": "count"},
                                        "name": "query2",
                                        "indexes": ["*"],
                                        "group_by": [],
                                    },
                                ],
                                "from": 1645705656000,
                                "to": 1645709256000,
                            },
                        }
                    ]
                },
                "avalibility": {"slo_id": row["slo_id"]},
            }
        }

        apps_data.update(temp)
    print("Payload genrated.")
    return apps_data


def fetch_apps():

    # payload_file = "apps_payload.csv". Its create dict of apps and payloads for apps performance and avalibility
    apps_payload = genrate_apps_payload("apps_payload.csv")
    t_range = time_range_1h()
    from_ = t_range["from"]
    to_ = t_range["to"]

    headers = {
        "Content-Type": "application/json",
        "DD-API-KEY": API_KEY,
        "DD-APPLICATION-KEY": APP_KEY,
    }

    # create a list of payloads for performance of the apps
    perf_payload = [value['performance'] for value in apps_payload.values()]
    print("Started pulling applications performance.")
    performance = get_apps_performance(headers, perf_payload, from_, to_)

    # create a list of payload for avalibility of the apps

    aval_payload = [value['avalibility']['slo_id']
                    for value in apps_payload.values()]

    print("Started pulling applications avalibility.")
    avalibility = get_apps_avalibility(headers, aval_payload, from_, to_)

    print("Organizing apps data for result.")
    apps_names = [app_name for app_name in apps_payload.keys()]
    final = {app_name: {'performance': performance, 'avalibility': avalibility}
             for app_name, performance, avalibility in zip(apps_names, performance, avalibility)}
    print("Done organizing apps.")

    return final


# print(fetch_apps())
