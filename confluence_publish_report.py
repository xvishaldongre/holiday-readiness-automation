from atlassian import Confluence
from confluence_report_template import template
from dotenv import load_dotenv
import os

# loading app key and API key from .env file
load_dotenv()
URL = os.getenv("CONFLUENCE_URL")
USERNAME = os.getenv("CONFLUENCE_USERNAME")
TOKEN = os.getenv("CONFLUENCE_TOKEN")
# Cloud bool can't set in env file.
CLOUD = True



def publish(page_id, data):

    print("Publishing report to confluence page.")
    auth_url, auth_username, auth_password, auth_cloud = URL, USERNAME, TOKEN, CLOUD

    # Initialize Confluence object
    confluence = Confluence(
        auth_url,
        auth_username,
        auth_password,
        auth_cloud,
    )

    # Get the page content
    page_content = confluence.get_page_by_id(page_id, expand="body.storage")
    title = page_content["title"]
    old_content = page_content["body"]["storage"]["value"]

    # Render the template with given data
    new_report = template.render(
        region=data["region"],
        date=data["date"],
        time_to_show=data["time_to_show"],
        status=data["status"],
        data=data["data"],
    )

    # Merge the old content with the new content because if we append the data it will go to bottom of the page
    updated_content = new_report + old_content

    # Update the page and if fails try 3 time
    for i in range(3):
        try:
            print(f"Trying{i}...")
            confluence.update_page(
                page_id,
                title=title,
                body=updated_content,
                parent_id=None,
                type="page",
                representation="storage",
                minor_edit=False,
            )
            print("Published Successfully")
        except Exception as e:
            print(f"Error occured: {e}")
            continue
        break
