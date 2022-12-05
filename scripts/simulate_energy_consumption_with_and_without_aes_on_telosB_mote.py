# %%
import random
from pprint import pp

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

# %%

# simulation parameters
NUM_PAYLOADS = 10**5
PAYLOAD_SIZE = 128  # bits
AES_ENCRYPTION = True
HAMMING_8_4_ENCODING = True


# see google sheets for the values
# cost is for the transmission of a single 128 bit message
# for hammming the size is doubled
cost = {
    'base': {
        'energy': 0.0000876347975, # mAh
        'time': 0.0, # seconds
        'payload_size': PAYLOAD_SIZE,

    },
    'with_software_aes': {
        'energy': 0.00008786787932, # mAh
        'time': 0.0, # seconds
        'payload_size': PAYLOAD_SIZE,
        'aes_encryption': True,
    },
    'with_hardware_aes': {
        'energy': 0.0000889883601294623, # mAh
        'time': 0.0,    # seconds
        'payload_size': PAYLOAD_SIZE,
    },
    'with_software_aes_and_8_4_hamming': {
        'energy': 0.0000911022232055664, # mAh
        'time': 0.0, # seconds
        'payload_size': PAYLOAD_SIZE * 2,
    },
    'with_hardware_aes_and_8_4_hamming': {
        'energy': 0.0000921822646247016, # mAh
        'time': 0.0,    # seconds
        'payload_size': PAYLOAD_SIZE * 2,
    },
}

noise_models = []


bit_error_probabilities: list[float] = [10**-i for i in range(1, 6)]

gen_random_payload = lambda size: random.getrandbits(size)

for probabilty in tqdm(bit_error_probabilities):
    for noise_model in noise_models:
        for configuration in cost.keys():

            packets_successfully_received = 0
            while packets_successfully_received < NUM_PAYLOADS:
                payload = gen_random_payload(cost[configuration]['payload_size'])
                # TODO use noise model to corrupt the payload


                # based on the configuration, check if the payload is too corrupted to be received
                # and if it is, discard it and generate a new one
                # if it is not, increment the counter

                if random.random() > probabilty:
                    packets_successfully_received += 1

      






# assume that it is more expensive to encrypt with software than hardware
cost_of_payload_transmission_without_sw_aes_and_fec = 0.5 * 2
cost_of_payload_transmission_with_sw_aes_but_without_fec = 0.6 * 2
cost_of_payload_transmission_with_sw_aes_and_fec = 1 * 2

cost_of_payload_transmission_without_hw_aes_and_fec = 0.5
cost_of_payload_transmission_with_hw_aes_but_without_fec = 0.6
cost_of_payload_transmission_with_hw_aes_and_fec = 1

# assume that the cost of transmitting the payload is constant over the time
# assume binary symmetric channel i.e. the probability of error is the same for both 0 and 1

# when forward error correction is used, the payload size is increased to 128 * 2 = 256 bits
# a (8,4) Hamming code is used, which means that 4 bits are encoded into 8 bits
# a (8,4) Hamming code, can correct up to 1 bit error in 8 bits

# number of packets that are dropped due to errors
dropped_packets: list[int] = [0 for _ in range(len(bit_error_probabilities))]
# assume that when a payload is dropped, the retranmission will be successful

payload: list[int] = [random.randint(0, 1) for _ in range(PAYLOAD_SIZE)]

for i, bep in tqdm(enumerate(bit_error_probabilities), desc="Running simulation"):
    dropped_packets[i] = 0
    for _ in tqdm(
        range(ITERATIONS), desc=f"going through simulation runs for BEP={bep:.0e}"
    ):
        # simulate the affect of the noisy channel on the payload
        noisy_payload = [
            (payload[i] ^ 1) if random.random() < bep else payload[i]
            for i in range(PAYLOAD_SIZE)
        ]
        # go over the payload in chunks of 8 bits and check if there is an error
        # if there are more than 1 error, the packet is dropped (the case when fec is used, else 0)
        diff: list[int] = [payload[i] ^ noisy_payload[i] for i in range(PAYLOAD_SIZE)]
        for j in range(0, PAYLOAD_SIZE, 8):
            if sum(diff[j : j + 8]) > 1:
                dropped_packets[i] += 1
                break

dropped_packets_mapped_to_their_bep = {
    bep: dropped_packets[i] for i, bep in enumerate(bit_error_probabilities)
}

# %%

pp(dropped_packets_mapped_to_their_bep)

# plot the results in a bar chart
# plot the results in a line plot, with the x-axis being the bitflip
# probability/(number of iterations) and the y-axis being the total energy consumption.

# %%
