# LAMBDA-PDF-COMPARE

## Description
This Lambda function takes a PDF file, extracts the text content and converts it to HTML file. This lambda function is called every time a new file is uploaded to a particular S3 bucket. The output file is saved in a different S3 bucket. This program uses the Python library PDFMiner. The required dependencies are compatible with Amazon Linux System and are already organized to be deployed as an zip file.

## Lambda Settings

- Git Clone repository
- zip file repository from terminal: zip -r9 ../index.zip *
- Create Function in Lambda console from scratch, using the following settings:
- Upload your zip file in the section Code entry type
- Runtime: `Python 3.6`
- Handler info: `lambda_function.handler`
- Timeout: 13 seconds
- Configuration Designer: Add trigger from the list. Select S3.
- Configure triggers: Select a Bucket that will be dedicated to only taking input files that will trigger the function. Then for Event Type select: Object Created(all). Finally check the box next to `Enable Trigger`.

### Basic Settings

Set the memory to `1536 MB`(XD) AND increase the timeout to `13 seconds`.

### Execution Role

To use S3, you will need to create a execution role with the correct permission.

### Triggers and Data
The trigger event will be the new upload of an S3 PDF file in a particular bucket you selected. In the file lambda_function.py, change the value of the variable bucket_to_upload to be correct bucket where you will output your HTML file. Also make sure is a different bucket that the one that triggers the function.
