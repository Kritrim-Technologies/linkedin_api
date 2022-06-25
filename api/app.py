from flask import Flask, jsonify, render_template, request, make_response
import jwt
import datetime
from functools import wraps
from api.linkedin import Linkedin, get_id_from_urn


api = Linkedin()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisisthesecretkey'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'message': 'Token is missing'}), 403

        data = jwt.decode(token, app.config['SECRET_KEY'])

        return f(*args, **kwargs)
    return decorated

@app.route('/')
def home():
    return {"message": "This is secured api for linkedin"}



@app.route('/login_api')
def login_api():
    auth = request.authorization
    if auth and auth.password == app.config['SECRET_KEY']:
        token = jwt.encode({'user' : auth.username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'token':token.decode('UTF-8')})
    
    return make_response('Could not verify!', 401, {'WWW-Authenticate':'Basic realm="Login Required"'})

@app.route('/api/login_linkedin')
@token_required
def login():

    username = request.values.get('username')
    password = request.values.get('password')

   
    if username and password:
        return jsonify(api.authenticate(username, password)), 201
        
    return render_template('login.html')

@app.route('/api/me')
@token_required
def get_profile():
    me = {}
    profile = api.get_user_profile()
    urn_id=get_id_from_urn(profile['miniProfile']['entityUrn'])
    me['firstName'] = profile["miniProfile"]['firstName']
    me['lastName'] = profile["miniProfile"]['lastName']
    me['occupation'] = profile["miniProfile"]['occupation']
    me['publicId'] = profile["miniProfile"]["publicIdentifier"]
      
    contact = api.get_profile_contact_info(urn_id=urn_id)
    profile = api.get_profile(urn_id=urn_id)
    skills = api.get_profile_skills(urn_id=urn_id)
  
    me['contact']=contact
    me['profile'] = profile
    me['skills'] = skills
    return jsonify(me)

@app.route('/api/connects')
@token_required
def get_connects():
    profile = api.get_user_profile()
    urn_id=get_id_from_urn(profile['miniProfile']['entityUrn'])
    profile_connections = api.get_profile_connections(urn_id)
    return jsonify(profile_connections)

@app.route('/api/connects/info')
@token_required
def get_connect_contacts():
    profile = api.get_user_profile()
    urn_id=get_id_from_urn(profile['miniProfile']['entityUrn'])
    profile_connections = api.get_profile_connections(urn_id)
    infos=[]
    for profile_connection in profile_connections:
        info = {}
        urn_id = profile_connection['urn_id']
        public_id = profile_connection ['public_id']
        contact = api.get_profile_contact_info(urn_id=urn_id)
        profile = api.get_profile(urn_id=urn_id)
        skills = api.get_profile_skills(urn_id=urn_id)
        info['public_id']=public_id
        info['contact']=contact
        info['profile'] = profile
        info['skills'] = skills
        infos.append(info)
    
    return jsonify(infos)
