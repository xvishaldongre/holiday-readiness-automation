from get_apps_value import fetch_apps
from get_server_values import fetch_prod
from get_network_tickets import fetch_tickets
from confluence_publish_report import publish
import re
import time


def prepare_data(region, network_data, apps_data, server_data):
    # For Network
    filter = region["filter"]
    networks = []
    for ticket_id, value in network_data.items():
        if re.search(filter, value["summary"], re.IGNORECASE):
            networks.append(
                {
                    "id": ticket_id,
                    "description": value["summary"],
                    "impact": "Network team is working on incident.",
                    "eta": "N/A",
                }
            )
    # print(networks)
    # For Applications
    apps = []
    for app_name, values in apps_data.items():
        performance = values["performance"]
        avalibility = values["avalibility"]
        if (performance is not None and performance < 40) or (
            avalibility is not None and avalibility < 90
        ):
            id = ""
            description = f"{app_name} performance is {round(performance)}% and its availability is {round(avalibility)}%"
            impact = "Informed to SME. Their team is working on it."
            eta = "N/A"
            apps.append(
                {
                    "id": id,
                    "description": description,
                    "impact": impact,
                    "eta": eta,
                }
            )

    # For Prod Servers
    # print(server_data)
    servers = []
    for node_id, node_value in server_data.items():
        if node_value["value"] is not None and node_value["value"] > 90:
            id = ""
            description = f"CPU usage in server {node_value['name']} is above 85%. Currently it is {node_value['value']}%"
            impact = "Server team is working on the issue."
            eta = "N/A"
            servers.append(
                {
                    "id": id,
                    "description": description,
                    "impact": impact,
                    "eta": eta,
                }
            )
    # print(servers)

    return {
        "Networks": networks,
        "Applications": apps,
        "Servers": servers,
    }


def prepare_status(data):
    status = {
        "overall": "green",
        "apps": "green",
        "network": "green",
        "server": "green",
        "jira": "green",
    }
    # network
    if len(data["Networks"]) == 0:
        status["network"] = "green"
    else:
        status["network"] = "red"
    # apps
    if len(data["Applications"]) == 0:
        status["apps"] = "green"
    elif len(data["Applications"]) < 3:
        status["apps"] = "yellow"
    else:
        status["apps"] = "red"
    # servers
    if len(data["Servers"]) == 0:
        status["server"] = "green"
    elif len(data["Servers"]) < 2:
        status["server"] = "yellow"
    else:
        status["server"] = "red"

    # overall
    status_val = [val for val in status.values()]
    if status_val.count("red"):
        status["overall"] = "red"
    elif status_val.count("yellow"):
        status["overall"] = "yellow"
    else:
        status["overall"] = "green"

    return status


def prepare_date():
    """
    return todays date in human readable format. Ex- February 24th, 2022
    """
    return time.strftime("%B %d, %Y")


def organize_for_report(region, network_data, apps_data, server_data):

    data = prepare_data(region, network_data, apps_data, server_data)
    status = prepare_status(data)
    date = prepare_date()
    region_name = region["name"]
    report_time = region["report_time"]
    return {
        "region": region_name,
        "date": date,
        "time_to_show": report_time,
        "status": status,
        "data": data,
    }


network_data = fetch_tickets()
apps_data = fetch_apps()
server_data = fetch_prod()


## Regions Data
# P Testing page - 41596224643
# V Testing page - 884737
regions = [
    {
        "page_id": 884737,
        "name": "US East",
        "report_time": "07:00 AM EST",
        "filter": "us-",
    }
]


report_data = organize_for_report(regions[0], network_data, apps_data, server_data)
page_id = regions[0]["page_id"]

# print(report_data)
publish(page_id, report_data)
