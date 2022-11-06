#include "aes-128-ctr.h"

// xor_blocks
void xor_blocks(uint8_t *dst, const uint8_t *src, size_t len) {
  for (size_t i = 0; i < len; i++) {
    dst[i] ^= src[i];
  }
}

void aes_128_ctr_encrypt(aes_128_key_t key, uint8_t *input_data,
                         uint8_t *output_data, const size_t data_len,
                         aes_128_block_t iv) {
  assert(data_len % AES_BLOCK_SIZE == 0);

  // encrypt the plaintext
  // xor the plaintext with the iv, to get the first block of ciphertext
  // xor the plaintext with the previous ciphertext block, to get the next block
  // of ciphertext
  aes_128_block_t block = {0};
  aes_128_block_t cipher_block = {0};
  aes_128_block_t iv_block = {0};
  memcpy(iv_block, iv, AES_BLOCK_SIZE);

  for (size_t i = 0; i < data_len; i += AES_BLOCK_SIZE) {
    memcpy(block, input_data + i, AES_BLOCK_SIZE);
    aes_128_encrypt_block(iv_block, cipher_block, key);
    xor_blocks(block, cipher_block, AES_BLOCK_SIZE);
    memcpy(output_data + i, block, AES_BLOCK_SIZE);
    increment_iv(iv_block);
  }
}

void aes_128_ctr_decrypt(aes_128_key_t key, uint8_t *input_data,
                         uint8_t *output_data, const size_t data_len,
                         aes_128_block_t iv) {
  assert(data_len % AES_BLOCK_SIZE == 0);

  // decrypt the cipher text
  // xor the decrypted cipher text with the iv to get the plain text
  aes_128_block_t block = {0};
  aes_128_block_t cipher_block = {0};
  aes_128_block_t iv_block = {0};
  memcpy(iv_block, iv, AES_BLOCK_SIZE);

  for (size_t i = 0; i < data_len; i += AES_BLOCK_SIZE) {
    memcpy(block, input_data + i, AES_BLOCK_SIZE);
    aes_128_encrypt_block(iv_block, cipher_block, key);
    xor_blocks(block, cipher_block, AES_BLOCK_SIZE);
    memcpy(output_data + i, block, AES_BLOCK_SIZE);
    increment_iv(iv_block);
  }
}
