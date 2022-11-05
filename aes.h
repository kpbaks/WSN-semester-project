#ifndef _WSN_AES_H_
#define _WSN_AES_H_

#include <stddef.h> // size_t
#include <stdint.h> // uint8_t
#include <string.h> // for memcpy

#define AES_BLOCK_SIZE 16

// A key of size 128 has 10 rounds.
// A key of size 192 has 12 rounds.
// A key of size 256 has 14 rounds.

// The state is a 4x4 matrix which is the input to the AES algorithm.
// For the functions below, the state is represented as a 1D array of
// 16 bytes. The first 4 bytes are the first column, the next 4 bytes
// are the second column, etc.
// NOTE: the cipher input bytes are mapped onto the state array in the order
// a(0,0), a(1,0), a(2,0), a(3,0), a(0,1), a(1,1), a(2,1), a(3,1) ... a(3,3).
typedef uint8_t aes_state_t[16];

typedef uint8_t aes_128_key_t[16]; // 128-bit key
typedef uint8_t aes_128_expanded_key_t[176]; // 176 bytes

typedef uint8_t aes_128_block_t[16]; // 128-bit block

enum e_aes_modes { AES_MODE_ECB, AES_MODE_CBC, AES_MODE_CTR, AES_MODE_GCM };

enum e_aes_key_sizes { AES_KEY_SIZE_128, AES_KEY_SIZE_192, AES_KEY_SIZE_256 };

// helper functions
void sub_bytes(aes_state_t state);
void shift_rows(aes_state_t state);
void inv_shift_rows(aes_state_t state);
void mix_columns(aes_state_t state);
void add_round_key(aes_state_t state, uint8_t *round_key);


void aes_128_expand_key(aes_128_expanded_key_t expanded_key,aes_128_key_t key);

// public functions
void aes_128_encrypt_block(aes_128_block_t input_block, aes_128_block_t output_block, aes_128_key_t key);
void aes_128_decrypt_block(aes_128_block_t input_block, aes_128_block_t output_block, aes_128_key_t key);

// encrypt data with key using ecb (electronic codebook) mode
void aes_128_ecb_encrypt(aes_128_key_t key, uint8_t *input_data, uint8_t* output_data, size_t data_len);
// decrypt data with key using ecb (electronic codebook) mode
void aes_128_ecb_decrypt(aes_128_key_t key, uint8_t *input_data, uint8_t* output_data, size_t data_len);

// encrypt data with key using cbc (cipher block chaining) mode
void aes_128_cbc_encrypt(aes_128_key_t key, uint8_t *input_data, uint8_t* output_data, size_t data_len, aes_128_block_t iv);
// decrypt data with key using cbc (cipher block chaining) mode
// NOTE: the iv is used as the first block of the input data
void aes_128_cbc_decrypt(aes_128_key_t key, uint8_t *input_data, uint8_t* output_data, size_t data_len, aes_128_block_t iv);

// encrypt data with key using ctr (counter) mode
void aes_128_ctr_encrypt(aes_128_key_t key, uint8_t *input_data, uint8_t* output_data, size_t data_len, aes_128_block_t iv);
// decrypt data with key using ctr (counter) mode
void aes_128_ctr_decrypt(aes_128_key_t key, uint8_t *input_data, uint8_t* output_data, size_t data_len, aes_128_block_t iv);


#endif // _WSN_AES_H_
