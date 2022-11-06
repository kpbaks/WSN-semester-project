#include "pkcs_7_padding.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>


void print_data(uint8_t *data, uint32_t data_len) {
  for (uint32_t i = 0; i < data_len; i++) {
    printf("%02x ", data[i]);
  }
  printf("\n");
}

int main(int argc, char **argv) {

  // test pkcs_7_pad
  uint8_t data[BLOCK_SIZE] = {
      0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
      0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
  };
  uint8_t expected[BLOCK_SIZE] = {0};
  memcpy(expected, data, BLOCK_SIZE);

  uint8_t N = 4;
  memset(expected + (BLOCK_SIZE - N), N, N);
  pkcs_7_pad(data, N);

  printf("data:\t\t");
  print_data(data, BLOCK_SIZE);
  printf("expected:\t");
  print_data(expected, BLOCK_SIZE);

  assert(memcmp(data, expected, BLOCK_SIZE) == 0);
  printf("pkcs_7_pad test passed for 15 bytes");
  // test pkcs_7_unpad

	pkcs_7_unpad_result_t result = pkcs_7_unpad(data, BLOCK_SIZE);

  assert(result.N == N);

  // print the address of every byte in data
  for (uint32_t i = 0; i < BLOCK_SIZE; i++) {
    printf("data[%2d] = %02x: %p\n", i, data[i], &data[i]);
  }
  // print where_padding_starts
  printf("where_padding_starts: %p\n", result.where_padding_starts);
	printf("data: %p\n", data);

  assert(result.where_padding_starts == data + (BLOCK_SIZE - result.N));

  printf("pkcs_7_unpad test passed for 15 bytes");

  return 0;
}
