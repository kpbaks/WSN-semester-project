#define AES_128_CONF aes_128_driver // Turns on software AES-128

#define ENERGEST_CONF_ON 1 // Enables energest to measure energy consumption

#include "contiki.h"
#include "sys/log.h"
#include <time.h>   
#include <lib/aes-128.h>


PROCESS(main_process, "main_process");

AUTOSTART_PROCESSES(&main_process);

PROCESS_THREAD(main_process, ev, data)
{
  PROCESS_BEGIN(); 
    const uint8_t key[16] = {0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f}; 
    AES_128.set_key(key);
    uint8_t *plaintext = (uint8_t *) "abcdefghijklmnop";
    AES_128.encrypt(plaintext);
    printf("result: %s\n", plaintext);
    AES_128.encrypt(plaintext);
    printf("result: %s", plaintext);

  PROCESS_END();
}