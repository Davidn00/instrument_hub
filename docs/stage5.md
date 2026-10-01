# Stage 5 — Integración del interrogador óptico IBSEN

## 1. Objetivo

La Etapa 5 incorpora soporte para interrogadores ópticos de la familia **I-MON USB de Ibsen Photonics** dentro de InstrumentHub.

El objetivo es proporcionar una integración desacoplada del hardware que permita:

* Comunicación con el interrogador mediante USB Virtual COM Port.
* Implementación del protocolo de comandos I-MON.
* Identificación automática del instrumento.
* Detección del número de píxeles.
* Adquisición de espectros ópticos.
* Representación de los espectros mediante el modelo `Spectrum`.
* Conversión de posición de píxel a longitud de onda.
* Aplicación de la calibración individual del instrumento.
* Integración con la abstracción `Instrument` existente.
* Pruebas unitarias sin necesidad de disponer físicamente del interrogador.

---

# 2. Arquitectura

La integración se implementa mediante tres capas:

```text
IBSENInstrument
       │
       ▼
IBSENProtocol
       │
       ▼
SerialTransport
       │
       ▼
USB Virtual COM Port
       │
       ▼
I-MON USB
```

Cada capa tiene una responsabilidad específica.

### `IBSENInstrument`

Representa el dispositivo dentro de InstrumentHub.

Responsabilidades:

* Conectar y desconectar el dispositivo.
* Inicializar el protocolo.
* Iniciar y detener operaciones.
* Solicitar espectros.
* Aplicar la calibración.
* Exponer `read()` para compatibilidad con `Instrument`.
* Exponer `read_spectrum()` para conservar el espectro completo.

### `IBSENProtocol`

Implementa el protocolo específico del I-MON USB.

Responsabilidades:

* Construcción de comandos.
* Terminación mediante `CR`.
* Procesamiento de `ACK`.
* Procesamiento de `NAK`.
* Procesamiento de `BELL`.
* Envío de `ESC`.
* Identificación del dispositivo.
* Obtención del número de píxeles.
* Configuración del formato de datos.
* Lectura de intensidades.

### `SerialTransport`

Proporciona el transporte físico serial.

Responsabilidades:

* Apertura del puerto.
* Configuración del puerto.
* Escritura de bytes.
* Lectura de bytes.
* Lectura hasta delimitador.
* Cierre del puerto.

La separación permite probar `IBSENProtocol` sin conectar físicamente un interrogador.

---

# 3. Hardware soportado

La documentación utilizada durante el desarrollo corresponde a la familia:

* I-MON 256 USB.
* I-MON 512 USB.

El número de píxeles no se debe asumir únicamente a partir del nombre del modelo.

InstrumentHub consulta:

```text
*PARAmeter:PIXel?
```

para determinar la cantidad de píxeles del instrumento conectado.

Esto permite utilizar el mismo driver para diferentes variantes del I-MON.

---

# 4. Comunicación USB

El I-MON USB utiliza:

```text
USB 2.0
Virtual COM Port
```

La configuración serial utilizada por el driver es:

```text
Data bits: 8
Parity:    None
Stop bits: 1
Handshake: None
```

Por tanto:

```text
8N1
```

## Baudrates

El protocolo documenta los siguientes valores:

```text
38400
115200
921600
```

El valor utilizado por defecto por InstrumentHub es:

```text
921600
```

Ejemplo:

```python
instrument = IBSENInstrument.from_serial(
    device_id="ibsen-001",
    name="I-MON USB",
    port="COM3",
    calibration=calibration,
)
```

En Linux:

```python
instrument = IBSENInstrument.from_serial(
    device_id="ibsen-001",
    name="I-MON USB",
    port="/dev/ttyUSB0",
    calibration=calibration,
)
```

---

# 5. Control del protocolo

El protocolo I-MON utiliza los siguientes caracteres de control.

| Nombre | Hexadecimal | Uso                           |
| ------ | ----------: | ----------------------------- |
| ACK    |      `0x06` | Comando aceptado              |
| NAK    |      `0x15` | Comando rechazado             |
| BELL   |      `0x07` | Medición finalizada           |
| ESC    |      `0x1B` | Abortamiento de medición      |
| CR     |      `0x0D` | Terminación de comandos/datos |

Los comandos se transmiten terminados por `CR`.

Por ejemplo:

```text
*IDN?\r
```

---

# 6. Comandos utilizados

La integración utiliza principalmente los siguientes comandos.

## Identificación

```text
*IDN?
```

Permite obtener la identificación del instrumento.

Ejemplo documentado:

```text
JETI_MP_SERS
```

## Número de píxeles

```text
*PARAmeter:PIXel?
```

Devuelve la cantidad de píxeles del sensor.

Ejemplos:

```text
256
```

o:

```text
512
```

## Número de serie

```text
*PARAmeter:SERNumber?
```

Permite obtener el número de serie del dispositivo.

## Firmware

```text
*VERS?
```

Devuelve la versión de firmware.

## Formato de datos

InstrumentHub configura:

```text
*CONFigure:FORMat 4
```

El formato 4 corresponde al formato ASCII con valores separados por `CR`.

## Adquisición

La lectura se realiza mediante:

```text
*READ 4
```

El flujo esperado es:

```text
Host
 │
 │ *READ 4\r
 ▼
I-MON
 │
 │ ACK
 ▼
Host
 │
 │ espera
 ▼
I-MON
 │
 │ BELL
 ▼
Host
 │
 │ intensidad[0]\r
 │ intensidad[1]\r
 │ ...
 │ intensidad[N-1]\r
 ▼
Host
```

---

# 7. Formato de adquisición

En esta etapa se utiliza deliberadamente el formato ASCII 4.

El motivo es proporcionar inicialmente una implementación:

* fácil de inspeccionar;
* fácil de depurar;
* independiente del endianess;
* sencilla de validar;
* adecuada para pruebas unitarias.

Cada intensidad corresponde a un píxel.

Para un instrumento de 256 píxeles:

```text
pixel 0
pixel 1
pixel 2
...
pixel 255
```

Para un instrumento de 512 píxeles:

```text
pixel 0
pixel 1
pixel 2
...
pixel 511
```

Los valores representan cuentas del ADC.

El ADC del I-MON utiliza una representación de 16 bits:

```text
0 ... 65535
```

InstrumentHub valida que cada intensidad esté dentro de ese rango.

---

# 8. Modelo `Spectrum`

Los datos espectrales no se representan mediante `Measurement`, porque un espectro contiene múltiples puntos.

Se introduce:

```python
Spectrum
```

con los siguientes componentes:

```text
timestamp
device_id
wavelength[]
intensity[]
wavelength_unit
intensity_unit
metadata
```

Conceptualmente:

```text
Spectrum
│
├── timestamp
├── device_id
├── wavelength[]
│
└── intensity[]
```

Por ejemplo:

```text
wavelength = [1525.0, 1525.1, 1525.2, ...]
intensity  = [1250,   1400,   1750,   ...]
```

Las dos matrices deben tener exactamente la misma longitud.

---

# 9. Diferencia entre `read()` y `read_spectrum()`

La interfaz general `Instrument` de InstrumentHub utiliza:

```python
read()
```

y devuelve:

```python
Measurement
```

Un espectrómetro, sin embargo, genera un conjunto completo de datos.

Por eso `IBSENInstrument` implementa:

```python
read_spectrum()
```

que devuelve:

```python
Spectrum
```

Además implementa:

```python
read()
```

para conservar compatibilidad con la arquitectura existente.

`read()` genera una medición representativa del espectro utilizando:

```text
peak intensity
```

y conserva información adicional en `metadata`, incluyendo:

```text
peak_wavelength_nm
pixel_count
wavelength_nm
intensity_counts
```

Por tanto:

```text
read_spectrum()
       │
       ▼
Spectrum completo
```

mientras:

```text
read()
       │
       ▼
Measurement
       │
       ├── peak intensity
       ├── peak wavelength
       └── spectrum metadata
```

---

# 10. Calibración de longitud de onda

La longitud de onda no debe asumirse directamente a partir del índice del píxel.

El I-MON utiliza una calibración polinómica de quinto grado.

La ecuación es:

```text
λ(p) =
    A
    + B1*p
    + B2*p²
    + B3*p³
    + B4*p⁴
    + B5*p⁵
```

donde:

```text
p = posición del píxel
λ = longitud de onda
```

y:

```text
A
B1
B2
B3
B4
B5
```

son coeficientes específicos de cada unidad.

---

# 11. Coeficientes de calibración

Los coeficientes no deben ser inventados ni sustituidos por valores genéricos.

Deben proceder de la calibración individual del interrogador.

Las fuentes válidas incluyen:

1. Certificate of Conformance del instrumento.
2. Datos de calibración almacenados en el equipo.
3. Información proporcionada por el fabricante.

El modelo utilizado por InstrumentHub es:

```python
IBSENCalibration(
    a=...,
    b1=...,
    b2=...,
    b3=...,
    b4=...,
    b5=...,
)
```

---

# 12. Calibración almacenada en el instrumento

La documentación del fabricante describe un bloque de datos de calibración de longitud de onda.

La estructura utilizada para los seis coeficientes es:

```text
Offset       Campo
--------------------------------
0–15         A
16–31        B1
32–47        B2
48–63        B3
64–79        B4
80–95        B5
```

Los coeficientes están almacenados como texto ASCII.

Ejemplo conceptual:

```text
-2.123456789E-05
```

Cada campo tiene una longitud de 16 bytes.

InstrumentHub implementa:

```python
IBSENCalibration.from_user_block(...)
```

para interpretar estos seis coeficientes.

---

# 13. Checksum de calibración

El bloque de calibración también contiene información de checksum.

Sin embargo, la documentación disponible durante el desarrollo no establece de forma suficientemente inequívoca el algoritmo necesario para reproducir y validar dicho checksum.

Por esta razón:

**InstrumentHub no inventa ni aproxima el algoritmo de checksum.**

La implementación actual:

* interpreta los seis campos de coeficientes;
* valida que sean valores ASCII numéricos;
* valida que el bloque tenga la longitud mínima esperada.

La validación completa del checksum podrá implementarse cuando el algoritmo sea confirmado mediante documentación adicional del fabricante o mediante el código de referencia correspondiente.

---

# 14. Flujo completo de adquisición

La adquisición física sigue este flujo:

```text
IBSENInstrument
      │
      │ connect()
      ▼
SerialTransport
      │
      │ USB/VCP
      ▼
I-MON USB
      │
      │ *IDN?
      ▼
Device identification
      │
      │ *PARAmeter:PIXel?
      ▼
Pixel count
      │
      │ *CONFigure:FORMat 4
      ▼
ASCII format configured
      │
      │ *READ 4
      ▼
ACK
      │
      ▼
BELL
      │
      ▼
Intensity[0..N-1]
      │
      ▼
Raw Spectrum
      │
      │ Pixel → Calibration
      ▼
Wavelength[0..N-1]
      │
      ▼
Spectrum
```

---

# 15. Manejo de errores

El protocolo define diferentes códigos de error.

Entre los documentados se encuentran:

```text
16   Invalid format
20   Parameter argument
21   Configuration argument
22   Control argument
23   Read argument
24   Fetch argument
25   Measuring argument

101  Parameter checksum
102  User file checksum
103  User file 2 checksum

120  Overexposure
121  Underexposure
123  Adaption integration time

130  Shutter does not exist
131  No dark measurement
132  No reference measurement
133  No transmission measurement
137  No dark compensation

140  Calibration data
141  Calibration wavelength exceeded
147  Scan break

170–172 Flash errors
180–186 Calibration file errors
```

A nivel de transporte/protocolo, InstrumentHub distingue principalmente:

```text
IBSENProtocolError
IBSENCommandError
TimeoutError
```

Esto permite mantener separados:

* errores de comunicación;
* errores del protocolo;
* errores de configuración;
* errores producidos durante la adquisición.

---

# 16. Detención de una medición

El protocolo utiliza:

```text
ESC = 0x1B
```

para abortar una medición en ejecución.

InstrumentHub expone:

```python
await instrument.stop()
```

que termina enviando:

```text
ESC
```

Esto es especialmente importante para futuras implementaciones de adquisición continua.

---

# 17. Streaming

La documentación del I-MON indica que durante una operación de streaming no se deben enviar comandos normales al instrumento.

Por este motivo, la arquitectura de InstrumentHub mantiene separadas las operaciones:

```text
command mode
```

y:

```text
streaming mode
```

La Etapa 5 implementa inicialmente adquisición bajo demanda mediante:

```text
*READ 4
```

El streaming continuo queda como una evolución posterior del driver.

---

# 18. Formatos binarios

La documentación del fabricante define varios formatos binarios y formatos ASCII.

Entre ellos existen formatos con:

* palabras de 16 bits;
* byte order low/high;
* byte order high/low;
* longitud;
* checksum;
* información de wavelength.

En esta etapa se utiliza:

```text
Format 4
```

porque proporciona una primera implementación robusta y fácilmente verificable.

Los formatos binarios no se implementan hasta disponer de una definición inequívoca del algoritmo de checksum.

Esto evita introducir una implementación potencialmente incompatible con el hardware.

---

# 19. Pruebas

La integración incluye pruebas con un transporte simulado.

No es necesario disponer físicamente de un I-MON para ejecutar:

```text
tests/acquisition/test_ibsen_protocol.py
```

ni:

```text
tests/devices/test_ibsen_instrument.py
```

Las pruebas verifican:

* identificación;
* detección de píxeles;
* configuración del formato;
* procesamiento de `ACK`;
* procesamiento de `NAK`;
* procesamiento de `BELL`;
* adquisición ASCII;
* validación de intensidades;
* polinomio de calibración;
* lectura de bloques de calibración;
* integración con `IBSENInstrument`;
* conversión de píxeles a longitud de onda.

---

# 20. Validación

Ejecutar:

```bash
uv run pytest tests/acquisition/test_ibsen_protocol.py tests/devices/test_ibsen_instrument.py -q
```

Resultado esperado:

```text
5 passed
```

Posteriormente ejecutar la suite completa:

```bash
uv run pytest -q
```

Y las herramientas de calidad:

```bash
uv run ruff check .
```

```bash
uv run mypy app
```

```bash
uv run pre-commit run --all-files
```

---

# 21. Validación con hardware físico

La validación software no equivale todavía a una validación con un I-MON físico.

Cuando el instrumento esté conectado, se debe comprobar:

1. El puerto COM/TTY correcto.
2. Baudrate.
3. Identificación mediante `*IDN?`.
4. Número de píxeles mediante `*PARAmeter:PIXel?`.
5. Número de serie.
6. Versión de firmware.
7. Respuesta `ACK`.
8. Respuesta `BELL`.
9. Cantidad de intensidades recibidas.
10. Rango de intensidades.
11. Coeficientes de calibración.
12. Rango de longitud de onda resultante.
13. Posición de los máximos espectrales.
14. Repetibilidad entre adquisiciones.

Una primera prueba de hardware debe registrar estos datos antes de utilizar el instrumento en una adquisición continua.

---

# 22. Estructura resultante

Después de Etapa 5, la arquitectura relevante de InstrumentHub es:

```text
app/
├── acquisition/
│   ├── protocols/
│   │   ├── ascii.py
│   │   ├── base.py
│   │   ├── binary.py
│   │   └── ibsen.py
│   │
│   └── transports/
│       ├── __init__.py
│       └── serial.py
│
├── devices/
│   └── instruments/
│       ├── ibsen.py
│       ├── serial.py
│       └── tcp.py
│
└── models/
    ├── measurement.py
    ├── signal.py
    └── spectrum.py
```

---

# 23. Estado de Etapa 5

La Etapa 5 incorpora:

* [x] Investigación del protocolo I-MON USB.
* [x] Transporte serial.
* [x] Configuración 8N1.
* [x] Baudrates soportados.
* [x] Comandos I-MON.
* [x] ACK/NAK/BELL/ESC.
* [x] Identificación del instrumento.
* [x] Descubrimiento del número de píxeles.
* [x] Adquisición ASCII Format 4.
* [x] Modelo `Spectrum`.
* [x] Validación de intensidades de 16 bits.
* [x] Driver `IBSENInstrument`.
* [x] Calibración polinómica de quinto grado.
* [x] Lectura de coeficientes de calibración.
* [x] Pruebas unitarias con transporte simulado.
* [x] Documentación de arquitectura.
* [ ] Validación con I-MON físico.
* [ ] Streaming continuo.
* [ ] Formatos binarios con checksum.
* [ ] Persistencia de espectros.
* [ ] Visualización de espectros en tiempo real.

---

# 24. Resultado de la etapa

Al finalizar esta etapa, InstrumentHub dispone de una abstracción de hardware específica para el interrogador óptico I-MON USB:

```text
                 I-MON USB
                     │
                     │ USB
                     ▼
              SerialTransport
                     │
                     ▼
               IBSENProtocol
                     │
                     ▼
             IBSENInstrument
                     │
                     ▼
                  Spectrum
                     │
                     ▼
          Pixel → Wavelength
                     │
                     ▼
             Processing Pipeline
```

La arquitectura mantiene la separación entre:

```text
Transport
Protocol
Device
Domain Model
Processing
```

permitiendo reemplazar el transporte físico por un transporte simulado durante las pruebas.

La calibración de longitud de onda utiliza exclusivamente los coeficientes específicos del instrumento y no valores genéricos.

La implementación queda preparada para las siguientes etapas de InstrumentHub, especialmente adquisición continua, procesamiento de espectros, persistencia, visualización y análisis de señales ópticas.
