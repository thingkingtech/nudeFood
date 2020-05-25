#from pad4pi import rpi_gpio
import time
import sys
import RPi.GPIO as GPIO
import logging
from hx711 import HX711
from decimal import Decimal, ROUND_DOWN
import os
import pickle

end_weight = None
rands = 0

GPIO.setmode(GPIO.BCM)

###########################UNIQUE DATA FOR EACH DISPENSER################
RperKg = 255
gperR = 1000/RperKg
UID = "cpt1nut1d6"
Product = "Nuts"
Store = "Nude Foods"
Location = "Cape Town"
#########################################################################

# Load Cell #
hx = HX711(dout_pin=5, pd_sck_pin=6)
swap_file_name = 'swap_file.swp'
if os.path.isfile(swap_file_name):
        with open(swap_file_name, 'rb') as swap_file:
            hx = pickle.load(swap_file)

######### TIME OUT TIME ######
# if dispense takes longer than 10 minutes -- stop transaction (timeout)

#timeout = 600

####BUTTONS####

START = 17

GPIO.setwarnings(False)
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
    
def dispense():
    
    #time.sleep(0.1)
    
    global rands
    global dispensed
    global end_weight
    global transnum
    
    dispensed =0
    rands=0
    
    lcd_string("Dispenser Active",LCD_LINE_1,2)
    lcd_string("R"+str(rands),LCD_LINE_2,2)
    lcd_string(str(int(dispensed))+"g",LCD_LINE_3,2)            
    lcd_string("Return lever to end",LCD_LINE_4,2)
    
    
    while GPIO.input(START) == GPIO.LOW:

        #time.sleep(0.1)
        
        dispensed = (-1)*hx.get_weight_mean(5)
     
        rands = float(dispensed/gperR)
        rands = Decimal(rands).quantize(Decimal('.01'), rounding=ROUND_DOWN)
        
        dispensed = round(dispensed, 0)
        dispensed = max(0, dispensed)
        rands = max(0, rands)
            
        dispensed = str(int(dispensed))
        
        lcd_string("R"+str(rands),LCD_LINE_2,2)
        lcd_string(dispensed+"g",LCD_LINE_3,2)            
      
    if GPIO.input(START) != GPIO.LOW:
            
        dispensed = (-1)*hx.get_weight_mean(15)
     
        rands = float(dispensed/gperR)
        rands = Decimal(rands).quantize(Decimal('.01'), rounding=ROUND_DOWN)
        
        dispensed = round(dispensed, 0)
        dispensed = max(0, dispensed)
        rands = max(0, rands)
            
        dispensed = str(int(dispensed))
            
        beepbeep()
        ledoff()
        printer(str(rands), str(int(dispensed)))                     ##  UNCOMMENT TO PRINT!

        lcd_string("Dispensing Complete",LCD_LINE_1,2)
        lcd_string("Total: R"+str(rands),LCD_LINE_2,2)
        lcd_string("Total: "+str(int(dispensed))+"g",LCD_LINE_3,2)       
        lcd_string("Collect your receipt",LCD_LINE_4,2)

        ## Log transaction info
        time.sleep(5)
        
        main()
                                      

# Main code #


def main():
    amount = 0
    
    ledoff()
    time.sleep(0.1)
    
    lcd_string("Welcome!",LCD_LINE_1,2)
    lcd_string("Raw Almonds",LCD_LINE_2,2)
    lcd_string("R" + str(RperKg) +" per Kg",LCD_LINE_3,2)
    lcd_string("Pull lever to begin",LCD_LINE_4,2)
    
    os.system("cancel -a ARGOX_OS-214_plus_PPLB_203dpi")
    
    while GPIO.input(START) != GPIO.LOW:
        hx.zero(5)
        
    if GPIO.input(START) == GPIO.LOW:                    ## START pushed                   
        beepbeep()
        ledon()
        dispense()
      
            
while True:     ## Loop main function ##
    try:
        main()
    
    except (KeyboardInterrupt, SystemExit):
        print("dead")
        lcd_byte(0x01, LCD_CMD)
        lcd_string("Goodbye!",LCD_LINE_1,2)
        noiseoff()
        ledoff()
        GPIO.cleanup()
