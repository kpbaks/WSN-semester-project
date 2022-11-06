#ifndef WSN_AES_128_ECB_H_
#define WSN_AES_128_ECB_H_

#include "aes.h"
#include <assert.h>

// encrypt data with key using ecb (electronic codebook) mode
void aes_128_ecb_encrypt(aes_128_key_t key, uint8_t *input_data, uint8_t* output_data, size_t data_len);
// decrypt data with key using ecb (electronic codebook) mode
void aes_128_ecb_decrypt(aes_128_key_t key, uint8_t *input_data, uint8_t* output_data, size_t data_len);













#endif // WSN_AES_128_ECB_H_
