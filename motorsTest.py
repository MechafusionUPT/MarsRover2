from gpiozero import PWMOutputDevice, DigitalOutputDevice
from time import sleep

# Motor A
in1 = DigitalOutputDevice(17)
in2 = DigitalOutputDevice(27)


# Motor B
in3 = DigitalOutputDevice(22)
in4 = DigitalOutputDevice(23)


def forward():
    in1.on()
    in2.off()
    in3.on()
    in4.off()


def backward():
    in1.off()
    in2.on()
    in3.off()
    in4.on()


def stop():
    in1.off()
    in2.off()
    in3.off()
    in4.off()

try:
    while True:
        print("Mergi înainte")
        forward()
        

except KeyboardInterrupt:
    stop()
    print("Oprit.")
