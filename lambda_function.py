from __future__ import print_function
import json
import boto3
import time
import os
import sys
import uuid
import logging
s3 = boto3.client('s3')
logger = logging.getLogger()
logger.setLevel(logging.INFO)
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
import pdfminer.layout as Layout
from pdfminer.converter import PDFPageAggregator, XMLConverter, HTMLConverter, TextConverter
from page import Page
from curve import Curve

def handler(event, context):
    print('Starting...')
    eventRecord = event['Records'][0]
    if(eventRecord):
        bucket = eventRecord['s3']['bucket']['name']
        key = eventRecord['s3']['object']['key']
        # response = s3.get_object(Bucket=bucket, Key=key)
        # print('response: '+ response)
        logger.info('reading file {} from bucket {}'.format(key, bucket))
        pdf_tmp = '/tmp/{}'.format(key)
        print('pdf_tmp is: '+pdf_tmp)
        html_key = '{}.html'.format(uuid.uuid4())
        html_tmp = '/tmp/{}'.format(html_key)
        bucket_to_upload = 'democracy-live'
        print('html_tmp is: '+html_tmp)
        try:
            s3.download_file(bucket, key, pdf_tmp)
            create_html(pdf_tmp, html_tmp, '')
            #upload a new file
            # data = open('me.jpg', 'rb')
            # s3.Bucket('democracy-live').put_object(Key='new.jpg', Body=data)
            print('Begin uploading process...')
            s3.upload_file(html_tmp, bucket_to_upload, html_key)
            print(html_key+ ' has been uploaded to '+ bucket_to_upload)
        except Exception as e:
            print(e)
            raise e
    else:
        print('no records in the event')

def create_html(pdf_file_path, newfile, password):
    doc = doc_parser(pdf_file_path, password)
    #manager to store resources such as fonts, images
    rsrcmgr = PDFResourceManager()
    #set params for analysis.layout analizer returns a LTPage that is a tree with child objects, like textbox, figure, curve, text line
    laparams = Layout.LAParams()
    with open(newfile,'w+') as f:
        # PDFDevice to translate content to our needs
        device = HTMLConverter(rsrcmgr, f, laparams=laparams)
        # processes page contents, renders intructions for device
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in doc.get_pages():
            interpreter.process_page(page)

def doc_parser(pdf_file, password):
    with open(pdf_file, 'rb') as fp:
        #parser obj feches data from file. Connect it to specific pdf
        parser = PDFParser(fp)
        #create document object that stores data from file
        # doc = PDFDocument(parser, password) no longer needs to set doc and parser
        doc = PDFDocument()
        #connect parser and doc
        parser.set_document(doc)
        doc.set_parser(parser)
        #if not password for initialization, provide an empty string
        doc.initialize(password)
        #if doc does not allow text extraction, abort!
        if not doc.is_extractable:
            raise PDFTextExtractionNotAllowed
        return doc
