################################################################
# DOWNLOAD ENTIRE FOLDER STRUCTURE FROM DROPBOX TO LOCAL DRIVE #
################################################################

# Instructions:
# (1) install dropbox API using pip
# > pip install dropbox

# (2) Create application to make requests to the Dropbox API
# - Go to: https://dropbox.com/developers/apps
# - Register your own App - e.g., call it "personal access to research data"
# - Copy secret *access token* after registering your app (click on get token)
#   Paste that access token to a file called *token_dropbox.txt*. 
#   Make sure you do not version this file on Git, as it would allow others
#   to obtain data from your Dropbox. For example, you can add that file name
#   to .gitignore.
import os
import dropbox
from get_dropbox import get_folders, get_files, wipe_dir

# read access token
DROPBOX_KEY = os.environ.get("DROPBOX_KEY")

# Authenticate with Dropbox
print('Authenticating with Dropbox...')
dbx = dropbox.Dropbox(DROPBOX_KEY)
print('...authenticated with Dropbox owned by ' + dbx.users_get_current_account().name.display_name)

# (3) Obtain ID of folder that needs to be downloaded
#   folders = get_folders(), which generates a list with ID numbers for each folder
#   in your Dropbox (may take some time!!!)
#   Specifiy a path (if you know that path) for a directory "close" to your target
#   directory. Otherwise, this script will loop through the *entire* file structure
#   of your Dropbox, which will take a lot of time.
print("Getting folders")
path = "/UWIN AudioMoth Pilot Data/Chicago, IL"
result = dbx.files_list_folder(path=path, recursive=True)
#result = dbx.files_list_folder(path='',shared_link = link, recursive=True)
#folders=get_folders(dbx, link)

# Let's take a look at these folder IDs
#print(folders)

# Select target folder and copy desired folder ID below
folder_id = 'id:RRmw_EHjdSAAAAAAAAAo9w'

# Set target download directory on your local computer; ends with (e.g., raw_data/)
download_dir = 'D:/dropbox/acoustic/'

##################
# DOWNLOAD FILES #
##################

# obtain list of files of target dir
#print('Obtaining list of files in target directory...')
#get_files(dbx, folder_id, download_dir)