#!/usr/bin/env python
# -*- coding: cp1252 -*-
"""
   Aggiunta device
config viene dato dalla somma dei seguenti valori:
   senza TA = 0               con TA = 1  (scambio o deviatore con TA)
   messaggi non criptati = 0  messaggi criptati = 2
   Alert disabilitato = 0     Alert abilitato =  4 (su scambio, non usato su deviatore e presa) 
   Ritardo prima di inviare Alert = 0,8,16,24 -> (0,2,4,6 watt oltre il max)
config1

"""
import MySQLdb
import os 
import random, time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from math import floor
from shutil import copyfile  #for copying files

try:
   import RPi.GPIO as GPIO
except:
   print "No root privileges.\nSkipping RPi.GPIO import"
try:
    from Pic_Berry_C import *
except:
    print "File di configurazione mancante"

db = MySQLdb.connect(host="localhost",user="root",passwd=passMy)
cursore = db.cursor()
cursore.execute('USE pic_berry')
print "Utlity inserimento devices Pic&Berry, (CRTL+C per uscire)"
device = raw_input("Nome device: ")
adr = input("indirizzo del device: ")
config = input("dammi il valore del config (6 -> senza TA, 7-> con TA: ")
config1 = input("dammi valore acceso (8): ")
config2 = input("dammi il valore spento (5): ")

strconf = raw_input("dammi STRCONF maiuscolo (SIC): ")
sql = "SELECT * FROM devices WHERE device = '%s'" %(device)
cursore.execute(sql)
results = cursore.fetchone()
print results
if results:
   print " DISPOSITIVO NON CONFIGURATO !!!!!"
   print 'Nome già usato'
   exit()  
sql = "SELECT * FROM devices WHERE adr = %d" %(adr)
cursore.execute(sql)
results = cursore.fetchone()
print results
if results:
   print " DISPOSITIVO NON CONFIGURATO !!!!!"
   print 'Indirizzo già usato'
   exit() 


#sql = "INSERT INTO devices(device,adr,net,pwd) values ('io', %d, %d, %d)" % (io, net, pwd)
#cursore.execute(sql)
sql = "INSERT INTO devices(device,adr,net,pwd,config,config1,config2,strconf) values ('%s', %d, %d, %d, %d, %d, %d, '%s')" % (device,adr, net, pwd, config,config1,config2,strconf) #2 è fotov, 2 è cripta messaggi
cursore.execute(sql)            
print "INSERIMENTO DEVICE COMPLETATO!!!!"
sql = "SELECT * FROM devices WHERE device = '%s'" %(device)
cursore.execute(sql)
results = cursore.fetchone()
print results
db.commit()
db.close()


