import os
import dropbox

DROPBOX_KEY = os.environ.get("DROPBOX_KEY")

dbx = dropbox.Dropbox(DROPBOX_KEY)

link_string = 'https://www.dropbox.com/sh/usqs9geu79sr782/AADa68cEF9WpVC4Yj24KjW9Ra/Chicago%2C%20IL?dl=0&subfolder_nav_tracking=1'
link = dropbox.files.SharedLink(url=link_string)

path = "/Late uploads"

download_path = "D:/acoustics/CHIL"
entries = dbx.files_list_folder(path=path, shared_link=link).entries
for entry in entries:
    tmp_path = f"{path}/{entry.name}"
    tmp_entries = dbx.files_list_folder(path=tmp_path, shared_link=link).entries
    # check to create folder if needed
    to_save = f"{download_path}{tmp_path}"
    if os.path.exists(to_save):
        print(f"{to_save} already exists, moving to next")
        continue
    os.makedirs(to_save)
    print(to_save)
    for tmp_entry in tmp_entries:
        if isinstance(tmp_entry, dropbox.files.FileMetadata):
            dropbox_path = f"{tmp_path}/{tmp_entry.name}"
            tmp_file_path = f"{download_path}{tmp_path}/{tmp_entry.name}"
            output_file = open(tmp_file_path, "wb")
            metadata, res = dbx.sharing_get_shared_link_file(url=link_string, path=dropbox_path)
            output_file.write(res.content)
            output_file.close()
            print(f"{tmp_entry.name} downloaded successfully")

# https://www.dropboxforum.com/t5/Dropbox-API-Support-Feedback/Get-refresh-token-from-access-token/td-p/596739