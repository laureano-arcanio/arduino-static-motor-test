# Static Rocket Motor Tester

Arduino UNO / Nano code for measuring the thrust and pressure of model rocket motors.

## Hardware

- Arduino Uno / Nano
- SD card reader with SPI interface
- Load cell with H711X amplifier
- Relay
- Push button
- 2 LEDs with resistors
- 1 pressure transducer (0–5V)

## Test Sequence

1. **Setup:** Load cell calibration and SD card check.
2. If an error occurs, the LEDs will remain off. If the system is ready for ignition, both LEDs will turn on.
3. **Standby state:** The system remains ready for ignition, with both LEDs on indefinitely.
4. Pressing the button starts a 30-second countdown. Both LEDs begin blinking.
5. The ignition relay closes, and data recording to the SD card begins.
6. After 10 seconds, the relay opens as a safety measure.
7. Data recording continues for another 120 seconds.
8. **End of sequence.**

## Data Output

The output is a CSV file named `STATIC_1.csv`. The number (1) is generated based on the number of existing files on the SD card.

The output format is:

| Time | Code | Weight | ADC Value |
| ---- | ---- | ------ | --------- |
| 772  | 40   | 0      | 0         |
| 782  | 60   | 3.2    | 10        |
| 792  | 60   | 5.4    | 15        |
| 802  | 40   | 10.3   | 30        |
| 812  | 40   | 30     | 50        |

- **Time:** Relative to when the Arduino is powered on.
- **Code:** Status values between 40 and 70, according to the following table:

```
STATUS_ERROR = 10
STATUS_READY = 20
STATUS_COUNTDOWN = 30
STATUS_IGNITION = 40
STATUS_BURNING = 60
STATUS_FINISHED = 70
```

- **Weight:** Load cell reading (mass).
- **ADC Value:** A value between 0 and 1023, corresponding to an input voltage range of 0–5V.

## Data Analysis

The Python script `src/analysis/performance.py` takes the CSV output and automatically calculates and generates the complete data analysis.

Its main features include:

1. Detection of the motor's operating start and end times.
2. Burn time estimation.
3. Calculation of thrust, total impulse, and specific impulse.
4. Maximum pressure and thrust calculations.

The output is a PDF report, as shown below:



Clarify the sensor and status definitionsExplain the ignition timing more precisely
