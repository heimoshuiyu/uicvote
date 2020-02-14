from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
import random


ADDRESS = ('0.0.0.0', 8080)
DONAME = 'example.com'
APP_SECRET_KEY = 'woshimima_blablablablabla_NicoNicoNI~~~~~'


app = Flask(__name__, static_url_path='')
app.debug = False


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/lookup')
def lookip():
    return render_template('lookup.html')


@app.route('/page/<id>')
def page(id):
    # 从数据库获取原始数据
    conn = sqlite3.connect('main.db')
    c = conn.cursor()

    # 获取描述
    c.execute('SELECT describe FROM main WHERE id="%s"' % id)
    describe = c.fetchall()[0][0]

    # 获取是否需要信息
    c.execute('SELECT needinfo FROM main WHERE id="%s"' % id)
    needinfo = c.fetchall()[0][0]

    # 列表循环方法
    result = [row for row in c.execute('SELECT * FROM t%s' % id)]
    conn.close()
    data = []
    for x in range(14):
        data.append([])
        for y in range(7):
            tmp = 0
            for row in result:
                if row[2] == x and row[3] == y:
                    tmp += 1
            data[x].append(tmp)

    # 处理上下文
    message = session.get('message')
    session['message'] = ''
    return render_template('page.html', id=id, data=data, message=message, describe=describe,
    needinfo=needinfo, doname=DONAME, port=ADDRESS[1])


@app.route('/record/<id>', methods=['GET'])
def get_record_redirect(id):
    return redirect('/page/' + id)


@app.route('/record/<id>', methods=['POST'])
def record(id):
    # 检查记录是否合法
    conn = sqlite3.connect('main.db')
    c = conn.cursor()
    c.execute('SELECT needinfo FROM main WHERE id="%s"' % id)
    needinfo = c.fetchall()[0][0]
    if needinfo:
        if not request.form.get('userid') or not request.form.get('username'):
            session['message'] = 'Please input the user name and user ID 请输入姓名和学号'
            return redirect('/page/' + id)

    selected_list = [] # 解析出选中项目(x, y)(竖, 横)
    for item in request.form:
        if request.form[item] == 'on':
            x, y = item.split('-')
            x = int(x)
            y = int(y)
            selected_list.append((x, y))
    username = request.form['username']
    userid = request.form['userid']
    
    data_list = [[userid, username, x, y] for x, y in selected_list]
    c.executemany('INSERT INTO t%s VALUES (?, ?, ?, ?)' % id, data_list)
    conn.commit()
    conn.close()

    return redirect('/page/' + str(id))


@app.route('/create', methods=['GET'])
def create_index():
    return render_template('create.html')


@app.route('/create', methods=['POST'])
def create_table():
    conn = sqlite3.connect('main.db')
    c = conn.cursor()
    
    table_list = [row[0] for row in c.execute('SELECT tbl_name FROM sqlite_master')]
    id = get_random_id(table_list)

    if request.form.get('needinfo') == 'on':
        needinfo = True
    else:
        needinfo = False

    c.execute('CREATE TABLE t%s (userid text, username text, x integer, y integer)' % id)
    c.execute('INSERT INTO main VALUES (?, ?, ?)', (id, request.form.get('describe'), needinfo))
    conn.commit()

    return redirect('/page/' + id)


@app.route('/result/<id>', methods=['POST', 'GET'])
def show_result(id):
    y_list = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

    selected_list = [] # 解析出选中项目(x, y)(竖, 横)
    for item in request.form:
        if request.form[item] == 'on':
            x, y = item.split('-')
            x = int(x)
            y = int(y)
            selected_list.append((x, y))

    conn = sqlite3.connect('main.db')
    c = conn.cursor()
    data = [row for row in c.execute('SELECT * FROM t%s' % id)]
    conn.close()

    result = []
    for x, y in selected_list:
        time_range = '%s %s-%s' % (y_list[y], x+8, x+9)
        for row in data:
            if row[2] == x and row[3] == y:
                userid = row[0]
                username = row[1]
                result.append((time_range, username, userid))
    
    return render_template('result.html', result=result, id=id)


def get_random_id(table_list):
    id = _get_random_id()
    while 't'+id in table_list:  # 检查是否存在重复id
        id = _get_random_id()
    return id

def _get_random_id():
    id = str(random.randint(0, 9999))
    while len(id) < 4:  # 补全字符串
        id = '0' + id
    return id


def init_db():
    if os.path.exists('main.db'):
        return
    conn = sqlite3.connect('main.db')
    c = conn.cursor()
    c.execute('CREATE TABLE main (id text, describe memo, needinfo bool)')
    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
    app.secret_key = APP_SECRET_KEY
    app.run(host=ADDRESS[0], port=ADDRESS[1])