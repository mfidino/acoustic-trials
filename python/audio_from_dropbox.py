import requests
import os

# Replace with your Dropbox access token
DROPBOX_API_KEY = os.environ.get("DROPBOX_API_KEY")

# Replace with your shared link
SHARED_LINK = "https://www.dropbox.com/sh/usqs9geu79sr782/AAA_RoFmnvimAPm7V3QXT0-ha?dl=0"

# Get the direct links for each WAV file in the shared link
headers = {
    "Authorization": f"Bearer {DROPBOX_API_KEY}",
    "Content-Type": "application/json"
}

url = "https://api.dropboxapi.com/2/sharing/get_shared_link_metadata"
print("try shared")
response = requests.post(url, headers=headers, json={"url": SHARED_LINK})
response.raise_for_status()
metadata = response.json()
links = []
for entry in metadata["metadata"]["links"]:
    if entry[".tag"] == "file":
        links.append(entry["url"].replace("?dl=0", "?dl=1"))

# Download each WAV file
for link in links:
    response = requests.get(link, allow_redirects=True)
    response.raise_for_status()
    file_name = link.split("/")[-1]
    with open(file_name, "wb") as f:
        f.write(response.content)