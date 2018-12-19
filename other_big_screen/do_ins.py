#!/usr/bin/python
#coding=utf8
import os
import sqlite3
import uuid
import pymssql
import commands

(status,rs)=commands.getstatusoutput("ping 192.168.0.1 -c 1")
if status:
 os.system('sleep 30')
 exit()
try:
 conn_sqlite=sqlite3.connect("/home/pi/jhdb.db")
 cur = conn_sqlite.cursor()
 cur.execute("select count(*) from t_bar")
 cnt = cur.fetchone()
 if cnt[0] == 0:
   os.system('sleep 60')
   exit()
 conn = pymssql.connect(host='192.168.0.1',database='jhmmdb',user='sa',password='sa',charset="utf8")
 cursor=conn.cursor()
 i = cnt[0]
 while i > 0:
    cur.execute("select guid,userid,barcode,createdate from t_bar limit 1")
    row = cur.fetchone()
    ins_sql="insert into mes_processfinishbarcodetemp([guid],[userid],[barcode],[createtime]) values('%s','%s','%s','%s')" % (row[0],row[1],row[2],row[3])
	
	##初步想法  insert into mes_processfinishbarcodetemp([guid],[userid],[barcode],[createtime]) 
	##          select row[0],row[1],row[2],row[3] 
	##   		 where not exists (select 1 from mes_processfinishbarcodetemp
	##                             where guid = row[0]      
	##          if not exists (select 1 from mes_processfinishbarcodetemp where guid = '%s') % (row[0]) 
    ##       	"insert into mes_processfinishbarcodetemp([guid],[userid],[barcode],[createtime]) values('%s','%s','%s','%s')" % (row[0],row[1],row[2],row[3])  
    flag=cursor.execute(ins_sql)
    conn.commit()
    if flag==None:
      del_sql="delete from t_bar where guid ='%s'" % row[0]
      cur.execute(del_sql)
      conn_sqlite.commit()
    conn.commit()
    i = i - 1
 os.system('sleep 60')
except:
  exit()

finally:
  exit()  

