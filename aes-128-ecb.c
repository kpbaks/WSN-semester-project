#include "aes-128-ecb.h"
#include <stdio.h>

// memcpy(dst, src, len)

void aes_128_ecb_encrypt(aes_128_key_t key, uint8_t *input_data,
                         uint8_t *output_data, const size_t data_len) {
  assert(data_len % AES_BLOCK_SIZE == 0);

  aes_128_block_t block = {0};

  for (size_t i = 0; i < data_len; i += AES_BLOCK_SIZE) {
    memcpy(block, input_data + i, AES_BLOCK_SIZE);
    aes_128_encrypt_block(input_data + i, block, key);
    memcpy(output_data + i, block, AES_BLOCK_SIZE);
  }
}

void aes_128_ecb_decrypt(aes_128_key_t key, uint8_t *input_data,
                         uint8_t *output_data, const size_t data_len) {
  assert(data_len % AES_BLOCK_SIZE == 0);

  aes_128_block_t block = {0};

  for (size_t i = 0; i < data_len; i += AES_BLOCK_SIZE) {
    // memcpy(block, input_data + i, AES_BLOCK_SIZE);
    aes_128_decrypt_block(input_data + i, block, key);
    memcpy(output_data + i, block, AES_BLOCK_SIZE);
  }
}
