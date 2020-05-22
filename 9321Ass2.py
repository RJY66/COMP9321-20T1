# Python version 3.7.2
# flask version 1.1.1
# flask-restplus version 0.13.0

import re as r
from flask_restplus import Resource
import os as o
from flask import Flask
import sqlite3
import urllib.request as ur
import json as j
from flask_restplus import Api
import time as t


def cmd_execute(database, cmd):
    conn = sqlite3.connect(database)
    cr = conn.cursor()
    length = len(r.findall(";", cmd))
    if length <= 1:
        cr.execute(cmd)
    else:
        cr.executescript(cmd)
    result = cr.fetchall()
    cr.close()
    conn.commit()
    conn.close()
    return result


def database_creation(db_name):
    if not o.path.exists(db_name):
        create_cmd1 = f'create table Collection(' \
            f'collection_id integer unique not null,' \
            f'collection_name varchar(200),' \
            f'indicator varchar(200),' \
            f'indicator_value varchar(200),' \
            f'creation_time date,' \
            f'constraint collection_pkey primary key (collection_id));'
        create_cmd2 = f'create table Entries(' \
            f'id integer not null,' \
            f'country varchar(200),' \
            f'date varchar(20),' \
            f'value varchar(200) not null,' \
            f'constraint entry_fkey foreign key (id) references Collection(collection_id));'
        full_create_cmd = create_cmd1 + create_cmd2
        cmd_execute(db_name, full_create_cmd)
        print("created db "+str(db_name)+" successfully")
        return True
    else:
        print("Db "+str(db_name)+" has been created before")
        return False


def get_raw_data(indicator):
    # only focus on first page 1000 records
    url = f'http://api.worldbank.org/v2/countries/all/indicators/' + \
          f'{indicator}?date=2012:2017&format=json&per_page=1000'
    # add a browser-like header
    # pretend to be browser visit instead of programming visit
    # in case of ip be banned by the website
    hd = dict()
    hd['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) ' \
                       'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                       'Chrome/58.0.3029.96 Safari/537.36'
    resource = ur.Request(url, headers=hd)
    data = ur.urlopen(resource).read()
    if r.findall(r'Invalid value', str(data), flags=r.I):
        return False
    raw_data = j.loads(data)[1]
    return raw_data


# filter 'None' value of entries
def isfloat(n):
    is_number = True
    try:
        num = float(n)
        is_number = (num == num)
    except ValueError:
        is_number = False
    return is_number


def get_single_json_show(collection_query, entries_query):
    result = dict()
    result["id"] = collection_query[0]
    result["indicator"] = f"{collection_query[2]}"
    result["indicator_value"] = f"{collection_query[3]}"
    result["creation_time"] = f"{collection_query[4]}"
    result["entries"] = []
    for i in range(len(entries_query)):
        entries_t = dict()
        entries_t["country"] = f"{entries_query[i][0]}"
        entries_t["date"] = int(entries_query[i][1])
        if isfloat(entries_query[i][2]):
            entries_t["value"] = float(entries_query[i][2])
            result["entries"].append(entries_t)
    return result


def Q6_show(collection_query, entries_query):
    result = dict()
    result["indicator"] = f"{collection_query[2]}"
    result["indicator_value"] = f"{collection_query[3]}"
    result["entries"] = []
    for i in range(len(entries_query)):
        entries_t = dict()
        entries_t["country"] = f"{entries_query[i][0]}"
        entries_t["date"] = int(entries_query[i][1])
        if isfloat(entries_query[i][2]):
            entries_t["value"] = float(entries_query[i][2])
            result["entries"].append(entries_t)
    return result


def collection_json_show(result):
    format_dict = dict()
    format_dict["uri"] = f"/{result[1]}/{result[0]}"
    format_dict["id"] = result[0]
    format_dict["creation_time"] = f"{result[4]}"
    format_dict["indicator_id"] = f"{result[2]}"
    return format_dict


def action_dispatching(database, collection, action, **kwargs):
    if action == 'get_all':
        return process_getreq(database, collection, 'get_all')
    elif action == 'get_one':
        return process_getreq(database, collection, 'get_one', collection_id=kwargs['collection_id'])
    elif action == 'get_one_by_year_country':
        return process_getreq(database, collection, 'get_one_by_year_country', collection_id=kwargs['collection_id'], year=kwargs['year'], country=kwargs['country'])
    elif action == 'get_t_b':
        top_t_plus = r.search(r"^(\+)(\d+)$", kwargs['query'])   # find +N
        top_t = r.search(r"^(\d+)$", kwargs['query'])            # find N
        bottom_t = r.search(r"^(-)(\d+)$", kwargs['query'])      # find -N
        if bottom_t and 1 <= int(bottom_t.group(2)) and int(bottom_t.group(2)) <= 100:
            return process_getreq(database, collection, 'get_t_b', collection_id=kwargs['collection_id'], year=kwargs['year'], flag='get_bottom', value=bottom_t.group(2))
        elif top_t_plus and 1 <= int(top_t_plus.group(2)) and int(top_t_plus.group(2)) <= 100:
            return process_getreq(database, collection, 'get_t_b', collection_id=kwargs['collection_id'], year=kwargs['year'], flag='get_top', value=top_t_plus.group(2))
        elif top_t and 1 <= int(top_t.group(1)) and int(top_t.group(1)) <= 100:
            return process_getreq(database, collection, 'get_t_b', collection_id=kwargs['collection_id'], year=kwargs['year'], flag='get_top', value=top_t.group(1))
        else:
            return {"message": "Your input arguments are invalid."}, 400
    elif action == 'post':
        return process_postreq(database, collection, kwargs['indicator'])
    elif action == 'delete':
        return process_deletereq(database, collection, kwargs['collection_id'])
    else:
        return {'message': f"Unknown action"}, 400


def Q3_show(result):
    format_dict = dict()
    format_dict["uri"] = f"/{result[1]}/{result[0]}"
    format_dict["id"] = result[0]
    format_dict["creation_time"] = f"{result[4]}"
    format_dict["indicator"] = f"{result[2]}"
    return format_dict


def process_getreq(database, collection, action, **kwargs):
    # Q4
    if action == 'get_one':
        collection_query = cmd_execute(database,
                                       f"select * from Collection where collection_name = '{collection}' AND collection_id = {kwargs['collection_id']};")
        entries_query = cmd_execute(database,
                                    f"select country, date, value from Entries where id = {kwargs['collection_id']};")
        if entries_query and collection_query:
            return get_single_json_show(collection_query[0], entries_query), 200
        else:
            return {"message": f"The collection '{collection}' with id {kwargs['collection_id']} not found"}, 404
    # Q3
    elif action == 'get_all':
        query = cmd_execute(database, f"select * from Collection where collection_name ='{collection}';")
        if query:
            result_list = []
            for i in range(len(query)):
                result_list.append(Q3_show(query[i]))
            return result_list, 200
        else:
            return {"message": f"The collection '{collection}' not found in data source!"}, 404

    # Q5
    elif action == 'get_one_by_year_country':
        j_query = cmd_execute(database, f"select collection_id, indicator, country, date, value from Collection "
                                        f"join Entries on (Collection.collection_id = Entries.id) "
                                        f"where collection_id = {kwargs['collection_id']} "
                                        f"and country = '{kwargs['country']}' and date = '{kwargs['year']}';")
        if j_query:
            result_dict = dict()
            result_dict["collection_id"] = j_query[0][0]
            result_dict["indicator"] = f"{j_query[0][1]}"
            result_dict["country"] = f"{j_query[0][2]}"
            result_dict["year"] = int(j_query[0][3])
            if isfloat(j_query[0][4]):
                result_dict["value"] = float(j_query[0][4])
            else:
                result_dict["value"] = "None"
            return result_dict, 200
        else:
            return {"message": f"The given arguments collections = '{collection}', {kwargs} not found in data source!"}, 404

    # Q6
    elif action == 'get_t_b':
        how_to_sort = 'COMP9321_a_good_course'
        if 'get_top' == kwargs['flag']:     # plus for descending sort
            how_to_sort = 'desc'
        if 'get_bottom' == kwargs['flag']:  # minus for ascending sort
            how_to_sort = 'asc'               # always get top N values
        collection_query = cmd_execute(database, f"select * from Collection where collection_id = {kwargs['collection_id']} "
                                                 f"and collection_name = '{collection}';")
        entries_query = cmd_execute(database, f"select country, date, value from Entries "
                                              f"where id = {kwargs['collection_id']} "
                                              f"and date = '{kwargs['year']}' and value != 'None' "
                                              f"group by country, date, value "
                                              f"order by cast(value as real) {how_to_sort} limit {kwargs['value']};")

        if collection_query:
            result_dict = Q6_show(collection_query[0], entries_query)
            return result_dict, 200
        else:
            return {"message": "No data under given parameters"}, 404
    else:
        return {'message': f"Unknown action"}, 400


# Q1
def process_postreq(database, collection, indicator):
    query = cmd_execute(database, f"select * from Collection where indicator = '{indicator}';")
    if query:
        return collection_json_show(query[0]), 200
    if not query:
        data = get_raw_data(indicator)
        if data == False:
            return {"message": "The indicator '{}' not found".format(indicator)}, 404
        new_id = r.findall(r'\d+', str(cmd_execute(database, 'select max(collection_id) from Collection;')))
        if new_id:
            new_id = 1 + int(new_id[0])
        else:
            new_id = 1
        process_insertreq(database, new_id, collection, data)
        new_query = cmd_execute(database, f"select * from Collection where indicator = '{indicator}';")
        return collection_json_show(new_query[0]), 201


def process_insertreq(database, given_id, given_collection_name, data):
    # insert collection table
    time_nw = t.strftime("%Y-%m-%d %H:%M:%S", t.localtime())
    collection = f"insert into Collection values ({given_id}, '{given_collection_name}', '{data[0]['indicator']['id']}', '{data[0]['indicator']['value']}', '{time_nw}');"
    cmd_execute(database, collection)
    # insert entries table
    entry_cmd = f"insert into Entries values"
    for d in data:
        temp = d['country']['value'].replace("'", " ")
        entry_cmd += f" ({given_id}, '{temp}', '{d['date']}', '{d['value']}'),"
    entry_cmd_prime = entry_cmd[0:-1]
    entry_cmd_prime = entry_cmd_prime + ";"
    cmd_execute(database, entry_cmd_prime)


# Q2
def process_deletereq(database, collection, collection_id):
    query = cmd_execute(database, f"select * from Collection Where collection_name = '{collection}' "
                                  f"and collection_id = {collection_id};")
    if query:
        cmd_execute(database, f"delete from Collection where collection_id = '{collection_id}';")
        cmd_execute(database, f"delete From Entries where id = {collection_id};")
        return {"message": f"Collection {collection_id} is removed from the database.", "id": collection_id}, 200
    else:
        return {"message": f"Collection {collection_id} not found in the database."}, 404


app = Flask(__name__)
api = Api(app, title="z5195715's API", description="API for COMP9321 Assignment 2")
parser = api.parser()
parser.add_argument('q', type=str, help='Q6 input a number N (1<=N<=100) using format: +N/N or -N', location='args')
parser.add_argument('order_by', type=str, help='Q3 input a sorting criteria', location='args')
parser.add_argument('indicator_id', type=str, help='Q1 input indicator_id', location='args')


http_code_content_map = dict()
http_code_content_map['200'] = "OK"
http_code_content_map['201'] = "Created"
http_code_content_map['400'] = "Bad Request"
http_code_content_map['404'] = "Not Found"
http_code_content_map['500'] = "Server internal error"


@api.route("/collections")
@api.response(200, http_code_content_map['200'])
@api.response(201, http_code_content_map['201'])
@api.response(400, http_code_content_map['400'])
@api.response(404, http_code_content_map['404'])
class Q1_Q3(Resource):
    para_dict1 = dict()
    para_dict1['indicator_id'] = 'indicator_id'
    para_dict3 = dict()
    para_dict3['order_by'] = 'one or more sorting criteria(comma separated)'

    @api.doc(params=para_dict1)
    def post(self):
        query = parser.parse_args()['indicator_id']
        if query:
            return action_dispatching(database='z5195715.db', collection='collections', action='post', indicator=query)
        else:
            return {"message": "Indicator id cannot be null"}, 400

    @api.doc(params=para_dict3)
    def get(self):
        query = parser.parse_args()['order_by']
        raw_json_collection = action_dispatching(database='z5195715.db', collection='collections', action='get_all')
        json_collection = raw_json_collection[0]
        cmd_list = query.replace("+", "s").replace("-", "j").split(",")
        for c in cmd_list:
            if c.startswith('j'):
                return sorted(json_collection, reverse=True, key=lambda j: j[c[1:]]), 200
            elif c.startswith('s'):
                return sorted(json_collection, key=lambda j: j[c[1:]]), 200
            else:
                return {'message': f"Given sorting criteria is invalid!"}, 400


@api.route("/collections/<int:collection_id>")
@api.response(200, http_code_content_map['200'])
@api.response(201, http_code_content_map['201'])
@api.response(400, http_code_content_map['400'])
@api.response(404, http_code_content_map['404'])
class Q2_Q4(Resource):
    def get(self, collection_id):
        return action_dispatching(database='z5195715.db', collection='collections', action='get_one', collection_id=collection_id)

    def delete(self, collection_id):
        if collection_id < 0:
            return {"message": f'Collection id cannot be a negative number.'}, 400
        else:
            return action_dispatching(database='z5195715.db', collection='collections', action='delete', collection_id=collection_id)


@api.route("/collections/<int:collection_id>/<int:year>/<string:country>")
@api.response(200, http_code_content_map['200'])
@api.response(201, http_code_content_map['201'])
@api.response(400, http_code_content_map['400'])
@api.response(404, http_code_content_map['404'])
class Q5(Resource):
    def get(self, collection_id, year, country):
        return action_dispatching(database='z5195715.db', collection='collections', action='get_one_by_year_country', collection_id=collection_id, year=year, country=country)


@api.route("/collections/<int:collection_id>/<int:year>")
@api.response(200, http_code_content_map['200'])
@api.response(201, http_code_content_map['201'])
@api.response(400, http_code_content_map['400'])
@api.response(404, http_code_content_map['404'])
class Q6(Resource):
    para_dict6 = dict()
    para_dict6['q'] = 'query'

    @api.doc(params=para_dict6)
    def get(self, collection_id, year):
        query = parser.parse_args()['q']
        return action_dispatching(database='z5195715.db', collection='collections', action='get_t_b', collection_id=collection_id, year=year, query=query)


if __name__ == "__main__":
    database_creation(db_name='z5195715.db')
    app.run(debug=True, port=6666, host='127.0.0.1')
