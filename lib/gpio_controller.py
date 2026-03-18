# lib/gpio_controller.py
import RPi.GPIO as GPIO
import threading

class GPIOController:
    def __init__(self, callback):
        self.callback = callback
        self.running = False
        
    def start(self):
        GPIO.setmode(GPIO.BCM)
        # Définir les pins pour NEXT, AGAIN, QUIT
        GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        GPIO.add_event_detect(17, GPIO.FALLING, 
                             callback=lambda x: self.callback('NEXT'), 
                             bouncetime=300)
        GPIO.add_event_detect(27, GPIO.FALLING, 
                             callback=lambda x: self.callback('AGAIN'), 
                             bouncetime=300)
        GPIO.add_event_detect(22, GPIO.FALLING, 
                             callback=lambda x: self.callback('QUIT'), 
                             bouncetime=300)
        
        self.running = True
        
    def stop(self):
        self.running = False
        GPIO.cleanup()