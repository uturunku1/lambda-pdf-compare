from __future__ import print_function
import json
import boto3
import time
import os
import sys
import uuid
import logging
import io
s3 = boto3.client('s3')
logger = logging.getLogger()
logger.setLevel(logging.INFO)
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams, LTPage, LTRect, LTCurve, LTFigure
import pdfminer.layout as Layout
from pdfminer.converter import PDFPageAggregator, XMLConverter, HTMLConverter, TextConverter

def handler(event, context):
    print('Starting...')
    eventRecord = event['Records'][0]
    if(eventRecord):
        bucket = eventRecord['s3']['bucket']['name']
        key = eventRecord['s3']['object']['key']
        logger.info('reading file {} from bucket {}'.format(key, bucket))
        # response = s3.get_object(Bucket=bucket, Key=key)
        # print('response: '+ response)
        if(key.endswith('.pdf')):
            pdf_tmp = '/tmp/{}'.format(key)
            print('pdf_tmp is: '+pdf_tmp)
            html_key = '{}.html'.format(uuid.uuid4())
            html_tmp = '/tmp/{}'.format(html_key)
            json_key = '{}.json'.format(uuid.uuid4())
            json_tmp = '/tmp/{}'.format(json_key)
            bucket_to_upload = 'democracy-live'
            print('html_tmp is: '+html_tmp)
            print('json_tmp is: '+json_tmp)
            try:
                s3.download_file(bucket, key, pdf_tmp)
                create_html(pdf_tmp, html_tmp, '')
                create_json(pdf_tmp, json_tmp, '')
                #upload a new file
                # data = open('me.jpg', 'rb')
                # s3.Bucket('democracy-live').put_object(Key='new.jpg', Body=data)
                print('Begin uploading process...')
                s3.upload_file(html_tmp, bucket_to_upload, html_key)
                s3.upload_file(json_tmp, bucket_to_upload, json_key)
                print(html_key+ ' and '+ json_key+ ' have been uploaded to '+ bucket_to_upload)
            except Exception as e:
                print(e)
                raise e
        else:
            raise ValueError('File must be a PDF')
    else:
        print('no records in the event')

def create_html(pdf_file_path, newfile, password):
    doc = doc_parser(pdf_file_path, password)
    #manager to store resources such as fonts, images
    rsrcmgr = PDFResourceManager()
    #set params for analysis.layout analizer returns a LTPage that is a tree with child objects, like textbox, figure, curve, text line
    laparams = Layout.LAParams(all_texts=True, detect_vertical=True)
    with open(newfile,'w+') as f:
        # PDFDevice to translate content to our needs
        device = HTMLConverter(rsrcmgr, f, laparams=laparams, layoutmode='loose', showpageno=False, rect_colors={'curve': None})
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

def parse_layoutPage(layoutPage, top, curves_list, page_num):
    """Recursively parse layoutPage objects found"""
    min_y = int(top/7)
    max_y = int(top/1.15)
    def point2coord(pt):
        x, y = pt
        return (int(x), top-int(y))
    def bbox2coord(bbox):
        x0, y0, x1, y1 = bbox
        return (int(x0), top-int(y0), int(x1), top-int(y1))
    for obj in layoutPage:
        if isinstance(obj, LTCurve):
            y = top - int(obj.y1)
            x = int(obj.x0)
            h = int(obj.height)
            w = int(obj.width)
            lw = obj.linewidth
            bbox = list(bbox2coord(obj.bbox))
            #[(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
            pts = list(map(point2coord, obj.pts))
            if(h>=4 and w>=7 and w<23 and w>h*1.29 and x>26 and x<400 and y>min_y and y<max_y):
                props = {'x': x, 'y': y, 'height': h, 'width': w, 'linewidth':lw, 'bbox':bbox,'points':pts,'page':page_num}
                curves_list.append(props)
        elif isinstance(obj, LTFigure):
            parse_layoutPage(obj, top, curves_list, page_num)

def create_json(pdf_file_path, json_tmp, password=''):
    doc = doc_parser(pdf_file_path, password)
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    # Create a PDF page aggregator object.
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    page_num = 0

    data = {}
    data['curves'] = []
    for page in doc.get_pages():
        interpreter.process_page(page)
        # receive the LTPage object for the page
        layoutPage = device.get_result()
        top_page = layoutPage.y1
        logger.info('width of page {} and height {}'.format(layoutPage.x1, layoutPage.y1))
        page_num+=1
        parse_layoutPage(layoutPage, top_page, data['curves'], page_num)

    #write to JSON file
    with io.open(json_tmp, 'w', encoding='utf8') as outfile:
        str = json.dumps(data, indent = 4, separators=(',',':'))
        outfile.write(str)
