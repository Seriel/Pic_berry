#!/usr/bin/env python
# -*- coding: cp1252 -*-
"""
   Installazione Pib&Berry 2.0  
      -cambiato setup
      -sistemato istantaneo
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
try:
   dbM = MySQLdb.connect(host="localhost",user="root",passwd='')
   cursoreM = dbM.cursor()
   cursoreM.execute("GRANT ALL ON pic_berry.* TO root@localhost IDENTIFIED BY '%s';" % (passMy)) 
   print "SETTO password in MariaDB"
   dbM.commit()
   dbM.close()
except:
   print " Passoword in MariaDB già Settata"
   
db = MySQLdb.connect(host="localhost",user="root",passwd=passMy)
cursore = db.cursor()

cursore.execute('CREATE DATABASE IF NOT EXISTS pic_berry;')
cursore.execute('USE pic_berry;')
sql = '''CREATE TABLE IF NOT EXISTS `fotov` (
  `id_pot` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `giorno` date DEFAULT NULL,
  `ora` time DEFAULT NULL,
  `watt` int(5) DEFAULT NULL,
  `maxi` int(6) DEFAULT NULL,
  PRIMARY KEY (`id_pot`)
);'''
print sql
cursore.execute(sql)
sql = '''CREATE TABLE IF NOT EXISTS `fotov_gg` (
  `id_gio` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `giorno` date DEFAULT NULL,
  `watt` int(7) DEFAULT NULL,  
  `max5` int(7) DEFAULT NULL,   
  `max5_time` time DEFAULT NULL,
  `maxi` int(7) DEFAULT NULL,
  `inizio` time DEFAULT NULL,
  `fine` time DEFAULT NULL,
  PRIMARY KEY (`id_gio`)
);'''
print sql
cursore.execute(sql)
sql = '''CREATE TABLE IF NOT EXISTS `fotov_mm` (
  `id_mm` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `giorno` date DEFAULT NULL,
  `watt` int(7) DEFAULT NULL,
  `prod_max_data` date DEFAULT NULL,
  `prod_max` int(7) DEFAULT NULL,  
  `watt_max5_data` date DEFAULT NULL,
  `watt_max5` int(7) DEFAULT NULL,
  `watt_max_data` date DEFAULT NULL,
  `watt_max` int(7) DEFAULT NULL,
  `totale` bigint(20) unsigned DEFAULT NULL,
  PRIMARY KEY (`id_mm`)
);'''
print sql
cursore.execute(sql)
sql = '''CREATE TABLE IF NOT EXISTS `fotov_ii` (
  `id_ist` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `giorno` date DEFAULT NULL,
  `ora` time DEFAULT NULL,
  `watt` int(7) DEFAULT NULL,
  `watt_max` int(7) DEFAULT NULL,
  PRIMARY KEY (`id_ist`)
);'''
print sql
cursore.execute(sql)
sql = '''CREATE TABLE IF NOT EXISTS `scambio` (
  `id_pot` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `giorno` date DEFAULT NULL,
  `ora` time DEFAULT NULL,
  `watt` int(5) DEFAULT NULL,
  `maxi` int(6) DEFAULT NULL,
  PRIMARY KEY (`id_pot`)
);'''
print sql
cursore.execute(sql)
sql = '''CREATE TABLE IF NOT EXISTS `scambio_gg` (
  `id_gio` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `giorno` date DEFAULT NULL,
  `watt` int(7) DEFAULT NULL,
  `max5` int(7) DEFAULT NULL,
  `max5_time` time DEFAULT NULL,  
  `maxi` int(7) DEFAULT NULL,  
  `inizio` time DEFAULT NULL,
  `fine` time DEFAULT NULL,
  PRIMARY KEY (`id_gio`)
);'''
print sql
cursore.execute(sql)
sql = '''CREATE TABLE IF NOT EXISTS `scambio_mm` (
  `id_mm` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `giorno` date DEFAULT NULL,
  `watt` int(7) DEFAULT NULL,
  `prod_max_data` date DEFAULT NULL,
  `prod_max` int(7) DEFAULT NULL,  
  `watt_max5_data` date DEFAULT NULL,
  `watt_max5` int(7) DEFAULT NULL,
  `watt_max_data` date DEFAULT NULL,
  `watt_max` int(7) DEFAULT NULL,
  `totale` bigint(20) unsigned DEFAULT NULL,
  PRIMARY KEY (`id_mm`)
);'''
print sql
cursore.execute(sql)
sql = '''CREATE TABLE IF NOT EXISTS `scambio_ii` (
  `id_ist` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `giorno` date DEFAULT NULL,
  `ora` time DEFAULT NULL,
  `watt` int(7) DEFAULT NULL,
  `watt_max` int(7) DEFAULT NULL,
  `wattProd` int(6) DEFAULT NULL,
  `wattCons` int(6) DEFAULT NULL,
  PRIMARY KEY (`id_ist`)
);'''
print sql
cursore.execute(sql)
sql = '''CREATE TABLE IF NOT EXISTS `devices` (
  `device` varchar(20),
  `adr` int(3) DEFAULT NULL,
  `net` int(3) DEFAULT NULL,
  `pwd` int(3) DEFAULT NULL,
  `config` int(3) DEFAULT NULL,
  `config1` int(6) DEFAULT NULL,
  `config2` int(6) DEFAULT NULL,
  `config3` int(6) DEFAULT NULL,
  `config4` int(6) DEFAULT NULL,
  `strconf` varchar(10) DEFAULT NULL,
  `file` varchar(20)
);'''
print sql
cursore.execute(sql)
sql = "SELECT * FROM devices WHERE adr = %d;" %(io)
cursore.execute(sql)
results = cursore.fetchone()
#print results
if results:
   print " DISPOSITIVO NON CONFIGURATO !!!!!"
   print "Indirizzo gia' usato"
else:
   sql = "INSERT INTO devices(device,adr,net,pwd) values ('io', %d, %d, %d);" % (io, net, pwd)
   print sql
   cursore.execute(sql)
sql = "SELECT * FROM devices WHERE adr = %d;" %(2)
cursore.execute(sql)
results = cursore.fetchone()
#print results
if results:
   print " DISPOSITIVO NON CONFIGURATO !!!!!"
   print "Indirizzo gia' usato"
else:
   sql = "INSERT INTO devices(device,adr,net,pwd,config,config1,config2,strconf) values ('fotov', %d, %d, %d, %d, %d, %d, 'SGI');" % (2, net, pwd, 2,0,0) #2 è fotov, 2 è cripta messaggi
   print sql
   cursore.execute(sql)

sql = "SELECT * FROM devices WHERE adr = %d;" %(3)
cursore.execute(sql)
results = cursore.fetchone()
#print results
if results:
   print " DISPOSITIVO NON CONFIGURATO !!!!!"
   print "Indirizzo gia' usato"
else:
   sql = "INSERT INTO devices(device,adr,net,pwd,config,config1,config2,strconf) values ('scambio', %d, %d, %d, %d, %d, %d, 'SGI');" % (3, net, pwd, 7, alert, Salert) # 3 è scambio, 7 scambio(TA)+ cripta messaggi + alert 
   print sql
   cursore.execute(sql) 
db.commit()
db.close()
print "Configurazione archivi terminata"
