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

	// Set the timer to 2 seconds
	etimer_set(&et, CLOCK_SECOND * 2);

	while (1)
	{
		PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&et));


	uint8_t payload[64] = { 0 };
	const char *msg = "Hello World!";
	memcpy(payload, msg, strlen(msg));


	nullnet_buf = payload; /* Point NullNet buffer to 'payload' */
	// nullnet_len = 2; /* Tell NullNet that the payload length is two bytes */
	nullnet_len = strlen(msg);
	NETSTACK_NETWORK.output(NULL); /* Send as broadcast */
	LOG_INFO("Sent: %s (len=%d) via NullNet network layer\n", msg, nullnet_len); 

	etimer_reset(&et);

	}
	

  PROCESS_END();
}





 


