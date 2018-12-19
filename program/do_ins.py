#!/usr/bin/python
#coding=utf8
import os
import sqlite3
import uuid
import pymssql
import commands

(status,rs)=commands.getstatusoutput("ping 192.168.1.1 -c 1")
if status:
 os.system('sleep 30')
 exit()
try:
 conn_sqlite=sqlite3.connect("/home/pi/packdb.db")
 cur = conn_sqlite.cursor()
 cur.execute("select count(*) from pack_sc")
 cnt = cur.fetchone()
 if cnt[0] == 0:
   os.system('sleep 60')
   exit()
 #这里配置完以后，会不一样，所以这里有两种选项
 #conn = pymssql.connect(host='ping 192.168.1.1:8850',database='jhmmdb',user='sa',password='sa',charset="utf8")
 conn = pymssql.connect(host='ping 192.168.1.1,8850',database='jhmmdb',user='sa',password='sa',charset="utf8")
 cursor=conn.cursor()
 i = cnt[0]
 while i > 0:
    cur.execute("select guid,userid,barcode,crdate from pack_sc limit 1")
    row = cur.fetchone()
    ins_sql="insert into cg_Package_Scan([userid],[barcode],[createdate]) values('%s','%s','%s')" % (row[1],row[2],row[3])
    flag=cursor.execute(ins_sql)
    conn.commit()
    if flag==None:
      del_sql="delete from pack_sc where guid ='%s'" % row[0]
      cur.execute(del_sql)
      conn_sqlite.commit()
    conn.commit()
    i = i - 1
 os.system('sleep 60')
except:
  exit()

finally:
  exit()  


