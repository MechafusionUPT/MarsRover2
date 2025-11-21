import time
import board
import busio
from adafruit_pca9685 import PCA9685


def duty(angle, min_us=500, max_us=2500):
    pulse = min_us + (angle / 180.0) * (max_us - min_us)
    return int((pulse / 20000) * 65535)

# ============================================================
#  PCA9685 SETUP (servos = address 0x40, frequency = 50Hz)
# ============================================================
i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c, address=0x40)
pca.frequency = 50

# ============================================================
#  SERVO CHANNELS
# ============================================================
channelGrip = 0   # gripper servo canal
channelPitch = 1  # pitch servo canal

# ============================================================
#  PWM PULSE LIMITS (în microsecunde)
# ============================================================
MIN_US = 500      # minim recomandat pentru servo
MAX_US = 2500     # maxim recomandat pentru servo
PERIOD_US = 20000 # 20ms => 50Hz

# ============================================================
#  RANGE DEFINIȚII
# ============================================================
# GRIPPER
GRIP_CLOSED = 140     # apropiat
GRIP_OPEN   = 180    # deschis total
DEFAULT_GRIP = 140

# PITCH
PITCH_UP = 70        # sus
PITCH_DOWN = 110      # jos
DEFAULT_PITCH = 90

# ============================================================
# Helper: convert angle → PCA9685 duty cycle
# ============================================================
def angle_to_duty(angle_deg, servo_range=180):
    angle_deg = max(0, min(angle_deg, servo_range))
    pulse_us = MIN_US + (angle_deg / servo_range) * (MAX_US - MIN_US)
    duty16 = int((pulse_us / PERIOD_US) * 65535)
    return duty16

# ============================================================
# INIT FUNCTION
# ============================================================
def init_servos():
    print("[SERVOS] PCA9685 @0x40 activ (50Hz)")

    # initialize gripper
    pca.channels[channelGrip].duty_cycle = angle_to_duty(DEFAULT_GRIP)
    print(f"[GRIP] setat default la {DEFAULT_GRIP}°")

    # initialize pitch
    pca.channels[channelPitch].duty_cycle = angle_to_duty(DEFAULT_PITCH)
    print(f"[PITCH] setat default la {DEFAULT_PITCH}°")

# ============================================================
#  GRIPPER FUNCTIONS
# ============================================================
def set_grip(angle):
    duty = angle_to_duty(angle)
    pca.channels[channelGrip].duty_cycle = duty

def close_grip():
    print("[GRIP] CLOSE")
    set_grip(GRIP_CLOSED)

def open_grip():
    print("[GRIP] OPEN")
    set_grip(GRIP_OPEN)

def grip_default():
    print("[GRIP] DEFAULT")
    set_grip(DEFAULT_GRIP)

# ============================================================
#  PITCH FUNCTIONS
# ============================================================
def set_pitch(angle):
    angle = max(PITCH_UP, min(angle, PITCH_DOWN))
    duty = angle_to_duty(angle)
    pca.channels[channelPitch].duty_cycle = duty

def pitch_up():
    print("[PITCH] UP")
    set_pitch(PITCH_UP)

def pitch_down():
    print("[PITCH] DOWN")
    set_pitch(PITCH_DOWN)

def reset_pitch():
    print("[PITCH] RESET")
    set_pitch(DEFAULT_PITCH)

def change_pitch(delta):

    """delta pozitiv = jos, negativ = sus"""
    # citește ultimul unghi (nu îl stocăm global — simplu și safe)
    # nu avem citire reală servo, deci îl ținem intern:
    global _last_pitch
    try:
        _last_pitch
    except NameError:
        _last_pitch = DEFAULT_PITCH

    new_angle = _last_pitch + delta
    new_angle = max(PITCH_UP, min(new_angle, PITCH_DOWN))
    _last_pitch = new_angle
    set_pitch(new_angle)

SERVO_CH = 0
servo_angle = 90
def servo_down(x):
    """Mișcă servo-ul în JOS cu x grade."""
    global current_angle
    current_angle = min(180, current_angle + x)  # creștem unghiul
    pca.channels[SERVO_CH].duty_cycle = angle_to_duty(current_angle)

def servo_up(x):
    """Mișcă servo-ul în SUS cu x grade."""
    global current_angle
    current_angle = max(0, current_angle - x)    # scădem unghiul
    pca.channels[SERVO_CH].duty_cycle = angle_to_duty(current_angle)

def grip_sus():
    pca.channels[0].duty_cycle = angle_to_duty(140)

def grip_jos():
    pca.channels[0].duty_cycle = angle_to_duty(180)