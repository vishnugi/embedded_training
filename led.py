import wiringpi
import time

LED = 17

# BCM GPIO numbering
wiringpi.wiringPiSetupGpio()

# GPIO17 as output
wiringpi.pinMode(LED, wiringpi.OUTPUT)

print("LED automation started")

for i in range(5):

    # LED ON
    wiringpi.digitalWrite(LED, wiringpi.HIGH)
    print("LED ON")
    time.sleep(1)

    # LED OFF
    wiringpi.digitalWrite(LED, wiringpi.LOW)
    print("LED OFF")
    time.sleep(1)

# Make sure LED is OFF
wiringpi.digitalWrite(LED, wiringpi.LOW)

print("Automation completed")
