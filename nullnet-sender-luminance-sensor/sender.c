#include "contiki.h"
#include "sys/log.h"
#define LOG_MODULE "App"
#define LOG_LEVEL LOG_LEVEL_INFO
#include <time.h>   
#include <string.h>
#include "net/netstack.h"
#include "net/nullnet/nullnet.h"
#include "dev/light-sensor.h"
#include "dev/leds.h"


#include "lib/aes-128.h"

PROCESS(main_process, "main_process");

AUTOSTART_PROCESSES(&main_process);

static uint32_t get_light() {
	   return 10 * light_sensor.value(LIGHT_SENSOR_PHOTOSYNTHETIC) / 7;
}

PROCESS_THREAD(main_process, ev, data)
{
	PROCESS_BEGIN();
	SENSORS_ACTIVATE(light_sensor);

	static struct etimer et;

	static uint32_t counter = 0;

	// Set the timer to 2 seconds
	etimer_set(&et, CLOCK_SECOND * 10);

const uint8_t key[16] = {
       0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x10
    };

		AES_128.set_key(key);
	while (1)
		{
			PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&et));

			// uint8_t payload[8] = { 0 };
			// memcpy(payload, &counter, sizeof(counter));
			++counter;
			uint32_t light = get_light();

			// memcpy(payload + sizeof(counter), &light, sizeof(light));



			counter = 1;
			light = 2;


			// uint8_t *plaintext = (uint8_t *) "abcdefghijklmno";
			uint8_t plaintext[16] = { 0 };
			memcpy(plaintext, &counter, sizeof(counter));
			memcpy(plaintext + sizeof(light), &light, sizeof(light));



			LOG_INFO("plaintext:\t");
			for (int i = 0; i < 16; i++) {
				LOG_INFO_("0x%02x", plaintext[i]);
			}
			LOG_INFO_("\n");


			// printf("plaintext: %s\n", plaintext);
			AES_128.encrypt(plaintext);

			LOG_INFO("ciphertext:\t");
			for (int i = 0; i < 16; i++) {
				LOG_INFO_("0x%02x", plaintext[i]);
			}

			LOG_INFO_("\n");



			nullnet_buf =  plaintext; /* Point NullNet buffer to 'payload' */
			nullnet_len = sizeof(plaintext); /* Set the length of the NullNet buffer to the length of 'payload' */

			NETSTACK_NETWORK.output(NULL); // send as broadcast
			LOG_INFO("Sent packet %u with light %u\n", (unsigned int) counter, (unsigned int) light);
			// LOG_INFO("Sent: %s (len=%d) via NullNet network layer\n", payload, nullnet_len); 

			etimer_restart(&et);

	}

	PROCESS_END();
}

