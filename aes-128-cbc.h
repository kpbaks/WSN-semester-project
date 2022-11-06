#ifndef _WSN_AES_128_CBC_H_
#define _WSN_AES_128_CBC_H_

#include "aes.h"
#include <assert.h>

// encrypt data with key using cbc (cipher block chaining) mode
void aes_128_cbc_encrypt(aes_128_key_t key, uint8_t *input_data, uint8_t* output_data, size_t data_len, aes_128_block_t iv);
// decrypt data with key using cbc (cipher block chaining) mode
// NOTE: the iv is used as the first block of the input data
void aes_128_cbc_decrypt(aes_128_key_t key, uint8_t *input_data, uint8_t* output_data, size_t data_len, aes_128_block_t iv);

#endif // _WSN_AES_128_CBC_H_
