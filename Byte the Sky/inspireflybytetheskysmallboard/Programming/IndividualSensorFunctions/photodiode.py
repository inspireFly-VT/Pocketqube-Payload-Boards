def photoDiodeConversion(volt_in, temperature)
 
    current_max = 0.000014 # 14 uA
    #implement using temperature data
    current_min = 0.0000001 # 10 nA
    # Convert voltage (0–3.3V) to current
    current = (volt_in/3.3)*(current_max - current_min) + current_min;
    # Convert current to irradiance (0.01–1.0)
    irradiance = (0.99)(current - current_min)/(current_max - current_min) + 0.01;
    return irradiance