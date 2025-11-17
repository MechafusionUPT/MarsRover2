import time
import board
import busio
from adafruit_pca9685 import PCA9685
from gpiozero import DigitalOutputDevice

# ------------------------
# SETUP PCA9685 (PWM)
# ------------------------
i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c, address=0x41)
pca.frequency = 1000  # recomandat pentru motoare DC

# Canalele PWM
ENA = 0  # motor stanga
ENB = 1  # motor dreapta
ENC = 2
END = 3

# ------------------------
# SETUP GPIOZERO (direcție)
# ------------------------
BR_IN1 = DigitalOutputDevice(17) 
BR_IN2 = DigitalOutputDevice(27)
BL_IN1 = DigitalOutputDevice(22)
BL_IN2 = DigitalOutputDevice(23)


FR_IN1 = DigitalOutputDevice(24) 
FR_IN2 = DigitalOutputDevice(25)
FL_IN1 = DigitalOutputDevice(5)
FL_IN2 = DigitalOutputDevice(6)

# ------------------------
# FUNCTII PWM
# ------------------------
def set_speed(channel, speed):
    """
    speed = 0 → 100 (%)
    PCA9685 duty_cycle este 16-bit (0 - 65535)
    """
    duty = int((speed / 100) * 65535)
    pca.channels[channel].duty_cycle = duty

# ------------------------
# FUNCTII MOTOARE
# ------------------------
def BL_forward(speed):
    BR_IN1.on()
    BR_IN2.off()
    set_speed(ENA, speed)

def BL_backward(speed):
    BR_IN1.off()
    BR_IN2.on()
    set_speed(ENA, speed)

def BR_backward(speed):
    BL_IN1.on()
    BL_IN2.off()
    set_speed(ENB, speed)

def BR_forward(speed):
    BL_IN1.off()
    BL_IN2.on()
    set_speed(ENB, speed)

def FL_backward(speed):
    FR_IN1.on()
    FR_IN2.off()
    set_speed(ENC, speed)

def FL_forward(speed):
    FR_IN1.off()
    FR_IN2.on()
    set_speed(ENC, speed)

def FR_forward(speed):
    FL_IN1.on()
    FL_IN2.off()
    set_speed(END, speed)

def FR_backward(speed):
    FL_IN1.off()
    FL_IN2.on()
    set_speed(END, speed)

def stop_all():
    set_speed(ENA, 0)
    set_speed(ENB, 0)
    BR_IN1.off()
    BR_IN2.off()
    BL_IN1.off()
    BL_IN2.off()

def move_forward(speed):
    if(speed>95):
        speed = 95 #limitam pt ca la valori mai mari se opreste tot 
    FR_forward(speed)
    FL_forward(speed)
    if(speed > 90):
        time.sleep(0.1)
    else: 
        time.sleep(0.07)
    BR_forward(speed)
    BL_forward(speed)
    time.sleep(0.05)

def stir_right(speed):
    FL_forward(speed)
    BL_forward(speed)

    FR_backward(0.8 * speed)
    BR_backward(0.8 * speed)

def stir_left(speed):
    FR_forward(speed)
    BR_forward(speed)

    FL_backward(0.8 * speed)
    BL_backward(0.8 * speed)

def stop_all():
    FR_forward(0)
    FL_forward(0)
    BR_forward(0)
    BL_forward(0)

    
try:
    while True:
         # mic delay ca să nu ocupe CPU 100%
        move_forward(95)
        time.sleep(5)
        stop_all()
        time.sleep(5)
finally:
    stop_all()