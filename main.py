import base64
import json
import os
import shutil
import sys
import time
from io import BytesIO

import boto3
import requests
import torch

from openchemie import OpenChemIE

ak = os.environ['OCHEM_ACCESS_KEY_ID']
sk = os.environ['OCHEM_SECRET_KEY']
s3_dest = os.environ['OCHEM_REACTIONS_DEST_S3PREFIX']
s3 = boto3.Session(aws_access_key_id=ak, aws_secret_access_key=sk).client('s3')

# if exactly one argument was not passed to the program, throw error
if len(sys.argv) != 2:
    raise ValueError("Usage: python main.py s3://bucket/path/to/sample.pdf")
# expect that the first arg to the program is the url to the pdf
test_url = sys.argv[1]


def download_from_s3(s3_url):
    bucket, key = s3_url.replace("s3://", "").split("/", 1)
    file_name = key.split("/")[-1]
    s3.download_file(bucket, key, file_name)
    return file_name


def download_from_url(url):
    base_name = os.path.basename(url)
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(base_name, 'wb') as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)
        return f.name


print('downloading pdf from {}'.format(test_url))
if test_url.startswith("s3://"):
    pdf_path = download_from_s3(test_url)
elif test_url.startswith('http://') or test_url.startswith('https://'):
    pdf_path = download_from_url(test_url)
else:
    raise ValueError("Invalid URL: {}".format(test_url))
print('done downloading file')
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = OpenChemIE(device=torch.device(device))
print('extracting reactions from pdf')
start_time = time.time()
# watch out! pdf and results should be small enough to fit into memory
extracted_results = model.extract_reactions_from_pdf(pdf_path)
end_time = time.time()
print(f'extracting reactions from pdf in {end_time - start_time} seconds')

# go through the figures and change the PIL images to base64 encoded strings
for figure in extracted_results['figures']:
    buffered = BytesIO()
    figure['figure'].save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())
    figure['figure'] = img_str.decode('utf-8')

# get the bucket from s3_dest
bucket, prefix = s3_dest.replace("s3://", "").split("/", 1)
# normalize the prefix to make sure it ends with a '/'
prefix = prefix if prefix.endswith("/") else prefix + "/"

file_name_no_ext = os.path.basename(pdf_path).split('.')[0]
upload_key = f'{prefix}{file_name_no_ext}.json'
print(f'saving extracted results to s3://{bucket}/{upload_key}')
s3.put_object(Body=json.dumps(extracted_results).encode(), Bucket=bucket, Key=upload_key)
print(f'Done!')
"""
        Returns:
            dictionary of reactions from multimodal sources
            {
                'figures': [
                    {
                        'figure': PIL image
                        'reactions': [
                            {
                                'reactants': [
                                    {
                                        'category': str,
                                        'bbox': tuple (x1,x2,y1,y2),
                                        'category_id': int,
                                        'smiles': str,
                                        'molfile': str,
                                    },
                                    # more reactants
                                ],
                                'conditions': [
                                    {
                                        'category': str,
                                        'text': list of str,
                                    },
                                    # more conditions
                                ],
                                'products': [
                                    # same structure as reactants
                                ]
                            },
                            # more reactions
                        ],
                        'page': int
                    },
                    # more figures
                ]
                'text': [
                    {
                        'page': page number
                        'reactions': [
                            {
                                'tokens': list of words in relevant sentence,
                                'reactions' : [
                                    {
                                        # key, value pairs where key is the label and value is a tuple
                                        # or list of tuples of the form (tokens, start index, end index)
                                        # where indices are for the corresponding token list and start and end are inclusive
                                    }
                                    # more reactions
                                ]
                            }
                            # more reactions in other sentences
                        ]
                    },
                    # more pages
                ]
            }

        """
