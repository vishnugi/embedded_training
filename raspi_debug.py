import RPi.GPIO as GPIO
import serial
import smbus2
import spidev

import threading
import queue
import logging
import time
import traceback


# ============================================================
# CONFIGURATION
# ============================================================

LED_PIN = 17
BUTTON_PIN = 27

UART_PORT = "/dev/serial0"
UART_BAUDRATE = 115200

I2C_BUS = 1
I2C_ADDRESS = 0x48

SPI_BUS = 0
SPI_DEVICE = 0


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] [%(threadName)s] %(message)s"
)

log = logging.getLogger(__name__)


# ============================================================
# GLOBAL OBJECTS
# ============================================================

data_queue = queue.Queue()

stop_event = threading.Event()

counter = 0
counter_lock = threading.Lock()


# ============================================================
# GPIO SETUP
# ============================================================

GPIO.setmode(GPIO.BCM)

GPIO.setup(LED_PIN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# ============================================================
# UART SETUP
# ============================================================

try:
    uart = serial.Serial(
        UART_PORT,
        UART_BAUDRATE,
        timeout=1
    )

    log.info("UART initialized")

except Exception as e:
    uart = None
    log.error("UART initialization failed: %s", e)


# ============================================================
# I2C SETUP
# ============================================================

try:
    i2c = smbus2.SMBus(I2C_BUS)
    log.info("I2C initialized")

except Exception as e:
    i2c = None
    log.error("I2C initialization failed: %s", e)


# ============================================================
# SPI SETUP
# ============================================================

try:
    spi = spidev.SpiDev()

    spi.open(SPI_BUS, SPI_DEVICE)

    spi.max_speed_hz = 1_000_000
    spi.mode = 0

    log.info("SPI initialized")

except Exception as e:
    spi = None
    log.error("SPI initialization failed: %s", e)


# ============================================================
# GPIO THREAD
# ============================================================

def gpio_worker():

    log.info("GPIO thread started")

    while not stop_event.is_set():

        GPIO.output(LED_PIN, GPIO.HIGH)

        log.debug("LED ON")

        time.sleep(1)

        GPIO.output(LED_PIN, GPIO.LOW)

        log.debug("LED OFF")

        time.sleep(1)


# ============================================================
# BUTTON THREAD
# ============================================================

def button_worker():

    log.info("Button thread started")

    previous_state = GPIO.input(BUTTON_PIN)

    while not stop_event.is_set():

        current_state = GPIO.input(BUTTON_PIN)

        if current_state != previous_state:

            log.info(
                "Button state changed: %d -> %d",
                previous_state,
                current_state
            )

            data_queue.put(
                ("BUTTON", current_state)
            )

            previous_state = current_state

        time.sleep(0.05)


# ============================================================
# UART THREAD
# ============================================================

def uart_worker():

    log.info("UART thread started")

    while not stop_event.is_set():

        try:

            if uart and uart.in_waiting:

                data = uart.readline()

                log.info("UART RX: %s", data)

                data_queue.put(
                    ("UART", data)
                )

            time.sleep(0.01)

        except Exception:

            log.error("UART error")

            traceback.print_exc()


# ============================================================
# I2C WORKER
# ============================================================

def i2c_worker():

    log.info("I2C thread started")

    while not stop_event.is_set():

        try:

            if i2c:

                # Example I2C read
                value = i2c.read_byte(I2C_ADDRESS)

                log.info(
                    "I2C DATA: 0x%02X",
                    value
                )

                data_queue.put(
                    ("I2C", value)
                )

        except Exception as e:

            log.warning(
                "I2C read failed: %s",
                e
            )

        time.sleep(2)


# ============================================================
# SPI WORKER
# ============================================================

def spi_worker():

    log.info("SPI thread started")

    while not stop_event.is_set():

        try:

            if spi:

                tx_data = [0xAA, 0x55]

                rx_data = spi.xfer2(tx_data)

                log.info(
                    "SPI TX=%s RX=%s",
                    tx_data,
                    rx_data
                )

                data_queue.put(
                    ("SPI", rx_data)
                )

        except Exception as e:

            log.warning(
                "SPI error: %s",
                e
            )

        time.sleep(2)


# ============================================================
# QUEUE / INTER-THREAD COMMUNICATION
# ============================================================

def queue_worker():

    global counter

    log.info("Queue worker started")

    while not stop_event.is_set():

        try:

            source, data = data_queue.get(
                timeout=1
            )

            log.info(
                "QUEUE received from %s: %s",
                source,
                data
            )

            # ------------------------------------------------
            # PROTECTED SHARED VARIABLE
            # ------------------------------------------------

            with counter_lock:

                counter += 1

                log.debug(
                    "Counter = %d",
                    counter
                )

            data_queue.task_done()

        except queue.Empty:

            pass


# ============================================================
# DEBUG THREAD
# ============================================================

def debug_worker():

    log.info("Debug thread started")

    while not stop_event.is_set():

        time.sleep(5)

        with counter_lock:

            current_counter = counter

        log.info(
            "DEBUG STATUS: counter=%d queue=%d",
            current_counter,
            data_queue.qsize()
        )


# ============================================================
# MAIN
# ============================================================

def main():

    log.info("================================")
    log.info(" Raspberry Pi Embedded Debugger ")
    log.info("================================")

    threads = [

        threading.Thread(
            target=gpio_worker,
            name="GPIO"
        ),

        threading.Thread(
            target=button_worker,
            name="BUTTON"
        ),

        threading.Thread(
            target=uart_worker,
            name="UART"
        ),

        threading.Thread(
            target=i2c_worker,
            name="I2C"
        ),

        threading.Thread(
            target=spi_worker,
            name="SPI"
        ),

        threading.Thread(
            target=queue_worker,
            name="QUEUE"
        ),

        threading.Thread(
            target=debug_worker,
            name="DEBUG"
        )
    ]

    for thread in threads:

        thread.start()

    try:

        while True:

            # =================================================
            # BREAKPOINT FOR PYTHON DEBUGGING
            # =================================================

            if counter == 5:

                log.warning(
                    "Counter reached 5"
                )

                # Uncomment for interactive PDB debugging
                #
                # breakpoint()

            time.sleep(1)

    except KeyboardInterrupt:

        log.info(
            "Ctrl+C received"
        )

    except Exception:

        log.error(
            "MAIN THREAD EXCEPTION"
        )

        traceback.print_exc()

    finally:

        log.info(
            "Stopping threads..."
        )

        stop_event.set()

        for thread in threads:

            thread.join()

        # =====================================================
        # CLEANUP
        # =====================================================

        GPIO.output(
            LED_PIN,
            GPIO.LOW
        )

        GPIO.cleanup()

        if uart:

            uart.close()

        if i2c:

            i2c.close()

        if spi:

            spi.close()

        log.info(
            "System shutdown complete"
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()
