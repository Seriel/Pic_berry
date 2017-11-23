#!/usr/bin/env python
# -*- coding: cp1252 -*-
"""
da fare : togliere trace o ridurre
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
import SocketServer             # per sockey python
import threading #Thread,Event,Lock   #per threadPHP

from datetime import datetime, date, time, timedelta
from time import sleep
from dateutil.relativedelta import relativedelta
from math import floor
from shutil import copyfile  #for copying files

import smtplib                       #per e-mail (vedere se devo installare anche 
from email.mime.text import MIMEText #cancellare mime che fa casini #su linux smtp server o non serve

import PeB
try:
    import RPi.GPIO as GPIO
except:
    print "No root privileges.\nSkipping RPi.GPIO import"
try:
    mqttEn = False
    from Pic_Berry_C import *
except:
    print "File di configurazione mancante"
try:
    mqttConnect = False 
    import paho.mqtt.client as mqtt
except:
    print "mqtt mancante"

MyID = []  # inizializzato cosi non da errore su thread definire global dove la voglio usare !!!
devices = [] # usare global dove la voglio usare !!!
GPIO.setmode(GPIO.BOARD)
GPIO.setup(15, GPIO.IN) # ingresso interrupt rfm12b
#enEvent = False
GPIOLock= threading.Lock()
logLock= threading.Lock()
# EventLock= threading.Lock()  # mettere il lock agli eventi dappertutto se non trovo niente di meglio 

def on_connect_mqtt(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe("$SYS/#")
    mqttclient.subscribe("pic_berry/istantaneo/on/set")
    print "REGISTRATO COME: istantaneo/on/set"
    for d in devices:
        if d[9] != None and d[9].find('C') != -1:
            
            mqttclient.subscribe("pic_berry/"+d[0]+"/on/set")
            print "REGISTRATO COME: " + "pic_berry/"+d[0]+"/on/set"

    
def on_message_mqtt(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    if disInt("Disabilita interrupt","da mqtt"):
        try:
            if msg.topic[10:-7] == "istantaneo":  # risponde a qualsiasi cosa !!!
                risposta = istantaneo()
                valori = risposta.split()
                print valori
                PV = int(valori[0])                
                SC = int(valori[4])
                PV_TA = int(valori[6])
                CO_TA = int(valori[7])
                
                if (PV_TA > CO_TA):
                    consumo = PV - SC
                else:
                    consumo = PV + SC
                risposta = risposta + str(consumo)                 
                mqttclient.publish("pic_berry/istantaneo/on", payload= risposta , qos=0, retain=False)
            else:
                risposta = inviaComando(msg.payload,msg.topic[10:-7])
        except IndexError:
            print "Comando mqtt errato"
            risposta = " 0 0 0 0 0 0 0 0 "
    else:
        trace("NON RIESCO A DISABILITARE INTERRUPT", " da mqtt")
        risposta = " 0 0 0 0 0 0 0 0 "
    
    enInt("abilita interrupt","da mqtt")
    return    







class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        global enEvent
        global devices
        #print devices
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print "{} wrote:".format(self.client_address[0])        
        print self.data
        #sleep(.5)
        richiesta = self.data.split()
        print richiesta  
        if disInt("Disabilita interrupt","da websocket"):                    
            try:
                if richiesta[0] == "aggiorna":
                    for d in devices:
                        if d[9] != None and d[9].find('G') != -1:
                            risposta = str(reqData(d))
                            sleep(.1)
                elif richiesta[0] == "istantaneo":
                    """
                    for i in devices:
                        if i[0] != 'io':
                            print istantRX(i)
                            sleep(1)
                    print richiesta
                    """
                    risposta = istantaneo()
                elif richiesta[0]== "accendi" or richiesta[0] == "spegni":                
                                   
                    risposta = inviaComando(richiesta[0],richiesta[1]) # richiesta 1 è il nome del device !!!
                    
                elif richiesta[0]== "stato":
                    risposta = leggiStato(richiesta[0], richiesta[1])
                else:
                    print "comando errato"
                    risposta = " Non ho capito"
                    #risposta= risposta.ljust(40)
            except IndexError:
                print "Arrivata richiesta nulla"
                risposta = " 0 0 0 0 0 0 0 0 "
            
        else:
            trace("NON RIESCO A DISABILITARE INTERRUPT", " da handle")
            risposta = " 0 0 0 0 0 0 0 0 "
            risposta= risposta.ljust(40)
            self.request.sendall(risposta)
            return            
        risposta= risposta.ljust(40)
            
            #print reqData(dev1) #aggiornare tutti non solo dev1
        enInt("abilita interrupt","da websocket")
            
            #PeB.rfmEn()    # ripristino la ricezione 2016 altrimenti non riceve più
            #GPIO.add_event_detect(15, GPIO.FALLING, callback=leggiReq, bouncetime=1)# 2016
            #enEvent = True
            #GPIOLock.release()        


            # just send back the same data, but upper-cased
            #self.request.sendall(self.data.upper())
            #print "Riaccendo interrupt"
        self.request.sendall(risposta)
        return

def enInt(subject="Abilita interrupt",text=":)"):
    global enEvent
    timeout = 0
    while (enEvent and timeout < 200):
        timeout = timeout + 1
        sleep(.1)
    if timeout >= 200:
        trace("NON POSSO ATTIVARE INTERRUPT",text)
        return False
    try:
        enEvent = False
        GPIOLock.acquire() #forse devo toglierlo perchè il lock ce lo ho già da interrupt disabilitato
        # sleep(.1) #tolto 11/01/17
        '''
        timeout = 0
        while (PeB.rfmTi() and timeout < 10):
            timeout = timeout + 1
            PeB.rfmWr(0x0000)
            PeB.rfmWr(0xB000)
            
            trace("PULISCO INTERRUPT", text)
            sleep(.1)
        #sleep(.1) #tolto 11/01/17
        '''
        PeB.rfmEn()
        #enEvent = True
        GPIO.add_event_detect(15, GPIO.FALLING, callback=leggiReq, bouncetime=1)# attenzione aggiungere solo se non c'è (legge solo le discese e non lo stato se era gia basso)
        enEvent = True
        
        trace("interrupt acceso",text)
    except RuntimeError:
        
        trace(subject,text)#se in log non trovo mai questo eliminare il try-except
        enEvent = False
    GPIOLock.release()
    return True

def disInt(subject="Disabilita interrupt",text=":)"):
    global enEvent
    timeout = 0
    while ((not enEvent) and timeout < 200):
        timeout = timeout + 1
        print timeout, enEvent, "dentro disInt"
        sleep(.1)
    if timeout >= 200:
        trace("NON POSSO DISATTIVARE INTERRUPT",text)
        return False
    try:
        enEvent = False
        sleep(.1) # attendo che esca da leggiReq1 se era dentro
        GPIOLock.acquire()
        # sleep(.2) #tolto 11/01/17
        GPIO.remove_event_detect(15)
        sleep(.2) # deve essere almeno .2 altrimenti da errore sulla prima letture da aggiornamento PIC
        
        trace("interrupt spento", text)
    except RuntimeError:
       
        trace("ERRORE DISABILITANDO INTERRUPT",text)   
    GPIOLock.release()
    return True  

 
def sendMail1(subject="ALERT da PiC & Berry",text=":)",text1="?"): #da cancellare MIMEText fa casini
    global MyMail
    global ToMail
    global MyMailPW
    message = '%s\n\n%s' % (text, text1)
    m = MIMEText(message)

    m['Subject'] = subject
    m['From'] = MyMail
    m['To'] = ToMail
    # print m
    mail = smtplib.SMTP('smtp.gmail.com',587)
    mail.ehlo()
    mail.starttls()
    mail.login(MyMail,MyMailPW)
    mail.sendmail(MyMail,ToMail, m.as_string())
    mail.close()
    return

def sendMail(subject="ALERT da PiC & Berry",text=":)",text1="?",text2="?"): # aggiungere modifica per mqtt che azzera al rientro del alert
    global MyMail
    global ToMail
    global MyMailPW
    testo = text+text1
    
    m= '\r\n'.join(['To: %s' % ToMail,
                    'From: %s' % MyMail,
                    'Subject: %s' % subject,
                    '',testo])
    #mail = smtplib.SMTP('smtp.gmail.com',587)
    #mail.ehlo()
    #mail.starttls()
    #mail.login(MyMail,MyMailPW)
 
    try:
        if (mqttEn and mqttConnect):
            if (text2 != "?"):
                mqttclient.publish("pic_berry/alert", payload= text2, qos=0, retain=False)
            else:
                mqttclient.publish("pic_berry/alert", payload= text1, qos=0, retain=False)
    except:
        print 'Problemi con Mqtt.'
    try:
        mail = smtplib.SMTP('smtp.gmail.com',587)
        mail.ehlo()
        mail.starttls()
        mail.login(MyMail,MyMailPW)        
        mail.sendmail(MyMail,ToMail, m)
        mail.close()        
    except:
        print 'Mail NON inviata...\nServer mail non disponibile.'
    #mail.close()
    return



def serverPHP():
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()    
    return

def WaitCall():
    #global MyID
    #print MyID
    #while True:
    #    strRep=PeB.rfmRX(False,*MyID)
    PeB.rfmEn()
    strRep=PeB.rfmRX(False,*MyID)
    print strRep 
    #try:
    #    server.serve_forever()
    #except KeyboardInterrupt:
    #    server.shutdown()    
    return strRep

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

def istantaneo():
    stringaI = ""
    for nd in range (1,3):
        if devices[nd][9] != None and devices[nd][9].find('I') != -1:
            for i in range(10):
                strRep = istantRX(devices[nd])
                if strRep != None and strRep[0]== 'i': # risponde con giorno, minuti, secondi giusti
                    stringaI = stringaI+" "+str(strRep[1])+" "+str(strRep[2])+" "+str(strRep[3])+" "+str(strRep[4])
                    break
                if i == 9:
                    stringaI = stringaI+" 0 "+" 0 "+" 0 "+" 0 "                
            sleep(.1)
        else:
            stringaI = stringaI+" 0 "+" 0 "+" 0 "+" 0 "
            print devices[nd]

    print stringaI              
    
    return stringaI.ljust(40)

def inviaComando(richiesta, ndev):    #ndev è il nome del device
    for nd in devices:
        #print nd
        if nd[0] == ndev and nd[9].find('C') != -1:
            print "trovata !!!"            
            if (richiesta == "accendi" or richiesta == "true"):
                comando = "G"
            elif (richiesta == "spegni" or richiesta == "false"):
                comando = "N"
            elif (richiesta == "state"):
                stato = nd[10]
                if stato == "g":
                    payl= "true"
                else:
                    payl= "false"
                if (mqttEn and mqttConnect):                
                    mqttclient.publish("pic_berry/"+nd[0]+"/on", payload= payl, qos=0, retain=False)
                return                  
            else:
                comando = "Q" 
            #elif (richiesta == "init"): # questo poi lo cancello !!!
            #    comando = "Q"stainit
            
            for i in range(10):
                #print nd
                #print devices
                #print devices[nd]
                strRep = comandoTX(nd,comando)
                if (strRep != None and (strRep[0] == chr(ord(comando)+32) or strRep[0] == 'k')): # risponde carattere minuscolo
                    stringaRisp = str(strRep[0])+" "+str(strRep[1])+" "+str(strRep[2])+" "+str(strRep[3])+" "+str(strRep[4])
                    salvaStato(strRep)
                    break
                if i == 9:
                    stringaRisp = "0 "+" 0 "+" 0 "+" 0 "                
                    break
                sleep(.1)
        else:
            stringaRisp = "0 "+" 0 "+" 0 "+" 0 "     
            
    print stringaRisp             
    return stringaRisp.ljust(40)

def salvaStato(risp):    # risp è la stringa arrivata da pic
    global devices
    print risp
    for d in devices:
        if (mqttEn and mqttConnect and d[1] == risp[6]):
            if (risp[1]==1 and risp[2]==1): # and risp[3]==1) and risp[4]==1): 3 = stato rele - 4 = Valore TA
                mqttclient.publish("pic_berry/"+d[0]+"/on", payload= "true", qos=0, retain=False)
            else:
                mqttclient.publish("pic_berry/"+d[0]+"/on", payload= "false", qos=0, retain=False)
                
    db = MySQLdb.connect(host="localhost",user="root",passwd=passMy, db="pic_berry")
    cursore = db.cursor()
    if (risp[1]==1 and risp[2]==1): # risp[0] == "g" or risp[0] == "n":
        sql = "UPDATE devices SET stato = '%s' WHERE adr = '%s';" % ('g', risp[6])
    else:
        sql = "UPDATE devices SET stato = '%s' WHERE adr = %s;" % ('n', risp[6])
    '''   
    elif risp[0] == "k" or risp[0] == "q" :
        if (risp[1]==1 and risp[2]==1): #and risp[3]==1) and risp[4]==1:
            sql = "UPDATE devices SET stato = '%s' WHERE adr = %s;" % ('g', risp[6])
        else:
            sql = "UPDATE devices SET stato = '%s' WHERE adr = %s;" % ('n', risp[6])            
    '''
    print sql

    cursore.execute(sql)
    db.commit()            
    db.close()
    loadDevices()
    return

def leggiStato(richiesta, ndev):     # valido solo per chiamate html
    for nd in devices:
       if nd[0] == ndev and nd[9].find('C') != -1:
           stato = nd[10]
           break
       else:
           stato = "X"
    if stato == "g":
        #stato = "ON"
        stato = stato + " 1 1 1 1"
    else:
        stato = stato + " 0 0 0 0"
        #stato = "OFF"
    return stato


def istantRX(device):  #device solo numero device
    pack = ["I",0,0,0,0,0,device[1],MyID[0],MyID[1],MyID[2]]
    PeB.rfmTX(*(pack))
    strRep = checkRX(True,device[1])
    return strRep

def comandoTX(device,comando):  #device solo numero device
    pack = [comando,0,0,0,0,0,device[1],MyID[0],MyID[1],MyID[2]]
    PeB.rfmTX(*(pack))
    strRep = checkRX(True,device[1])
    return strRep



def confPic(device,deviceOld): # device tutti i numeri ID e conf, device old solo indirizzo vecchio 
    pack = ["C"] + device[1:5] +[0,deviceOld,MyID[0],MyID[1],MyID[2]]   
    PeB.rfmTX(*(pack))
    strRep = checkRX(True,device[1])
    return strRep

def confPicW(device): # invio config, alertSet, AlertRet, 0,0 
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
        pack = ["S",giorno,ora,minuti,secondi,0,device[1],MyID[0],MyID[1],MyID[2]] 
        print pack
        #PeB.rfmTX(giorno,ora,minuti,secondi,0,device[1],MyID[0],MyID[1],MyID[2])
        PeB.rfmTX(*(pack))
        strRep = checkRX(True,device[1])
        print strRep
        if strRep != None and strRep[0]=="s" and strRep[1]== giorno and strRep[2]== ora  and strRep[3]==minuti and strRep[4]== secondi and (-3 < strRep[5] < 3): # risponde con giorno, minuti, secondi giusti e deltasec !!!attenzione nuovi pic rispondono solo in positivo !!!
            break
    return strRep

def ReqPic(device): # richiesta watt
    pack = ["R", 0, 0, 0, 0, 0,device[1],MyID[0],MyID[1],MyID[2]]
    for i in range(10):
        PeB.rfmTX(*(pack))
        strRep = checkRX(True,device[1])
        if strRep != None:
            break
    return strRep

def ReqPic1(device,waRic): # richiesta watt successivi
    pack = ["A", 0, 0, 0, 0, waRic,device[1],MyID[0],MyID[1],MyID[2]]
    for i in range(10):
        PeB.rfmTX(*(pack))
        strRep = checkRX(True,device[1])
        if strRep != None:
           break
    return strRep

def ReqPicS(device): # invio 1 per risponrere alla 'o' e poi fino a che non mi risponde con la 'i', così sono sicuro che è uscito dall'invio dei watt
    pack = ["O", 0, 0, 0, 0, 0,device[1],MyID[0],MyID[1],MyID[2]]
    for i in range(10):
        PeB.rfmTX(*(pack))
        strRep = checkRX(True,device[1])  
        if strRep != None and strRep[0]=='i':
           break
    return strRep

def reqData(dev):
    trace("Agg.",str(dev[0]))  #registro log collegamenti 
    esito = False 
    db = MySQLdb.connect(host="localhost",user="root",passwd=passMy, db="pic_berry")
    cursore = db.cursor()
    watt = ReqPic(dev)
    wacount = 0
    if watt != None:
        data= datetime.now()
        if watt[0] == 'r' and watt[5]< 3: # vedere valore di c2 per inserire in database !!!!!!
            try:
                giorno = datetime(data.year, 1, 1,watt[2]/60,watt[2]%60) + timedelta(watt[1] - 1)  # vedere cosa succede fine anno , meglio fare un controllo prima di inserire
                print giorno
            except ValueError:
                trace("ricevuto data errata",str(dev[0]))               
                db.close()
                return esito        
            if giorno > data:
                giorno = giorno.replace(year= giorno.year -1) #tolgo 1 anno (sono all'inizio dell'anno !!!)
            for i in range(0,wacount+watt[5]):                                                                 
                sql = "insert into %s(giorno, ora, watt) values ('%s','%s', %d );" % (dev[0],giorno.strftime('%Y-%m-%d'),giorno.strftime('%H:%M:%S'), watt[3+i])
                cursore.execute(sql)
                giorno = giorno + timedelta(minutes =+5)
            wacount = wacount+watt[5]
            count= 0  # contatore per avere massimo 10 ERRORI prima di uscire
            while True:
                watt = ReqPic1(dev,wacount)
                if watt != None :              # fa la short evaluetion Python si !!
                    if (watt[0]== 'a' and wacount<watt[5]<(wacount+5)):    
                        for i in range(0,watt[5]-wacount):
                            sql = "insert into %s(giorno, ora, watt) values ('%s','%s', %d );" % (dev[0],giorno.strftime('%Y-%m-%d'),giorno.strftime('%H:%M:%S'), watt[1+i])
                            #print sql
                            cursore.execute(sql)
                            giorno = giorno + timedelta(minutes =+5)                            
                        wacount = watt[5]  #incremento per controllare che non sia lo stesso invio
                           
                        count = 0
                    elif watt[0] == 'o':               
                        count = 11         
                count = count + 1
                if count >=10:
                    break
            if count == 10: # ha sbagliato dieci volte consecutive, cancello entries fatte
                    sql = "SELECT MAX(id_pot) FROM %s;" % (dev[0])
                    cursore.execute(sql)
                    lastEntry = cursore.fetchone()
                    toDel = lastEntry[0]-wacount
                    #print toDel
                    sql = "DELETE FROM %s WHERE id_pot > %d;" % (dev[0], toDel)
                    cursore.execute(sql)
                
        db.commit()
        if watt != None and watt[0] =='o':
            if watt[5] > 0:  # e solo watt del giorno, confrontare con campo già inserito e se sup aggiornare
                sql = "SELECT id_pot, maxi FROM %s WHERE id_pot = (SELECT MAX(id_pot) FROM %s);" % (dev[0],dev[0]) 
                #sql = "SELECT MAX(id_pot), giorno, maxi FROM %s;" % (dev[0])
                cursore.execute(sql)
                potRec = list(cursore.fetchone())
                if watt[3] > potRec[1]:  # non mi interesso del giorno ?                      
                    sql = "update %s SET maxi= %d WHERE id_pot= %d ;" % (dev[0],watt[3],potRec[0])
                    cursore.execute(sql)
            ReqPicS(dev)
            
            esito = True 
        db.commit() 
    db.close()
    return esito

def leggiReq(bit):
    """  Qui leggo le richieste dai dispositivi
    """
    global enEvent
    global enEmail
    if not enEvent:
        trace("NON DOVEVO LEGGERE !!!! ESCO IMMEDIATAMENTE")
        return
    #timeout = 0
    #while ((not enEvent) or timeout > 200):
    #    timeout = timeout + 1
    #    print timeout, enEvent, "dentro leggiReq"
    #    sleep(.1)
    #if timeout > 200:
        
    #    trace("Dentro leggiReq","Lettura richiesta")
    #    return False
    enEvent = False
    GPIOLock.acquire()
    
   

    
    #disInt("disabilito interrupt", "Leggo richieste da dispositivo") # ATTENZIONE non posso disabilitare l'evento da dentro l'evento
    
    strRep = checkRX(True)
    trace("arrivato interrupt ",str(strRep))# dopo togliere per non riempire il log e metterlo dentro if qui sotto
    
    
    #sleep(.5)
    #se mi blocco qui, incasino il PIC ATTENZIONE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    if strRep !=None and strRep[0] == 'b':
        pack = ["B",0,0,0,0,0,strRep[6],MyID[0],MyID[1],MyID[2]]
        PeB.rfmTX(*(pack))
        trace("LeggiReq",str(strRep))        
        if enEmail == True:
            sendMail("ALERT da PiC & Berry","RISCHIO DISTACCO CORRENTE \nPotenza watt:",str(strRep[1]))
    elif strRep !=None and strRep[0] == 'f':
        pack = ["F",0,0,0,0,0,strRep[6],MyID[0],MyID[1],MyID[2]]
        PeB.rfmTX(*(pack))
        trace("LeggiReq",str(strRep))        
        if enEmail == True:
            sendMail("ALERT da PiC & Berry","RIENTRATO IN VALORI ACCETTABILI \nPotenza watt:",str(strRep[1]),"0")
        
    elif strRep !=None and strRep[0] == 'e':
        try:
            chiamante = devices[strRep[6]-1]
        except:            
            trace("Chaimante non valido, strRep:",str(strRep))
            PeB.rfmEn()
            GPIOLock.release()
            print 'esco da interrupt, abilita di nuovo evento'
            enEvent = True
            return
        
        sincPic(chiamante)        
        if chiamante[9] != None and chiamante[9].find('C') != -1:            
            statoIniziale(chiamante)           
        #pack = ["B",0,0,0,0,0,strRep[6],MyID[0],MyID[1],MyID[2]]
        #PeB.rfmTX(*(pack))
        trace("LeggiReq1",str(strRep))
       
    elif strRep !=None and strRep[0] == 'k':
        pack = ["K",0,0,0,0,0,strRep[6],MyID[0],MyID[1],MyID[2]]
        PeB.rfmTX(*(pack))
        salvaStato(strRep)
        trace("LeggiReq1",str(strRep))
    PeB.rfmEn()
    GPIOLock.release()
    

    #sleep(5) # tolto 20 ottobre
    
    #GPIO.add_event_detect(15, GPIO.FALLING, callback=leggiReq, bouncetime=1)# attenzione aggiungere solo se non c'è
    #enEvent = True           
    print 'esco da interrupt, abilita di nuovo evento'
    enEvent = True
    return

def update(dev):   
   dev_gg = dev+"_gg"
   
   db = MySQLdb.connect(host="localhost", user="root", passwd= passMy, db="pic_berry")
   cursore = db.cursor()
   MySql= "SELECT MAX(giorno) FROM %s;" %(dev_gg)
   cursore.execute(MySql)   
   risp = cursore.fetchone()
   print risp
   if risp[0] == None:
      MySql= "SELECT MIN(giorno) FROM %s;" % (dev)
      cursore.execute(MySql)
      risp = cursore.fetchone()
      if risp[0] == None:          
         db.close()
         return
      giornoReg = risp[0]
   else:
      giornoReg = risp[0]+ relativedelta(days=1)
   print risp
   oggi = datetime.now()

   while (giornoReg < oggi.date()):
      MySql= "SELECT SUM(watt) FROM %s WHERE giorno='%s';" %(dev,giornoReg)
      cursore.execute(MySql)
      risp = cursore.fetchone()
      if risp[0] == None: 
         watt = 0
      else:
         watt = risp[0]     
      MySql= "SELECT maxi FROM %s WHERE maxi =(SELECT MAX( maxi )FROM %s WHERE giorno = '%s') AND giorno = '%s';" % (dev,dev, giornoReg,giornoReg) 
      cursore.execute(MySql)
      risp = cursore.fetchone()
      if risp == None:
         massimo = 0
      else:
         massimo = risp[0]
      MySql= "SELECT ora, watt FROM %s WHERE watt=(SELECT MAX( watt )FROM %s WHERE giorno = '%s') AND giorno = '%s';" % (dev, dev, giornoReg,giornoReg) 
      cursore.execute(MySql)
      risp = cursore.fetchone()
      if risp == None:   ## perche senza [0] ??
         ora_massimo5 ='00:00:00'
         watt5M = 0
      else:
         ora_massimo5 = risp[0]
         watt5M = risp[1]
      MySql= "SELECT MIN( ora )FROM %s WHERE (giorno = '%s' AND watt <> 0) ;" % (dev,giornoReg) 
      cursore.execute(MySql)
      risp = cursore.fetchone()
      if risp == None:
         inizio ='00:00:00'
      else:
         inizio = risp[0]        
      MySql= "SELECT MAX( ora )FROM %s WHERE (giorno = '%s' AND watt <> 0) ;" % (dev,giornoReg) 
      cursore.execute(MySql)
      risp = cursore.fetchone()
      if risp == None:
         fine ='00:00:00'
      else:
         fine = risp[0]          
      MySql= "INSERT INTO %s (giorno, watt, maxi, max5, max5_time, inizio, fine ) values ('%s', %d, %d, %d, '%s', '%s', '%s');" %(dev_gg, giornoReg, watt, massimo, watt5M, ora_massimo5, inizio, fine)
      MySql= "INSERT INTO %s (giorno, watt, maxi, max5, max5_time, inizio, fine ) values ('%s', %d, %d, %d, '%s', '%s', '%s');" %(dev_gg, giornoReg, watt, massimo, watt5M, ora_massimo5, inizio, fine)
      
      print MySql
      print type(dev_gg)
      print type(giornoReg)
      print type(watt)  #questo è errato
      print type(massimo)
      print type(watt5M)
      print type(ora_massimo5)
      print type(inizio)
      print type(fine) #oReg, watt, massimo, watt5M, ora_massimo5, inizio, fine
     
    
      cursore.execute(MySql)
      giornoReg = giornoReg+ relativedelta(days=1)   

   db.commit()
   db.close()
   return

def update_m(dev):
   #dev = "fotov"  #rimuovere questa riga !!!!!!!!!!!!!
   dev_gg = dev+"_gg"
   dev_mm = dev+"_mm"
   db = MySQLdb.connect(host="localhost", user="root", passwd= passMy, db="pic_berry")
   cursore = db.cursor()
   MySql = "SELECT giorno FROM %s WHERE id_mm =(SELECT MAX(id_mm) FROM %s);" %(dev_mm,dev_mm)

   cursore.execute(MySql)
   risp = cursore.fetchone()   
   if risp == None: #tolto[0]
      MySql= "SELECT giorno FROM %s WHERE id_gio = (SELECT MIN(id_gio) FROM %s);" %(dev_gg,dev_gg)
      cursore.execute(MySql)
      risp = cursore.fetchone()
      if risp == None:           
         db.close()
         return      
      giornoReg = risp[0]
      giornoReg = giornoReg.replace(day =1)
   else:
      giornoReg = risp[0]+ relativedelta(days=1)
   oggi = datetime.now()
   giornoLast = giornoReg + relativedelta(months=1)
   #print giornoReg, giornoLast
   while (giornoLast < oggi.date()):
      MySql= "SELECT SUM(watt) FROM %s WHERE giorno>='%s' and giorno < '%s';" %(dev_gg,giornoReg,giornoLast)
      cursore.execute(MySql)
      risp = cursore.fetchone() #sono qui !!!
      watt = risp[0]
      if watt == None:
         watt=0
      MySql= "SELECT giorno, watt FROM %s WHERE watt=(SELECT MAX( watt )FROM %s WHERE giorno>='%s' AND giorno < '%s') AND (giorno>='%s' AND giorno < '%s');" % (dev_gg,dev_gg,giornoReg,giornoLast,giornoReg,giornoLast) 
      cursore.execute(MySql)
      risp = cursore.fetchone()
      if risp == None:
         max_gg = 0;
         max_gg_D= datetime(giornoReg.year,giornoReg.month,giornoReg.day);
      else:
         max_gg_D = risp[0]
         max_gg =risp[1]
      MySql= "SELECT max5, giorno FROM %s WHERE max5=(SELECT MAX( max5 )FROM %s WHERE giorno>='%s' and giorno < '%s') AND (giorno>='%s' AND giorno < '%s');" % (dev_gg,dev_gg,giornoReg,giornoLast,giornoReg,giornoLast) 
      cursore.execute(MySql)
      risp = cursore.fetchone()
      if risp == None:
         max5 = 0;
         max5_D= datetime(giornoReg.year,giornoReg.month,giornoReg.day);
      else:
         max5 = risp[0]
         max5_D =risp[1]
      MySql= "SELECT maxi, giorno FROM %s WHERE maxi=(SELECT MAX( maxi )FROM %s WHERE giorno>='%s' and giorno < '%s') AND (giorno>='%s' AND giorno < '%s') ;" % (dev_gg,dev_gg,giornoReg,giornoLast,giornoReg,giornoLast) 
      cursore.execute(MySql)
      risp = cursore.fetchone()
      if risp == None:
         massimo = 0;
         max_D= datetime(giornoReg.year,giornoReg.month,giornoReg.day);
      else:
         massimo = risp[0]
         max_D =risp[1]
      MySql = "SELECT totale FROM %s WHERE id_mm =(SELECT MAX(id_mm) FROM %s);" %(dev_mm,dev_mm)
      cursore.execute(MySql)
      risp = cursore.fetchone()   
      if risp == None:
         totPrec = 0
      else:
         totPrec = risp[0]
      tot = totPrec + watt 
      

      dayToReg = str(giornoLast - relativedelta(days=1))
      MySql= "INSERT INTO %s (giorno, watt, prod_max_data, prod_max, watt_max_data, watt_max, watt_max5_data, watt_max5, totale ) values ('%s', %d, '%s', %d, '%s', %d, '%s', %d, %d);" %(dev_mm, dayToReg, watt, max_gg_D, max_gg, max_D, massimo, max5_D, max5, tot)
      print MySql
      cursore.execute(MySql)
      giornoLast = giornoLast + relativedelta(months=1)
      giornoReg = giornoReg+ relativedelta(months=1)   

   db.commit()
   db.close()
   return

def trace(funzione="vuota", esito="Vuoto"):
    logLock.acquire()
    log = open("log.txt","a")
    logTime = datetime.now()
    log.write(logTime.strftime('%Y-%m-%d %H:%M:%S')+":"+funzione+" ")  #registro log collegamenti
    log.write(esito)
    log.write("\n")
    log.close()
    logLock.release()
    print(logTime.strftime('%Y-%m-%d %H:%M:%S :')+funzione+" "+esito+"\n")
    return

def loadDevices():
    global devices
    db = MySQLdb.connect(host="localhost",user="root",passwd=passMy, db="pic_berry")
    cursore = db.cursor()
    sql = "SELECT * FROM devices;" 
    try:   
        cursore.execute(sql)
        devices = list(cursore.fetchall()) #attenzione è diventata una lista di tuple
        if (devices[0][0] == 'io'):
            MyID= list(devices[0][1:4]) #mi serve lista perchè tuple non le concateno
            #print MyID
    except:
        print "Error unable to fecth data"
    db.close()
    return

def statoIniziale(nd):
    for i in range(10):        
        #print nd
        #print devices
        #print devices[nd]
        comando = "Q"
        strRep = comandoTX(nd,comando)
        if (strRep != None and (strRep[0] == chr(ord(comando)+32))): # risponde carattere minuscolo
            salvaStato(strRep)
            break        
    return 



    
    
#def Main():

if __name__ == "__main__":
    #Main() # se sposto main in funzione interna non va thread quindi la lascio qui
    
    try:
        # PER SOCKET php
        HOST, PORT = "localhost", 9999
        server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)        
        threadPHP = threading.Thread(target=serverPHP)
        threadPHP.start()        
        db = MySQLdb.connect(host="localhost",user="root",passwd=passMy, db="pic_berry")
        cursore = db.cursor()
        sql = "SELECT * FROM devices;" 
        try:   
            cursore.execute(sql)
            devices = list(cursore.fetchall()) #attenzione è diventata una lista di tuple
            if (devices[0][0] == 'io'):
                MyID= list(devices[0][1:4])    #mi serve lista perchè tuple non le concateno
                print MyID
        except:
            print "Error unable to fecth data"
        db.close()
        initRadio()

        #print istantRX(2)
        #dev1= list(devices[1][1:5])
        # dev1= list(devices[1])
        
        #threadWaitCall = Thread(target=WaitCall)
        #threadWaitCall.start()

        #confPic(dev1,2) // mando device completo (adr,net,pasword,config) e solo il numero del vecchio device
        #confAlert(dev)   
        #print sincPic(2)
        #print reqData(dev1)
        
                
      
        ''' funzione ok per dire che ho capito che stai per staccare corrente !!!!
            while True:
           st = checkRX(True)
           if st != None:
                pack = ["B", 0, 0, 0, 0, 0,dev1[1]] #sistemare non mettere dev1[1] ma chi ha inviato richiesta
                for i in range(10):
                    PeB.rfmTX(*(pack+MyID)) #invio una scarica senza attendere risposte 

        '''
        #GPIO.add_event_detect(15, GPIO.FALLING, callback=leggiReq, bouncetime=1)

        
        '''
        while True:
            WaitCall()
            #strRep = checkRX(True)
            #print strRep
            #a = 'D'
        '''
        
        #PeB.rfmEn()
        
        #GPIO.add_event_detect(15, GPIO.FALLING, callback=leggiReq, bouncetime=1)# attenzione aggiungere solo se non c'è




        
        #GPIOLock.acquire()
        if mqttEn:
            try:
                mqttclient = mqtt.Client()    
                mqttclient.username_pw_set(mqttUser, mqttPw)
                mqttclient.on_connect = on_connect_mqtt
                mqttclient.on_message = on_message_mqtt
                mqttclient.connect(mqttHost, mqttPort, 60)
                mqttclient.loop_start()
                mqttConnect = True
            except:
                mqttConnect = False
                trace("NON RIESCO A CONNETERMI AL BROKER", " MQTT")
            enEvent = True
        disInt("Disabilito interrupt", "INIZIO PROGRAMMA")
        for d in devices:
            if d[9] != None and d[9].find('S') != -1:
                print d
                
                sincPic(d) # togliere commento per sincronizzare ad ogni avvio
        for d in devices:
            if d[9] != None and d[9].find('C') != -1:
                print d
                
                statoIniziale(d)
                
        #GPIOLock.release()
        #enEvent =True
        enInt("Ablito interrupt","prima di entrare nel while principale")
        while True:
            print "INIZIO ATTESA"
            #if not enEvent:
            #    enInt("Ablito interrupt","nel while principale")
        
                #GPIOLock.acquire()
                #PeB.rfmEn()
                #try:
                #    GPIO.add_event_detect(15, GPIO.FALLING, callback=leggiReq, bouncetime=1)# attenzione aggiungere solo se non c'è
                #except RuntimeError:
                #    print "ERA GIA ATTIVATO L'INTERRUPT" #se in log non trovo mai questo eliminare il try-except
                #    trace("dentro while Principale:","Errore Interrupt gia attivato")
                #           
                #enEvent = True
                #GPIOLock.release()


            #sleep(20000) #5,5 ore
            sleep(10000) # 2,5 ore
            #sleep(10) #ogni 5 secondi

            #GPIOLock.acquire()
            #GPIO.remove_event_detect(15)
            #enEvent = False            
            if disInt("Disabilito interrupt","Per lettura ogni xx ore"):
                # sleep(.5) #tolto 11/01/17
                for i in devices:
                    if i[9] != None and i[9].find('G') != -1:
                        print reqData(i)  # fare anche il sink 1 volta al gg prima delle 8:00 !
                        data = datetime.now()
                        # sleep(5) #tolto 11/01/17
                        if data.hour < 8 or data.hour > 20:
                            sincPic(i)
                            sleep(2)
                        update(i[0]) 
                        update_m(i[0])
                enInt("Ablito interrupt","nel while principale")
            else:
                
                trace("NON RIESCO A DISABILITARE INTERRUPT","Riprovo più tardi")
                

            #GPIOLock.release()
            

        server.shutdown() # messo per chiudere il server quando esco !!!! togliere in produzione
        GPIO.cleanup()
    except KeyboardInterrupt:
        print "keyboard interrupt"
        #GPIO.cleanup()
        server.shutdown()
        #threadPHP.stop() # spengo soket PHP         
        GPIO.cleanup()
    
