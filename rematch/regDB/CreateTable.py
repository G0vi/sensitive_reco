from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, query
from sqlalchemy import Table, Date, ForeignKey, Column, String, Integer, Float, BIGINT, SMALLINT, UniqueConstraint
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
import time

Base = declarative_base()


# text_data表
class TextData(Base):
    __tablename__ = 'text_data'
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    content = Column(String(500), index=True, default='')
    regs = Column(String(256), nullable=False)
    fuzzy_match_allowed = Column(SMALLINT, nullable=False, default=1)
    UniqueConstraint(content, regs)

    def __repr__(self):
        return "<id: {}, regs: '{}', content: '{}', fuzzy_match_allowed: {}>".format(self.id, self.regs,
                                                                                     self.content,
                                                                                     self.fuzzy_match_allowed)


# reg_rules表
class RegRules(Base):
    __tablename__ = 'reg_rules'
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    regexp_no = Column(BIGINT, unique=True)
    reg_exp = Column(String(300), nullable=False)
    description = Column(String(56), nullable=False)
    is_default = Column(SMALLINT, default=0)
    is_combined_data = Column(SMALLINT, default=0)
    modified_time = Column(BIGINT, default=int(time.time()))
    is_enabled = Column(SMALLINT, default=1)
    pos_dt_id_list = Column(String(255), default='')
    pos_dt_list = Column(String(255), default='')

    def __repr__(self):
        return "<id: {}, regexp_no: {}, reg_exp: '{}', description: '{}', is_enabled: {}, is_combined_data: {}, " \
               "is_modified: {}, is_enabled: {}, pos_dt_id_list: {}, pos_dt_list: {}>".format(self.id, self.regexp_no,
                                                                                              self.reg_exp,
                                                                                              self.description,
                                                                                              self.is_default,
                                                                                              self.is_combined_data,
                                                                                              self.modified_time,
                                                                                              self.is_enabled,
                                                                                              self.pos_dt_id_list,
                                                                                              self.pos_dt_list)


class Users(Base):
    __tablename__ = 'users'
    userid = Column(BIGINT, primary_key=True, nullable=False, autoincrement=True)
    username = Column(String(256), unique=True, nullable=False)
    passwd = Column(String(256), nullable=False)

    def __repr__(self):
        return "<userid: {}, username: {}>".format(self.userid, self.username)


class UserRegs(Base):
    __tablename__ = 'user_rules'
    userid = Column(BIGINT, primary_key=True, nullable=False)
    regid = Column(BIGINT, primary_key=True)
    is_enabled = Column(SMALLINT, default=1)

    def __repr__(self):
        return "<userid: {}, regid: {}, is_enabled: {}>".format(self.userid, self.regid, self.is_enabled)


class DataTypeByte(Base):
    __tablename__ = 'datatype_byte'
    data_type_id = Column(BIGINT, primary_key=True, nullable=False)
    back_event_id = Column(BIGINT, default=None)
    data_type = Column(String(50), default=None)
    secret_level = Column(String(20), default=None)
    description = Column(String(256), default=None)

    def __repr__(self):
        return "<data_type_id: {}, back_event_id: {}, data_type: {}, secret_level: {}, description: {}>".format(
            self.data_type_id, self.back_event_id, self.data_type, self.secret_level, self.description
        )
