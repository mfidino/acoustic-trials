import requests
import json
import os
import dropbox

DROPBOX_API_KEY = os.environ.get("DROPBOX_API_KEY")
type(DROPBOX_API_KEY)
print(DROPBOX_API_KEY)

shared_link = 'https://www.dropbox.com/sh/usqs9geu79sr782/AAA_RoFmnvimAPm7V3QXT0-ha?dl=0'

response = requests.post(
    'https://api.dropboxapi.com/2/sharing/get_shared_link_metadata',
    headers={
        'Authorization': f'Bearer {DROPBOX_API_KEY}',
        'Content-Type': 'application/json'
    },
    json={
        'url': shared_link,
        'path': ''
    }
)

response.raise_for_status()

metadata = response.json()

if metadata['is_downloadable']:
    # The shared link is valid and the content is downloadable
    print("The shared link is valid and the content is downloadable.")
else:
    # The shared link is not valid or the content is not downloadable
    print("The shared link is not valid or the content is not downloadable.")

