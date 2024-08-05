from flask import Flask, request, session, jsonify
# from datetime import timedelta, datetime
from flask_mysqldb import MySQL
import MySQLdb.cursors 
# import googlemaps
# import geocoder
# from geopy.geocoders import Nominatim
# from geopy.distance import geodesic
# import geopy
import requests
from requests.structures import CaseInsensitiveDict
from credentials import api_key
# geolocator = Nominatim(user_agent="todo")

app = Flask(__name__)
mysql = MySQL(app)
app.secret_key = "key"


geoapi = api_key #geopify

headers = CaseInsensitiveDict()
headers["Accept"] = "application/json"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Jayjagtap@2291'
app.config['MYSQL_DB'] = 'Todolist'

def add_task(task, loc, ui):   
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f"INSERT INTO todo (Task, location, userid) VALUES {task, loc, ui}")
    mysql.connection.commit()
    return task     

def myip():
    url_ip = f"https://api.geoapify.com/v1/ipinfo?&apiKey={geoapi}"
    resp = requests.get(url_ip, headers=headers)
    response = resp.json()
    location = response.get('location')
    latitude = location.get('latitude')
    longitude = location.get('longitude')
    return latitude, longitude

def nearby_tasks(categories):
    latitude, longitude = myip()
    radius = 3000
    filter_param = f'circle:{longitude},{latitude},{radius}'
    bias_param = f'proximity:{longitude},{latitude}'
    limit= 1
    url = f"https://api.geoapify.com/v2/places?categories={categories}&filter={filter_param}&bias={bias_param}&limit={limit}&apiKey={geoapi}"
    return url

# def find_nearby_places(goo, radius, keyword):
#     location = f"{goo}"
#     search_query = f"{keyword} near {location}"
    
    
#     location_data = geolocator.geocode(search_query)
    
#     if location_data:
#         return {
#             "name": location_data.address,
#             "latitude": location_data.latitude,
#             "longitude": location_data.longitude
#         }
#     else:
#         return None

@app.route("/login", methods = ["POST","GET"])
def login():
    if request.method == "POST" and 'user' in request.json:
        user = request.json["user"]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f"SELECT * FROM user WHERE id = {user}")
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session["userid"] = account["id"]
            session["username"] = account["username"]
            un = session['username']
            return jsonify({un: 'Login Successfull'})

        else:    
            return jsonify({'message': 'User not found.'}), 404

@app.route("/home")
def home():
    if "loggedin" in session:
        ui = session['userid']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f"Select * from todo where userid = {ui}")
        task = cursor.fetchall()
        return jsonify({"to-do": task})
    else:
        return jsonify({'message': 'User not loggedin.'})

@app.route('/nearby')
def nearby():
        ui = session['userid']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f"Select category from todo where userid =1679720529")
        task = cursor.fetchall()
        placelst=[]
        if task:
            for i in task:
                categories = i['category']
                url = nearby_tasks(categories)
                resp = requests.get(url, headers=headers)
                status_code = resp.status_code
                if status_code == 200:
                    response_json=resp.json()
                    # return jsonify({'msg': response_json})
                    for place in response_json['features']:
                        cursor.execute(f"Select Task from todo where location = '{categories}'")
                        todo = cursor.fetchall() 
                        place_info = [todo] 
                        if 'shop' in place['properties']['datasource']['raw']:
                            shop = place['properties']['datasource']['raw']['shop']
                            place_info.append(shop)
                        add = place['properties']['formatted']
                        dis = place['properties']['distance']
                        place_info.append([ add, dis])
                        
                        placelst.append(place_info)                             
            return jsonify({"nearby": placelst})

        else:
            return jsonify({"msg": 'Not found'})
    
# @app.route('/addtask', methods = ["POST","GET"])
# def addtask():
#     if "loggedin" in session:
#         ui = session['userid']
#         if request.method == "POST" and 'task' in request.json and 'location' in request.json:
#             task = request.json['task']
#             loc = request.json['location']
#             cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#             cursor.execute(f"INSERT INTO todo (Task, location, userid) VALUES {task, loc, ui}")
#             mysql.connection.commit()
#             return jsonify({"msg":"Task added"})
#         else:
#             return jsonify({"message": "Invalid Data"}), 400
#     else:
#         return jsonify({"msg": "User not loggedin"})        

if __name__ == "__main__":
    app.run(debug=True)