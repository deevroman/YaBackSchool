import json
from datetime import datetime
from itertools import groupby
from operator import itemgetter

import numpy as np
from flask import Flask
from flask import make_response, jsonify
from flask import request
from flaskext.mysql import MySQL
from jsonschema import validate
from pymysql.cursors import DictCursor
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.config['JSON_AS_ASCII'] = False

mysql = MySQL(cursorclass=DictCursor)
mysql.init_app(app)
conn = mysql.connect()
cursor = conn.cursor()

schemas = {'imports': json.load(open("schemas/imports.json", "r")),
           'update_citizen': json.load(open("schemas/update_citizen.json", "r"))}


@app.route('/imports', methods=['POST'])
def imports():
    data = request.get_json()
    try:
        validate(instance=data, schema=schemas['imports'])
    except:
        return make_response(jsonify("Invalid data"), 400)
    if len({i['citizen_id'] for i in data['citizens']}) != len(data['citizens']):
        return make_response(jsonify("Invalid data. Not unique citizen_id"), 400)

    data = data['citizens']
    graph = {i['citizen_id']: set(i['relatives']) for i in data}
    for i in graph:
        for j in graph[i]:
            if j not in graph or i not in graph[j]:
                return make_response(jsonify("Invalid data. Invalid relatives."), 400)
    today = datetime.today()
    for i in range(len(data)):
        data[i]['relatives'] = json.dumps(sorted(data[i]['relatives']))
        try:
            tmp_date = datetime.strptime(data[i]['birth_date'], "%d.%m.%Y")
            if tmp_date >= today:
                return make_response(jsonify("Invalid data. Invalid field of date. Date more today"), 400)
            data[i]['birth_date'] = datetime.strftime(tmp_date, "%Y-%m-%d")
        except:
            return make_response(jsonify("Invalid data. Invalid field of date."), 400)

    cursor.execute("INSERT INTO `imports` VALUES ()")
    conn.commit()
    cursor.execute("SELECT LAST_INSERT_ID()")
    import_id = cursor.fetchone()["LAST_INSERT_ID()"]
    sql_create_table_import = f"""
            create table imports_{import_id}
            (
            citizen_id int,
            town text null,
            street text null,
            building text null,
            apartment int null,
            name text null,
            birth_date date null,
            gender text null,
            relatives text null,
            constraint imports_{import_id}_pk
            primary key (citizen_id)
            );
    """
    cursor.execute(sql_create_table_import)
    conn.commit()

    sql_add_data_import = f"""
    INSERT INTO 
    `imports_{import_id}`
    (
    `citizen_id`,
    `town`,
    `street`,
    `building`,
    `apartment`,
    `name`, 
    `birth_date`, 
    `gender`, 
    `relatives`) 
    VALUES (
    %(citizen_id)s, %(town)s,
    %(street)s, %(building)s,
    %(apartment)s, %(name)s,
    %(birth_date)s, %(gender)s,
    %(relatives)s);
    """
    cursor.executemany(sql_add_data_import, data)
    conn.commit()
    return make_response(jsonify({'data': {'import_id': import_id}}), 201)


@app.route('/imports/<int:import_id>/citizens/<int:citizen_id>', methods=['PATCH'])
def update_citizen(import_id, citizen_id):
    data = request.get_json()
    try:
        validate(instance=data, schema=schemas['update_citizen'])
    except:
        return make_response(jsonify("Invalid data"), 400)

    sql_cit_info = f"""
        SELECT * from `imports_{import_id}` WHERE citizen_id={citizen_id} LIMIT 1
    """
    try:
        cursor.execute(sql_cit_info)
        if cursor.rowcount == 0:
            return make_response(jsonify("Invalid query. Invalid citizen_id"), 404)
    except:
        return make_response(jsonify("Invalid query. Invalid import_id"), 404)

    user_info = cursor.fetchone()
    user_info['relatives'] = json.loads(user_info['relatives'])
    sql_cit_ids = f"""
        SELECT `citizen_id` FROM `imports_{import_id}`
    """
    cursor.execute(sql_cit_ids)
    cit_ids = [i['citizen_id'] for i in cursor.fetchall()]
    for i in user_info['relatives']:
        if i not in cit_ids:
            return make_response(jsonify("Invalid relative_id"), 400)
    user_info['birth_date'] = user_info['birth_date'].strftime("%Y-%m-%d")
    citizens_for_add = []
    citizens_for_delete = []
    for i in data:
        if i == 'birth_date':
            try:
                tmp_date = datetime.strptime(data[i], "%d.%m.%Y")
                if tmp_date >= datetime.today():
                    return make_response(jsonify("Invalid data. Invalid field of data. Data more today"), 400)
                user_info[i] = datetime.strftime(tmp_date, "%Y-%m-%d")
            except:
                return make_response(jsonify("Invalid data. Invalid field of data"), 400)
        elif i == 'relatives':
            before = set(user_info['relatives'])
            after = set(data['relatives'])
            for j in before:
                if j not in after:
                    citizens_for_delete.append(tuple(str(j)))
            for j in after:
                if j not in before:
                    citizens_for_add.append(tuple(str(j)))
            user_info['relatives'] = data['relatives']
        else:
            user_info[i] = data[i]
    user_info['relatives'] = json.dumps(sorted(user_info['relatives']))
    sql_update_citizen = f"""
        UPDATE `imports_{import_id}`
    SET
    `town` = %(town)s,
    `street` = %(street)s,
    `building` = %(building)s,
    `apartment` = %(apartment)s,
    `name` = %(name)s, 
    `birth_date` = %(birth_date)s, 
    `gender` = %(gender)s, 
    `relatives` = %(relatives)s
    WHERE 
    `citizen_id` = {citizen_id}
    """
    cursor.execute(sql_update_citizen, user_info)

    sql_get_citizens = f"""
        SELECT `citizen_id`, `relatives` FROM `imports_{import_id}` WHERE citizen_id=%s
    """
    citizens_for_update = []
    # delete
    cursor.executemany(sql_get_citizens, citizens_for_delete)
    rows = cursor.fetchall()
    for i in rows:
        rels = json.loads(i['relatives'])
        rels.remove(citizen_id)
        citizens_for_update.append({'citizen_id': i['citizen_id'], 'relatives': json.dumps(rels)})
    # add
    cursor.executemany(sql_get_citizens, citizens_for_add)
    rows = cursor.fetchall()
    for i in rows:
        rels = json.loads(i['relatives'])
        rels.append(citizen_id)
        citizens_for_update.append({'citizen_id': i['citizen_id'], 'relatives': json.dumps(rels)})
    sql_update_relatives = f"""
        UPDATE `imports_{import_id}`
    SET
    `relatives` = %(relatives)s
    WHERE 
    citizen_id=%(citizen_id)s
    """
    cursor.executemany(sql_update_relatives, citizens_for_update)
    conn.commit()
    user_info['relatives'] = json.loads(user_info['relatives'])
    user_info['birth_date'] = datetime.strftime(datetime.strptime(user_info['birth_date'], "%Y-%m-%d"), "%d.%m.%Y")
    return make_response(jsonify({'data': user_info}), 200)


@app.route('/imports/<int:import_id>/citizens', methods=['GET'])
def get_imports(import_id):
    sql_get_import = f"""
        SELECT * from `imports_{import_id}`
    """
    try:
        cursor.execute(sql_get_import)
    except:
        return make_response(jsonify("Invalid import_id"), 404)
    rows = cursor.fetchall()
    for i in range(len(rows)):
        rows[i]['relatives'] = json.loads(rows[i]['relatives'])
        rows[i]['birth_date'] = datetime.strftime(rows[i]['birth_date'], "%d.%m.%Y")
    return make_response(jsonify({'data': rows}), 200)


@app.route('/imports/<int:import_id>/citizens/birthdays', methods=['GET'])
def get_birthdays(import_id):
    sql_get_birthdays = f"""
        SELECT `citizen_id`, MONTH(birth_date) as month, `relatives` from `imports_{import_id}`
    """
    try:
        cursor.execute(sql_get_birthdays)
    except:
        return make_response(jsonify("Invalid import_id"), 404)
    rows = cursor.fetchall()
    presents = {str(i): {} for i in range(1, 12 + 1)}
    for i in rows:
        rels = json.loads(i['relatives'])
        for j in rels:
            if str(j) in presents[str(i['month'])]:
                presents[str(i['month'])][str(j)] += 1
            else:
                presents[str(i['month'])][str(j)] = 1
    result = {str(i): [] for i in range(1, 12 + 1)}
    for i in presents:
        for j in presents[i]:
            result[i].append({'citizen_id': int(j), 'presents': presents[i][j]})
    return make_response(jsonify({"data": result}), 200)


@app.route('/imports/<int:import_id>/towns/stat/percentile/age', methods=['GET'])
def get_percentile_age(import_id):
    sql_get_import = f"""
        SELECT 
        `town`,
        (TIMESTAMPDIFF(YEAR, birth_date, UTC_TIMESTAMP())) as age 
        FROM `imports_{import_id}`
    """
    try:
        cursor.execute(sql_get_import)
    except:
        return make_response(jsonify("Invalid import_id"), 404)
    rows = [[i[j] for j in i] for i in cursor.fetchall()]
    rows.sort(key=itemgetter(0))
    result = []
    for elt, items in groupby(rows, itemgetter(0)):
        p50, p75, p99 = np.percentile(np.array([i[1] for i in items]), q=[50, 75, 99]).round(2).tolist()
        result.append({'town': elt, 'p50': p50, 'p75': p75, 'p99': p99})
    return make_response(jsonify({'data': result}), 200)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
