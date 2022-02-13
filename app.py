
from functools import partial
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from itsdangerous import json 
from marshmallow import Schema, fields, ValidationError
from bson.json_util import dumps
from json import loads
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
#app.config["MONGO_URI"] = "mongodb+srv://week3:J9eEhmeSISjZIvqw@cluster0.enls6.mongodb.net/fruit_basket?retryWrites=true&w=majority"
app.config["MONGO_URI"] = os.getenv("MONGO_CONNECTION_STRING")
mongo = PyMongo(app) 
# datetime object containing current date and time
date_time = datetime.now()#gets day and time
datetime_string = date_time.strftime("%d/%m/%Y, %H:%M:%S")#formats day and time

FAKE_DATABASE = {} # data base for user objects 
id_count = 0
count = 0
""""" PROFILE"""
#CREATE PROFILE
@app.route("/profile", methods=["POST"])
def post():
    username = request.json["username"] #recieves username from server
    role = request.json["role"] #reciever user role
    color = request.json["color"] #recieves user fav colour
    user_profile = { #dictionary containing user profile data 
        "data":{
            "role": role,
            "color":color,
            "username": username,
            "last_updated":datetime_string,
        },
        
    }
    global FAKE_DATABASE    # makes fakedatabase a global variable
    FAKE_DATABASE = user_profile  #assigns the user profile dictionary to the fake database
    
    return jsonify(FAKE_DATABASE) # for the fake database to be return we have to jsonify it 

#READ PROFILE
@app.route("/profile",methods = ["GET"])
def getuser(): # the read profile http get request returns the profile information from our fake database 
    return jsonify(FAKE_DATABASE)

#UPDATE PROFILE 
@app.route("/profile",methods = ["PATCH"]) # patch request to update user profile info 
def patchuser():
    new_date_time = datetime.now()#gets day and time
    new_datetime_string = new_date_time.strftime("%d/%m/%Y, %H:%M:%S")#formats day and time
    if "username" in  request.json: # if the json request from the client which in this case is our postman web app is a username 
        FAKE_DATABASE["data"]["username"] = request.json["username"] # store the json request from the client into the location in our dictionary that correspends to where usernames are stored 
        FAKE_DATABASE["data"]["last_updated"] = new_datetime_string 
    if "color" in request.json: # if the json request from the client which in this case is our postman web app is a color
        FAKE_DATABASE["data"]["color"] = request.json["color"]# store the json request from the client into the location in our dictionary that correspends to where colors are stored 
        FAKE_DATABASE["data"]["last_updated"] = new_datetime_string 
    if  "role" in request.json: # if the json request from the client which in this case is our postman web app is a role 
        FAKE_DATABASE["data"]["role"] = request.json["role"] # store the json request from the client into the location in our dictionary that correspends to where roles are stored 
        FAKE_DATABASE["data"]["last_updated"] = new_datetime_string 
   # if "last_updated" in (FAKE_DATABASE["data"]) != datetime_string:  # IF THE TIME STORED IN LAST UPDATED TIME IS NOT EQUAL TO THE CURRENT TIME WHEN WE PATCH THEN UPDATE THE TIME 
        #FAKE_DATABASE["data"]["last_updated"] = new_datetime_string ttttt
    return jsonify(FAKE_DATABASE)


"""TANKS"""

class TankSchema(Schema):
    location = fields.String(required=True)
    lat = fields.Float(required=True)
    long = fields.Float(required=True)
    percentage_full = fields.Integer(required=True)

@app.route("/data",methods = ["POST"])
def add_new_tank():    
    request_dict = request.json
    try:

        new_tank =  TankSchema().load(request_dict)
    except ValidationError as err:
        return (err.messages,400)
    tank_document = mongo.db.tanks.insert_one(new_tank)
    tank_id = tank_document.inserted_id

    tank = mongo.db.tanks.find_one({"_id":tank_id})

    tank_json = loads(dumps(tank))
    return jsonify(tank_json)

@app.route("/data",methods = ["GET"])
def get_tanks(): 
    tanks = mongo.db.tanks.find()
    tanks_list = loads(dumps(tanks))
    return jsonify(tanks_list)

@app.route("/data/<ObjectId:id>",methods = ["PATCH"])
def patch_tank(id):
    request_dict = request.json
    try:
        tank_patch = TankSchema(partial=True).load(request_dict)
    except ValidationError as err:
        return(err.messages,400)
    mongo.db.tanks.update_one({"_id": id}, {"$set": request.json})
    
    tank = mongo.db.tanks.find_one({"_id":id})
    tank_json = loads(dumps(tank))
   
    return (tank_json)
    

@app.route("/data/<ObjectId:id>",methods = ["DELETE"])
def delete_tANK(id):
    result = mongo.db.tanks.delete_one({"_id": id})
    if result.deleted_count == 1:
        return {"success": True}
    else:
        return{ "success": False},404
   

if __name__ == '__main__':
    app.run(debug=True, port=3000, host="0.0.0.0")