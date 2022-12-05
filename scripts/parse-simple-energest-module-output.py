#!/usr/bin/env python

import sys
import argparse
import os
from serde import serialize, deserialize # third party
from serde.json import from_json, to_json # third party 
from dataclasses import dataclass
import re
from typing import List, Optional

# contiki-ng/arch/cpu/msp430/rtimer-arch.h:45
RTIMER_ARCH_SECOND = 4096 * 8 # 32768 ticks

VOLTAGE = 3.0 # assume 3 volts battery (2 AA batteries)

# low power mode (LPM) 
# deep low power mode (Deep LPM)
# radio transmit (Radio Tx)
# radio receive (Radio Rx)
# - CPU is off, but the MCU is still running
CURRENT_MA = {
    "LPM" : (5.1 + 21) / 10**3, # mA  /datasheets/CPU_LPM_DLPM.png
    "Deep LPM" : (5.1 + 1) / 10**3, # mA see ../datasheets/CPU_LPM_DLPM.png
    'CPU': 1.8, # mA see ../datasheets/CPU_LPM_DLPM.png
    "Radio Tx" : 17.4, # mA see ../datasheets/Radio_Rx_Radio_Tx_params.png
    "Radio Rx" : 18.4, # mA see ../datasheets/Radio_Rx_Radio_Tx_params.png
}

STATES = CURRENT_MA.keys()

# example of a energest summary block
# the first number e.g. 10374 is the number of ticks spent in that state

# permil = parts per thousand = 1/1000

# ENERGEST: --- Period summary #3 (50 seconds)
# ENERGEST: Total time  :    1638401
# ENERGEST: CPU         :      72514/   1638401 (44 permil)
# ENERGEST: LPM         :    1565887/   1638401 (955 permil)
# ENERGEST: Deep LPM    :          0/   1638401 (0 permil)
# ENERGEST: Radio Tx    :        531/   1638401 (0 permil)
# ENERGEST: Radio Rx    :        387/   1638401 (0 permil)
# ENERGEST: Radio total :        918/   1638401 (0 permil)

@serialize
@deserialize
@dataclass
class EnergestSummary:
    summary_id: int # a number that increments each time a summary is printed
    total_time: int # in ticks aka the period_ticks = cpu + lpm + deep_lpm
    cpu: int # ticks
    lpm: int # ticks
    deep_lpm: int # ticks
    radio_tx: int # ticks
    radio_rx: int # ticks
    radio_total: int # ticks = radio_tx + radio_rx


# TODO: the regexp are kinda brittle, as they used fixed length for whitespace instead of a dynamic quantifier like '+'
# but they work for now.
def parse_summary(summary: List[str]) -> Optional[EnergestSummary]:
    """
    Parse a energest summary block and return a EnergestSummary object 
    Args:
        summary: a list of lines of the summary block, length should be 8
    Returns:
        return None if the summary block is not valid
    """ 
    if len(summary) != 8:
        return None

    # parse the summary
    period_summary_re = re.compile(r"ENERGEST: --- Period summary #(\d+) \((\d+) seconds\)")
    if (captures := period_summary_re.match(summary[0])):
        summary_id = int(captures.group(1))

    # parse the total time
    total_time_re = re.compile(r"ENERGEST: Total time  : +(\d+)")
    if (captures := total_time_re.match(summary[1])):
        total_time = int(captures.group(1))
    
    # parse the CPU time
    cpu_re = re.compile(r"ENERGEST: CPU         : +(\d+)/ +(\d+) \((\d+) permil\)")
    if (captures := cpu_re.match(summary[2])):
        cpu = int(captures.group(1))
    
    # parse the LPM time
    lpm_re = re.compile(r"ENERGEST: LPM         : +(\d+)/ +(\d+) \((\d+) permil\)")
    if (captures := lpm_re.match(summary[3])):
        lpm = int(captures.group(1))

    # parse the Deep LPM time
    deep_lpm_re = re.compile(r"ENERGEST: Deep LPM    : +(\d+)/ +(\d+) \((\d+) permil\)")
    if (captures := deep_lpm_re.match(summary[4])):
        deep_lpm = int(captures.group(1))
    
    # parse the Radio Tx time
    radio_tx_re = re.compile(r"ENERGEST: Radio Tx    : +(\d+)/ +(\d+) \((\d+) permil\)")
    if (captures := radio_tx_re.match(summary[5])):
        radio_tx = int(captures.group(1))

    # parse the Radio Rx time
    radio_rx_re = re.compile(r"ENERGEST: Radio Rx    : +(\d+)/ +(\d+) \((\d+) permil\)")
    if (captures := radio_rx_re.match(summary[6])):
        radio_rx = int(captures.group(1))
    
    # parse the Radio total time
    radio_total_re = re.compile(r"ENERGEST: Radio total : +(\d+)/ +(\d+) \((\d+) permil\)")
    if (captures := radio_total_re.match(summary[7])):
        radio_total = int(captures.group(1))

    

    return EnergestSummary(summary_id, total_time, cpu, lpm, deep_lpm, radio_tx, radio_rx, radio_total)
        
@serialize
@deserialize
@dataclass
class Report:
    summary: EnergestSummary
    total_charge_mC: float
    total_charge_mAh: float
    total_energy_mJ: float




if __name__ == '__main__':
    name_of_this_script = os.path.basename(sys.argv[0])

    parser = argparse.ArgumentParser(prog=name_of_this_script, description='Parse simple energest module output', epilog=f"example:\n{name_of_this_script} simple-energest.log")
    parser.add_argument('log_file', type=str, help='log file')
    parser.add_argument('--json', action='store_true', required=False, help='output in json format')
    parser.add_argument('--csv', action='store_true', required=False, help='output in csv format')
    parser.add_argument('--average', action='store_true', required=False, help='output average values, instead of per summary values')

    args = parser.parse_args()
    
    node_ticks = {}
    node_total_ticks = {}

    try:
        with open(args.log_file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError as e:
        print(f"File not found: {e}", file=sys.stderr)
        sys.exit(1)

    lines = list(filter(lambda x: 'ENERGEST: ' in x, lines))
    lines = list(map(lambda x: x.strip(), lines))

    indices_of_where_a_summary_block_starts = [i for i, line in enumerate(lines) if '--- Period summary' in line]

    # print(f"Found {len(indices_of_where_a_summary_block_starts)} summary blocks")

    # # split the lines into blocks based on the indices
    blocks = [lines[i:j] for i, j in zip(indices_of_where_a_summary_block_starts, indices_of_where_a_summary_block_starts[1:] + [None])]

    # # parse the blocks into energest summaries
    summaries = [parse_summary(block) for block in blocks]

    # print the summaries
    # for summary in summaries:
    #     print(summary)

    # known variables
    # - ticks - the number of ticks spent it a state
    # - RTIMER_SECOND - the number of ticks per second
    # - current_mA - the current consumption in that state in mA
    # - voltage - the voltage provided by the system to the component (radio or CPU) in mV
    # - period_sec - the duration of the accounting period in seconds
    # - period_ticks - the duration of the accounting period in ticks

    # TODO: handle --average

    reports: list[Report] = []
    
    for summary in summaries:
        total_avg_current_mA = 0
        period_ticks = summary.total_time
        period_sec = period_ticks / RTIMER_ARCH_SECOND

        current_cpu_mA = summary.cpu * CURRENT_MA['CPU'] / period_ticks
        current_lpm_mA = summary.lpm * CURRENT_MA['LPM'] / period_ticks
        current_deep_lpm_mA = summary.deep_lpm * CURRENT_MA['DEEP LPM'] / period_ticks
        current_radio_tx_mA = summary.radio_tx * CURRENT_MA['RADIO Tx'] / period_ticks
        current_radio_rx_mA = summary.radio_rx * CURRENT_MA['RADIO Rx'] / period_ticks

        total_avg_current_mA = current_cpu_mA + current_lpm_mA + current_deep_lpm_mA + current_radio_tx_mA + current_radio_rx_mA

        # total_avg_current_mA += summary.cpu * CURRENT_MA['CPU'] / period_ticks
        # total_avg_current_mA += summary.lpm * CURRENT_MA['LPM'] / period_ticks
        # total_avg_current_mA += summary.deep_lpm * CURRENT_MA['Deep LPM'] / period_ticks
        # total_avg_current_mA += summary.radio_tx * CURRENT_MA['Radio Tx'] / period_ticks
        # total_avg_current_mA += summary.radio_rx * CURRENT_MA['Radio Rx'] / period_ticks

        total_charge_mC = period_sec * total_avg_current_mA
        total_charge_mAh = total_charge_mC / 3600
        total_energy_mJ = total_charge_mC * VOLTAGE
        
        reports.append(Report(summary, total_charge_mC, total_charge_mAh=total_charge_mAh, total_energy_mJ=total_energy_mJ))



    if args.json:
        print(to_json(reports, indent=4))
    elif args.csv:
        print("summary_id,cpu,lpm,deep_lpm,radio_tx,radio_rx,radio_total,total_time,total_charge_mC,total_charge_mAh,total_energy_mJ")

        for report in reports:
            print(f"{report.summary.summary_id},{report.summary.cpu},{report.summary.lpm},{report.summary.deep_lpm},{report.summary.radio_tx},{report.summary.radio_rx},{report.summary.radio_total},{report.summary.total_time},{report.total_charge_mC},{report.total_charge_mAh},{report.total_energy_mJ}")
    else:
        for report in reports:
            summary = report.summary
            period_ticks = summary.total_time
            period_sec = period_ticks / RTIMER_ARCH_SECOND

            total_charge_mC = report.total_charge_mC
            total_charge_mAh = report.total_charge_mAh
            total_energy_mJ = report.total_energy_mJ

            print(f"""
Period {summary.summary_id}:
Total time: {summary.total_time} ticks
CPU time: {summary.cpu} ticks
LPM time: {summary.lpm} ticks
Deep LPM time: {summary.deep_lpm} ticks
Radio Tx time: {summary.radio_tx} ticks
Radio Rx time: {summary.radio_rx} ticks
Radio total time: {summary.radio_total} ticks
Total charge consumpion: {total_charge_mC:2f} mC ({total_charge_mAh:3f} mAh)
Total energy comsumption: {total_energy_mJ:2f} mJ
in {period_sec:2f} seconds
            """)
    
