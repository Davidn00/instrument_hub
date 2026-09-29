# Stage 3 — Acquisition Pipeline

## Goal

Stage 3 introduces the acquisition core without coupling acquisition logic to FastAPI.

```text
Physical instrument / simulator
            |
            v
      Instrument interface
            |
            v
   Serial / TCP transport
            |
            v
       Raw bytes
            |
            v
        Frame decoder
            |
            v
          Frame
            |
            v
      Protocol parser
            |
            v
       Measurement
            |
            v
   AcquisitionManager
       |        |
       |        +--> throughput / errors / reconnects
       |
       +--> bounded async buffer
