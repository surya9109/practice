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
        First_Name=data.get("firstName")
        Last_Name=data.get("lastName")
        Mobile_No=data.get("Phonenumber")
        Mail_Id=data.get("email")
        Otp=Generate(Mobile_No,random.randint(100000,999999))
        Time=time.time()
        print(First_Name,Last_Name,Mobile_No)
        Save(Mobile_No,Otp,First_Name,Last_Name,Mail_Id,Time)
        

#        return render_template("otp.html",mobile_html=Mobile_No)
#    return render_template("Registration1.html")
        return jsonify(success='s',mobile_No=Mobile_No)

def Generate(mobileno,otp):
    OTP_GEN_URL = "https://control.msg91.com/api/sendotp.php"
    OTP_AUTHKEY = '297073Ast2offG5d9efc2d'
    OTP_MSG = 'your verification otp is {}'
    querystring = {"otp": otp,"sender":"MSGIND","message": OTP_MSG.format(otp),
                   "mobile":mobileno,"authkey":OTP_AUTHKEY}
    requests.post(OTP_GEN_URL, params=querystring)
    return otp

def Save(Mobile_No,Otp,First_Name,Last_Name,Mail_Id,Time):
    d1[Mobile_No]={"mobile":None,"first_name":None,"last_name":None,"otp":None,"mail":None,"time":None}
    d1[Mobile_No]["mobile"]=Mobile_No
    d1[Mobile_No]["first_name"]=First_Name
    d1[Mobile_No]["last_name"]=Last_Name
    d1[Mobile_No]["otp"]=Otp
    d1[Mobile_No]["mail"]=Mail_Id
    d1[Mobile_No]["time"]=Time
    print(d1)
    
    
@app.route('/verify',methods=['GET','POST'])
def verify():
    if request.method=="POST":
        Mobile_Number=request.args.get("mobile")
        print(Mobile_Number, request.form, sep='\n')
        ver=verify_Otp(Mobile_Number)
        if ver:
            return jsonify(success='s',mobile_No=Mobile_Number)
        else:
            return "Verification Failed"
        
@app.route('/resume',methods=['GET','POST'])
def resume():
    if request.method=="POST":
         data=request.get_json()
         Mobile_Number=data.args.get('Mobile_Number')
         URL=Skills()
         Insert(Mobile_Number,URL)
         return "Registration Success"
        
        
        
        
        
def verify_Otp(Mobile_Number):
    time_now=time.time()
    verify_time=d1[Mobile_Number]['time']+300
    
    
    if time_now<=verify_time:
        Entered_Otp=request.form.get('entered_Otp')
        Verification_Otp=d1[Mobile_Number]["otp"]
        if str(Verification_Otp)==Entered_Otp:
            return True
        else:
            return False
    else:
        del d1[Mobile_Number]
        
def Skills():
        file_Name=request.files["resume"]
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
        
        
def Insert(Mobile_Number,URL):
    table.put_item(
            Item={ 
                "First_Name":d1[Mobile_Number]["first_name"],
                "Last_Name":d1[Mobile_Number]["last_name"],
                "Mail_Id":d1[Mobile_Number]["mail"],
                "Mobile_No": d1[Mobile_Number]["mobile"],
                "File_Url":URL
                }
            )
                
        
        
     
        
        
if __name__=="__main__":
#    app.run(debug=True)
    PORT = 8085
    HTTP_SERVER = WSGIServer(('0.0.0.0', PORT), app)
    print('Running on',PORT, '...')
    HTTP_SERVER.serve_forever()
#    print('Serving on 8088...')
#    WSGIServer(('127.0.0.1', 8088), application).serve_forever()

    