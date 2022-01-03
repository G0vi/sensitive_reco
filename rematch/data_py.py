# 以列表的形式直接将样本数据加载到内存，以列表形式存入texts
texts = [
    "他们两个生下一个孩子，名字叫做王振义，身份证号是350211198903056176，他的弟弟身份证号是320101200201015915。。为什么前两位不一样呢？\
    全智贤的身份证号码是880410-1641569，主要是因为他是韩国人。土耳其的身份证号和中国的比起来少了几位，比如一个身份证样例就是：17291716060；\
    新加坡的身份证号就不一样了，它不光有数字，还有字母，比如：F1234567G， 还有S开头的，像S0000003E，还有像S7712345K的。\
    印度尼西亚的身份证号是比如5101016001800010、5937414810070465以及6237284910370445这样子的。印度的唯一身份号码不叫身份证号，而是叫做Aadhaar号，\
    比如2341-2314-3425， 324-2243-4254还有3221 3241 5466这样子\
    南非身份证号可以通过一个网站https://chris927.github.io/generate-sa-idnumbers/来生成样本，比如8907020111082，2001014800086 \
    还有9705055800085这样子的。\
    ",
    "接下来我们开始讲各个地区的电话号码，我们通常见到的电话号码是132-34256738，153-2042-5436这个样子的对吧？但是这些都是中国的电话号码格式，"
    "在国际上的话，我们的电话号码要写成+86-18542375846，前面的+86是我们的国际区号。你们知道其他国家的电话号码是什么样子的吗？如果是美国的话，就"
    "要写成001-3128081300，前面的加号可以没有，00也可以没有，比如变成1-4155787342这样子，而同样的道理，在美国内部，就不用写区号了，直接类似于"
    "2023282516这样的就可以了；同理，日本的电话号码区号是81，你们明白了改是什么样子了吗？没错，就是+0081-0312345678，当然像+81-04-1234-5678"
    "也是对的，自己国家内部就是03-12345678了。印度电话号码是：+91-7428731249或者0091 7428731249这种样子。英国的电话格式是+0044-7121385420"
    "，吧前面的00去掉，然后像这样+44 7121385420把-变成空格也是一样的，香港的电话为00852 9124 5321、法国电话号码是+0033-623153412、台湾"
    "的为+00886-932547408或者把所有的符号都去掉，变成00886932547408",

    "电子邮箱信息是：zhangziyi.yanyuan@bytedance.com，汪峰的邮箱是wangfeng@voice.com，小明有自己的qq邮箱，是42341a@qq.com，还有一个"
    "163邮箱，为t214255@163.com",

    "张千羽的护照是P2312490，但是护照有好几种格式，还有S开头的，比如S0000004，S00000032，还有像洪世贤的以E开头的E00000000",

    "今天新办了银行卡，卡号是6217001930007680664，自己原来还有两张别的卡6221386102180111256以及6214830119460961",

    "我们的邮编信息为110202，他们的邮编信息是100191，还有200120这样子。都是大陆的邮编",

    "The us zipcode in America is formatted well, whose format should be like 85701, 72201, 72219 and so on. ",

    "中国的车牌号满大街都是，比如有GK12001， 还有浙A1063警，以及辽ABT522，后面的都是地区名开头，前面的那个是字母开头",

    "我经常访问的网站是\'https://www.youtube.com/watch?v=_9I-tfu1d6M，还有http://www.baidu.com，我也偶尔会使用一下ftp，比如ftp://"
    "192.168.3.14?v=_9I-tfu1d6M&a=0",

    "外国人居留许可证的样子是bac123456789012，还有zyp542376098504，以及gxy241365427859",

    "我的本机ip地址是192.168.3.14，还有10.2.34.78，这些都是nat地址分配的，the IP address of my docker is 172.12.56.124",

    "我的本机ipv6地址是fe80::1048:e6ff:fea8:bbf9%awdl0，这种地址比较特殊，还有fe80::1048:e6ff:fea8:bbf9%llw0，当然也有常规的那种"
    "：fdbd:ff1:ce00:f:cff:9d49:35be:bf8f，以及带省略版的fdbd:ff1:ce00:f::d7",

    "倚天屠龙记中男主角是张三丰，女主角中有周芷若，他们都是金庸笔下的人物，同时射雕英雄传也是一部经典小说，里面的欧阳锋、黄药师和周伯通等都是五绝"
    "大佬",

    "我名字叫胡图图，爸爸叫胡英俊，妈妈叫张小丽，我家住在翻斗大街翻斗花园2号楼1001室，我今年3岁。胡英俊的老家是在莲花镇稻香村6组30号，后来他考上了北航，"
    "北航的地址是学院路37号，他最后保送了研究生，并读上了博士",

    "doctor wei is my professor, I am a graduate from the same university of him",

    "在用户的登录之后，通常会使用session_id来保存一下当前用户的信息，比如登录之后server给client发送了一个OnNo0KfLMpkzB9GewqTFg7RUIEbuQmvH，"
    "之后client就可以通过这个id来当做令牌提交给服务端，用于之后的访问，同样的session id的样子还有WOHjUEdl2FVRoTfBDYnMpikv4Zm60b3y，"
    "oVAF6itb4BU0uRhgEP8fy2vwCT3q9dsN等……都是32个字符",

    "现在好多用户都会使用弱密码，比如birthday1225，Article2134这样的弱口令。不过虽然苹果手机的解锁口令是6位，比如210135，但是很难攻破，其"
    "原因是只有很少的次数去尝试 。",

    "There are many kinds of credit card. For example, master card is like 5101234567890123, also like 5590 2334 6215 "
    "0986, "
    "in which has some blank. And it always begins with 5, one exception is the ones beginning with 2, such as 25456231"
    "23478543. Visa card is also common, 4839627253481062, 4475 2373 4479 9222 and 4006 8123 6776 9266 which begins wit"
    "h 4 is the format of it. Express card is like 3798 888488 61820, 374360796737126, which begins with 37. Some other"
    "s like 38600279842739 and 38600948984896 is dayun card, 6011392766997691 and 6011630115738476 is Discover Card, "
    "3566181766091225 is JCB Card, 6521939694112918 is Rupay Card.",

    "首先这个图里面的就是梁爽，本身是一个比较自私有些高傲的女生，开始和自己宿舍的女生关系处的不是很好，还是比较自我的，但是本身的性格还比较善良，"
    "后面也有所改善，出演这个角色的就是关晓彤了，也是大家很熟悉的一个女演员，她是97年出生的，到现在是23岁，正是大学毕业的年纪，还是很"
    "符合人设的。",

    "接下来的这个图里面的就是段振宇了，是上面所说的这个大宝的弟弟，颜值相当的高，也是非常帅气的，一出场也是收获了很多人的目光，出演这个角色的演员"
    "就是王安宇了，之前也有过一些作品，不知道大家有没有关注过，这个男生他是98年出生的，现在是22岁，也是正青春。",

    "session_key是3h2a276nbn6nai8spnj0shalsn6nmiv4994o5i83cphmuqwbjkxuvhryj0oidjhp\nag1rw8yj9v3owtdgev8zz0hqm3k8xhsb\nm"
    "2ionzxwaju8jj9gthb48h6e5hvhbq7h\nmra547b0ahsmx7viaertbn8n7frijh3x\ns7bahfzestwlg4sgxtbpjx08jd02ed1l\ny32y0wbir1bxg"
    "p9dgytyz9gn7beiqsv3，还有这种m2ionzxwaju8jj9gthb48h6e5hvhbq7h994o5i83cphmuqwbjkxuvhryj0oidjhp\nzciwv054m5psx65uhvll4"
    "1awhclvh83r\nmra547b0ahsmx7viaertbn8n7frijh3x\ns7bahfzestwlg4sgxtbpjx08jd02ed1l\ny32y0wbir1bxgp9dgytyz9gn7beiqsv"
    "3\n3h2a276nbn6nai8spnj0shalsn6nmiv4\nag1rw8yj9v3owtdgev8zz0hqm3k8xhsb，这些就是session的样子",

    "公司内部有的服务需要service_key，即ST-1599656295-TekpfTL8h8NDnN5GSjxHYjOxxqaiEY1d,994o5i83cphmuqwbjkxuvhryj0oidjhp还有"
    "ST-1604305960-WCg5fKcJbciP9RQKQmTX1vNE5EN99R0J,mra547b0ahsmx7viaertbn8n7frijh3x这样的，以及ST-1605690553-O2LW6iEWLSn"
    "Zd70l06amIqBKSxBr9zCT,y32y0wbir1bxgp9dgytyz9gn7beiqsv3的。。",

    "那么cookie呢？Cookie: _ga=GA1.2.721781128.1556518728; locale=zh-CN; tt_webid=6698498988091835907; __tea_sdk__user_u"
    "nique_id"
    "=bf18bca38b3e806176fa7755941a39ba0802fe5e; __tea_sdk__ssid=d4669f2a-360a-45f9-8416-c1425114faad; AMCV_983502BE5329"
    "60BE0A490D4C%40AdobeOrg=283337926%7CMCIDTS%7C18082%7CMCMID%7C73729113402700275311037126474014837730%7CMCAAMLH-156"
    "2839583%7C3%7CMCAAMB-1562839583%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCAID%7CNONE; "
    "local=zh-CN; tableau-session-2=7142d47f-9a7e-4f48-80e8-884a050d30dd; _gid=GA1.2.1947927040.1586660136; portal_tok"
    "en=df2ba11b-4970-48a3-a3aa-d337122fce58，这是一个cookie样例.\n",

    "还有的cookie的样子是另一种格式的，即："
    "__tea__ug__uid: \"6899702025190327822\"\n_csrf_token: \"c3a4489d2bf638ed648f1d797df2739fd8157581-1606465291\"\n"
    "trust_browser_id: \"5e885cc3-dc76-42d5-8bcc-eb5378768f4c\"\nnumber: 234. 还有从网页端截获的如下：\n"
    "Cookie: locale=zh-CN; trust_browser_id=5e885cc3-dc76-42d5-8bcc-eb5371768f4c; passport_web_did=689970203344455270"
    "7; __tea__ug__uid=6899702025190327822; session=XM0YXJ0-f30fc7c9-df41-21a5-891e-70d046f4fd3g-WVuZA; is_anonymous_se"
    "ssion=; _csrf_token=57046437b3608b5cefa5b838afe77e36cdc759f3-1606719827; lang=zh",

    "此外，我们还拿到了几种存储在数据库中的加密编码后的password，如!orcnmsy6HbzzDwzbWdHAkvxDTHoVxiJsq2C8VDj0、!GPUIaPQYmrQrqvZkV"
    "IyQeMrpldg6UCrgLWzneVE8以及!EHZie7yKwQmfM8NfI5s2tcWhSMsL2raz8cCmLTFQ。。。",

    "一些api-key的格式是这样的：Fxx51qhT22aQ2e9cQn0bsMmWtAbWC/AuaWZ7FC6iH1+JKC5Q6hhVGZ3CKNW4h/Lx，即base64的编码格式",

    "ssh-rsa的公钥是这样的AAAAB3NzaC1yc2EAAAADAQABAAABAQDUsly27QhXPGabAqPzqBuXuYO5xfrPSfUS9lpilL7+HmEo/LRjaPrKWZZJfMQSFbQY"
    "XCj2qmlXtfCrXRFbxG10mYHGmqP1QV5z4gZHaZU/8rpWKX08xuBtmK3Xk6KOP0MAMN6n3uBrP4+JEbYn3zHfJRjqWgcCDkn4OVnXuYoObh7AnCTAUb"
    "tB0Slv9UIEvy32lbVhw4SM7+7yyzZIQIvzW4+MjJQxDQyjL1mVsOndgDJ59UZbq4vQpH3xZ3L0nMyr3p/8ZpBUU7ictgwa2A/NZpk8BQmAORvtbfY2"
    "wg1ohZhhAlDq6vfBWnLTMzqz/DVcfNHA5v7PxL6prfzLsrZz，同样用的是base编码"

]
