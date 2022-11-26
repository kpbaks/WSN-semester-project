#define ENERGEST_CONF_ON 1 // Enables energest to measure energy consumption

#include "contiki.h"
#include "sys/log.h"
#define LOG_MODULE "App"
#define LOG_LEVEL LOG_LEVEL_INFO
#include <lib/aes-128.h>
#include <time.h>

PROCESS(main_process, "main_process");

AUTOSTART_PROCESSES(&main_process);

PROCESS_THREAD(main_process, ev, data) {
  PROCESS_BEGIN();

  // const uint8_t key[16] = {0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
  // 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f};

  const uint8_t key[16] = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
                           0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x10};

  AES_128.set_key(key);

  // uint8_t *plaintext = (uint8_t *) "abcdefghijklmno";
  uint8_t plaintext[] = {0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
                         0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f};

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

  // printf("encrypted: %s\n", plaintext);
  // AES_128.encrypt(plaintext);

  // LOG_INFO("ciphertext encrypted again:\t");
  // for (int i = 0; i < 16; i++) {
  //   LOG_INFO_("0x%02x", plaintext[i]);
  // }

  // LOG_INFO_("\n");

  PROCESS_END();
}
