import os
import dropbox
import itertools

DROPBOX_KEY = os.environ.get("DROPBOX_KEY")

dbx = dropbox.Dropbox(DROPBOX_KEY)

link_string = 'https://www.dropbox.com/sh/usqs9geu79sr782/AABXmUrlU02ZkwqfisKFETaJa/Wilmington%2C%20DE?dl=0&subfolder_nav_tracking=1'
link = dropbox.files.SharedLink(url=link_string)

path = ""

download_path = "D:/uwin_sounds/WIDE"
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
    max_files = 10
    num_downloaded = 0

    for i, tmp_entry in enumerate(tmp_entries):
        if isinstance(tmp_entry, dropbox.files.FileMetadata):
            if i % 9 == 0 and num_downloaded < max_files:
                dropbox_path = f"{tmp_path}/{tmp_entry.name}"
                tmp_file_path = f"{download_path}{tmp_path}/{tmp_entry.name}"
                output_file = open(tmp_file_path, "wb")
                metadata, res = dbx.sharing_get_shared_link_file(url=link_string, path=dropbox_path)
                output_file.write(res.content)
                output_file.close()
                num_downloaded += 1
                print(f"{tmp_entry.name} downloaded successfully")
            elif num_downloaded >= max_files:
                break
