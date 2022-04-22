# ot-reproductibility

Testing reproductibility with Opentrons robot

### Install

```
conda env create -f environment.yaml -n opentrons
```

### Serial dilution

Web ressources: https://protocols.opentrons.com/protocol/customizable_serial_dilution_ot2

Testing
```
opentrons_simulate src/customizable_serial_dilution_ot2.py -L labwares/
```