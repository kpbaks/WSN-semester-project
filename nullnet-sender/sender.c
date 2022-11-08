#include "contiki.h"
#include "sys/log.h"
#include <time.h>   
#include "net/nullnet/nullnet.h"

PROCESS(main_process, "main_process");

AUTOSTART_PROCESSES(&main_process);

PROCESS_THREAD(main_process, ev, data)
{
	PROCESS_BEGIN(); 
	uint8_t payload[64] = { 0 };
	nullnet_buf = payload; /* Point NullNet buffer to 'payload' */
	nullnet_len = 2; /* Tell NullNet that the payload length is two bytes */
	NETSTACK_NETWORK.output(NULL); /* Send as broadcast */

  PROCESS_END();
}





 


