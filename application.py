from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import requests
import random
import jsonpickle
from JRecInterface import JRecInterface
import uuid

interfaces = {} 

doc_id_to_text = {}

application = Flask(__name__)
CORS(application)

@application.route('/')
def hello_world():
    return 'Hello, World! Shuhan'

@application.route('/initialize/', methods=['GET'])
def initialize():
  jrec = JRecInterface()
  req = jrec.request() 
  return jsonify(user_id=str(uuid.uuid4()), 
                 session_id=str(uuid.uuid4()),
                 jrec=jrec.recommender_json_str(),
                 doc_id=req.id,
                 text=req.text) 

@application.route('/get_request/', methods=['POST']) 
def get_request(): 
  jrec = JRecInterface(request.data) 
  req = jrec.request() 
  return jsonify(doc_id=req.id, 
                text=req.text) 
 
@application.route('/get_request_id/', methods=['POST']) 
def get_request_id(): 
  return JRecInterface(request.data).request().id  
 
@application.route('/get_request_text/', methods=['POST']) 
def get_request_text():
  return JRecInterface(request.data).request().text

@application.route('/record_response/<userResponse>', methods=['POST']) 
def record_response(userResponse): 
  try:
    jrec = JRecInterface(request.data)
    if userResponse == 'true':
      jrec.response(True)
    else:
      jrec.response(False) 
    req = jrec.request()
  except Exception as e:
    print e.args  
  return jsonify(jrec=jrec.recommender_json_str(), 
                 next_doc_id=req.id,
                 next_text=req.text) 
    
@application.route('/get_uuid/', methods=['GET'])
def generate_UUID():
  global interfaces
  uuid_str = str(uuid.uuid4())
  interfaces[uuid_str] = JRecInterface()  
  return uuid_str

@application.route('/doc_id/<user_id>/', methods=['GET'])
def article_id(user_id):
	global interfaces
	global doc_id_to_text
        try:
          if user_id not in interfaces:
            interfaces[user_id] = JRecInterface()
          req = interfaces[user_id].request()
          req_id = req.doc_id 
          doc_id_to_text[req_id] = req.text
	  return req_id
        except Exception as e:
          print e.args
          print e
        return ""

@application.route('/text/<doc_id>/', methods=['GET'])
def get_text(doc_id):
        return doc_id_to_text[doc_id] 

@application.route('/response/<user_id>/<doc_id>/<userResponse>', methods=['POST'])
def processResponse(user_id, doc_id, userResponse):
	global interfaces
	if not interfaces.has_key(user_id):
	  return "Error"
	if userResponse == 'true': 
          interfaces[user_id].response(True) 
        elif userResponse == 'false':
          interfaces[user_id].response(False)
	return doc_id  

@application.route('/test/<user_id>', methods=['GET'])
def jsonpickle_test(user_id):
  return jsonpickle.encode(interfaces[user_id])

@application.route('/test2', methods=['POST'])
def jsonpickle_decode_test(): 
  try:
    print request.data
    json = jsonpickle.decode(request.data)
    temp = json.request()
    print temp.doc_id 
    ##jrecObject = jsonpickle.decode(jsonpickle.encode(json_string))
    return "hello"    
#return json_string 
  except Exception as e:
    print e.args
  return "wat" 

if __name__ == "__main__":
  application.run(host='0.0.0.0')
