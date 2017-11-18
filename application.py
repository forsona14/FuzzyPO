from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import DateTime, and_
import requests
import random
import jsonpickle
from JRecInterface import JRecInterface
import uuid

#interfaces = {} 

#doc_id_to_text = {}

application = Flask(__name__)
application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://eland:Erikandersen17@eland-shuhan-language-learn.caeprog7ikpm.us-east-1.rds.amazonaws.com:3306/shuhan_language_learning'
CORS(application)
db = SQLAlchemy(application)

class UserData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(128), unique=False)
    session_id = db.Column(db.String(128), unique=False)
    tag = db.Column(db.String(128), unique=False)
    summary = db.Column(db.Float, unique=False)
    responses = db.Column(db.String(128), unique=False)
    
    def __init__(self, user_id, session_id, tag, summary, responses):
        self.user_id = user_id 
        self.session_id = session_id
        self.tag = tag 
        self.summary = summary
        self.responses = responses

    def __repr__(self):
        return '<UserData %r %r %r %r %r>' % (self.user_id, self.session_id, self.tag, str(self.summary), self.responses)

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(128), unique=False)
    article_id = db.Column(db.String(128), unique=False)
    answer = db.Column(db.Boolean, unique=False)
    session_id = db.Column(db.String(128), unique=False)
    sequence_id = db.Column(db.Integer, unique=False)
    info = db.Column(db.String(128), unique=False)
    seen_at = db.Column(DateTime)
    answered_at = db.Column(DateTime)

    def __init__(self, user_id, article_id, answer, session_id, sequence_id, info, seen_at, answered_at):
        self.user_id = user_id 
        self.article_id = article_id 
        self.answer = answer
        self.session_id = session_id 
        self.sequence_id = sequence_id
        self.info = info
        self.seen_at = datetime.fromtimestamp(seen_at / 1000.0)
        self.answered_at = datetime.fromtimestamp(answered_at / 1000.0)

    def __repr__(self):
        return '<Response %r %r %r %r %r %r>' % (self.user_id, self.article_id, self.answer, self.session_id, str(self.sequence_id), self.info, self.seen_at, self.answered_at)

@application.route('/')
def hello_world():
    return 'Hello, World! Shuhan'

@application.route('/initialize/', methods=['GET'])
def initialize():
  jrec = JRecInterface()
  req = jrec.request()
  user_id = str(uuid.uuid4()) 
  session_id = str(uuid.uuid4()) 
  return jsonify(user_id=user_id, 
                 session_id=session_id,
                 jrec=jrec.recommender_json_str(),
                 doc_id=req.doc_id,
                 text=req.text,
                 info=req.info) 

@application.route('/record_user/', methods=['POST'])
def record_user():
  try:
    json = request.get_json() 
    user_id = json['user_id']
    session_id = json['session_id']
    jrec = JRecInterface(json['jrec']) 
    tag = jrec.user_tag()
    summary = jrec.user_summary()
    responses = json['responses']
 
    userData = db.session.query(UserData).filter(UserData.session_id == session_id).first()
    userData.user_id = user_id
    userData.summary = summary
    userData.responses = responses    
    db.session.commit()
  except Exception as e:
    print e.args
    return "failure"
  jrec = JRecInterface()
  req = jrec.request()
  return jsonify(jrec=jrec.recommender_json_str(),
                 doc_id=req.doc_id,
                 text=req.text,
                 info=req.info,
                 session_id=str(uuid.uuid4()))

@application.route('/record_response/<userResponse>', methods=['POST']) 
def record_response(userResponse): 
  try:
    json = request.get_json()
    doc_id = json['doc_id']
    info = json['info']
    jrec = JRecInterface(json['jrec'])
    sequence_id = json['sequence_id']
    session_id = json['session_id']
    user_id = json['user_id']
    seen = json['seen'] 
    answered = json['answered']

    answer = True 
    if userResponse == 'false':
      answer = False

    userData = db.session.query(UserData).filter(UserData.session_id == session_id).first()
    if userData is None:
      userData = UserData(user_id, session_id, jrec.user_tag(), 0.0, "")
      db.session.add(userData)
      db.session.commit()
 
    response_data = Response(user_id, 
                             doc_id, 
                             answer, 
                             session_id, 
                             sequence_id,
                             info, 
                             seen, 
                             answered)

    db.session.add(response_data)
    db.session.commit()
    jrec.response(answer)
  except Exception as e:
    print e.args  
  
  if sequence_id < 39: 
    req = jrec.request()
    return jsonify(jrec=jrec.recommender_json_str(), 
                 next_doc_id=req.doc_id,
                 next_text=req.text,
                 next_info=req.info,
                 end=False) 
  else:
    _new_jrec = JRecInterface()
    req = _new_jrec.request()
    return jsonify(end=True,
                   new_jrec=_new_jrec.recommender_json_str(),
                   next_doc_id=req.doc_id,
                   next_text=req.text,
                   next_info=req.info,
                   user_summary=jrec.user_summary())
#@application.route('/get_uuid/', methods=['GET'])
#def generate_UUID():
#  global interfaces
#  uuid_str = str(uuid.uuid4())
#  interfaces[uuid_str] = JRecInterface()  
#  return uuid_str

#@application.route('/doc_id/<user_id>/', methods=['GET'])
#def article_id(user_id):
#	global interfaces
#	global doc_id_to_text
#        try:
#          if user_id not in interfaces:
#            interfaces[user_id] = JRecInterface()
#          req = interfaces[user_id].request()
#          req_id = req.doc_id 
#          doc_id_to_text[req_id] = req.text
#	  return req_id
#        except Exception as e:
#          print e.args
#          print e
#        return ""

#@application.route('/text/<doc_id>/', methods=['GET'])
#def get_text(doc_id):
#        return doc_id_to_text[doc_id] 
#
#@application.route('/response/<user_id>/<doc_id>/<userResponse>', methods=['POST'])
#def processResponse(user_id, doc_id, userResponse):
#	global interfaces
#	if not interfaces.has_key(user_id):
#	  return "Error"
#	if userResponse == 'true': 
#          interfaces[user_id].response(True) 
#        elif userResponse == 'false':
#          interfaces[user_id].response(False)
#	return doc_id  

#@application.route('/test/<user_id>', methods=['GET'])
#def jsonpickle_test(user_id):
#  return jsonpickle.encode(interfaces[user_id])

#@application.route('/test2', methods=['POST'])
#def jsonpickle_decode_test(): 
#  try:
#    print request.data
#    json = jsonpickle.decode(request.data)
#    temp = json.request()
#    print temp.doc_id 
    ##jrecObject = jsonpickle.decode(jsonpickle.encode(json_string))
#    return "hello"    
#return json_string 
#  except Exception as e:
#    print e.args
#  return "wat" 

if __name__ == "__main__":
  application.run(host='0.0.0.0')
