#this the practice file

from flask import Flask,request
import boto3,io,logging
from gevent.pywsgi import WSGIServer
from flask_cors import CORS
from botocore.exceptions import ClientError

dynamodb=boto3.resource("dynamodb")
table=dynamodb.Table("RegistrationForm")

app=Flask(__name__)
CORS(app)


@app.route('/save',methods=['POST','GET'])
def save():
    if request.method=='POST':
        file_Name=request.files.get("audio_data")
        print(file_Name)
        upload=Skills(file_Name)
        if upload:
            return "File Uploaded Succesfully" 


def Skills(file_Name):
        
        print(dir(file_Name))
        print("filename is ",file_Name.filename)
        bucket_name = 'uploadingaudio'
        file_name = file_Name.stream.read()
        object_name = file_Name.filename
        print(type(object_name))
        print(type(file_name))
        logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s: %(asctime)s: %(message)s')
        if object_name is None:
            object_name = file_name
        s3 = boto3.client('s3')
        file_name = io.BytesIO(file_name)
        try:
            response = s3.upload_fileobj(file_name, bucket_name, object_name)
        except ClientError as e:
            logging.error(e)
            return False
        return True


if __name__=="__main__":
    
    PORT = 8088
    HTTP_SERVER = WSGIServer(('0.0.0.0', PORT), app)
    print('Running on',PORT, '...')
    HTTP_SERVER.serve_forever()
    
    
    
    
    
    