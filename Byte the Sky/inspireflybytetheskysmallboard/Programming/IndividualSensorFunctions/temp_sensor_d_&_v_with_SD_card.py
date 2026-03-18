from machine import I2C, Pin, ADC, SPI
import uos
import sdcard
import time

# ────────────────────────────
# YOUR SETTINGS
# ────────────────────────────
SDA_PIN        = 0      # wiring pin for data
SCL_PIN        = 1      # wiring pin for clock
PHOTODIODE_PIN = 26     # wiring pin for photodiode
SENSOR_ADDRESS = 0x18   # don't change this
REFERENCE_TEMP = 25.0   # calibration temperature
TEMP_COEFF     = -0.003 # from your photodiode datasheet

# SD Card pins (Pico defaults)
SD_SCK  = 10   # clock
SD_MOSI = 11   # data out
SD_MISO = 12   # data in
SD_CS   = 13   # chip select

FILE_NAME = "/sd/readings.csv"  # where data gets saved on the SD card

# ────────────────────────────
# SETUP
# ────────────────────────────
i2c = I2C(0, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN), freq=400000)
adc = ADC(Pin(PHOTODIODE_PIN))

# Connect to SD card
spi = SPI(1, sck=Pin(SD_SCK), mosi=Pin(SD_MOSI), miso=Pin(SD_MISO))
sd  = sdcard.SDCard(spi, Pin(SD_CS))
uos.mount(sd, "/sd")
print("SD card mounted!")

# Write a header row to the file (only on first run)
try:
    # Check if file already exists
    uos.stat(FILE_NAME)
    print("Existing file found, adding to it...")
except:
    # File doesn't exist yet, create it with a header
    with open(FILE_NAME, "w") as f:
        f.write("time_seconds,temperature_c,light_raw,light_corrected\n")
    print("New file created!")

print("Ready! Saving to", FILE_NAME, "\n")

# ────────────────────────────
# READING FUNCTIONS
# ────────────────────────────

def get_temperature():
    data = i2c.readfrom_mem(SENSOR_ADDRESS, 0x05, 2)
    raw = ((data[0] << 8) | data[1]) & 0x1FFF
    if raw & 0x1000:
        raw -= 0x2000
    return raw * 0.0625  # converts to °C

def get_photodiode():
    return adc.read_u16()  # returns 0 (dark) to 65535 (bright)

def get_corrected_photodiode(raw, temp):
    factor = 1.0 + TEMP_COEFF * (temp - REFERENCE_TEMP)
    return raw / factor

def save_to_sd(timestamp, temp, raw, corrected):
    # Open the file and add a new line
    with open(FILE_NAME, "a") as f:
        f.write("{},{},{},{}\n".format(timestamp, round(temp, 2), raw, int(corrected)))

# ────────────────────────────
# MAIN LOOP
# ────────────────────────────
start_time = time.time()

while True:
    temp      = get_temperature()
    raw       = get_photodiode()
    corrected = get_corrected_photodiode(raw, temp)
    elapsed   = time.time() - start_time  # seconds since startup

    # Print to screen
    print("Temp:      ", round(temp, 2), "°C")
    print("Light raw: ", raw)
    print("Light fixed:", int(corrected))
    print("Saved at:  ", elapsed, "seconds")
    print("---")

    # Save to SD card
    save_to_sd(elapsed, temp, raw, corrected)

    time.sleep(1)