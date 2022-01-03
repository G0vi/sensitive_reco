### 文件说明
- reMatch2.py
   
   ReMatch类，内封装了含有的匹配规则以及匹配算法函数
- Create_Table.py

   根据数据库的表项创建类
- data_test.py

   根据已有的规则数据以及测试数据，调用ReMatch运行测试
- SqlServer.py

   数据库的交互程序
-  RegToSql.py

   正则和数据库关联的程序，外部直接调用这个文件内的函数 
- data_py.py

   样本数据，直接存入列表（方便测试）

- data.txt

   老版的数据形式
   
- text.txt

   测试文本
 
- casual.sql

     已经存好规则集合样本的数据库文件
   
###  使用说明
#### 安装必要库

```bash
pip3 install sqlalchemy
```

#### 数据库建立
将数据库文件casual.sql导入数据库

```bash
mysql -u $username -p $pwd casual < ./casual.sql
```

#### 运行测试
将data_test.py中的

```bash
python3 HttpServer.py
```
打开网页http://localhost:8080
