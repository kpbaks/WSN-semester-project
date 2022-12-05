#ifndef _ENERGEST_UTILS_H_
#define _ENERGEST_UTILS_H_

#include "contiki.h"
#include "sys/log.h"
#include "sys/energest.h"
#include <stdint.h>
#include <stdio.h>

static uint64_t last_tx, last_rx, last_time, last_cpu, last_lpm, last_deep_lpm;

static uint64_t to_permil(uint64_t delta_metric, uint64_t delta_time) {
  return (1000ul * delta_metric) / delta_time;
}

static void
log_energest_utils(const char *name, uint64_t delta, uint64_t delta_time) {
//   LOG_INFO("%-12s: %10"PRIu64"/%10"PRIu64" (%"PRIu64" permil)\n", name, delta,delta_time, to_permil(delta, delta_time));

  printf("ENERGEST: %-12s: %10"PRIu64"/%10"PRIu64" (%"PRIu64" permil)\n", name, delta,delta_time, to_permil(delta, delta_time));

}


static void energest_utils_init() {
  energest_flush();
  last_time = ENERGEST_GET_TOTAL_TIME();
  last_cpu = energest_type_time(ENERGEST_TYPE_CPU);
  last_lpm = energest_type_time(ENERGEST_TYPE_LPM);
  last_deep_lpm = energest_type_time(ENERGEST_TYPE_DEEP_LPM);
  last_tx = energest_type_time(ENERGEST_TYPE_TRANSMIT);
  last_rx = energest_type_time(ENERGEST_TYPE_LISTEN);
}


static void energest_utils_step(void) {
  static unsigned count = 0;
  uint64_t curr_tx, curr_rx, curr_time, curr_cpu, curr_lpm, curr_deep_lpm;
  uint64_t delta_time;

  energest_flush();

  curr_time = ENERGEST_GET_TOTAL_TIME();
  curr_cpu = energest_type_time(ENERGEST_TYPE_CPU);
  curr_lpm = energest_type_time(ENERGEST_TYPE_LPM);
  curr_deep_lpm = energest_type_time(ENERGEST_TYPE_DEEP_LPM);
  curr_tx = energest_type_time(ENERGEST_TYPE_TRANSMIT);
  curr_rx = energest_type_time(ENERGEST_TYPE_LISTEN);

//   delta_time = MAX(curr_time - last_time, 1);
  delta_time = (curr_time - last_time) > 1 ? curr_time - last_time : 1;

  printf("ENERGEST: --- Period summary #%u (%"PRIu64" seconds)\n",
           count++, delta_time / ENERGEST_SECOND);
  printf("ENERGEST: Total time  : %10"PRIu64"\n", delta_time);
  log_energest_utils("CPU", curr_cpu - last_cpu, delta_time);
  log_energest_utils("LPM", curr_lpm - last_lpm, delta_time);
  log_energest_utils("Deep LPM", curr_deep_lpm - last_deep_lpm, delta_time);
  log_energest_utils("Radio Tx", curr_tx - last_tx, delta_time);
  log_energest_utils("Radio Rx", curr_rx - last_rx, delta_time);
  log_energest_utils("Radio total", curr_tx - last_tx + curr_rx - last_rx, delta_time);

  last_time = curr_time;
  last_cpu = curr_cpu;
  last_lpm = curr_lpm;
  last_deep_lpm = curr_deep_lpm;
  last_tx = curr_tx;
  last_rx = curr_rx;
}



#endif /* _ENERGEST_UTILS_H_ */