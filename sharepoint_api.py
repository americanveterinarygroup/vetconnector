import logging
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential



def sharepoint_auth(usr, pwd, url):
    ### Initialize the client credentials
    user_credentials = UserCredential(usr, pwd)

    # create client context object
    ctx = ClientContext(url).with_credentials(user_credentials)
    logging.info(f'authenticate to sharepoint: {url}')

    return ctx



def download_files(ctx, dir, fp):
    libraryRoot = ctx.web.get_folder_by_server_relative_url(dir)
    files = libraryRoot.files
    ctx.load(files)
    ctx.execute_query()
    logging.info(f'get list of files from directory: {dir}')

    for myFiles in files:
        sru = myFiles.properties['ServerRelativeUrl']
        fn = str(sru).split('/')[-1]
        f = fp + fn

        with open(f, 'wb') as local_file:
            file = ctx.web.get_file_by_server_relative_url(sru)
            file.download(local_file)
            ctx.execute_query()
            logging.info(f'save file: {f}')




def create_sharepoint_directory(dir_name: str, ctx):
    if dir_name:

        result = ctx.web.folders.add(dir_name).execute_query()

        if result:
            # documents is titled as Shared Documents for relative URL in SP
            relative_url = dir_name
            logging.info(f'folder created: {dir_name}')
            return relative_url