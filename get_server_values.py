import grequests
import requests
from dotenv import load_dotenv
import os

# loading app key and API key from .env file
load_dotenv()
APP_KEY = os.getenv("DATADOG_APP_KEY")
API_KEY = os.getenv("DATADOG_API_KEY")

headers = {
    "Content-Type": "application/json",
    "DD-API-KEY": API_KEY,
    "DD-APPLICATION-KEY": APP_KEY,
}


def node_by_group(headers):

    params = (
        ("filter", ""),
        ("groups", "environment"),
        ("ungrouped", "true"),
        ("node_type", "host"),
    )

    try:
        print("Started pulling nodes by group")
        response = requests.get(
            "https://app.datadoghq.com/api/v1/node_map/nodes_by_group",
            headers=headers,
            params=params,
        )
        # print("Success")
        return response
    except Exception as e:
        print(e)


def seprate_prod(nodes):
    prod = []
    print("Seprating prod nodes.")
    for item in nodes["groups"]:
        if item["key"] == "prod":
            prod = item['nodes']
    print("Done seprating prod nodes.")
    return prod


def fetch_prod():
    nodes = node_by_group(headers).json()
    prod_nodes = seprate_prod(nodes)
    get = {
        'for_names': {
            'url': 'https://app.datadoghq.com/api/v1/node_map/node_names',
            'payload': {
                "ids": prod_nodes,
                "name_to_display": "name",
                "node_type": "host",
            }
        },
        'for_values': {
            'url': 'https://app.datadoghq.com/api/v1/node_map/node_values',
            'payload': {
                "ids": prod_nodes,
                "metric": "DD_HOSTMAP_COMPOSITE_METRIC",
                "aggr": "avg",
                "node_type": "host",
            }
        }
    }

    server_rs = (grequests.post(
        url=value['url'], headers=headers, json=value['payload']) for value in get.values())

    server_result = grequests.map(server_rs)

    prod_names = server_result[0].json()
    prod_node_values = server_result[1].json()

    def get_server_data(prod_names, prod_node_values):
        for node_id, node_name in prod_names["nodes"].items():
            node_name['value'] = prod_node_values['nodes'][node_id]
        return prod_names["nodes"]

    return get_server_data(prod_names, prod_node_values)
