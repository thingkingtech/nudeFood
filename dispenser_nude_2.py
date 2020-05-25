#from pad4pi import rpi_gpio
import time
import sys
import RPi.GPIO as GPIO
import logging
from hx711 import HX711
from decimal import Decimal, ROUND_DOWN
import os

end_weight = None
rands = 0

###########################UNIQUE DATA FOR EACH DISPENSER################
gperR = 30
UID = "cpt1nut1d6"
Product = "Nuts"
Store = "Nude Foods"
Location = "Cape Town"
#########################################################################

# Load Cell #
hx = HX711(5, 6)
hx.set_reading_format("MSB", "MSB")
hx.set_reference_unit(167)
tare = 1200
hx.reset()

######### TIME OUT TIME ######
# if dispense takes longer than 10 minutes -- stop transaction (timeout)

#timeout = 600

####BUTTONS####

START = 17

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(START, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

##############

buzzer = 4
led = 21

GPIO.setup(led, GPIO.OUT)
GPIO.setup(buzzer, GPIO.OUT)

###########################################################LCD_START#########################################

# Define GPIO to LCD mapping
LCD_RS = 7
LCD_E  = 8
LCD_D4 = 26
LCD_D5 = 13
LCD_D6 = 16
LCD_D7 = 12
LED_ON = 15
 
# Define some device constants
LCD_WIDTH = 20    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False
 
LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line
 
# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)
 
def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command
 
  GPIO.output(LCD_RS, mode) # RS
 
  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)
 
  # Toggle 'Enable' pin
  lcd_toggle_enable()
 
  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)
 
  # Toggle 'Enable' pin
  lcd_toggle_enable()
 
def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)
 
def lcd_string(message,line,style):
      if style==1:
        message = message.ljust(LCD_WIDTH," ")
      elif style==2:
        message = message.center(LCD_WIDTH," ")  
      elif style==3:
        message = message.rjust(LCD_WIDTH," ")
 
      lcd_byte(line, LCD_CMD)
 
      for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]),LCD_CHR)

GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
GPIO.setup(LCD_E, GPIO.OUT)  # E
GPIO.setup(LCD_RS, GPIO.OUT) # RS
GPIO.setup(LCD_D4, GPIO.OUT) # DB4
GPIO.setup(LCD_D5, GPIO.OUT) # DB5
GPIO.setup(LCD_D6, GPIO.OUT) # DB6
GPIO.setup(LCD_D7, GPIO.OUT) # DB7
GPIO.setup(LED_ON, GPIO.OUT) # Backlight enable

lcd_init()

########################################LCD_END################################################

######################### Logging Setup ############################ 

#filenamed=UID+'_dispenser_log_'+time.strftime("%Y%m%d")+'.csv'
#logging.basicConfig(filename=filenamed, filemode='a', format='%(asctime)s %(message)s', datefmt="%Y-%m-%d; \t %H:%M:%S;", level=logging.INFO)
#logfile = open(UID+"_dispenser_log_"+time.strftime("%Y%m%d")+".csv", "a")
#logfile.write("Date; \tTime; \tMessage; \tQuantity; \tUnit; \tUID; \tStore; \tLocation; \tProduct; \tTransaction;\n")
#logfile.close()

#logstring1 = UID + ";\t" + Store + ";\t" + Location + ";\t" + Product + ";\t" + "NULL;"     # String at the end of most logs

########################################################################

#def email():
#    subject = UID+" logfile"
    #os.system('mpack -s "' +subject+'" ' + filenamed + ' jwaisbi@gmail.com' )
    
def beepbeep():
    noiseon()
    time.sleep(0.1)
    noiseoff()
    time.sleep(0.1)
    noiseon()
    time.sleep(0.1)
    noiseoff()
    
def beep():
    noiseon()
    time.sleep(0.1)
    noiseoff()
            
def noiseon():
    GPIO.output(buzzer, GPIO.HIGH)        

def noiseoff():
    GPIO.output(buzzer, GPIO.LOW)

def ledon():
    GPIO.output(led, GPIO.HIGH)
    
def ledoff():
    GPIO.output(led, GPIO.LOW)
    
def printer(rands, dispensed):
    os.system("echo \" \n\n RANDS: R" + rands + "\n\n GRAMS: " + dispensed + "g \" | lp")
    
def dispense(start_weight):
    
  #  timeout_time = time.time() + timeout        # Timeout
    
    time.sleep(0.1)
    
    global rands
    global dispensed
    global end_weight
    global transnum
    
    dispensed =0
    rands=0
    
    current_weight = hx.get_weight(5) - tare
    
    lcd_string("Gcwalisa Active",LCD_LINE_1,2)
    lcd_string("R"+str(rands),LCD_LINE_2,2)
    lcd_string(str(int(dispensed))+"g",LCD_LINE_3,2)            
    lcd_string("Return lever to end",LCD_LINE_4,2)
    
    ## The number of the transaction is checked -- transnum saved as text file so that the variable is read, plus oned, and re-written 
 #   transfile = open('transnum.txt', 'r')
 #   transnum = transfile.readline()
 #   transfile.close()
    
 #   if transnum == None or '':
 #       transnum = 0
    
  #  transnum = int(transnum)
  #  transnum += 1
  #  transfile = open('transnum.txt', 'w')
  #  transfile.write(str(transnum))
  #  transfile.close()
  #  transnum = str(transnum)
    
  #  logstring2 = UID + ";\t" + Store + ";\t" + Location + ";\t" + Product + ";\t" + transnum + ";"      ## Transactions have the transnum added to their logs hence logstring2
    
    if end_weight == None:
        end_weight = start_weight
    
    ## Check if there has been a re-fill
    
    #if start_weight > end_weight + 100:
        #logging.info('\tRefill detected;\t' + '-; \t-; \t' + logstring1)
        #logging.info('\tAmount Refilled; \t' + str(start_weight - end_weight) + ';\t g; \t' + logstring1)
    
        
  #  logging.info('\tSTART; \t-; \t-; \t' + logstring2)
    
    while GPIO.input(START) == GPIO.LOW:

        time.sleep(0.1)
        
        current_weight = hx.get_weight(5) - tare
     
        dispensed = float(start_weight) - float(current_weight)
        rands = float(dispensed/gperR)
        rands = Decimal(rands).quantize(Decimal('.01'), rounding=ROUND_DOWN)
        
        dispensed = round(dispensed, 0)
        dispensed = max(0, dispensed)
        rands = max(0, rands)
        
        lcd_string("Gcwalisa Active",LCD_LINE_1,2)
        lcd_string("R"+str(rands),LCD_LINE_2,2)
        lcd_string(str(int(dispensed))+"g",LCD_LINE_3,2)            
        lcd_string("Return lever to end",LCD_LINE_4,2)
      
    if GPIO.input(START) != GPIO.LOW:
        
            beepbeep()
            ledoff()
            printer(str(rands), str(int(dispensed)))                     ##  UNCOMMENT TO PRINT!
            
            lcd_string("Dispensing Complete",LCD_LINE_1,2)
            lcd_string("Total: R"+str(rands),LCD_LINE_2,2)
            lcd_string("Total: "+str(int(dispensed))+"g",LCD_LINE_3,2)       
            lcd_string("Collect your receipt",LCD_LINE_4,2)

            ## Log transaction info
            time.sleep(2)
            
        #    logging.info('\tR dispensed; \t' + str(rands) + ';\t R; \t' + logstring2)
        #    logging.info('\tg dispensed; \t' + str(dispensed) + ';\t g; \t' + logstring2)
        #    logging.info('\tStart quantity; \t' + str(start_weight) + ";\t g; \t" + logstring2)
        #    logging.info('\tCurrent quantity; \t' + str(max(0,current_weight)) + ";\t g; \t" + logstring2)
            
        #    email()
            
            main()
                                      

# Main code #


def main():
    amount = 0
    
    ledoff()
    time.sleep(0.1)
    
    current_weight = hx.get_weight(5)-tare
    current_weight = max(0,current_weight)
    
    if current_weight<5:
        current_weight=0
        current_weight = str(current_weight)
    
    lcd_string("Pull lever to start",LCD_LINE_1,2)
    lcd_string("",LCD_LINE_2,2)
    lcd_string("",LCD_LINE_3,2)
    lcd_string("Total: " + str(current_weight) + "g",LCD_LINE_4,2)
    
    #logging.info('\tIDLE; \t-; \t-; \t' + logstring1)
    
    while GPIO.input(START) != GPIO.LOW:
        time.sleep(0.1)
        
    if GPIO.input(START) == GPIO.LOW:                    ## START pushed                   
        beepbeep()
        ledon()
        #logging.info('\tFree Mode; \t-; \t-; \t' + logstring1)
        
        start_weight = hx.get_weight(5) - tare
        
        dispense(start_weight)
      
            
while True:     ## Loop main function ##
    try:
        main()
    
    except (KeyboardInterrupt, SystemExit):
        print "dead"
        lcd_byte(0x01, LCD_CMD)
        lcd_string("Goodbye!",LCD_LINE_1,2)
        noiseoff()
        ledoff()
        GPIO.cleanup()
