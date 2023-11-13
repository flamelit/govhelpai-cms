import datetime as dt
import logging
import os
from typing import List

from openai import OpenAI

logger = logging.getLogger(__name__)

api_key = os.environ['OPENAI_API_KEY']
org_key = os.environ['OPENAI_ORG_KEY']

client = OpenAI(
    organization=org_key,
    api_key = api_key
)

def parse_files_list(input_info : dict) -> List[str]:
    """Parse filenames from OpenAI in org"""
    if len(input_info['data'])==0:
        return []
    else:
        return [x['filename'] for x in input_info['data']]

class UploadFileList():
    def __init__(
            self,
            file_list: List[str],
            org_key: str,
            api_key:str ,
            purpose: str,
            overwrite: bool =True):
        """Init file uploader"""
        client = OpenAI(organization=org_key, api_key=api_key)
        self.purpopose = purpose
        self.overwrite = overwrite
        self.file_list = self.file_list_parse(file_list, client)

    def file_list_parse(self, file_list, client):
        """Reduce list of files to upload if same-named files exist"""
        # Ensure files don't exist. This will bottleneck as filecount increases
        if self.overwrite is False:
            existing_files = parse_files_list(client.files.list().dump())
            self.files_to_write = [x for x in file_list if x not in existing_files]
        else:
            self.files_to_write = file_list
        logging.info('Filelist ready for upload')

    def upload_files(self, client):
        """Upload files"""
        file_count = len(self.file_list)
        for n, file_name in enumerate(self.file_list):
            logger.info(f'Uploading file {n} of {file_count}')
            try:
                resp = client.files.create(
                    filecontent = open(file_name,'rb'),
                    purpose = self.purpose
                )
                logger.info(f'File {resp["filename"]} uploaded at '
                            f'{dt.datetime.utcfromtimestamp(resp["created_at"]).isoformat()}'
                            f' for {self.purpose}')
            except Exception as e:
                logger.error(f'Failure to upload {file_name}. Exception Traceback: {str(e)}')

