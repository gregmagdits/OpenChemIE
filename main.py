import json
import os
import shutil
import sys

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


pdf_path = download_from_url(test_url)
model = OpenChemIE(device=torch.device('cuda'))  # change to cuda for gpu
# TODO this needs to be a small enough pdf where the reactions will fit into memory. Shouldnt be a problem
extracted_results = model.extract_reactions_from_pdf(pdf_path)
print(extracted_results)

# get the bucket from s3_dest
bucket, prefix = s3_dest.replace("s3://", "").split("/", 1)
file_name_no_ext = os.path.basename(pdf_path).split('.')[0]
upload_key = f'{prefix}/{file_name_no_ext}.json'
s3.put_object(Body=json.dumps(extracted_results).encode(), Bucket=bucket, Key=upload_key)

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
