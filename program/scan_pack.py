# -*- coding: utf-8 -*- 


import wx
import wx.xrc
import sqlite3
import string
import time
import uuid
from serial import Serial
from wx.lib.pubsub import Publisher
import threading

g_conn = None
cur = None
barcode = None
userid = '0'
def OpenDB():
	global g_conn, cur
	g_conn=sqlite3.connect("/home/pi/packdb.db")
	

def CloseDB():
	global g_conn
	g_conn.close()
	
def InsDB(sql):
    cur = g_conn.cursor()
    cur.execute(sql)
    cur.close()
    g_conn.commit()
    
# this is db is difference another jhdb    
def If_bar(uid,barcode_no):
    guid = uuid.uuid4()
    sql_ins = "insert into pack_sc(guid,userid,barcode,crdate) values('%s','%s','%s',datetime('now','localtime'));" %(guid,uid,barcode_no)
    InsDB(sql_ins)

def No_bar(not_barcode):
    sql_ins_nobar = "insert into pack_bad(barcode,crdate) values('%s',datetime('now','localtime'));" %(not_barcode)
    InsDB(sql_ins_nobar)	
	
	

class MyFrame1 ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u'包装箱扫描程序', pos = wx.DefaultPosition, size = wx.Size( 320,240 ), style = wx.DEFAULT_FRAME_STYLE|wx.MAXIMIZE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer1 = wx.BoxSizer( wx.HORIZONTAL )
		
		sbSizer1 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"left" ), wx.VERTICAL )
		
		sbSizer1.SetMinSize( wx.Size( 100,185 ) ) 
		bSizer2 = wx.BoxSizer( wx.HORIZONTAL )
		
		id_lsChoices = []
		self.id_ls = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 57,170 ), id_lsChoices, 0 )
		bSizer2.Add( self.id_ls, 0, 0, 5 )
		
		num_lsChoices = []
		self.num_ls = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 43,170 ), num_lsChoices, 0 )
		bSizer2.Add( self.num_ls, 0, 0, 5 )
		
		
		sbSizer1.Add( bSizer2, 1, wx.EXPAND, 5 )
		
		
		bSizer1.Add( sbSizer1, 0, 0, 5 )
		
		sbSizer2 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"right" ), wx.VERTICAL )
		
		bSizer3 = wx.BoxSizer( wx.HORIZONTAL )
		
		all_lsChoices = []
		self.all_ls = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), all_lsChoices, 0 )
		bSizer3.Add( self.all_ls, 1, wx.EXPAND, 5 )
		
		
		sbSizer2.Add( bSizer3, 1, wx.EXPAND, 5 )
		
		
		bSizer1.Add( sbSizer2, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer1 )
		self.Layout()
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	
class SerialFrame(MyFrame1):
    def __init__(self,parent=None):
        super(SerialFrame,self).__init__(parent)

        self.Ser = Serial('/dev/ttyUSB0',9600)
        if not self.Ser.isOpen():
            self.Ser.open()
        self.serialThread = SerialThread(self.Ser)
		
        #create a pubsub receiver
        Publisher().subscribe(self.on_txtMain_update,'update')
		
		
    def on_txtMain_update(self, msg):   
	global userid,barcode		
        barcode = msg.data.strip('\n\r')
        if barcode.__len__() == 5:
            userid = barcode
	        return
        #if barcode.__len__() != 16:
		#    return
	    if not barcode.isdigit():
		    No_bar(barcode)
		    return
        f=self.id_ls.FindString(userid)
        if f == -1:
            self.id_ls.Append(userid)
            self.num_ls.Append(str(1))
        else:
            i=self.num_ls.GetString(f)
            self.num_ls.SetString(f,str(string.atoi(i)+1))
        self.all_ls.Append(userid+' '+barcode)
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
                text = self.Ser.readline(self.Ser.inWaiting())
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

