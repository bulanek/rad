import os
from os.path import join,exists
import sys
sys.path.append(os.getcwd()) # pokial mas hid knihovnu na tom istom mieste ako tento skript
import hid
import time
import math
import argparse

print("==============================")
print("Radiactive At Home Test Script")
print("==========atoms.eu============\n")
print("Show you all the HID devices of your PC")

INTEGRATION_TIME=3
#OUTPUT_PATH="E:\honza_helebrant\python_script" #  nazov 
OUTPUT_PATH="/tmp" # cesta k suboru
OUTPUT_NAME='log' # prefix nazvu suboru
#vystupny format: <OUTPUT_PATH>\<OUTPUT_NAME>_<den>_<mesiac>_<rok>.txt


#-------------------------------------------------
#   
#-------------------------------------------------
def getOutput(OUTPUT_PATH,OUTPUT_NAME,aDate):
    outputFileName=join(OUTPUT_PATH,"{}_{}_{}_{}.txt".format(OUTPUT_NAME,aDate.tm_mday,aDate.tm_mon,aDate.tm_year))
    return outputFileName


#-------------------------------------------------
#   
#-------------------------------------------------
if __name__=='__main__':

    current_date=time.localtime()
    outputFileName=getOutput(OUTPUT_PATH,OUTPUT_NAME,current_date)
    outputFile=open(outputFileName,'a')

    print("----------------------Parametre-------------------------------------------------")
    print("Vystupny subor: {}".format(os.path.basename(outputFileName)))
    print("Cesta k suboru: {}".format(os.path.dirname(outputFileName)))
    print("integracny cas: {}".format(INTEGRATION_TIME))
    print("--------------------------------------------------------------------------------")

    for d in hid.enumerate(0, 0):
        keys = d.keys()
        for key in sorted(keys):
            print("%s : %s"%(key, d[key]))
        print("")

    try:
        print("Opening selected device")
        h = hid.device()
        h.open(0x4d8, 0xf6fe)


        print("Manufacturer: %s"%(h.get_manufacturer_string()))
        print("Product: %s" % h.get_product_string())
       # print("Serial No: %s" % h.get_serial_number_string())
        #Configuration
        GM_SUPPLY_ON    = int(0xa1)
        GM_SUPPLY_OFF   = int(0xa0)
        RESET_COUNTERS  = int(0xa2)
        LCD_BACKLIGHT_ON =int(0x11)
        LCD_BACKLIGHT_OFF=int(0x10)
        BUZZER_ON        =int(0x41)
        BUZZER_OFF       =int(0x40)
        BUZZER_ALERT     =int(0x42)
        LCD_OPT_0        =int(0x50)
        LCD_OPT_1        =int(0x51)
        LCD_OPT_2        =int(0x52)
        com= [0] * 129

        #BL off
        com[1]=LCD_BACKLIGHT_OFF

        #h.send_feature_report(com)
        #Buzzer off 
        com[1]=BUZZER_OFF
     #   h.send_feature_report(com)
        #Counter reset
        com[1]=RESET_COUNTERS
#    h.send_feature_report(com)
        #time.sleep(30)

        #Get ticks
        status=h.get_feature_report(0,129)
        print("Status: {}".format(status))
        if status:
                print(status)
                clock=status[1]+status[2]*256+status[3]*256*256
                print("Realtime clock: %gs" % (clock/1000.0))
                counts=status[5]+status[6]*256+status[7]*256*256
                print("Counts: %d" % counts)
                print("counting - please wait")
#-------------------------------------------------
#   vytvorenie vystpuneho suboru
#-------------------------------------------------

        outputFileNameTmp=outputFileName
        try:
            while 1:
                outputFileNameTmp=getOutput(OUTPUT_PATH,OUTPUT_NAME,time.localtime())
                if outputFileNameTmp!=outputFileName:
                        outputFileName=outputFileNameTmp
                        outputFile.close()
                        outputFile=open(outputFileName,'a')
                time.sleep(INTEGRATION_TIME)
                status=h.get_feature_report(0,129)
                clock=status[1]+status[2]*256+status[3]*256*256
                counts=status[5]+status[6]*256+status[7]*256*256
                print("Realtime clock: %gs, Counts: %d" % ((clock/1000.0), counts))
                cpm=counts*1000.0*60/clock
                print("%g CPM,  %g mikroSv/h" % (cpm,cpm/171.2))
                #This conversation factor is a bit arbitrary. Another one would be 150.51,
                #so expect that your readings are to low
                #Dead time correction
                CPM = cpm/(1-(cpm*(200e-6/60)))
                std = math.sqrt(counts)*1000.0*60/clock
                print("Corrected %g CPM,  %g+-%g mikroSv/h" % (CPM,CPM/171.2,std/171.2))

# vystup do suboru
                outputFile.write("Realtime clock: %gs, Counts: %d \n" % ((clock/1000.0), counts))
                outputFile.write("%g CPM,  %g mikroSv/h\n" % (cpm,cpm/171.2))
                outputFile.write("Corrected %g CPM,  %g+-%g mikroSv/h\n" % (CPM,CPM/171.2,std/171.2))
                outputFile.flush()

        except KeyboardInterrupt as e:
                print("Koniec!!!")
                outputFile.close()

        print("Closing device")
        h.close()

    except IOError as ex:
        print(ex)
        print("You probably don't have the hard coded hid. Update the hid.device line")
        print("in this script with one from the enumeration list output above and try again.")

    print("Have a nice day!")
