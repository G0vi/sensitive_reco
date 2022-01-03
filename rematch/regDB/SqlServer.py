#! /usr/bin/env python3
from sqlalchemy import create_engine, exc, and_
from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import Table, Date, ForeignKey, Column, String, Integer, Float, BIGINT, text
from sqlalchemy.ext.automap import automap_base
from .CreateTable import TextData, RegRules, Users, UserRegs
import traceback
import pymysql
import time

# engine = create_engine("mysql+pymysql://root:@localhost:3306/sql_test")


# 基本数据库的操作
class SqlServer:
    def __init__(self, host='', user='', password='', database='', port=None, db_type='pymysql'):

        url = 'mysql+%s://%s:%s@%s:%s/%s?charset=utf8' % (
                db_type, user, password, host, port, database)

        # print(url, url == "mysql+pymysql://root:@localhost:3306/sql_test")
        engine = create_engine(url, echo=False, encoding='utf8')
        # base = automap_base()
        # base.prepare(engine, reflect=True)
        print('Connection completed!')
        self.url = url
        self.engine = engine
        # self.base = base
        # self.tables = base.classes
        self.__session = sessionmaker(engine)()
        self.session = self.__session

    def remake(self):
        '''self.engine = create_engine(self.url, echo=False, encoding='utf8')
        self.base = automap_base()
        self.tables = self.base.classes'''
        self.__session = sessionmaker(self.engine)()
        self.session = self.__session
        time.sleep(0.01)

    def flush(self):
        self.__session.flush()

    def commit(self):
        try:
            self.__session.commit()
            print('Update success!')
        except:
            self.__session.rollback()

    def close(self):
        self.__session.close()
        print('Your session is closed.')

    def rollback(self):
        self.__session.rollback()
        print('your operation has been rolled back!')

    def query(self, *table_type: object, condition=None) -> list:
        # result = self.session.query(self.tables[table_name])
        flag = 1
        while flag:
            try:
                if condition is not None:
                    result = self.__session.query(*table_type).filter(condition)
                else:
                    result = self.__session.query(*table_type)
                flag = 0
                return result.all()
            except pymysql.err.OperationalError or pymysql.err.InternalError or exc.OperationalError as e:
                print(str(e), 'query')
                print(traceback.format_exc())
                flag = 1
                self.remake()

                print(flag)

            except Exception as e:
                print(str(e))
                flag = 1
                self.__session.rollback()
                self.remake()

    def select(self, *table_type: object, condition=None) -> list:
        result = self.__session.query(*table_type).filter(condition)
        return result.all()

    def insert(self, ob: object):
        try:
            self.__session.merge(ob)
        except pymysql.err.OperationalError or pymysql.err.InternalError or exc.OperationalError as e:
            print(str(e), 'insert')
            self.remake()

        except:
            self.__session.rollback()
            self.remake()
            traceback.print_exc()

        # self.session.add_all(obs)
        # self.session.commit()

    def insert_all(self, obs):
        # for ob in obs:
        #   self.__session.merge(ob)
        try:
            self.__session.add_all(obs)
        except pymysql.err.OperationalError or pymysql.err.InternalError or exc.OperationalError as e:
            print(str(e), 'insert_all')
            self.remake()

        except:
            self.__session.rollback()
            self.remake()

    def delete(self, table_type: object, condition=''):
        try:
            self.__session.query(table_type).filter(condition).delete(synchronize_session='fetch')
            self.__session.commit()
        except pymysql.err.InternalError or pymysql.err.OperationalError or exc.OperationalError as e:
            print(str(e), 'delete')
            self.remake()
        except:
            self.__session.rollback()
            self.remake()
            traceback.print_exc()

    def update_user_regs(self, en, condition=None):
        try:
            to_update = self.__session.query(UserRegs).filter(condition).update({UserRegs.is_enabled: en})
            # self.commit()
            # for eve in waiting_list:
            #   eve.is_enabled = en
            return True
        except pymysql.err.InternalError or pymysql.err.OperationalError or exc.OperationalError as e:
            print(str(e), 'update_user_regs')
            self.rollback()
            self.remake()
            return False
        except Exception as e:
            print(str(e))

            self.rollback()
            print('Update failed!')
            traceback.print_exc()
            # print(traceback.format_exc())
            self.remake()
            return False

    def update_regs(self, exp_no, exp, is_combined_data, is_default, description, modified_time, condition=None):
        try:
            to_update = self.__session.query(RegRules).filter(condition).update({
                RegRules.regexp_no: exp_no,
                RegRules.reg_exp: exp,
                RegRules.is_combined_data: is_combined_data,
                RegRules.is_default: is_default,
                RegRules.description: description,
                RegRules.modified_time: modified_time
            })
            return True
        except pymysql.err.OperationalError or pymysql.err.InternalError or exc.OperationalError as e:
            print(str(e), 'update_regs')
            self.rollback()
            traceback.print_exc()
            self.remake()
            return False
        except Exception as e:
            print(str(e))
            self.rollback()
            traceback.print_exc()
            self.remake()
            return False


# print(test())
'''A = UserRegs(userid=2, regid=23, is_enabled=1)
B = UserRegs(userid=12, regid=42, is_enabled=1)

C = RegRules(regexp_no=107, reg_exp="dafe", description="I love gxy", is_default=0, is_combined_data=0, modified_time=int(time.time()))
sql.insert([C])
sql.commit()'''
# ans = sql.query(RegRules, UserRegs).filter(text("userid=1 and id=regid"))
# ans = sql.query(RegRules, UserRegs, condition='userid=1 and id=regid')
# aa = sql.__session.query(RegRules, UserRegs).filter(text("userid=1 and id=regid"))
# sql.insert([C])

# ans = sql.query(RegRules, condition="is_default=1")
# condition = "userid=" + str(10) + " and regid=id and is_enabled=1"
# ans = sql.query(RegRules, UserRegs, condition=condition + " and is_default=1")
# C = RegRules(regexp_no=128, reg_exp="afefe", description="I love gxy", is_default=0, is_combined_data=0, modified_time=int(time.time()))

# too = sql.session.query(RegRules).filter(text('id=84')).delete(synchronize_session='fetch')
# sql.insert(C)
