# %%
import random
from pprint import pp
from abc import ABC, abstractmethod
from dataclasses import dataclass
import functools as ft
import itertools as it
import time
import operator as op

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm


# %%

# simulation parameters
NUM_PAYLOADS = 10**3
NUM_PAYLOADS_TO_TRY_BEFORE_GIVING_UP = NUM_PAYLOADS * 10 # if the number of received packets exceeds this number, the simulation for the current configuration is aborted
PAYLOAD_SIZE = 128  # bits
AES_ENCRYPTION = True
HAMMING_8_4_ENCODING = True

@dataclass
class Configuration:
    energy: float # mAh
    time: float # seconds
    payload_size: int # bits
    aes: bool # True if {soft,hard}ware AES is used
    hamming: bool # True if Hamming (8,4) encoding is used

    def __str__(self) -> str:
        return f'{self.energy} mAh, {self.time} s, {self.payload_size} bits, AES: {self.aes}, Hamming: {self.hamming}'



# see google sheets for the values
# cost is for the transmission of a single 128 bit message
# for hammming the size is doubled
cost = {
    'base': {
        'energy': 0.0000876347975, # mAh
        'time': 0.0, # seconds
        'payload_size': PAYLOAD_SIZE,
        'aes': False,
        'hamming': False,

    },
    'with_software_aes': {
        'energy': 0.00008786787932, # mAh
        'time': 0.0, # seconds
        'payload_size': PAYLOAD_SIZE,
        'aes': True,
        'hamming': False,
    },
    'with_hardware_aes': {
        'energy': 0.0000889883601294623, # mAh
        'time': 0.0,    # seconds
        'payload_size': PAYLOAD_SIZE,
        'aes': True,
        'hamming': False,
    },
    'with_software_aes_and_8_4_hamming': {
        'energy': 0.0000911022232055664, # mAh
        'time': 0.0, # seconds
        'payload_size': PAYLOAD_SIZE * 2,
        'aes': True,
        'hamming': True,
    },
    'with_hardware_aes_and_8_4_hamming': {
        'energy': 0.0000921822646247016, # mAh
        'time': 0.0,    # seconds
        'payload_size': PAYLOAD_SIZE * 2,
        'aes': True,
        'hamming': True,
    },
}

configurations: dict[str, Configuration] = {
    name: Configuration(**values)
    for name, values in cost.items()
}

pp(configurations)

#%%

class NoiseModel(ABC):
    @abstractmethod
    def apply_noise(self, payload: list[int]) -> list[int]:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass


class BinarySymmetricChannel(NoiseModel):
    def __init__(self, p: float):
        assert 0 <= p <= 1, 'p must be between 0 and 1, but is {}'.format(p)
        self.p = p

    def apply_noise(self, payload: list[int]) -> list[int]:
        length = len(payload)
        assert length > 0, 'payload must not be empty, but is {}'.format(payload)

        noise = [1 if random.random() < self.p else 0 for _ in range(length)]
        return [a ^ b for a, b in zip(payload, noise)]

    def get_name(self) -> str:
        return 'BSC({})'.format(self.p)
    

class GilbertElliotChannel(NoiseModel):
    def __init__(self, p: float, r: float, initial_state_is_good: bool):
        assert 0 <= p <= 1, 'p must be between 0 and 1, but is {}'.format(p)
        assert 0 <= r <= 1, 'r must be between 0 and 1, but is {}'.format(r)
        self.p = p
        self.r = r
        self.state_is_good = initial_state_is_good


    def apply_noise(self, payload: list[int]) -> list[int]:
        length = len(payload)
        assert length > 0, 'payload must not be empty, but is {}'.format(payload)

        noisy_payload: list[int] = []
        for bit in payload:
            if self.state_is_good:
                if random.random() < self.p:
                    self.state_is_good = False
            else:
                if random.random() < self.r:
                    self.state_is_good = True

            noisy_payload.append(bit ^ 1 if not self.state_is_good else bit)

        return noisy_payload
            

    def get_name(self) -> str:
        return 'Gilbert-Elliot Model({},{})'.format(self.p, self.r)



noise_models: list[NoiseModel] =  [
    BinarySymmetricChannel(0.1),
    BinarySymmetricChannel(0.01),
    BinarySymmetricChannel(0.001),
    BinarySymmetricChannel(0.0001),
    BinarySymmetricChannel(0.00001),

    # GilbertElliotChannel(0.1, 0.5, True),  
    GilbertElliotChannel(0.001, 0.1, True),
    GilbertElliotChannel(0.001, 0.3, True),
    GilbertElliotChannel(0.0001, 0.1, True),
] 

#%%

class OrderingScheme(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def order(self, payload: list[int]) -> list[int]:
        pass

    @abstractmethod
    def reorder(self, payload: list[int]) -> list[int]:
        pass


class NoOrdering(OrderingScheme):
    def get_name(self) -> str:
        return 'No Ordering'

    def order(self, payload: list[int]) -> list[int]:
        return payload

    def reorder(self, payload: list[int]) -> list[int]:
        return payload



# NO INTERLEAVE
# 0, 1, 2, 3, 4, 5, 6, 7,   | 8, 9, 10, 11, 12, 13, 14, 15
# 16, 17, 18, 19, 20, 21,   | 22, 23, 24, 25, 26, 27, 28, 29, 30, 31
# 32, 33, 34, 35, 36, 37,   | 38, 39, 40, 41, 42, 43, 44, 45, 46, 47
# 48, 49, 50, 51, 52, 53,   | 54, 55, 56, 57, 58, 59, 60, 61, 62, 63
# 64, 65, 66, 67, 68, 69,   | 70, 71, 72, 73, 74, 75, 76, 77, 78, 79
# 80, 81, 82, 83, 84, 85,   | 86, 87, 88, 89, 90, 91, 92, 93, 94, 95
# 96, 97, 98, 99, 100, 101, | 102, 103, 104, 105, 106, 107, 108, 109, 110, 111
# 112, 113, 114, 115, 116,  | 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127


# WITH INTERLEAVE
# 0, 8, 16, 24, 32, 40, 48, 56,  | 64, 72, 80, 88, 96, 104, 112, 120
# 1, 9, 17, 25, 33, 41, 49, 57,  | 65, 73, 81, 89, 97, 105, 113, 121
# 2, 10, 18, 26, 34, 42, 50, 58, | 66, 74, 82, 90, 98, 106, 114, 122
# 3, 11, 19, 27, 35, 43, 51, 59, | 67, 75, 83, 91, 99, 107, 115, 123
# 4, 12, 20, 28, 36, 44, 52, 60, | 68, 76, 84, 92, 100, 108, 116, 124
# 5, 13, 21, 29, 37, 45, 53, 61, | 69, 77, 85, 93, 101, 109, 117, 125
# 6, 14, 22, 30, 38, 46, 54, 62, | 70, 78, 86, 94, 102, 110, 118, 126
# 7, 15, 23, 31, 39, 47, 55, 63, | 71, 79, 87, 95, 103, 111, 119, 127
class OctetInterleaving(OrderingScheme):
    def get_name(self) -> str:
        return 'Octet Interleaving'

    def order(self, payload: list[int]) -> list[int]:
        assert len(payload) % 8 == 0, 'payload must be a multiple of 8, but is {}'.format(payload)
     
        return np.array(payload) \
            .reshape((len(payload) // 8, 8)) \
            .transpose() \
            .reshape(-1) \
            .tolist()

     
    def reorder(self, payload: list[int]) -> list[int]:
        assert len(payload) % 8 == 0, 'payload must be a multiple of 8, but is {}'.format(payload)

        return np.array(payload) \
            .reshape((8, len(payload) // 8)) \
            .transpose() \
            .reshape(-1) \
            .tolist()

ordering_schemes: list[OrderingScheme] = [
    NoOrdering(),
    OctetInterleaving(),
]



#%%

@dataclass
class SimulationResult:
    name: str
    total_energy: float
    total_cumulative_energy_over_payloads: list[float]
    total_time: float
    total_cumulative_time_over_payloads: list[float]
    payload_size: int
    num_payloads: int
    aes_encryption: bool
    hamming_8_4_encoding: bool
    noise_model: NoiseModel
    ordering_scheme: OrderingScheme
    concede: bool = False

#%%
gen_random_payload = lambda size: [random.randint(0, 1) for _ in range(size)]

simulation_results: list[SimulationResult] = []

pbar0 = tqdm(total=len(noise_models) * len(ordering_schemes) * len(configurations.keys()), desc='configurations')

for name, configuration in configurations.items():
    for noise_model in noise_models:
        for ordering_scheme in ordering_schemes:
            pbar0.set_description('configurations: {} noise model: {} ordering scheme: {}'.format(name, noise_model.get_name(), ordering_scheme.get_name()))
            pbar0.update(1)

            pbar1 = tqdm(total=NUM_PAYLOADS, desc='{} - {}'.format(name, noise_model.get_name()))

            print(f'configuration: {name}, noise model: {noise_model.get_name()}, ordering scheme: {ordering_scheme.get_name()}', end='\r')

            total_energy: float = 0.0
            total_time: float = 0.0
            cummulitive_energy_used: list[float] = []
            cummulitive_time_used: list[float] = []

            payloads_successfully_received = 0
            payloads_received = 0

            payload_size: int = configuration.payload_size
            max_bit_error_tolerance_per_byte = 1 if configuration.hamming else 0

            while payloads_successfully_received < NUM_PAYLOADS and payloads_received < NUM_PAYLOADS_TO_TRY_BEFORE_GIVING_UP:
                payloads_received += 1
                total_energy += configuration.energy
                total_time += configuration.time

                payload: list[int] = gen_random_payload(payload_size)
                # simulate ordering of the bits in the payload
                ordered_payload: list[int] = ordering_scheme.order(payload)
                # simulate applying the noise model
                noisy_payload: list[int] = noise_model.apply_noise(ordered_payload)
                # simulate reordering of the bits in the payload
                reordered_payload: list[int] = ordering_scheme.reorder(noisy_payload)

                # based on the configuration, check if the payload is too corrupted to be received
                # and if it is, discard it and generate a new one
                # if it is not, increment the counter
                payload_diff: list[int] = [a ^ b for a, b in zip(payload, reordered_payload)]

                error_detected: bool = False
                for i in range(0, payload_size, 8):
                    byte = payload_diff[i:i+8]
                    if sum(byte) > max_bit_error_tolerance_per_byte:
                        # error detected, discard payload and try again
                        # print('error detected')
                        error_detected = True
                        break

                if not error_detected:        
                    # store the cummulatively used energy and time
                    # for the number of payloads successfully received
                    payloads_successfully_received += 1
                    cummulitive_energy_used.append(total_energy)
                    cummulitive_time_used.append(total_time)
                    pbar1.update(1)

            
            print(f"""
configuration: {name}
noise model: {noise_model.get_name()}
total energy: {total_energy}
total time: {total_time}
payloads received: {payloads_received}
payloads successfully received: {payloads_successfully_received}

""")
            pbar1.close()
            
            concede = payloads_received == NUM_PAYLOADS_TO_TRY_BEFORE_GIVING_UP
            if concede:
                print('conceded')

            simulation_results.append(SimulationResult(
                name=f'{name} - {noise_model.get_name()} - {ordering_scheme.get_name()}',
                total_energy= total_energy,
                total_cumulative_energy_over_payloads=cummulitive_energy_used,
                total_time= total_time,
                total_cumulative_time_over_payloads=cummulitive_time_used,
                payload_size=payload_size,
                num_payloads=payloads_received,
                aes_encryption=configuration.aes,
                hamming_8_4_encoding=configuration.hamming,
                noise_model=noise_model,
                ordering_scheme=ordering_scheme,
                concede=concede
            ))
      
print('simulation done')


#%%

print(len(simulation_results))

for simulation_result in simulation_results:
    print(simulation_result.name)
    print(simulation_result.num_payloads)
    print(simulation_result.total_energy)
    print(simulation_result.total_time)

    print()



#%%

for simulation_result in simulation_results:
    if simulation_result.concede:
        print(f'{simulation_result.name} conceded')
        continue

    plt.plot(np.arange(1, NUM_PAYLOADS + 1), simulation_result.total_cumulative_energy_over_payloads, label=simulation_result.name)

plt.xlabel('number of payloads received')
plt.ylabel('cumulative energy used')
plt.legend()
plt.grid()
plt.show()

