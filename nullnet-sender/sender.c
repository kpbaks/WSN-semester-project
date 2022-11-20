#include "contiki.h"
#include "sys/log.h"
#define LOG_MODULE "App"
#define LOG_LEVEL LOG_LEVEL_INFO
#include <time.h>   
// #include <stdlib.h>
#include <string.h>
#include "net/netstack.h"
#include "net/nullnet/nullnet.h"

PROCESS(main_process, "main_process");

AUTOSTART_PROCESSES(&main_process);

PROCESS_THREAD(main_process, ev, data)
{
	PROCESS_BEGIN();

	static struct etimer et;

	static uint32_t counter = 0;

	// Set the timer to 2 seconds
	etimer_set(&et, CLOCK_SECOND * 2);

	while (1)
		{
			PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&et));

			// uint8_t payload[64] = { 0 };

			// char *msg = "hello world: ";
			// // sprintf(payload, "%s %u", msg, counter);
			// ++counter;

			// memcpy(payload, msg, strlen(msg));
			// memcpy(payload + strlen(msg), &counter, sizeof(counter));

			uint8_t payload[4] = { 0 };
			memcpy(payload, &counter, sizeof(counter));
			++counter;

			nullnet_buf =  payload; /* Point NullNet buffer to 'payload' */
			nullnet_len = sizeof(payload); /* Set the length of the NullNet buffer to the length of 'payload' */

			// nullnet_len = strlen(msg) + sizeof(counter); /* Set payload length */


			NETSTACK_NETWORK.output(NULL); // send as broadcast
			LOG_INFO("Sent: %s (len=%d) via NullNet network layer\n", payload, nullnet_len); 

			etimer_reset(&et);

	}

	PROCESS_END();
}

