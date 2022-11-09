#!/usr/bin/env python

import sys
import argparse
import os

RTIMER_ARCH_SECOND = 32768
VOLTAGE = 3.0 # assume 3 volts battery

# TODO: find datasheet for our board and update these values
# From Z1 node datasheet
CURRENT_MA = {
        "LPM" : 0.0001,
        "CPU" : 0.0001,
        "TX" : 17.0,
        "RX" : 17.0,
        "DEEP LPM" : 0.0001,
        "Total time" : 0.0001
    }

STATES = CURRENT_MA.keys()
    
if __name__ == '__main__':
    name_of_this_script = os.path.basename(sys.argv[0])

    parser = argparse.ArgumentParser(prog=name_of_this_script, description='Parse simple energest module output', epilog=f"example:\n{name_of_this_script} simple-energest.log")
    parser.add_argument('log_file', type=str, help='log file')

    args = parser.parse_args()
    
    node_ticks = {}
    node_total_ticks = {}

    with open(args.log_file, 'r') as f:
        lines = f.readlines()
        lines = filter(lambda x: 'INFO: Energest' in x, lines)
        for line in lines:
            print(line)
            fields = line.split()
            try:
                node = int(fields[1])
            except Exception as ex:
                print("Failed to process line '{}': {}".format(line, ex), file=sys.stderr)
                continue
                
            if node not in node_ticks:
                # initialize to zero
                node_ticks[node] = { u : 0  for u in STATES }
                node_total_ticks[node] = 0

            try:
                state_index = 5
                state = fields[state_index]
                tick_index = state_index + 2
                if state not in STATES:
                    state = fields[state_index] + " " + fields[state_index+1]
                    tick_index += 1
                    if state not in STATES:
                        # add to the total time
                        if state == "Total time":
                            node_total_ticks[node] += int(fields[tick_index])
                        continue
                # add to the time spent in specific state
                ticks = int(fields[tick_index][:-1])
                node_ticks[node][state] += ticks
            except Exception as ex:
               print("Failed to process line '{}': {}".format(line, ex), file=sys.stderr)

    nodes = sorted(node_ticks.keys())

    for node in nodes:
        total_avg_current_mA = 0
        period_ticks = node_total_ticks[node]
        period_seconds = period_ticks / RTIMER_ARCH_SECOND
        for state in STATES:
            ticks = node_ticks[node].get(state, 0)
            current_mA = CURRENT_MA[state]
            state_avg_current_mA = ticks * current_mA / period_ticks
            total_avg_current_mA += state_avg_current_mA
        total_charge_mC = period_ticks * total_avg_current_mA / RTIMER_ARCH_SECOND
        total_energy_mJ = total_charge_mC * VOLTAGE
        print("Node {}: {:.2f} mC ({:.3f} mAh) charge consumption, {:.2f} mJ energy consumption in {:.2f} seconds".format(
            node, total_charge_mC, total_charge_mC / 3600.0, total_energy_mJ, period_seconds))         
    