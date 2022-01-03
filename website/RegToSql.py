from rematch.regDB.SqlServer import SqlServer
from rematch.regDB.CreateTable import RegRules, TextData, UserRegs, DataTypeByte
from rematch.reMatch.ReMatch import ReMatch
import time
from sqlalchemy import and_
from config import config
import json


def split_id(string: str):
    return json.loads('[' + string.strip() + ']')


def split_dt(string: str):
    return string.strip().split(', ')


# 关联数据库
class Reg2Sql:
    def __init__(self):
        mysqldb_conn = config.get_mysqldb_conn("read")
        self.read_sql = SqlServer(host=mysqldb_conn.get('host'),
                                  user=mysqldb_conn.get('user'),
                                  password=mysqldb_conn.get('password'),
                                  database=mysqldb_conn.get('db'),
                                  port=mysqldb_conn.get('port'))
        mysqldb_conn = config.get_mysqldb_conn("write")
        self.write_sql = SqlServer(host=mysqldb_conn.get('host'),
                                   user=mysqldb_conn.get('user'),
                                   password=mysqldb_conn.get('password'),
                                   database=mysqldb_conn.get('db'),
                                   port=mysqldb_conn.get('port'))
        self.rematch = None
        self.block_list = [42, 53, 54]
        self.type2level = {}
        self.sys_rematch()

    def init_rematch(self, userid: int, choice=1):
        rule_obs = []
        # condition = "userid=" + str(userid) + " and regid=id and is_enabled=1"
        condition = and_(UserRegs.userid == userid, UserRegs.regid == RegRules.id, UserRegs.is_enabled == 1)
        condition1 = and_(UserRegs.userid == userid, UserRegs.regid == RegRules.id)
        ans = []
        rule_obs1 = []
        ans1 = []
        if choice == 3:
            ans = self.read_sql.query(RegRules, UserRegs, condition=condition)
            ans1 = self.read_sql.query(RegRules, UserRegs, condition=condition1)
            if not ans:
                print(ans, 1)
        elif choice == 2:
            ans = self.read_sql.query(RegRules, UserRegs, condition=and_(condition, RegRules.is_default == 0))
            ans1 = self.read_sql.query(RegRules, UserRegs, condition=and_(condition1, RegRules.is_default == 0))
            if not ans:
                print(ans, 2)
        elif choice == 1:
            ans = self.read_sql.query(RegRules, UserRegs, condition=and_(condition, RegRules.is_default == 1))
            ans1 = self.read_sql.query(RegRules, UserRegs, condition=and_(condition1, RegRules.is_default == 1))
            if not ans:
                print(ans, 3)
        for eve in ans:
            cur = {'id': eve[0].id, 'regexp_no': eve[0].regexp_no, 'regexp': eve[0].reg_exp,
                   'is_enabled': eve[1].is_enabled & eve[0].is_enabled,
                   'is_combined_data': eve[0].is_combined_data, 'description': eve[0].description,
                   'id_list': split_id(eve[0].pos_dt_id_list), 'dt_list': split_dt(eve[0].pos_dt_list)}
            rule_obs.append(cur)
        for eve in ans1:
            cur = {'id': eve[0].id, 'regexp_no': eve[0].regexp_no, 'regexp': eve[0].reg_exp,
                   'is_enabled': eve[1].is_enabled & eve[0].is_enabled,
                   'is_combined_data': eve[0].is_combined_data, 'description': eve[0].description,
                   'id_list': split_id(eve[0].pos_dt_id_list), 'dt_list': split_dt(eve[0].pos_dt_list)}
            rule_obs1.append(cur)
        cur_rematch = ReMatch(rule_obs)
        return rule_obs1, cur_rematch

    def sys_rematch(self):
        rule_obs = []
        ans = self.read_sql.query(RegRules, condition=and_(RegRules.is_default == 1, ~RegRules.id.in_(self.block_list)))
        for eve in ans:
            cur = {'id': eve.id, 'regexp_no': eve.regexp_no, 'regexp': eve.reg_exp, 'is_enabled': eve.is_enabled,
                   'is_combined_data': eve.is_combined_data, 'description': eve.description,
                   'id_list': split_id(eve.pos_dt_id_list), 'dt_list': split_dt(eve.pos_dt_list)}
            rule_obs.append(cur)
        self.rematch = ReMatch(rule_obs)
        cur_ans = self.read_sql.query(DataTypeByte.secret_level, DataTypeByte.data_type_id)
        for eve in cur_ans:
            if eve[0].isdigit():
                self.type2level[eve[1]] = int(eve[0])
            else:
                self.type2level[eve[1]] = -1
        return rule_obs

    # 插入单条数据到reg_rules表中
    def import_reg(self, reg_id: int, regexp_no: int, reg_exp: str, description: str, is_default=0, is_combined_data=0,
                   modified_time=int(time.time())) -> RegRules:
        to_add = RegRules(id=reg_id, regexp_no=regexp_no, reg_exp=reg_exp, description=description,
                          is_default=is_default, is_combined_data=is_combined_data, modified_time=modified_time)
        self.write_sql.insert([to_add])
        self.write_sql.commit()
        print('Ok!')
        return to_add

    # 插入多条数据到reg_rules表中
    def import_reg_list(self, list_2fold) -> list:  # 每个元素都不许为None，且按照固定顺序传参
        to_add = []
        for eve in list_2fold:
            cur = RegRules(id=eve[0], regexp_no=eve[1], reg_exp=eve[2], description=eve[3],
                           is_combined_data=eve[5], modified_time=int(time.time()))
            to_add.append(cur)
        self.write_sql.insert(to_add)
        self.write_sql.commit()
        return to_add

    # 插入文本到text_data表中，传参内容为字符串
    def import_text(self, text: str, text_id=None):

        if text_id is None:
            ids = self.read_sql.query(TextData.id)
            max_id = max(ids)[0]
            text_id = max_id + 1
        waiting_list = []
        cur_result = self.rematch.match_text(text)
        new_format_result = []
        for k in cur_result:
            cur_value = cur_result[k]
            for j in cur_value:
                new_format_result.append([k, j[1], j[2]])
        cur_ob = TextData(id=text_id, content=text, regs=str(new_format_result), fuzzy_match_allowed=1)
        waiting_list.append(cur_ob)
        try:
            self.write_sql.insert(waiting_list)
            self.write_sql.commit()
        except:
            self.write_sql.rollback()
            raise
        print('Insert success!')
        return waiting_list

    # 插入文本到text_data中，传参内容为文件名
    def import_text_file(self, filename: str, text_id=None):
        text = open(filename, 'r').read()
        return self.import_text(text, text_id)


'''database = 'reapp'
# wa = import_data('./data2.txt', 'localhost', 'root', '', database, 3306, 'pymysql')
ans = import_text('./standard_text.txt', 'localhost', 'root', '', database, 3306)
rematch, waiting_list = ans'''
'''engine = create_engine("mysql+pymysql://root:@localhost:3306/sql_test")
Base = automap_base()
conn = engine.connect()
Base.prepare(engine, reflect=True)
tables = Base.classes
print(tables)
event = tables.sec_dbmap_auto_event
session = sessionmaker(engine)()


metadata = MetaData(engine)
user_table = Table('sec_dbmap_auto_event', metadata, autoload=True)

sel = user_table.select()

result = conn.execute(sel, id==1234)
ins = user_table.insert()

#result = conn.execute(ins, id=1334214, front_event_content='abcdg', attrtype_id=2113424125)
#print(result)
result = session.query(event).filter(event.id > 0)
ans = result.all()
for eve in ans:
    print(eve.__dict__)'''

'''def standardize(words, result):
    ans = []
    for i in result:
        cur = result[i]
        for eve in cur:
            ans.append(eve[1:])
    ans.sort()
    length = len(ans)
    use = [list(ans[0])]
    i = 1
    last = ans[0][0:2]
    while i < length:
        if ans[i][0] == last[0]:
            if ans[i][1] == last[1]:
                use[-1][2] += '/' + ans[i][2]
        else:
            if ans[i][0] >= last[1]:
                use.append(list(ans[i]))
                last = ans[i][0: 2]

            else:
                if ans[i][1] <= last[1]:
                    use.pop()
                    last = use[-1][0:2]
                    continue
                else:
                    use.append([last[1], ans[i][1], ans[i][2]])
                last = ans[i][0: 2]

        i += 1
    return use

reg2sql = Reg2Sql('localhost', 'root', '', 'casual', 3306, 'pymysql')
sql = reg2sql.sql
text = open('../rematch/textfile/text2', 'r').read()
result = reg2sql.rematch.match_text(text)
print(result)
ans = []
for i in result:
    cur = result[i]
    for eve in cur:
        ans.append(eve[1:])
ans.sort()
print(ans)
aa = standardize(text, result)
print(aa)'''
