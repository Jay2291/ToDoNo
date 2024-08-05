from credentials import bot_token,api_key,user,password
import mysql.connector
import requests
from requests.structures import CaseInsensitiveDict

headers = CaseInsensitiveDict()
headers["Accept"] = "application/json"

conn = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "Jayjagtap@2291",
    database = "todolist"
    )
cursor = conn.cursor()

def add_task(task, cate, prio, ui):
    comm = ['marketplace', 'supermarket', 'shopping_mall', 'department_store', 'elektronics', 'stationery', 'houseware_and_hardware', 'florist', 'pharmacy', 'ice_cream', 'cheese_and_dairy', 'bakery']
    foo = ['ice_cream', 'cheese_and_dairy', 'bakery']
    if cate in comm:
        if cate in foo:
            cate = 'food_and_drink.'+cate
        if cate=='pharmacy':
            cate = 'health_and_beauty.pharmacy'
        categf = f"commercial."+cate
    cat = ['restaurant', 'bar']
    if cate in cat:
        categf = 'catering.'+cate
    if categf:
        query = f"INSERT INTO todo (task, category, userid, priority) VALUES ('{task}', '{categf}', {ui}, {prio})"
        cursor.execute(query)
        conn.commit()
    else:
        print("category not found" )
    return task

def del_task(task):
    query = f"DELETE FROM todo WHERE task = '{task}'"
    cursor.execute(query)
    conn.commit()
    return task

def show_tasks(ui):
    cursor.execute(f"Select task, status from todo where userid = {ui}")
    tasks = cursor.fetchall()
    return tasks

def nearby_tasks(ui, latitude, longitude, rad):
    if rad>0:
        radius = rad
    else:
        radius = 500
    filter_param = f'circle:{longitude},{latitude},{radius}'
    bias_param = f'proximity:{longitude},{latitude}'
    limit= 1
    cursor.execute(f"Select category from todo where userid = {ui} and status=0 ORDER BY priority DESC")
    tasks = cursor.fetchall()
    placelst=[]
    if tasks:
        for task in tasks:
            cat = task[0]
            url = f"https://api.geoapify.com/v2/places?categories={cat}&filter={filter_param}&bias={bias_param}&limit={limit}&apiKey={api_key}"
            resp = requests.get(url, headers=headers)
            status_code = resp.status_code
            if status_code == 200:
                response_json=resp.json()
                for place in response_json['features']:
                    cursor.execute(f"SELECT task FROM todo WHERE category = '{cat}' and status=0 ORDER BY priority DESC")
                    todo = cursor.fetchall()
                    if todo:
                        place_info = [todo]
                        add = place['properties']['formatted']
                        lon = place['properties']['lon']
                        lat = place['properties']['lat']
                        place_info.append(add)
                        place_info.append(lat)
                        place_info.append(lon)
                        placelst.append(place_info)
        return placelst

def done(task):
    query = f"Update todo SET status=1 where task = '{task}'"
    cursor.execute(query)
    conn.commit()
    return True

def on_completion(user_id):
    query = f"SELECT COUNT(*) AS total_tasks, SUM(CASE WHEN status = 1 THEN 1 ELSE 0 END) AS completed_tasks FROM todo WHERE userid = {user_id}"
    cursor.execute(query)
    result = cursor.fetchone()
    total_tasks = result[0]
    completed_tasks = result[1]
    return total_tasks > 0 and total_tasks == completed_tasks

# def myip():
#     url_ip = f"https://api.geoapify.com/v1/ipinfo?&apiKey={api_key}"
#     resp = requests.get(url_ip, headers=headers)
#     response = resp.json()
#     location = response.get('location')
#     latitude = location.get('latitude')
#     longitude = location.get('longitude')
#     return latitude, longitude



