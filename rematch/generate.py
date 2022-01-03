from xeger import Xeger
import re
from random import randint, choice
import sys
sys.path.append('..')
from website.RegToSql import Reg2Sql
import string


reg2sql = Reg2Sql()


def gen_struct_data(key_list, pattern, num):
    length = len(key_list) - 1
    x = Xeger()
    data = []
    for i in range(num):
        cur_re = x.xeger(pattern)
        while not re.match('^' + pattern + '$', cur_re):
            print('结构化生成错误：', cur_re)
            cur_re = x.xeger(pattern)
        while cur_re == '::':
            cur_re = x.xeger(pattern)
        if cur_re[0] == '+':
            cur_re = 'is ' + cur_re
        cur = (key_list[randint(0, length)], cur_re)
        data.append(cur)
    return data


def generate_data(pre_list, back_list, pattern, num, disturb_en=0):
    x = Xeger()
    ans = []
    pre_len = len(pre_list) - 1
    back_len = len(back_list) - 1
    for i in range(num):
        cur_re = x.xeger(pattern)
        while not re.match('^' + pattern + '$', cur_re):
            print('非结构化生成错误：', cur_re)
            cur_re = x.xeger(pattern)
        while cur_re == '::':
            cur_re = x.xeger(pattern)
        cur_direction = randint(0, 1)
        disturb_ctrl = randint(0, 1000)
        disturb_type = 1 if disturb_ctrl < disturb_en * 1000 else 0
        disturb_times = randint(1, 3)
        disturb_loc = randint(0, 1)
        disturb = ''
        if disturb_type:
            for j in range(disturb_times):
                disturb += choice(string.digits + string.ascii_letters)
            if disturb_loc:
                cur_re += disturb
            else:
                cur_re = disturb + cur_re

        if cur_direction:
            cur_ans = pre_list[randint(0, pre_len)] + cur_re
        else:
            cur_ans = cur_re + back_list[randint(0, back_len)]
        if cur_ans[0] == '+':
            cur_ans = '获取到' + cur_ans
        ans.append(cur_ans)
    return ans


def verify(data_list, type_id, structed=0):
    ans = []

    for eve in data_list:
        if structed:
            reg_result = reg2sql.rematch.match_text(eve[1], [type_id])
            if type_id in reg_result:
                ans.append((eve, 1))
            else:
                ans.append((eve, 0))
        else:
            reg_result = reg2sql.rematch.match_text(eve, [type_id])
            if type_id in reg_result:
                cur_re = reg_result[type_id][0]
                if len(cur_re) > 1:
                    print(eve, cur_re)
                ans.append((eve, cur_re[0][1:]))
            else:
                ans.append((eve, (-1, -1)))
    return ans


def test_gen(pattern, num, test_id, k_list=None, p_list=None, b_list=None, struct=0, disturb_en=0):
    if struct:
        data1 = gen_struct_data(k_list, pattern, num)
    else:
        data1 = generate_data(p_list, b_list, pattern, num, disturb_en=disturb_en)
    ans = verify(data1, test_id, structed=struct)
    if not struct:
        for eve in ans:
            print(eve[0], end='\t0\tgen\t')
            print(eve[1])
    else:
        for eve in ans:
            print('\t'.join(eve[0]), end='\t1\tgen\t')
            print(eve[1])


'''pat = "\\b(((13[4-9])|(14[7-8])|(15[0-2,7-9])|(165)|(178)|(18[2-4,7-8])|(19[5,7,8]))\\d{8}\\b|\\b(170[3,5,6])\\d{7})|" \
      "(((13[0-2])|(14[5,6])|(15[5-6])|(16[6-7])|(17[1,5,6])|(18[5,6])|(196))\\d{8}\\b|\\b(170[4,7-9])\\d{7})|" \
      "(((133)|(149)|(153)|(162)|(17[3,7])|(18[0,1,9])|(19[0,1,3,9]))\\d{8}\\b|\\b((170[0-2])|(174[0-5]))\\d{7})\\b"
pre_list = ['手机号', '联系方式为', '号码是', '可以拨打', 'phone-number: ', '一个和他有关的信息']
back_list = ['是李娜的手机号码', '是一个可能的线索', ' is his mobile', ' is his number']      
55
'''
# pat = "\\b(\\+?001)?(\\ |\\-)?[2-9]\\d{2}(\\ |\\-)?[2-9]\\d{2}(\\ |\\-)?\\d{4}\\b"

pat = "[0-9a-fA-F]{2}(:[0-9a-fA-F]{2}){5}"
# pat = "(?<![\da-zA-Z])((1[45]\d{7})|([S|s|G|g|E|e]\d{8})|([P|p|S|s]\d{7})|([Gg|Tt|Ss|Ll|Qq|Dd|Aa|Ff]\d{8})|([H|h|M|m]\d{8,10}))(?![\da-zA-Z])"
pre_list = ['MAC地址是', 'MAC: ', 'its mac address is ', '物理地址', '通过以下地址发包']
back_list = [' is its mac address', '是物理地址', ' is its M4c addr3ss']
key_list = ['MAC', '物理地址', 'MAC地址', 'address', 'm4c address']

test_gen(pat, 300, 71, p_list=pre_list, b_list=back_list, k_list=key_list, struct=1, disturb_en=1)


'''back_suffix = ['net.sy', 'netease.com', 'hknet.com', 'yandex.ru', 'mail.mn', 'MAIL.RU EV', 'yeah.net', 'terra.es', 'aviso.ci', 'walla.com', 'xx.org.il', 'EMIRATES.NET.AE', 'xtra.co.nz', 'TOPMARKEPLG.COM.TW', 'wilnetonline.net', 'excite.com', 'sinos.net', '***.hinet.net', 'infoclub.com.np', 'gmail.com', 'chinaren.com', 'mail.hk.com', 'aim.com', 'scs-net.org', 'sbcglobal.net', 'ask.com', 'BIGPOND.NET.AU', 'ITCCOLP.COM.HK', 'sina.com', 'cal3.vsnl.net.in', 'SCS-NET.ORG', 'etang.com', 'amet.com.ar', 'mynet.com', 'hongkong.com', 'citiz.com', 'eyou.com', 'mail.ru', 'comcast.net', 'afnet.net', 'indigo.ie', 'SEED.NET.TW', '163.com', 'ntlworld.com', '126.com', 'cyber.net.pk', 'gionline.com.au', 'club-internet.fr', '21cn.com', 'QUALITYNET.NET', 'mindspring.com', 'swe.com.hk', '263.net', 'yahoo.com', 'vodamail.co.za', 'rediffmail.com', 'spark.net.gr', 'tiscali.co.uk', 'PCHOME.COM.TW', 'twcny.rr.com', 'yahoo.com.cn', 'zamnet.zm', 'mti.gov.na', 'NETVISION.NET.IL', 'msn.com', '0355.net', 't-online.de', 'live.com', 'mweb.co.zw', 'bigpond.com', 'sotelgui.net.gn', 'netvigator.com', 'namibnet.com', 'candel.co.jp', 'tom.com', 'hotmail.com', 'eunet.at', 'be-local.com', '56.com', 'mail.sy', '163.net', 'nesma.net.sa', 'wannado.fr', 'xxx.meh.es', 'caron.se', 'inbox.com', 'kalianet.to', 'aol.com', 'qq.com', 'eircom.net', 'iway.na', 'ctimail.com', 'dnet.net.id', 'citechco.net', 'sohu.com', 'pacific.net.sg', '3721.net', 'yemen.net.ye', 'mos.com.np', 'zol.co.zw', 'vsnl.com', 'mt.net.mk', 'africaonline.co.zw', 'samara.co.zw', 'africaonline.co.ci', 'otenet.gr', 'prodigy.net.mx', 'DEL3.VSNL.NET.IN', 'googlemail.com', 'x.cn', 'ADSL.LOXINFO.COM', 'cytanet.com.cy', 'westnet.com.au', 'libero.it', 'sancharnet.in', 'netzero.net', 'mail.com', 'hn.vnn.vn', 'infovia.com.ar', 'verizon.net', 'FASTMAIL.FM', 'swiszcz.com', 'cairns.net.au', 'ntc.net.np', 'BIZNETVIGATOR.COM', 'sogou.com', 'ZAHAV.NET.IL']

# test_gen(pat, 200, 14, p_list=pre_list, b_list=back_list, struct=0)
# test_gen(pat, 100, 25, p_list=pre_list, b_list=back_list, k_list=key_list, struct=1)
a = ugtwbrvheah642@china.com;
lhregaftpbjt@qq.com;
bndgw02@126.com;
gihodrvsetljh5@etang.com;
jqmku7@qq.com;
dlqdejj@35.com;
v14240034525@yeah.net;
ueswjnawfojbbp0@265.com;
opv@netease.com;
jrksapnmhfhfn6@126.com;
f2608063558@35.com;
wrsnoce@35.com;
uqshtjsvmqqoqwj@126.com;
ianenghkseww@21cn.com;
odffhmftb702@email.com.cn;
e827543@hotmail.com;
ajnovnw48071@china.com;
demjnavj8@msn.com;
v51@eastday.com;
qhdo1@sohu.com;
s488@126.com;
w42@265.com;
lbwontvbtpuib7@tom.com;
wjem@china.com;
awqsw1@xinhuanet;
lffeaogfvwsbo8@qq.com;
wikcafolno@263.net;
p752@sohu.com;
klidwngoj@265.com;
bpemtalw@163.com;
wdctgalikwu@21cn.com;
hdjwwceovbjl2@126.com;
ofsciatra570@sina.com;
trmmub055@163.com;
bjrq7@163.com;
oah5@eyou.com;
vhfe06@eastday.com;
rehwnneuwtrhfu@citiz.com;
umsj@sohu.com;
jbhhafkdtwwn74@netease.com;
j53436312873@msn.com;
vrmmgtuqjnlf8@265.com;
d48827003@eastday.com;
gmsbocpauer848@citiz.com;
klo@msn.com;
tsio0@citiz.com;
jpdktskossa6@163.com;
jgscfuimmvsvffl@126.com;
wigjkedj76@21cn.com;
scsvhhog20054@tom.com;
ihf@163.net;
iqatnwtcpqi3@35.com;
gdf@etang.com;
hesuege3353@email.com.cn;
bulqp@citiz.com;
ifewa601@eyou.com;
f04@yahoo.com.cn;
poohdv@21cn.com;
i364@sohu.com;
wsmpegkieniwnpm@china.com;
asmafgcrvip@263.net;
mqbqpgfi1@sina.com;
n15376@netease.com;
u885@enet.com.cn;
ibpqc2@etang.com;
twfbpogv@yeah.net;
dmmwhgcprcd@35.com;
wcnjkhqr@hotmail.com;
udgfqaunogtm@citiz.com;
drclqnngpmp4@msn.com;
jrnf4@163.net;
abgs@21cn.com;
nua@qq.com;
offdhto6045@35.com;
bvlvp3@265.com;
k756487@etang.com;
grmhbcgeq@163.net;
mnpcoicvsnmssir@tom.com;
g000@hotmail.com;
n373@china.com;
utf8@qq.com;
jjo3@263.net;
mqiecvqll44@citiz.com;
vgmovjuwds@sina.com;
uolmktraqjfaqji@xinhuanet;
mufkcbs@china.com;
nmmekksuawwq@265.com;
t252845424623@163.net;
rauketam2@citiz.com;
pmsbeffre4@eyou.com;
cgqqfiioffpu5@enet.com.cn;
b83@263.net;
rpqaehongellb52@citiz.com;
d6421151241433@163.net;
bweeawowki0@xinhuanet;
evetoglmljabdk6@35.com;
qcgttac67357@msn.com;
mvnfmb0044@msn.com;
seeqgffgph016@35.com;
uqtsfomdlmsqc6@qq.com;



youxiang = a.split(';\n')[:-1]
for_sure = []
not_sure = []
for eve in youxiang:
    cur = eve.split('@')[1]
    if cur in back_suffix:
        for_sure.append(eve)
    else:
        not_sure.append(eve)
struct_list = []
data_list = []
for eve in for_sure:
    struct_list.append(pre_list[randint(0, len(pre_list) - 1)] + eve)
for eve in not_sure:
    data_list.append(eve + back_list[randint(0, len(back_list) - 1)])

ans = verify(struct_list, 25, structed=0)
for eve in ans:
    print('EMAIL_ADDRESS_OTHERS_AFFIRMED\t\t', end='')
    print(eve[0], end='\t0\tgen\t')
    print(eve[1])'''
