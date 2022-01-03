from rematch.regDB.CreateTable import Users, UserRegs, RegRules
from sqlalchemy import and_

from website.RegToSql import Reg2Sql

reg2sql = Reg2Sql()
ans = reg2sql.read_sql.query(UserRegs, RegRules,
                             condition=and_(UserRegs.userid == 18, UserRegs.is_enabled == 1, UserRegs.regid == RegRules.id,
                                            RegRules.is_default == 1))
print(ans[0])
