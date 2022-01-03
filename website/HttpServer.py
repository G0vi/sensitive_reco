import sys

sys.path.append('..')
from flask import Flask, render_template, request, redirect, Response, \
    make_response, url_for
from combine.all_condition import ComDetector
from rematch.loadRules.basic_rules import rules
from rematch.regDB.CreateTable import Users, RegRules, UserRegs
from hashlib import sha256, md5
import json
from website.RegToSql import Reg2Sql
from sqlalchemy import and_
import os
import time
import re

prefix = 'aeiou'
app = Flask(__name__, static_url_path='', static_folder='./static')
key = b'0123456789abcdee'
salt = '!fnfaow$2'

PREFIX = '/security/datare'

# app.config.from_object(__name__)
# reg2sql = Reg2Sql('localhost', 'root', '', 'casual', 3306, 'pymysql')
reg2sql = Reg2Sql()
read_sql = reg2sql.read_sql
write_sql = reg2sql.write_sql
choice = 1
default_rules = read_sql.query(RegRules, condition=RegRules.is_default == 1)
flag = 0
rematches = {}
detector = ComDetector(rules)


def process_reg(reg):
    reg = reg.strip()
    start = 0
    end = len(reg)
    if reg[0] == '^':
        start += 1

    if reg[-1] == '$':
        end -= 1
    return '^(' + reg[start: end] + ')$'


def update_key():
    global key
    key = os.urandom(16)


def hmac(userid):
    return sha256(prefix.encode() + userid.encode() + key).hexdigest()


def get_userid(cur_request):
    cookie = cur_request.cookies
    if 'token' not in cookie:
        return None
    token = cookie['token']
    userid = int(token[:32], 16)
    return userid


def get_userid_name(cur_request):
    cookie = cur_request.cookies
    if 'token' not in cookie:
        return None
    token = cookie['token']
    userid = int(token[:32], 16)
    try:
        username = read_sql.query(Users.username, condition=Users.userid == userid)[0][0]
    except:
        username = None
    return userid, username


def check_logged_in(cur_request):
    cookie = cur_request.cookies
    if 'token' not in cookie:
        return False
    token = cookie['token'].strip()
    userid, mac = token[0:32], token[32:]
    if hmac(userid) == mac:
        return True
    return False


@app.route(PREFIX + '/')
def index():
    time.sleep(0.5)
    if check_logged_in(request):
        return redirect("./main")
    return render_template("index.html")


@app.route(PREFIX + '/register', methods=["GET"])
def register():
    return render_template("register.html")


@app.route(PREFIX + '/register', methods=["POST"])
def register_user():
    username = request.form['username']
    pwd = request.form['passwd']
    passwd = sha256((salt + pwd).encode()).hexdigest()
    resp = make_response()
    cur_user = Users(username=username, passwd=passwd)
    userid = read_sql.query(Users.userid, condition=Users.username == username)
    if userid:
        data = {"success": False, "message": "This user has already exists!"}
    else:
        write_sql.insert(cur_user)
        write_sql.commit()
        userid = read_sql.query(Users.userid, condition=Users.username == username)[0][0]
        user_rules = []
        for eve in default_rules:
            regid = eve.id
            is_enabled = 1 if regid not in reg2sql.block_list else 0
            user_rules.append(UserRegs(userid=userid, regid=regid, is_enabled=is_enabled))

        write_sql.insert_all(user_rules)
        write_sql.commit()

        data = {"success": True}
    resp.data = json.dumps(data)
    return resp


@app.route(PREFIX + '/login', methods=["GET"])
def get_login():
    return render_template("index.html")


@app.route(PREFIX + '/login', methods=["POST"])
def post_login():
    username = request.form['username']
    pwd = request.form['passwd']
    passwd = sha256((salt + pwd).encode()).hexdigest()
    write_sql.commit()
    resp = Response()
    data = {'success': False}
    userid = read_sql.query(Users.userid, condition=and_(Users.username == username, Users.passwd == passwd))

    if userid:
        userid = hex(userid[0][0])[2:].rjust(32, '0')
        # resp = Response()
        resp.set_cookie('token', userid + hmac(userid))
        data = {"success": True}
    else:
        data['message'] = '用户不存在'
    resp.data = json.dumps(data)
    return resp


@app.route(PREFIX + '/logout', methods=["GET"])
def logout():
    resp = make_response(redirect('./login'), 302)
    if check_logged_in(request):
        resp.delete_cookie('token')
    return resp


@app.route(PREFIX + '/showAll', methods=['GET'])
def get_all_regs():
    write_sql.commit()
    res = make_response()
    dic = {"success": False, "rules": []}
    global choice
    if check_logged_in(request):
        dic["success"] = True
        userid = get_userid(request)
        choice = int(request.args.get("rulesrc"))
        condition = and_(UserRegs.userid == userid, UserRegs.regid == RegRules.id, UserRegs.is_enabled == 1)
        condition1 = and_(UserRegs.userid == userid, UserRegs.regid == RegRules.id)
        rule_obs = []
        if choice == 1:
            first_query = reg2sql.read_sql.query(UserRegs, RegRules, condition=and_(condition,
                                                                                    RegRules.is_default == 1))

            list_ids = []
            for eve in first_query:
                if eve[1].is_enabled == 1:
                    list_ids.append(eve[1].id)
            for ever in rules:
                cur = ever.copy()
                if cur['id'] in list_ids:
                    cur['is_enabled'] = 1
                else:
                    cur['is_enabled'] = 0
                rule_obs.append(cur)
        elif choice == 2:
            first_query = reg2sql.read_sql.query(UserRegs, RegRules, condition=and_(condition1,
                                                                                    RegRules.is_default == 0))

            for eve in first_query:
                rule_obs.append(eve[1])
        else:
            first_query = reg2sql.read_sql.query(UserRegs, RegRules, condition=condition1)

            for eve in first_query:
                rule_obs.append(eve[1])
        # rule_obs, rematches[userid] = reg2sql.init_rematch(userid, choice)

        '''regs = sql.query(RegRules, UserRegs, condition="")
        li = []
        for eve in regs:
            eve = eve.__dict__
            eve.pop('_sa_instance_state')
            li.append(eve)'''
        dic["rules"] = rule_obs
    res_regs = json.dumps(dic, ensure_ascii=False)
    res.data = res_regs
    return res


@app.route(PREFIX + '/match', methods=["POST"])
def rematch_text():
    text = request.form['text']
    res = make_response()
    try:
        choice = int(request.form['rulesrc'])
    except:
        res.data = json.dumps({'words': text, 'table': []})
        return res
    userid = get_userid(request)
    # if userid not in rematches:
    #    print(userid, rematches)
    query_id = reg2sql.read_sql.query(UserRegs.regid,
                                      condition=and_(UserRegs.userid == userid, UserRegs.is_enabled == 1))
    list_id = []
    for eve in query_id:
        list_id.append(eve[0])
    cur_ans, table = detector.detect_text(text, list_id=list_id)
    data = {'words': cur_ans, 'table': table}

    res.data = json.dumps(data)
    return res


@app.route(PREFIX + '/addrules',
           methods=["POST"])  # 传递json格式：{"exp": str, "description": str, "is_combined_data": int, "is_enabled": int}
def add_user_rules():
    if not check_logged_in(request):
        return redirect(url_for('get_login'))
    new_rules = request.form
    userid = int(request.cookies['token'][:32], 16)
    cur_id = 0
    exp = new_rules['exp']
    ok = True
    try:
        re.compile(exp)
    except:
        ok = False
    if ok:
        description = new_rules['description']
        is_combined_data = new_rules['is_combined_data']
        is_enabled = new_rules["is_enabled"]
        cur_id = new_rules['cur_id']
        flag = 0 if cur_id == 0 or cur_id == '0' else 1
        exp_no = int(md5((str(is_combined_data) + exp + description).encode()).hexdigest()[0:8], 16)
        if flag:
            cur_rule = RegRules(id=cur_id, regexp_no=exp_no, reg_exp=exp, is_combined_data=is_combined_data,
                                is_default=0,
                                description=description, modified_time=int(time.time()),
                                is_enabled=is_enabled, pos_dt_id_list='0', pos_dt_list='自定义')
            real_id = read_sql.query(RegRules, UserRegs, condition=and_(RegRules.id == UserRegs.regid,
                                                                        RegRules.is_default == 0,
                                                                        UserRegs.regid == cur_id))
            if real_id and real_id[0][1].userid == userid:
                ok = write_sql.update_regs(exp_no, exp, is_combined_data, 0, description, int(time.time()),
                                           condition=RegRules.id == cur_id)
            else:
                ok = False
        else:
            cur_rule = RegRules(regexp_no=exp_no, reg_exp=exp, is_combined_data=is_combined_data, is_default=0,
                                description=description, modified_time=int(time.time()),
                                is_enabled=is_enabled, pos_dt_id_list='0', pos_dt_list='自定义')

            write_sql.insert(cur_rule)
            write_sql.commit()
            # if not flag:
            cur_id = read_sql.query(RegRules.id, condition=RegRules.regexp_no == exp_no)[0][0]
            user_rule = UserRegs(userid=userid, regid=cur_id, is_enabled=is_enabled)
            write_sql.insert(user_rule)
            write_sql.commit()
    resp = make_response()
    data = {"success": ok, "id": cur_id}
    resp.data = json.dumps(data)
    return resp


@app.route(PREFIX + '/delrules', methods=["POST"])
def del_user_rules():
    if not check_logged_in(request):
        return redirect(url_for('get_login'))

    ruleid = request.form['cur_id']
    userid = int(request.cookies['token'][:32], 16)
    write_sql.delete(RegRules, condition=RegRules.id == ruleid)
    write_sql.delete(UserRegs, condition=UserRegs.regid == ruleid)
    write_sql.commit()
    # sql.delete(UserRegs, condition="userid=" + str(userid) + ' and regid=' + str(ruleid))
    resp = make_response()
    data = {"success": True}
    resp.data = json.dumps(data)
    return resp


@app.route(PREFIX + '/setenable', methods=["GET"])
def set_enable():
    if not check_logged_in(request):
        return redirect(url_for('get_login'))
    userid = get_userid(request)
    op = request.args.get('op')
    en = 1 if op == '1' else 0
    rule_src = request.args.get('rulesrc')
    if rule_src:
        write_sql.update_user_regs(en, condition=UserRegs.userid == userid)
    else:
        ruleid = request.args.get('id')
        userrule = UserRegs(userid=userid, regid=ruleid, is_enabled=en)
        write_sql.insert(userrule)
    write_sql.commit()
    data = {"success": True}
    resp = make_response()
    resp.data = json.dumps(data)
    global flag
    flag = 0
    return resp


@app.route(PREFIX + '/main', methods=["GET"])
def go2main():
    if not check_logged_in(request):
        return redirect('./login')

    username = get_userid_name(request)[1]
    return render_template('mainfunc.html', xiaoxi='hello {}, welcome to our R3G system'.format(username))


@app.route(PREFIX + '/manage', methods=["GET"])
def get_demo():
    return render_template('demo.html')


@app.route(PREFIX + '/text', methods=["GET"])
def text():
    op = int(request.args.get('op'))
    res = make_response()

    if op == 1:
        res.data = open('../rematch/textfile/text1', 'r').read()
    if op == 2:
        res.data = open('../rematch/textfile/text2', 'r').read()
    return res


# 运行flask
if __name__ == '__main__':
    try:
        app.run(host="0.0.0.0", port=1234, debug=True)

    except KeyboardInterrupt:
        exit(0)
