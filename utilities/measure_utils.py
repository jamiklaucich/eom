import time
from .qcodes_utils import *
import numpy as np

def wavelength_sweep(evo, rf,wavs, delay,funcs=None, func_args=None):
    evo.module_status()
    # Check the Interlock status
    interlock = evo.interlock_reset()
    # Set the operating mode and get the operating mode in a single function call
    setup = evo.setup(1)

    # Get the output level
    #print('Level {}%'.format(nkt.register_read_u16(DEVICE_ID, 0x27) * 0.1))

    # Turn on the laser
    if(not rf.power):
        rf.power(True)
    if(not evo.emission):
        evo.emission(True)
    #turns laser on if not already on

    time.sleep(1)
    start_time = time.time()
    for i, wav in enumerate(wavs):
        rf.wavelength=wav
        time.sleep(delay)
        print("Wavelength:{}".format(wav))
        print(progress_bar_time(i+1, len(wavs)+1, time.time()-start_time))
        if(funcs):
            for j, func in enumerate(funcs):
                func_args[j][0] = func(i, wavs[:i+1],*func_args[j])


def smu_wavelength_sweep(evo, rf, smu, wavs, delay, voltage, current_lim, nplc, funcs=None, func_args=None):
    currents = np.zeros_like(wavs)
    #How many power line cycles to measure over
    smu.source.limit(current_lim)
    smu.source.delay(1)
    #seconds delay between changing source and measurement
    smu.timeout(1000)
    #seconds for the SMU to respond to a command (including taking measurements)
    smu.sense.nplc(nplc)
    smu.source.voltage(voltage)
    buffer_name = "defbuffer1"
    buffer = smu.buffer(buffer_name)
    buffer.clear_buffer()
    smu.wait()
    buffer_elements = ["timestamp","source_value", "measurement"]
    buffer.elements(buffer_elements)
    fetch_elements = [buffer.buffer_elements[element] for element in buffer.elements()]
    evo.module_status
    # Check the Interlock status
    interlock = evo.interlock_reset()
    # Set the operating mode and get the operating mode in a single function call
    setup = evo.setup(1)

    # Get the output level
    #print('Level {}%'.format(nkt.register_read_u16(DEVICE_ID, 0x27) * 0.1))

    # Turn on the laser
    evo.emission=True
    #turns laser on if not already on

    time.sleep(1)
    start_time = time.time()
    #rf.amplitude = rf_power*10 #10=1%
    with smu.output_enabled.set_to(True):
        smu.sense.auto_zero_enabled(False)
        for i, wav in enumerate(wavs):
            rf.wavelength=wav
            time.sleep(delay)
            currents[i] = buffer.ask(f":MEASure? '{buffer_name}', {','.join(fetch_elements)}").split(",")[-1]
            print("\nWavelength:{} nm Current:{} A".format(wav, currents[i]))
            print(progress_bar_time(i+1, len(wavs)+1, time.time()-start_time))
            if(funcs):
                for j, func in enumerate(funcs):
                    func_args[j][0] = func(i, wavs[:i+1], currents[i], *func_args[j])
                
    if(not funcs):
        return currents
    else:
        return currents, func_args

def smu_source_sweep(smu, voltage, delay,  current_lim, nplc, funcs=None, func_args=None):
    smu.source.delay(delay)
    smu.source.limit(current_lim)
    smu.sense.nplc(nplc)
    smu.timeout(1000)
    appl_voltage = np.zeros_like(voltage)
    current = np.zeros_like(voltage)

    start_time = time.time()
    with smu.output_enabled.set_to(True):
        for i, v in enumerate(voltage):
            if(smu.source.limit_tripped()):
                appl_voltage = voltage[:i-1]
                current = current[:i-1]
                #remove the tripped measurement
                break
            smu.source.voltage(v)
            appl_voltage[i] = smu.source.voltage()
            current[i] = smu.sense.current()
            print(progress_bar_time(i+1, len(voltage)+1, time.time()-start_time))

    return appl_voltage, current

def smu_constant_source(smu, voltage, time_length, dt, delay, current_lim, nplc, funcs=None, func_args=None):
    smu.source.limit(current_lim)
    smu.source.delay(delay)
    #seconds delay between changing source and measurement
    smu.timeout(1000)
    #seconds for the SMU to respond to a command (including taking measurements)
    smu.sense.nplc(nplc)
    smu.source.voltage(voltage)
    buffer_name = "defbuffer1"
    buffer=smu.buffer(buffer_name)
    buffer.clear_buffer()
    smu.wait()
    buffer.write(f':TRIGger:LOAD "DurationLoop", {time_length}, {dt}')
    buffer_elements = ["timestamp","source_value", "measurement"]
    buffer.elements(buffer_elements)
    fetch_elements = [buffer.buffer_elements[element] for element in buffer.elements()]
    with smu.output_enabled.set_to(True):
        init_cur = buffer.ask(f":MEASure? '{buffer_name}', {','.join(fetch_elements)}").split(",")
        #take measurement to check if current limit will be tripped
        #if tripped then smu will apply the bias that provides the current limit
        if(smu.source.limit_tripped()):
            smu.source.voltage(init_cur[1])
            #to get a constant bias we re-set the voltage
            
        smu.sense.auto_zero_enabled(False)
        smu.initiate()
        #start the selected trigger function

        time.sleep(time_length+2)
        smu.sense.auto_zero_enabled(True)
        
        buf_len = buffer.number_of_readings()
        data = np.array(buffer.get_data(2,buf_len))

    split_data = np.array_split(data, buf_len-1)
    Tsplit_data = np.transpose(split_data)
    #splits data into arrays of measurements then transposes into arrays of elements

    timestamps = Tsplit_data[0]
    #convert timestamp into seconds
    #Definitely a better way to do this...
    seconds = np.array([float(stamp[-12:]) for stamp in timestamps])
    minutes = np.array([float(stamp[-15:-13]) for stamp in timestamps])
    hours = np.array([float(stamp[-18:-16]) for stamp in timestamps])
    times = hours*3600+minutes*60+seconds
    times = times-times[0]
    #splits seconds from timestamp string
    source = np.array(Tsplit_data[1], dtype=float)
    current = np.array(Tsplit_data[2], dtype=float)
    #times = [data[i] for i in range(data) if not i%3 ]

    return times, source, current

def power_wavelength_sweep(evo, rf, pm, wavs, delay, repeats, dt_repeat, funcs=None, func_args=None):
    powers = np.zeros_like(wavs)
    start_time = time.time()
    measurements = np.zeros(repeats)
    for i, wav in enumerate(wavs):
        pm.sense.correction.wavelength=wav
        rf.wavelength=wav
        time.sleep(delay)
        for j in range(repeats):
            measurements[j] = pm.read
            time.sleep(dt_repeat)
        powers[i]=sum(measurements)/len(measurements)
        print("Wavelength:{} nm\t\tPower:{} W\t\t\t".format(wav, powers[i]) + progress_bar_time(i+1, len(wavs)+1, time.time()-start_time))

    return powers

def power_smu_wavelength_sweep(evo, rf, pm, smu, wavs, voltage, current_lim, nplc, delay, repeats, dt_repeat, funcs=None, func_args=None):
    currents = np.zeros_like(wavs)
    powers = np.zeros_like(wavs)
    #How many power line cycles to measure over
    smu.source.limit(current_lim)
    smu.source.delay(1)
    #seconds delay between changing source and measurement
    smu.timeout(1000)
    #seconds for the SMU to respond to a command (including taking measurements)
    smu.sense.nplc(nplc)
    smu.source.voltage(voltage)
    buffer_name = "defbuffer1"
    buffer=smu.buffer(buffer_name)
    buffer.clear_buffer()
    smu.wait()
    buffer_elements = ["timestamp","source_value", "measurement"]
    buffer.elements(buffer_elements)
    fetch_elements = [buffer.buffer_elements[element] for element in buffer.elements()]
    evo.module_status
    # Check the Interlock status
    interlock = evo.interlock_reset()
    # Set the operating mode and get the operating mode in a single function call
    setup = evo.setup(1)

    # Get the output level
    #print('Level {}%'.format(nkt.register_read_u16(DEVICE_ID, 0x27) * 0.1))

    # Turn on the laser
    evo.emission=True
    #turns laser on if not already on

    time.sleep(1)
    start_time = time.time()
    #rf.amplitude = rf_power*10 #10=1%
    current_measurements = np.zeros(repeats)
    power_measurements = np.zeros(repeats)
    with smu.output_enabled.set_to(True):
        smu.sense.auto_zero_enabled(False)
        for i, wav in enumerate(wavs):
            pm.sense.correction.wavelength=wav
            rf.wavelength=wav
            time.sleep(delay)
            for j in range(repeats):
                current_measurements[j] = buffer.ask(f":MEASure? '{buffer_name}', {','.join(fetch_elements)}").split(",")[-1] 
                power_measurements[j] = pm.read
                time.sleep(dt_repeat)
            powers[i]= sum(power_measurements)/len(power_measurements)
            currents[i] = sum(current_measurements)/len(current_measurements)

            print("\nWavelength:{} nm".format(wav))
            print("Power:{} W\tCurrent:{} A".format( powers[i], currents[i]))
            print(progress_bar_time(i+1, len(wavs)+1, time.time()-start_time))
            if(funcs):
                for j, func in enumerate(funcs):
                    func_args[j][0] = func(i, wavs[:i+1], currents[i], *func_args[j])
                
    if(not funcs):
        return currents, powers
    else:
        return currents, func_args