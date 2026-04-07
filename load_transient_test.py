import pyvisa
import time
import csv
import statistics
from datetime import datetime

# --- Configuration & Parameters ---
# (Assuming 3.3V Rail based on previous tests, 50mV limit)
PSU_ADDR = 'USB0::0x05E6::0x2230::1234567::INSTR' # Keithley 2230
LOAD_ADDR = 'USB0::0x05E6::0x2380::7654321::INSTR' # Keithley 2380
SCOPE_ADDR = 'USB0::0x0957::0x17A6::MY123456::INSTR' # Keysight DSOX

TEST_RAIL = "3.3V"
V_TOLERANCE_PP = 0.050  # 50mV peak-to-peak limit
TRANSIENT_LOW_A = 0.5   # 0.5 Amps
TRANSIENT_HIGH_A = 2.5  # 2.5 Amps
TEST_ITERATIONS = 5

def main():
    rm = pyvisa.ResourceManager()
    results = []

    try:
        print("Initializing Instruments...")
        psu = rm.open_resource(PSU_ADDR)
        load = rm.open_resource(LOAD_ADDR)
        scope = rm.open_resource(SCOPE_ADDR)

        # 1. Setup Power Supply (Input)
        psu.write('*RST')
        psu.write('APPLy 5.0, 4.0') # 5V input, 4A limit

        # 2. Setup Electronic Load (Transient Mode)
        load.write('*RST')
        load.write('SOUR:FUNC CURR')
        load.write('SOUR:TRAN:MODE CONT') # Continuous transient
        load.write(f'SOUR:TRAN:ALEV {TRANSIENT_LOW_A}')
        load.write(f'SOUR:TRAN:BLEV {TRANSIENT_HIGH_A}')
        load.write('SOUR:TRAN:FREQ 10') # 10 Hz pulse

        # 3. Setup Oscilloscope
        scope.write('*RST')
        scope.write('CHAN1:DISP ON')
        scope.write('CHAN1:COUP AC') # AC Coupling for ripple/transient
        scope.write('CHAN1:BWL ON')  # 20MHz Bandwidth limit
        scope.write('TRIG:MODE EDGE')
        
        print("Starting Test Sequence...")
        psu.write('OUTP ON')
        time.sleep(1) # Let power stabilize
        load.write('INP ON') # Turn on load
        
        # 4. Execution Loop
        for i in range(1, TEST_ITERATIONS + 1):
            time.sleep(2) # Wait for transient events to occur
            
            # Measure Peak-to-Peak Voltage
            scope.write('MEAS:VPP? CHAN1')
            vpp_str = scope.read()
            vpp_val = float(vpp_str)
            
            # Determine Pass/Fail
            status = "PASS" if vpp_val < V_TOLERANCE_PP else "FAIL"
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"Iteration {i}: Vp-p = {vpp_val:.4f}V -> {status}")
            results.append([timestamp, i, TEST_RAIL, vpp_val, status])
            
            # Capture and Save Waveform (Screen Image)
            scope.write(':DISPlay:DATA? PNG, COLOR')
            image_data = scope.read_raw()
            filename = f"Transient_Waveform_Iter{i}_{datetime.now().strftime('%H%M%S')}.png"
            with open(filename, 'wb') as f:
                f.write(image_data)
                
    except Exception as e:
        print(f"TEST FAILED OR INTERRUPTED: {e}")
        
    finally:
        # 5. Teardown & Safety (Always runs, even if code crashes)
        print("Safely shutting down instruments...")
        try:
            load.write('INP OFF')
            psu.write('OUTP OFF')
        except:
            pass # Ignore errors during emergency shutdown

    # 6. Generate Report
    generate_report(results)

def generate_report(results):
    print("\nGenerating CSV Report...")
    csv_filename = f"Transient_Test_Report_{datetime.now().strftime('%Y%m%d')}.csv"
    
    vpp_values = [row[3] for row in results]
    if not vpp_values:
        return

    # Calculate Statistics
    avg_vpp = statistics.mean(vpp_values)
    max_vpp = max(vpp_values)
    min_vpp = min(vpp_values)
    overall_status = "PASS" if max_vpp < V_TOLERANCE_PP else "FAIL"

    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write Header
        writer.writerow(['Timestamp', 'Iteration', 'Rail', 'Vp-p (V)', 'Status'])
        # Write Data
        writer.writerows(results)
        # Write Statistics
        writer.writerow([])
        writer.writerow(['--- Statistics ---'])
        writer.writerow(['Average Vp-p (V)', f"{avg_vpp:.4f}"])
        writer.writerow(['Max Vp-p (V)', f"{max_vpp:.4f}"])
        writer.writerow(['Min Vp-p (V)', f"{min_vpp:.4f}"])
        writer.writerow(['Overall Result', overall_status])
        
    print(f"Report saved to {csv_filename}")

if __name__ == "__main__":
    main()