// contiki-ng specific
#include "contiki.h"
// #include "sys/energest.h"
#include "sys/log.h"
#define LOG_MODULE "App"
#define LOG_LEVEL LOG_LEVEL_INFO

#include "aes.h"

PROCESS(homemade_aes, "homemade_aes");

AUTOSTART_PROCESSES(&homemade_aes);

PROCESS_THREAD(homemade_aes, ev, data) {

  static struct etimer periodic_timer;

  PROCESS_BEGIN();

  etimer_set(&periodic_timer, CLOCK_SECOND * 10);

  aes_128_key_t key = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
                       0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x10};

  while (1) {
    PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&periodic_timer));
    etimer_reset(&periodic_timer);

    // DO CPU WORK - START
    aes_128_block_t plaintext_block = "hello world abc";
    LOG_INFO("plaintext: %s\n", plaintext_block);

    aes_128_block_t ciphertext_block = {0};
    aes_128_encrypt_block(plaintext_block, ciphertext_block, key);

    LOG_INFO("ciphertext: ");
    for (int i = 0; i < 16; i++) {
      LOG_INFO_("%c", ciphertext_block[i]);
    }
    LOG_INFO_("\n");

    aes_128_block_t decrypted_block = {0};
    aes_128_decrypt_block(ciphertext_block, decrypted_block, key);
    LOG_INFO("decrypted: %s\n", decrypted_block);
    // DO CPU WORK - END
  }

  PROCESS_END();
}
