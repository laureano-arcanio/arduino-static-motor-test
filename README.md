
# Probador Estatico de Motores de Cohete
Codigo para Arduino UNO / Nano para medir fuerza y presion de Motores de coheteria modelo.

## Hardware

 - Arduino Uno / Nano
 - Lector de memorias SD con puerto SPI
 - Celda de carga con amplificador H711X
 - Relay
 - Push Button
 - 2 x Leds con resistencias
 - 1 Transductor de 0 a 5v

## Secuencia de prueba

 1. Setup: Calibracion de la Balanza y chequeo de Memoria
 2. Si hay algun error los leds no se encenderan. Si esta listo para ignicion, los 2 leds se encenderan.
 3. Estado de espera, de ignicion con 2 leds encendidos por tiempo indefinido.
 4. El boton inicia el conteo de 30 segundos. Los dos leds parpadean.
 5. El relay de ignicion se cierra y se comienzan a grabar los datos en la SD
 6. Luego de 10 segundos el relay se abre por seguridad.
 7. Se mantendran grabando datos por 120 segundos.
 8. Fin de la secuencia

## Salida de datos

La salida de datos es un archivo con nombre `STATIC_1.csv` el numero 1 se genera segunb la cantidad de archivos en la memoria.

El formato de salida es:

| Tiempo | Codigo | Peso | ADC Value|
|--|--|--|--|
| 772 | 40 | 0 | 0 |
| 782 | 60 | 3.2 | 10 |
| 792 | 60 | 5.4 | 15|
| 802 | 40 | 10.3 | 30 |
| 812 | 40 | 30 | 50 |

El tiempo es relativo al encendido del arduino
El codigo son valores entre 40 y 70 segun la tabla:

    STATUS_ERROR = 10
    STATUS_READY = 20
    STATUS_COUNTDOWN = 30
    STATUS_IGNITION = 40
    STATUS_BURNING = 60
    STATUS_FINISHED = 70

Peso es el valor de la celda de carga (masa).
ADC Value es un valor entre 0 y 1023 correspondiente a 0 - 5v

