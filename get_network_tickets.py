from jira import JIRA
from dotenv import load_dotenv
import os

# loading app key and API key from .env file
load_dotenv()
TOKEN = os.getenv("JIRA_TOKEN")
SERVER_URL = os.getenv("JIRA_URL")


def fetch_tickets():
    jira = JIRA(server=SERVER_URL,
                token_auth=TOKEN)

    # TASK: There is max limit. Figure out how to remove it.
    jql = 'project = EI AND issuetype = Incident AND status in (Open, Reopened, "Waiting for customer", Escalated, "Work in progress", "Waiting for Vendor", "Waiting for IT Observation", "Waiting for Escalation Team") AND "ET Services" = Network'
    print("Started fetching network tickets")
    tickets = {ticket.key: {'summary': ticket.fields.summary}
               for ticket in jira.search_issues(jql_str=jql)}
    print("Done with network tickets.")
    return tickets
