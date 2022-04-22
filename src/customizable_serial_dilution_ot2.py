#!/usr/bin/env python

"""Customizable serial dilution protocol for Opentrons

Labware preparation:
- diluent: pre-loaded in row 1 of trough
- samples/standards: pre-loaded in Column 1 of a standard 96-well plate

This is a modified version from https://protocols.opentrons.com/protocol/customizable_serial_dilution_ot2.
"""

def get_values(*names):
    import yaml
    _all_values = yaml.safe_load("""
        pipette_type: p300_multi_gen2
        mount_side: left
        tip_rack: tipone_yellow_3dprinted_96_tiprack_300ul  # custom labware
        trough_type: citadel_12_wellplate_22000ul  # custum labware
        plate_type: black_96_wellplate_200ul_pcr  # custom labware
        dilution_factor: 3
        num_of_dilutions: 10
        total_mixing_volume: 150
        blank_on: true
        tip_use_strategy: never
        air_gap_volume: 10
    """)
    return [_all_values[n] for n in names]


"""DETAILS."""
metadata = {
    'protocolName': 'Customizable Serial Dilution',
    'author': 'Opentrons <protocols@opentrons.com>',
    'source': 'Protocol Library',
    'apiLevel': '2.11'
    }


def run(protocol_context):
    """PROTOCOL BODY."""
    [
        pipette_type, mount_side,
        tip_rack, trough_type,
        plate_type, dilution_factor, num_of_dilutions,
        total_mixing_volume, blank_on,
        tip_use_strategy, air_gap_volume
    ] = get_values(  # noqa: F821
        'pipette_type', 'mount_side',
        'tip_rack', 'trough_type',
        'plate_type', 'dilution_factor', 'num_of_dilutions',
        'total_mixing_volume', 'blank_on',
        'tip_use_strategy', 'air_gap_volume'
    )
    # check for bad setup here
    if not 1 <= num_of_dilutions <= 11:
        raise Exception('Enter a number of dilutions between 1 and 11')

    if num_of_dilutions == 11 and blank_on == 1:
        raise Exception('No room for blank with 11 dilutions')

    # labware
    trough = protocol_context.load_labware(trough_type, '2')
    plate = protocol_context.load_labware(plate_type, '3')
    tipracks = [protocol_context.load_labware(tip_rack, '1')]  # list expected

    # pipette
    pipette = protocol_context.load_instrument(
        pipette_type, mount=mount_side, tip_racks=tipracks
    )

    # reagents
    diluent = trough.wells()[0]

    transfer_volume = total_mixing_volume / dilution_factor
    diluent_volume = total_mixing_volume - transfer_volume

    if 'multi' in pipette_type:
        dilution_destination_sets = [
            [row] for row in plate.rows()[0][1:num_of_dilutions]
        ]
        dilution_source_sets = [
            [row] for row in plate.rows()[0][:num_of_dilutions-1]
        ]
        blank_set = [plate.rows()[0][num_of_dilutions+1]]

    else:
        dilution_destination_sets = plate.columns()[1:num_of_dilutions]
        dilution_source_sets = plate.columns()[:num_of_dilutions-1]
        blank_set = plate.columns()[num_of_dilutions]

    all_diluent_destinations = [
        well for set in dilution_destination_sets for well in set]

    pipette.pick_up_tip()
    for dest in all_diluent_destinations:
        # Distribute diluent across the plate to the the number of samples
        # And add diluent to one column after the number of samples for a blank
        pipette.transfer(
                diluent_volume,
                diluent,
                dest,
                air_gap=air_gap_volume,
                new_tip='never')
    pipette.drop_tip()

    # Dilution of samples across the 96-well flat bottom plate
    if tip_use_strategy == 'never':
        pipette.pick_up_tip()
    for source_set, dest_set in zip(dilution_source_sets,
                                    dilution_destination_sets):
        for s, d in zip(source_set, dest_set):
            pipette.transfer(
                    transfer_volume,
                    s,
                    d,
                    air_gap=air_gap_volume,
                    mix_after=(5, total_mixing_volume/2),
                    new_tip=tip_use_strategy)
    if tip_use_strategy == 'never':
        pipette.drop_tip()

    if blank_on:
        pipette.pick_up_tip()
        for blank_well in blank_set:
            pipette.transfer(
                    diluent_volume,
                    diluent,
                    blank_well,
                    air_gap=air_gap_volume,
                    new_tip='never')
        pipette.drop_tip()
