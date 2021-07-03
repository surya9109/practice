from flask import Flask,request,jsonify
import random,requests,time,boto3,io,logging
from gevent.pywsgi import WSGIServer
from flask_cors import CORS
from botocore.exceptions import ClientError


dynamodb=boto3.resource("dynamodb")
table=dynamodb.Table("RegistrationForm")


d1={}

app=Flask(__name__)
CORS(app)


@app.route("/login",methods=["POST","GET"])
def Show():
    if request.method=="POST":
        data=request.get_json()
        print(data)
        Mobile_No=request.get_json()
        Otp=Generate(Mobile_No,random.randint(100000,999999))
        Time=time.time()
        Save(Mobile_No,Otp,Time)
        d2={}
        d2[Mobile_No]={"Mobile_No":Mobile_No,"Otp":Otp}
        return jsonify(success='s',mobile_No=Mobile_No)
#        return d2[Mobile_No]
    
def Generate(mobileno,otp):
    OTP_GEN_URL = "https://control.msg91.com/api/sendotp.php"
    OTP_AUTHKEY = '297073Ast2offG5d9efc2d'
    OTP_MSG = 'your verification otp is {}'
    querystring = {"otp": otp,"sender":"MSGIND","message": OTP_MSG.format(otp),
                   "mobile":mobileno,"authkey":OTP_AUTHKEY}
    requests.post(OTP_GEN_URL, params=querystring)
    return otp


def Save(Mobile_No,Otp,Time):
    d1[Mobile_No]={"mobile":None,"otp":None,"time":None}
    d1[Mobile_No]["mobile"]=Mobile_No
    d1[Mobile_No]["otp"]=Otp
    d1[Mobile_No]['time']=Time
    print(d1[Mobile_No])
    
    
@app.route('/verify',methods=['GET','POST'])
def verify():
    if request.method=="POST":
        data=request.get_json()
        print(data)
        Mobile_Number=data['TempPhonenumber']
        print(Mobile_Number, request.form, sep='\n')
        
        time_now=time.time()
        verify_time=d1[Mobile_Number]['time']+300
        ver=verify_Otp(Mobile_Number,data,time_now,verify_time)
        if time_now<=verify_time:
        
            if ver:
                return jsonify(success='s',mobile_No=Mobile_Number)
            else:
                return jsonify("Verification Failed")
        else:
            del d1[Mobile_Number]
            return jsonify("Otp Expired")
        
     
def verify_Otp(Mobile_Number,data,time_now,verify_time): 
    
    if time_now<=verify_time:
        Entered_Otp=data['Otp']
        Verification_Otp=d1[Mobile_Number]["otp"]
        if str(Verification_Otp)==Entered_Otp:
            return True
        else:
            return False
        
        
@app.route('/submitteddata',methods=['GET','POST'])
def resume():
    if request.method=="POST":
         data=request.get_json()
         file_Name=request.files.get('fileData')
         print(file_Name)
         print(data)
         Mobile_Number=data['Phonenumber']
         First_Name=data['firstName']
         Last_Name=data["lastName"]
         Mail_Id=data["email"]
         print("Mobile_Number is ",Mobile_Number,"First_Name is ",First_Name,"Last_Name is",Last_Name,"Mail_Id is",Mail_Id,"file_Name is",file_Name)
         URL=Skills(file_Name)
         Insert(First_Name,Last_Name,Mail_Id,Mobile_Number,URL)
         print("file saved")
         
         return "Registration Success"
     
def Skills(file_Name):
    print("data enterd into s3")
    
    print("your file name is",file_Name)
    print(dir(file_Name))
    print("filename is ",file_Name.filename)
    bucket_name = 'uploadingdocument'
    file_name = file_Name.stream.read()
    object_name = file_Name.filename
    print(type(object_name))
    print(type(file_name))
    url='https://uploadingdocument.s3.ap-south-1.amazonaws.com/'+file_Name.filename
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
    return url    
   
def Insert(First_Name,Last_Name,Mail_Id,Mobile_Number,URL):
    print("data entered into dynamodb")
    table.put_item(
            Item={ 
                "First_Name":First_Name,
                "Last_Name":Last_Name,
                "Mail_Id":Mail_Id,
                "Mobile_No": Mobile_Number,
                "File_Url":URL
                }
            )
                
        
        
     
        
        
if __name__=="__main__":
#    app.run(debug=True)
    PORT = 8085
    HTTP_SERVER = WSGIServer(('0.0.0.0', PORT), app)
    print('Running on',PORT, '...')
    HTTP_SERVER.serve_forever()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    