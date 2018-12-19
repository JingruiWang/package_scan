# -*- coding: utf-8 -*- 
 

import wx
import wx.xrc
import wx.grid
import sqlite3
import uuid
import string
import time
import pymssql
from serial import Serial
from wx.lib.pubsub import Publisher
import threading
import commands

g_conn = None
cur = None
S_g_conn = None
S_cur = None
userid = ""
barcode = ""
guid = ""
cnt = 0
uid_dict = {}
bar_dict = {}
lb_Arr = []
col_num=0
def OpenDB():    
	global g_conn, cur, S_g_conn, S_cur
	global userid,barcode,guid,uid_dict
	g_conn=sqlite3.connect("/home/pi/jhdb.db")	

    
def CloseDB():
	global g_conn, S_g_conn
	g_conn.close()

	
#sqlite3 
def InsDB(sql):
	cur = g_conn.cursor()
	cur.execute(sql)
	cur.close()
	g_conn.commit()

def If_bar(uid,barcode_no):	
	guid=uuid.uuid4()
	sql_ins = "insert into t_bar(guid,barcode,userid,createdate) values('%s','%s','%s',datetime('now','localtime'));" %(guid,barcode_no,uid)
	InsDB(sql_ins)

#SQL Server 2008	
def Query(uid):
 #try:
     if len(uid) == 6:
        sql_query = "select barcode,username,process+'/'+workcontent gxnr"
        sql_query = sql_query + " from mes_WorkTeamWithProcess mw inner join mes_UserGroup mu "
        sql_query = sql_query + "  on mw.groupid = mu.groupid "
        sql_query = sql_query + " where barcode = '%s' " %uid
     else:
        sql_query = " select jp.orderid,sp.xuhao,cast(jp.pthick as varchar)+'*'+cast(jp.pwidth as varchar)+'*'+cast(jp.pheight as varchar) gg, "
        sql_query = sql_query + " jp.pcolor+' '+sp.diaok sz,sap.plandate,jp.gmodel,jp.gcode,sp.hey,sp.rl,sp.lck "
        sql_query = sql_query + " from js_productbom jp inner join sal_proorddetail sp "
        sql_query = sql_query + " on jp.orderid = sp.orderid "
        sql_query = sql_query + " and jp.gcode = sp.pronumber "
        sql_query = sql_query + " left join sal_proordtotal sap on jp.orderid = sap.orderid "
        sql_query = sql_query + "  where jp.barcode = '%s' " %uid
     
     S_g_conn=pymssql.connect(host='192.168.0.1:8850',database='jhmmdb',user='sa',password='sa',login_timeout=1,charset="utf8")
     S_cur=S_g_conn.cursor()
     S_cur.execute(sql_query)
     rows = S_cur.fetchall()
     S_cur.close()
     S_g_conn.close()
     return rows
 #except:
 #    return ' '


def F_key(uid):
 try:
       if uid in uid_dict:		
           return uid_dict[uid][0],uid_dict[uid][1]
       else:	
           rs = Query(uid)
           num=0
           str1=""
           for i in rs:
             if num == 0:
                str1 = i[1]
             else:
                str1=str1+'/'+i[1]
             num=num+1
           uid_dict[uid]=[str1.encode("utf8"),i[2].encode("utf8")]
           return str1.encode("utf8"),i[2].encode("utf8")
 except:
    return ' ',' '


def F_key_L(bar_code):
 try:
       if bar_code in bar_dict:		
           return bar_dict[bar_code]
       else:	
           rs = Query(bar_code)
           bar_dict[bar_code]= [rs[0]]
           return bar_dict[bar_code]
 except:
    return ' '    
	
	


class MyFrame1 ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"工序扫描录入程序", pos = wx.DefaultPosition, size = wx.Size( 900,600 ), style = wx.DEFAULT_FRAME_STYLE|wx.MAXIMIZE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer6 = wx.BoxSizer( wx.HORIZONTAL )
		
		sbSizer1 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"工序录入" ), wx.VERTICAL )
		
		sbSizer1.SetMinSize( wx.Size( 300,-1 ) ) 
		bSizer1 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.label1 = wx.StaticText( self, wx.ID_ANY, u"当前卡号：", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.label1.Wrap( -1 )
		bSizer1.Add( self.label1, 1, 0, 5 )
		
		self.label10 = wx.StaticText( self, wx.ID_ANY, u"当前姓名：", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.label10.Wrap( -1 )
		bSizer1.Add( self.label10, 1, 0, 5 )
		
		self.label2 = wx.StaticText( self, wx.ID_ANY, u"当前工序：", wx.Point( -1,-1 ), wx.DefaultSize, 0 )
		self.label2.Wrap( -1 )
		bSizer1.Add( self.label2, 1, wx.ALIGN_TOP, 5 )
		
		self.bt_cl = wx.Button( self, wx.ID_ANY, u"清除", wx.DefaultPosition, wx.Size( -1,19 ), 0 )
		self.bt_cl.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHT ) )
		
		bSizer1.Add( self.bt_cl, 0, 0, 5 )
		
		
		sbSizer1.Add( bSizer1, 0, wx.EXPAND|wx.ALL, 5 )
		
		bSizer5 = wx.BoxSizer( wx.HORIZONTAL )
		
		#self.lb_no = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
                self.lb_no = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 70,-1 ), 0 )
		self.lb_no.Wrap( -1 )
		self.lb_no.SetFont( wx.Font( 12, 70, 90, 92, False, "宋体" ) )
		
		#bSizer5.Add( self.lb_no, 1, wx.TOP|wx.BOTTOM, 5 )
                bSizer5.Add( self.lb_no, 0, wx.TOP|wx.BOTTOM|wx.RIGHT|wx.EXPAND, 5 )
		self.lb_name = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lb_name.Wrap( -1 )
		self.lb_name.SetFont( wx.Font( 9, 70, 90, 92, False, "宋体" ) )
		
		bSizer5.Add( self.lb_name, 1, wx.TOP|wx.BOTTOM|wx.RIGHT, 5 )
		
		self.lb_gx = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lb_gx.Wrap( -1 )
		self.lb_gx.SetFont( wx.Font( 9, 70, 90, 92, False, "宋体" ) )
		
		bSizer5.Add( self.lb_gx, 1, wx.TOP|wx.BOTTOM|wx.RIGHT, 5 )
		
		
		sbSizer1.Add( bSizer5, 0, wx.EXPAND, 5 )
		
		bSizer2 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.label3 = wx.StaticText( self, wx.ID_ANY, u"卡号", wx.Point( -1,-1 ), wx.DefaultSize, 0 )
		self.label3.Wrap( -1 )
		bSizer2.Add( self.label3, 1, wx.ALIGN_TOP|wx.ALL, 5 )
		
		self.label4 = wx.StaticText( self, wx.ID_ANY, u"姓名", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.label4.Wrap( -1 )
		bSizer2.Add( self.label4, 1, wx.ALL, 5 )
		
		self.label5 = wx.StaticText( self, wx.ID_ANY, u"工序", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.label5.Wrap( -1 )
		bSizer2.Add( self.label5, 1, wx.ALL, 5 )
		
		self.label6 = wx.StaticText( self, wx.ID_ANY, u"次数", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.label6.Wrap( -1 )
		bSizer2.Add( self.label6, 1, wx.ALL, 5 )
		
		
		sbSizer1.Add( bSizer2, 0, wx.EXPAND, 5 )
		
		bSizer3 = wx.BoxSizer( wx.HORIZONTAL )
		
		id_listChoices = []
		self.id_list = wx.ListBox( self, wx.ID_ANY, wx.Point( -1,-1 ), wx.Size( 70,-1 ), id_listChoices, 0 )
                #self.id_list.SetFont( wx.Font( 9, 70, 90, 90, False, "宋体" ) )
		bSizer3.Add( self.id_list, 0, wx.ALL|wx.EXPAND, 0 )
		
		name_listChoices = []
		self.name_list = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 120,-1 ), name_listChoices, 0 )
                self.name_list.SetFont( wx.Font( 8, 70, 90, 90, False, "宋体" ) )

		bSizer3.Add( self.name_list, 0, wx.ALL|wx.EXPAND, 0 )
		
		gx_listChoices = []
		self.gx_list = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 120,-1 ), gx_listChoices, 0 )
                self.gx_list.SetFont( wx.Font( 8, 70, 90, 90, False, "宋体" ) )
		bSizer3.Add( self.gx_list, 0, wx.EXPAND|wx.ALL, 0 )
		
		num_listChoices = []
		self.num_list = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 50,-1 ), num_listChoices, 0 )
		bSizer3.Add( self.num_list, 0, wx.ALIGN_TOP|wx.ALL|wx.EXPAND, 0 )
		
		
		sbSizer1.Add( bSizer3, 1, wx.EXPAND, 5 )
		
		
		bSizer6.Add( sbSizer1, 0, wx.EXPAND, 0 )
		
		sbSizer2 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"工序条码查看" ), wx.VERTICAL )
		
		bSizer4 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.mygrid = wx.grid.Grid( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 100,100 ), 0 )
		
		# Grid
        	colLableVale = [u'卡号',u'条形码',u'订单号',u'姓名',u'序号',u'规格',u'色泽',u'交货期',u'型号',u'产品编码',u'合页',u'左右手',u'锁',u'材质',u'类别']
		
		self.mygrid.CreateGrid( 0, len(colLableVale) )
		self.mygrid.EnableEditing( True )
		self.mygrid.EnableGridLines( True )
		self.mygrid.EnableDragGridSize( False )
		self.mygrid.SetMargins( 0, 0 )
		
		# Columns
		self.mygrid.EnableDragColMove( False )
		self.mygrid.EnableDragColSize( True )
		self.mygrid.SetColLabelSize( 30 )
		self.mygrid.SetColLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
		
        
        	# Columns Name
		for j in range(len(colLableVale)):
			self.mygrid.SetColLabelValue(j,colLableVale[j])
		# Rows
		self.mygrid.EnableDragRowSize( True )
		self.mygrid.SetRowLabelSize( 80 )
		self.mygrid.SetRowLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
		
		# Label Appearance
		
		# Cell Defaults
		self.mygrid.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
		bSizer4.Add( self.mygrid, 1, wx.EXPAND, 5 )
		
		
		sbSizer2.Add( bSizer4, 1, wx.EXPAND, 5 )
		
		
		bSizer6.Add( sbSizer2, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer6 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.bt_cl.Bind( wx.EVT_BUTTON, self.bt_clOnButtonClick )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def bt_clOnButtonClick( self, event ):
		self.id_list.Clear()
        	self.name_list.Clear()
        	self.gx_list.Clear()
        	self.num_list.Clear()
		rows=self.mygrid.GetNumberRows()
		self.mygrid.ClearGrid()
		self.mygrid.DeleteRows(0,rows)
		global col_num,lb_Arr,userid
        	col_num = 0
		lb_Arr = []
		userid = ""
		self.lb_no.SetLabel('')
		self.lb_name.SetLabel('')
		self.lb_gx.SetLabel('')
        	#event.Skip()


	
	

class SerialFrame(MyFrame1):
    def __init__(self,parent=None):
        super(SerialFrame,self).__init__(parent)

        self.Ser = Serial('/dev/ttyUSB0',9600)
        if not self.Ser.isOpen():
            self.Ser.open()
        self.serialThread = SerialThread(self.Ser)
		
        #create a pubsub receiver
        Publisher().subscribe(self.on_txtMain_update,'update')
	
    def StarThread(self):
        pass
        #self.thread = threading.Thread(target=self.GetDataThread)
        #self.thread.setDaemon(1)
        #self.thread.start()
    
    def GetDataThread(self):
        pass
    
    def on_txtMain_update(self, msg):   
	global userid,barcode,guid,uid_dict,lb_Arr,col_num,bar_dict		
        barcode = msg.data.strip('\n\r')
        if barcode.replace(' ','').__len__() == 6:
            userid = barcode
	    lb_Arr = F_key(userid)
            self.lb_no.SetLabel(userid)
	    self.lb_name.SetLabel(lb_Arr[0])
	    self.lb_gx.SetLabel(lb_Arr[1])
	    return			

        if userid.strip() == "":            
            return
        if barcode.__len__() < 18 or barcode.__len__() > 20:
            return
 
        f=self.id_list.FindString(userid)
        if f == -1:
            self.id_list.Append(userid)
	    self.name_list.Append(lb_Arr[0])
	    self.gx_list.Append(lb_Arr[1])
            self.num_list.Append(str(1))
        else:
            i=self.num_list.GetString(f)
            self.num_list.SetString(f,str(string.atoi(i)+1))
            self.name_list.SetString(f,lb_Arr[0])
            self.gx_list.SetString(f,lb_Arr[1])
        rs_d = F_key_L(barcode)
        if rs_d == ' ':
         rs_d = [(' ',' ',' ',' ',' ',' ',' ',' ',' ',' ')]
        self.mygrid.AppendRows(1, 1)
        self.mygrid.SetCellValue(col_num,0,userid)        
        self.mygrid.SetCellValue(col_num,1,barcode)
        self.mygrid.SetCellValue(col_num,2,str(rs_d[0][0].encode("utf8")))
        self.mygrid.SetCellValue(col_num,3,lb_Arr[0])
        self.mygrid.SetCellValue(col_num,4,str(rs_d[0][1].encode("utf8")))
        self.mygrid.SetCellValue(col_num,5,str(rs_d[0][2].encode("utf8")))
        self.mygrid.SetCellValue(col_num,6,str(rs_d[0][3].encode("utf8")))
        self.mygrid.SetCellValue(col_num,7,str(rs_d[0][4].encode("utf8")))
        self.mygrid.SetCellValue(col_num,8,str(rs_d[0][5].encode("utf8")))
        self.mygrid.SetCellValue(col_num,9,str(rs_d[0][6].encode("utf8")))
        self.mygrid.SetCellValue(col_num,10,str(rs_d[0][7].encode("utf8")))
        self.mygrid.SetCellValue(col_num,11,str(rs_d[0][8].encode("utf8")))
        self.mygrid.SetCellValue(col_num,12,str(rs_d[0][9].encode("utf8")))
        self.mygrid.AutoSizeColumns()
        self.mygrid.EnableEditing(False)
        col_num = col_num + 1
        If_bar(userid,barcode)

class SerialThread(threading.Thread):
    def __init__(self,Ser):
        super(SerialThread,self).__init__()

        self.Ser=Ser
        self.setDaemon(True)
        self.start()

    def run(self):
        while True:
            if self.Ser.isOpen() and self.Ser.inWaiting():
                text = self.Ser.readline()
                wx.CallAfter(Publisher().sendMessage,'update',text)
            time.sleep(0.01)
       
			
		
if __name__ == "__main__":
	try:
		OpenDB()
		app = wx.App()
		forms = SerialFrame(None)
		forms.Show(True)
		app.MainLoop()		
	except Exception, e:
		print e
	finally:
		CloseDB()



