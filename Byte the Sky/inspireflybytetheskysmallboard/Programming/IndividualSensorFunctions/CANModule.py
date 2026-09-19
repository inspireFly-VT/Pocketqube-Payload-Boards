from machine import UART, Pin
import time

# 1. Initialize UART
# For ESP32: UART(1) uses TX=GPIO17, RX=GPIO16 by default
# For Pico: UART(0) uses TX=Pin(0), RX=Pin(1)
uart = UART(1, baudrate=9600, tx=17, rx=16) 

print("UART Communication Started. Waiting for data...")

while True:
    # 2. Send Data
    uart.write('Ping\n')
    print("Sent: Ping")
    
    # 3. Check for Received Data
    if uart.any():
        # Read the incoming bytes
        data = uart.read()
        
        # Convert bytes to string and clean up whitespace
        message = data.decode('utf-8').strip()
        
        print(f"Received: {message}")
    
    time.sleep(2) # Wait 2 seconds between pings