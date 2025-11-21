import time
import board
import busio
from adafruit_pca9685 import PCA9685
from gpiozero import DigitalOutputDevice

# -------------------------------------------------------
# SETUP PCA9685 (PWM)
# -------------------------------------------------------
i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c, address=0x41)
pca.frequency = 1000  # PWM pentru motoare

# PWM Channels
ENA = 0   # Back Left
ENB = 1   # Back Right
ENC = 2   # Front Left
END = 3   # Front Right

# -------------------------------------------------------
# SETUP GPIO (direction control)
# -------------------------------------------------------

# BACK RIGHT MOTOR (spate dreapta)
BR_IN1 = DigitalOutputDevice(17)
BR_IN2 = DigitalOutputDevice(27)

# BACK LEFT MOTOR (spate stanga)
BL_IN1 = DigitalOutputDevice(22)
BL_IN2 = DigitalOutputDevice(23)

# FRONT RIGHT MOTOR (fata dreapta)
FR_IN1 = DigitalOutputDevice(24)
FR_IN2 = DigitalOutputDevice(25)

# FRONT LEFT MOTOR (fata stanga)
FL_IN1 = DigitalOutputDevice(5)
FL_IN2 = DigitalOutputDevice(6)

# -------------------------------------------------------
# FUNCTIE PWM
# -------------------------------------------------------

def set_speed(channel, speed):
    """ speed = 0 → 100 (%) """
    duty = int((speed / 100) * 65535)
    pca.channels[channel].duty_cycle = duty

# -------------------------------------------------------
# FUNCTII MOTOR INDIVIDUAL — CORECTE
# -------------------------------------------------------

# Back Left
def BL_forward(speed):
    BL_IN1.on()
    BL_IN2.off()
    set_speed(ENC, speed)

def BL_backward(speed):
    BL_IN1.off()
    BL_IN2.on()
    set_speed(ENC, speed)

# Back Right
def BR_forward(speed):
    BR_IN1.off()
    BR_IN2.on()
    set_speed(ENB, speed)

def BR_backward(speed):
    BR_IN1.on()
    BR_IN2.off()
    set_speed(ENB, speed)

# Front Left
def FL_forward(speed):
    FL_IN1.off()
    FL_IN2.on()
    set_speed(END, speed)

def FL_backward(speed):
    FL_IN1.on()
    FL_IN2.off()
    set_speed(END, speed)

# Front Right
def FR_forward(speed):
    FR_IN1.off()
    FR_IN2.on()
    set_speed(ENA, speed)

def FR_backward(speed):
    FR_IN1.on()
    FR_IN2.off()
    set_speed(ENA, speed)

# -------------------------------------------------------
# FUNCTII ROVER COMPLET
# -------------------------------------------------------

def move_forward(speed):
    BL_forward(speed)
    BR_forward(speed)
    FL_forward(speed)
    FR_forward(speed)

def move_backward(speed):
    BL_backward(speed)
    BR_backward(speed)
    FL_backward(speed)
    FR_backward(speed)

def stir_right(speed):
    # stanga inainte, dreapta inapoi
    BL_forward(speed)
    FL_forward(speed)
    BR_backward(int(speed * 0.8))
    FR_backward(int(speed * 0.8))

def stir_left(speed):
    # dreapta inainte, stanga inapoi
    BR_forward(speed)
    FR_forward(speed)
    BL_backward(int(speed * 0.8))
    FL_backward(int(speed * 0.8))

def stop_all():
    set_speed(ENA, 0)
    set_speed(ENB, 0)
    set_speed(ENC, 0)
    set_speed(END, 0)

    BR_IN1.off(); BR_IN2.off()
    BL_IN1.off(); BL_IN2.off()
    FR_IN1.off(); FR_IN2.off()
    FL_IN1.off(); FL_IN2.off()

# -------------------------------------------------------
# MAIN LOOP
# -------------------------------------------------------

"""
try:
    while True:
        #move_forward(80)
        stir_right(80)
        time.sleep(5)
        stop_all()
        time.sleep(3)

finally:
    stop_all()
"""