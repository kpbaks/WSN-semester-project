#ifndef _WSH_AES_128_CTR_H_
#define _WSH_AES_128_CTR_H_

#include "aes.h"
#include <assert.h>

// encrypt data with key using ctr (counter) mode
void aes_128_ctr_encrypt(aes_128_key_t key, uint8_t *input_data,
                         uint8_t *output_data, size_t data_len,
                         aes_128_block_t iv);
// decrypt data with key using ctr (counter) mode
void aes_128_ctr_decrypt(aes_128_key_t key, uint8_t *input_data,
                         uint8_t *output_data, size_t data_len,
                         aes_128_block_t iv);

#endif // _WSH_AES_128_CTR_H_
