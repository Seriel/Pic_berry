#!/usr/bin/env python
# -*- coding: cp1252 -*-
"""
struttura risposte:
0     1  2    3   4  5
c1 , d1, d2, d3, d4, c2

6f = o
52 72 R r
41 61 A a   
"""

import MySQLdb

import os 
import random #, time

from datetime import datetime, date, time, timedelta

from dateutil.relativedelta import relativedelta
from math import floor
from shutil import copyfile  #for copying files

import PeB
try:
    import RPi.GPIO as GPIO
except:
    print "No root privileges.\nSkipping RPi.GPIO import"


try:
    from Pic_Berry_C import *
except:
    print "File di configurazione mancante"
    




MyID = []  # definire global dove la voglio usare !!!


def initRadio():
    PeB.spiInit()
    PeB.rfmInit()
    return

def checkRX(timeout,deviceAtteso=255): # controlla che chi invia messaggio sia effettivamente chi era stato chiamato !!!
    global MyID
    PeB.rfmEn()
    strRep=PeB.rfmRX(timeout,*MyID)
    if deviceAtteso == 255:           # usato per chiamata da dispositivi, dove non viene impostato deviceAtteso da chiamata 
        return strRep        
    if (strRep != None and strRep[6] != deviceAtteso):
        print "risponditore:"+ str(strRep[6])+" atteso da:"+ str(deviceAtteso) # test togliere
        return None    
    return strRep

def istantRX(device):  #device solo numero device
    pack = ["I",0,0,0,0,0,device]
    PeB.rfmTX(*(pack+MyID))
    strRep = checkRX(True)
    return strRep

def confPic(device,deviceOld): # device tutti i numeri ID e conf, device old solo indirizzo vecchio 
   
    pack = ["C"] + device[1:5] +[0,deviceOld,MyID[0],MyID[1],MyID[2]]   
    print pack
    PeB.rfmTX(*(pack))
    strRep = checkRX(True,device[1])
    return strRep

def confPicW(device): # invio config, alertSet, AlertRet, 0,0
    print device
   
    pack = ["D"] + device[4:7] +[0,0,device[1],MyID[0],MyID[1],MyID[2]]   
    print pack
    PeB.rfmTX(*(pack))
    strRep = checkRX(True,device[1])
    return strRep

def sincPic(device): # ritorna la differenza di ora 
    for i in range(10):
        data = datetime.now()
        giorno = int(data.strftime("%j"))
        ora = data.hour
        minuti = data.minute
        secondi = data.second   
        pack = ["S", giorno, ora, minuti,secondi,0,device[1],MyID[0],MyID[1],MyID[2]] 
        print pack
    
        PeB.rfmTX(*(pack))
        strRep = checkRX(True,device[1])
        print strRep
        if strRep != None and strRep[0]=="s" and strRep[1]== giorno and strRep[2]== ora  and strRep[3]==minuti and strRep[4]== secondi and (-3 < strRep[5] < 3): # risponde con giorno, minuti, secondi giusti e deltasec !!!attenzione nuovi pic rispondono solo in positivo !!!
            break
    return strRep



def ReqPic1(device): # richiesta watt successivi
    pack = ["A", 0, 0, 0, 0, 0,device]
    for i in range(10):
        PeB.rfmTX(*(pack+MyID))
        strRep = checkRX(True)
        if strRep != None:
            break
    return strRep
def ReqPicS(device): # stop invio 1 solo richiesta watt successivi
    pack = ["O", 0, 0, 0, 0, 0,device]
    #for i in range(5):
    PeB.rfmTX(*(pack+MyID))
    #strRep = checkRX(True) 
        #if strRep != None:
        #   break
    return 

   

'''   
   Main
'''



db = MySQLdb.connect(host="localhost",user="root",passwd=passMy, db="pic_berry")
cursore = db.cursor()
sql = "SELECT * FROM devices;" 
try:   
    cursore.execute(sql)
    devices = list(cursore.fetchall()) #attenzione è diventata una lista di tuple
    if (devices[0][0] == 'io'):
        MyID= list(devices[0][1:4]) #mi serve lista perchè tuple non le concateno
        print MyID
except:
    print "Error: unable to fecth data"


initRadio()

#print istantRX(2)
#dev1= list(devices[1])
#dev2= list(devices[2])
req = "nulla"
print "\n"
while True:
    for i in devices:
        print i
    azione = input( "\nCosa vuoi fare ? (CTRL+c per uscire) \n 0-> modificare impostazioni database, 1-> inviare configurazione al modulo:")
    if not azione:
        dToC = input(" device da configurare (io = 1):")
        dToC = dToC - 1
        devToConf = list(devices[dToC])
        print "\nSTAI MODIFICANDO IL RECORD: !!!"
        print devToConf           
        devMod0 = raw_input( "\ndevice: " + devToConf[0] +" diventa: ") or devToConf[0]          
        devMod1 = int(raw_input( "\nadr: " + str(devToConf[1]) +" diventa: ") or devToConf[1])    
        devMod2 = int(raw_input( "\nnet: " + str(devToConf[2])+" diventa: ") or devToConf[2])    
        devMod3 = int(raw_input( "\npwd: " + str(devToConf[3])+" diventa: ")  or devToConf[3])  
        devMod4 = int(raw_input( "\nconfig: " + str(devToConf[4]) +" diventa: ")  or devToConf[4])    
        devMod5 = int(raw_input( "\nconfig1: " + str(devToConf[5]) +" diventa: ") or devToConf[5])    
        devMod6 = int(raw_input( "\nconfig2: " + str(devToConf[6]) +" diventa: ")  or devToConf[6])    
        #devMod7 = int(raw_input( "\nconfig3: " + str(devToConf[7]) +" diventa: ") or devToConf[7])    
        #devMod8 = int(raw_input( "\nconfig4: " + str(devToConf[8]) +" diventa: ") or devToConf[8])    
        devMod9 = raw_input( "\nstrconf: " + devToConf[9] +" diventa: ") or devToConf[9]
        print "\n"
        sql = "UPDATE devices SET device = '%s', adr = %d, net = %d, pwd = %d, config =%d, config1 = %d, config2= %d, strconf='%s' WHERE adr = '%s';" % (devMod0,devMod1,devMod2,devMod3,devMod4,devMod5,devMod6,devMod9, devToConf[1])
        #print sql
        #sql = "INSERT INTO devices(device,adr,net,pwd) values ('io', %d, %d, %d)" % (io, net, pwd)
        cursore.execute(sql)
        db.commit()
        sql = "SELECT * FROM devices;"
        cursore.execute(sql)
        devices = list(cursore.fetchall())
    elif azione:               
        dToC = input(" device da configurare (io = 1):")
        dToC = dToC - 1
        devToConf = list(devices[dToC]) 
        a = raw_input(" scegli cosa fare c(cambia indirizzo,d(invia configurazioni),x(esci):")
        if (a == 'c'):
            i= input ("dammi il vecchio indirizzo per " +str(devToConf)+":")
            #old = dev1[1]
            #sql = "REPALCE INTO devices
            req = confPic(devToConf,i)
        elif (a == 'd'):      
            req = confPicW(devToConf)
        elif (a == 'x'):
            break
        else:
            GPIO.remove_event_detect(15)
            enEvent = False
        print req 


db.close()



