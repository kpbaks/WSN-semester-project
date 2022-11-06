#include "aes-128-ecb.h"
#include <stdio.h>

// test aes-128-ecb implementation

int main() {
  // test data from
  // https://csrc.nist.gov/CSRC/media/Projects/Cryptographic-Standards-and-Guidelines/documents/examples/AES_ECB.pdf
  uint8_t key[16] = {0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
                     0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f};
  uint8_t input_data[16] = {0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,
                            0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff};
  uint8_t output_data[16] = {0};
  uint8_t expected_output_data[16] = {0x69, 0xc4, 0xe0, 0xd8, 0x6a, 0x7b,
                                      0x04, 0x30, 0xd8, 0xcd, 0xb7, 0x80,
                                      0x70, 0xb4, 0xc5, 0x5a};

  aes_128_ecb_encrypt(key, input_data, output_data, 16);

	// print input data and output data next to each other
	printf("input_data:\t");
	  for (size_t i = 0; i < 16; i++) {
	printf("%02x ", input_data[i]);
  }
	  printf("\n"); 
	printf("output_data:\t");
	  for (size_t i = 0; i < 16; i++) {
	printf("%02x ", output_data[i]);
		  }
	  printf("\n");

	printf("expected_output_data:\t");
	  for (size_t i = 0; i < 16; i++) {
	printf("%02x ", expected_output_data[i]);
		  }
	  printf("\n");

assert(memcmp(output_data, expected_output_data, 16) == 0);

  for (int i = 0; i < 16; i++) {
    if (output_data[i] != expected_output_data[i]) {
      printf("error: output_data[%d] = %02x, expected_output_data[%d] = %02x\n", i,
             output_data[i], i, expected_output_data[i]);
      return 1;
    }
  }

	  printf("encryption success\n");

	uint8_t decrypted_output_data[16] = {0};

  aes_128_ecb_decrypt(key, output_data, decrypted_output_data, 16);

	  printf("decrypted_output_data:\t");
	  for (size_t i = 0; i < 16; i++) {
	printf("%02x ", decrypted_output_data[i]);
		  }
	  printf("\n");

	  for (int i = 0; i < 16; i++) {
	if (decrypted_output_data[i] != input_data[i]) {
	  printf("error: decrypted_output_data[%d] = %02x, input_data[%d] = %02x\n", i,
			 decrypted_output_data[i], i, input_data[i]);
	  return 1;
	}
	  }

	  printf("decryption success\n");


  printf("success\n");
  return 0;
}
