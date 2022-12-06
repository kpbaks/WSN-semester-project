#include "contiki.h"
#include "sys/log.h"
#define LOG_MODULE "App"
#define LOG_LEVEL LOG_LEVEL_INFO

#include "lib/aes-128.h" // The implementation (either software or hardware) is set in ./project-conf.h
#include "net/netstack.h"
#include "net/nullnet/nullnet.h"

#include "dev/leds.h" 
#include "dev/light-sensor.h"

// for timing measurements RTIMER_NOW() AND RTIMER_SECOND
#include "sys/rtimer.h"


#include "../energest-utils.h"




#include <string.h> // for memcpy, memset


#define AES_128_BLOCK_LENGTH 16 // 128 bits
// #define SEND_INTERVAL (CLOCK_SECOND * 5)
#define SEND_INTERVAL (CLOCK_SECOND * 2.5)
#define LIGHT_SENSOR_READ_INTERVAL (CLOCK_SECOND * 0.25)


static uint32_t get_light() {
	return 10 * light_sensor.value(LIGHT_SENSOR_PHOTOSYNTHETIC) / 7;
}

// static void print_aes_block_as_hex(uint8_t *block) {
// 	for (int i = 0; i < AES_128_BLOCK_LENGTH; i++) {
// 		LOG_INFO_("%02x ", block[i]);
// 	}
// 	LOG_INFO_("\n");
// }



// Encode 8 bits of data into 2 (8,4) hamming codes concatenated
// into a short word (16 bits)
// The encoding of the upper 4 bits is stored in the upper 8 bits
// of the output word, and the encoding of the lower 4 bits is
// stored in the lower 8 bits of the output word.
uint16_t hamming_8_4_encode(uint8_t byte) {

  // lookup table for (8,4) hamming code
  // 4 data bits -> 8 hamming code bits
  // (d1,d2,d3,d4) -> (p1,p2,d1,p3,d2,d3,d4,p4)
  // the 0th is used for error detection, and is the parity of the encoded byte
  // the 1st is used for error correction, and is the parity of
  //
  // clang-format off
static const uint8_t hamming_8_4_encode_lut[16] = {
    0b00000000, // 0b0000 [0]
	0b11010010, // 0b0001 [1]
	0b01010101, // 0b0010 [2]
	0b10000111, // 0b0011 [3]
	0b10011001, // 0b0100 [4]
	0b01001011, // 0b0101 [5]
    0b11001100, // 0b0110 [6]
	0b00011110, // 0b0111 [7]
	0b11100001, // 0b1000 [8]
	0b00110011, // 0b1001 [9]
	0b10110100, // 0b1010 [10]
	0b01100110, // 0b1011 [11]
    0b01111000, // 0b1100 [12]
	0b10101010, // 0b1101 [13]
	0b00101101, // 0b1110 [14]
	0b11111111, // 0b1111 [15]
};
  // clang-format on

  const uint8_t upper4 = byte & 0xf0;
  const uint8_t lower4 = byte & 0x0f;

  const uint8_t upper4_encoded = hamming_8_4_encode_lut[upper4 >> 4];
  const uint8_t lower4_encoded = hamming_8_4_encode_lut[lower4];

  const uint16_t encoded =
      ((uint16_t)upper4_encoded << 8) | (uint16_t)lower4_encoded;
  return encoded;
}

void encode_128_bit_aes_block_with_8_4_hamming_code(const uint8_t *data,
                                                    uint16_t *hamming_code) {
  for (int i = 0; i < 16; i++) {
    const uint16_t encoded = hamming_8_4_encode(data[i]);
    hamming_code[i] = encoded;
  }
}


PROCESS(main_process, "main_process");

AUTOSTART_PROCESSES(&main_process);

PROCESS_THREAD(main_process, ev, data) {

	static struct etimer periodic_timer;
  static struct etimer light_sample_rate_periodic_timer;

	static uint32_t count = 0;
	// static uint32_t light = 0;
	static uint8_t encrypted[16] = {0};
  static rtimer_clock_t t_start, t_end, t_elapsed;

	static uint16_t hamming_encoded[16] = {0};
	// static clock_time_t t_total = 0;
	// static clock_time_t t_start = 0;
	// static clock_time_t t_end = 0;

	static const uint8_t key[16] = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
	0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x10};

	PROCESS_BEGIN();

	SENSORS_ACTIVATE(light_sensor);
	// clock_init();

	// Set the timer to 10 seconds
	etimer_set(&periodic_timer, SEND_INTERVAL);
  etimer_set(&light_sample_rate_periodic_timer, LIGHT_SENSOR_READ_INTERVAL);


	AES_128.set_key(key);

	// We reuse the same buffer for the encrypted data to be sent
	// As the size of the data is 16 bytes, we can use the same buffer.
	nullnet_buf = (uint8_t *) &hamming_encoded;
	nullnet_len = sizeof(hamming_encoded);

  energest_utils_init();


	while (1) {
		PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&periodic_timer));
		// get the time right now
		// t_start = clock_time();

	    memset(encrypted, 0, sizeof(encrypted));


		static int i = 0;
		i = 1;
		i -= 1;
		for (i = 0; i < 4; i++) {
      etimer_reset(&light_sample_rate_periodic_timer);

			uint32_t light = get_light();
			uint8_t offset = i * 4;

			memcpy(encrypted + offset, &light, sizeof(uint32_t));
			// PROCESS_PAUSE(); // yield to other processes
			  PROCESS_WAIT_EVENT_UNTIL(
          etimer_expired(&light_sample_rate_periodic_timer));
		}

		// The last 8 bytes, are empty, as the the aes block size is 16 bytes
		// and we only need 4 bytes for the light value, and 4 bytes for the counter.
		// memset(encrypted, 0x00, sizeof(encrypted));
		// memcpy(encrypted, &count, sizeof(count));
		// memcpy(encrypted + sizeof(count), &light, sizeof(light));

		t_start = RTIMER_NOW();
		// LOG_INFO("packet (cleartext) %d: ", i);
		// print_aes_block_as_hex(encrypted);
		AES_128.encrypt(encrypted);
		encode_128_bit_aes_block_with_8_4_hamming_code(encrypted, hamming_encoded);


		PROCESS_PAUSE(); // yield to other processes

		// LOG_INFO("packet (encrypted): ");
		// print_aes_block_as_hex(encrypted);
		// PROCESS_PAUSE(); // yield to other processes
		// contiki-ng and the cc2420 driver, does not have functionality to
		// decrypt the packets, so we can't check if the decryption is correct.
		// Decryption is instead done in a python script, see the README.md

		// uint8_t decrypted[16] = {0};
		// memcpy(decrypted, encrypted, sizeof(encrypted));
		// AES_128.encrypt(decrypted);
		// LOG_INFO_("packet (decrypted): ");
		// print_aes_block_as_hex(decrypted);
		// PROCESS_PAUSE();

		// t_end = clock_time();
		// dt
		// clock_time_t dt = t_end - t_start;
		// t_total += dt;
		// LOG_INFO("dt: %lu\n", dt);

		// LOG_INFO("Sending (%u, %u) encrypted with AES 128 key, as nullnet BROADCAST. Time passed %lu\n", (unsigned int) count, (unsigned int) light,  t_total);
		// LOG_INFO("Sending (%u, %u) encrypted with AES 128 key, as nullnet BROADCAST\n", (unsigned int) count, (unsigned int) light  );

		// For this project, this process is acting only as a source of data
		// and does not need to receive any data
		// Therefore, we turn off the radio to save power,
		// and turn it back on when we need to send data.
		// This should give us a more accurate power consumption measurement.
		NETSTACK_RADIO.on();
		NETSTACK_NETWORK.output(NULL); // send as broadcast
		NETSTACK_RADIO.off();

		 t_end = RTIMER_NOW();
    t_elapsed = t_end - t_start;
  
    LOG_INFO("TIMING: Time elapsed: %u RTIMER_SECOND = %u\n", t_elapsed, RTIMER_SECOND);
   

		 // print energest summary every iterations
    // to get a more accurate power consumption measurement
    // The user can then average the values with / 10
    if (count % 10 == 0) {
      energest_utils_step();
    }

		count += 1;
		etimer_reset(&periodic_timer);
	}

	PROCESS_END();
}

