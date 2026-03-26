# coding: UTF-8
# ==================================================================
# lib/gpio_controller.py
# ==================================================================
# VintageRadio - Librairie.
# David de Lorenzo (2026)
# ==================================================================
import RPi.GPIO as GPIO


# --------------------------------------------------------------------- #
# Gestion des I/O de la carte Raspberry Pi.
# NON UTILISE ACTUELLEMENT - FOR FUTURE USE -
# --------------------------------------------------------------------- #
class GPIOController:

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def __init__(self, callback):
        """
        Constructeur
        :param callback: La callback à appeler quand un GPI est déclenché.
        """
        self.callback = callback
        self.running = False

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def start(self):
        """ Commence la surveillance des GPI. """
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
        GPIO.add_event_detect(29, GPIO.FALLING,
                              callback=lambda x: self.callback('RESET'),
                              bouncetime=300)

        self.running = True

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def stop(self):
        """ Termine la surveillance des GPI. """
        self.running = False
        GPIO.cleanup()
