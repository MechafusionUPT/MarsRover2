import time
import board
import busio
from adafruit_pca9685 import PCA9685

i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c, address=0x40)
pca.frequency = 50

def duty(angle, min_us=500, max_us=2500):
    pulse = min_us + (angle / 180.0) * (max_us - min_us)
    return int((pulse / 20000) * 65535)

print("Servo test: LEFT")
pca.channels[0].duty_cycle = duty(0)
time.sleep(1)

print("Servo test: RIGHT")
pca.channels[0].duty_cycle = duty(180)
time.sleep(1)

print("Servo test: CENTER")
pca.channels[0].duty_cycle = duty(90)
