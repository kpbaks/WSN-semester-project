#include "contiki.h"
#include "sys/log.h"
#define LOG_MODULE "App"
#define LOG_LEVEL LOG_LEVEL_INFO

#include "lib/aes-128.h" // The implementation (either software or hardware) is set in ./project-conf.h
#include "net/netstack.h"
#include "net/nullnet/nullnet.h"

#include "dev/leds.h"
#include "dev/light-sensor.h"

#include <string.h> // for memcpy, memset

#define AES_128_BLOCK_LENGTH 16 // 128 bits
#define SEND_INTERVAL (CLOCK_SECOND * 2.5)
#define LIGHT_SENSOR_READ_INTERVAL (CLOCK_SECOND * 0.25)

static uint32_t get_light() {
  return 10 * light_sensor.value(LIGHT_SENSOR_PHOTOSYNTHETIC) / 7;
}

// static void print_aes_block_as_hex(uint8_t *block) {
//   for (int i = 0; i < AES_128_BLOCK_LENGTH; i++) {
//     LOG_INFO_("%02x ", block[i]);
//   }
//   LOG_INFO_("\n");
// }


PROCESS(main_process, "main_process");

AUTOSTART_PROCESSES(&main_process);

PROCESS_THREAD(main_process, ev, data) {

  static struct etimer periodic_timer;
  static struct etimer light_sample_rate_periodic_timer;
  static uint32_t count = 0;
  // static uint32_t light = 0;
  static uint8_t encrypted[16] = {0};

  static const uint8_t key[16] = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06,
                                  0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c,
                                  0x0d, 0x0e, 0x0f, 0x10};

  PROCESS_BEGIN();

  SENSORS_ACTIVATE(light_sensor);

  etimer_set(&periodic_timer, SEND_INTERVAL);
  etimer_set(&light_sample_rate_periodic_timer, LIGHT_SENSOR_READ_INTERVAL);

  AES_128.set_key(key);

  // We reuse the same buffer for the encrypted data to be sent
  // As the size of the data is 16 bytes, we can use the same buffer.
  nullnet_buf = (uint8_t *)&encrypted;
  nullnet_len = sizeof(encrypted);

  while (1) {
    PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&periodic_timer));

    memset(encrypted, 0, sizeof(encrypted));

    static int i = 0;
    i = 1;
    i -= 1;
    for (i = 0; i < 4; i++) {
      etimer_reset(&light_sample_rate_periodic_timer);
      uint32_t measured_light = get_light();
      // LOG_INFO("Light: %lu ", measured_light);
      // PROCESS_PAUSE(); // yield to other processes
      memcpy(encrypted + (i * sizeof(uint32_t)), &measured_light,
             sizeof(uint32_t));
      PROCESS_WAIT_EVENT_UNTIL(
          etimer_expired(&light_sample_rate_periodic_timer));
    }

    // LOG_INFO_("\n");

    // LOG_INFO("packet (cleartext) %d: ", i);
    // print_aes_block_as_hex(encrypted);
    AES_128.encrypt(encrypted);
    // PROCESS_PAUSE(); // yield to other processes

    // LOG_INFO("packet (encrypted): ");
    // print_aes_block_as_hex(encrypted);
    PROCESS_PAUSE(); // yield to other processes

    // LOG_INFO(
    //     "Sending (%u, %u) encrypted with AES 128 key, as nullnet BROADCAST\n",
    //     (unsigned int)count, (unsigned int)light);

    // For this project, this process is acting only as a source of data
    // and does not need to receive any data
    // Therefore, we turn off the radio to save power,
    // and turn it back on when we need to send data.
    // This should give us a more accurate power consumption measurement.
    NETSTACK_RADIO.on();
    NETSTACK_NETWORK.output(NULL); // send as broadcast
    NETSTACK_RADIO.off();

    count += 1;
    etimer_reset(&periodic_timer);
  }

  PROCESS_END();
}
