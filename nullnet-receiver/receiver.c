#include "contiki.h"
#include "net/nullnet/nullnet.h"
#include "sys/log.h"

#define LOG_MODULE "App"
#define LOG_LEVEL LOG_LEVEL_INFO
#include <time.h>

void input_callback(const void *data, uint16_t len, const linkaddr_t *src,
                    const linkaddr_t *dest) {
  LOG_INFO("Received %d bytes from ", len);
}

PROCESS(main_process, "main_process");

AUTOSTART_PROCESSES(&main_process);

PROCESS_THREAD(main_process, ev, data) {
  PROCESS_BEGIN();

  /* At process initialization */
  nullnet_set_input_callback(input_callback);
  static struct etimer et;
  etimer_set(&et, CLOCK_SECOND * 1);

  while (1) {
    PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&et));
    etimer_reset(&et);
  }

  PROCESS_END();
}
