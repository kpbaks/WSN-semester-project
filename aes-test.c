#include "aes.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

int main(int argc, char **argv) {

  // test shift_rows
  {
    // clang-format off
	aes_state_t state = {
		0x00, 0x01, 0x02, 0x03,
		0x10, 0x11, 0x12, 0x13,
		0x20, 0x21, 0x22, 0x23,
		0x30, 0x31, 0x32, 0x33
	};
    // clang-format on

    // clang-format off
	aes_state_t expected = {
		0x00, 0x01, 0x02, 0x03,
		0x11, 0x12, 0x13, 0x10,
		0x22, 0x23, 0x20, 0x21,
		0x33, 0x30, 0x31, 0x32
	};
    // clang-format on

    shift_rows(state);

    assert(memcmp(state, expected, sizeof(aes_state_t)) == 0);
    printf("shift_rows test passed\n");
  }

  // test inv_shift_rows
  {
    // clang-format off
	aes_state_t state = {
		0x00, 0x01, 0x02, 0x03,
		0x11, 0x12, 0x13, 0x10,
		0x22, 0x23, 0x20, 0x21,
		0x33, 0x30, 0x31, 0x32
	};
    // clang-format on

    // clang-format off
	aes_state_t expected = {
		0x00, 0x01, 0x02, 0x03,
		0x10, 0x11, 0x12, 0x13,
		0x20, 0x21, 0x22, 0x23,
		0x30, 0x31, 0x32, 0x33
	};
    // clang-format on

    printf("before inv_shift_rows\n");
    // print state
    for (int i = 0; i < 4; i++) {
      // printf("hello\n");
      for (int j = 0; j < 4; j++) {
        printf("%02x ", state[i * 4 + j]);
      }

      printf("\t");
      for (int j = 0; j < 4; j++) {
        printf("%02x ", expected[i * 4 + j]);
      }
      printf("\n");
    }

    printf("\nafter inv_shift_rows\n");

    inv_shift_rows(state);
    // print state
    for (int i = 0; i < 4; i++) {
      for (int j = 0; j < 4; j++) {
        printf("%02x ", state[i * 4 + j]);
      }

      printf("\t");
      for (int j = 0; j < 4; j++) {
        printf("%02x ", expected[i * 4 + j]);
      }
      printf("\n");
    }

    assert(memcmp(state, expected, sizeof(aes_state_t)) == 0);
    printf("inv_shift_rows test passed\n");
  }

  // test expand_key
  {
    aes_128_key_t key = {0};
    aes_128_expanded_key_t expanded_key = {0};
    aes_128_expand_key(expanded_key, key);

    // clang-format off
	const uint8_t expected_expanded_key[176] = {
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x62, 0x63, 0x63, 0x63, 0x62, 0x63, 0x63, 0x63, 0x62, 0x63, 0x63, 0x63, 0x62, 0x63, 0x63, 0x63,
		0x9b, 0x98, 0x98, 0xc9, 0xf9, 0xfb, 0xfb, 0xaa, 0x9b, 0x98, 0x98, 0xc9, 0xf9, 0xfb, 0xfb, 0xaa,
		0x90, 0x97, 0x34, 0x50, 0x69, 0x6c, 0xcf, 0xfa, 0xf2, 0xf4, 0x57, 0x33, 0x0b, 0x0f, 0xac, 0x99,
		0xee, 0x06, 0xda, 0x7b, 0x87, 0x6a, 0x15, 0x81, 0x75, 0x9e, 0x42, 0xb2, 0x7e, 0x91, 0xee, 0x2b,
		0x7f, 0x2e, 0x2b, 0x88, 0xf8, 0x44, 0x3e, 0x09, 0x8d, 0xda, 0x7c, 0xbb, 0xf3, 0x4b, 0x92, 0x90,
		0xec, 0x61, 0x4b, 0x85, 0x14, 0x25, 0x75, 0x8c, 0x99, 0xff, 0x09, 0x37, 0x6a, 0xb4, 0x9b, 0xa7,
		0x21, 0x75, 0x17, 0x87, 0x35, 0x50, 0x62, 0x0b, 0xac, 0xaf, 0x6b, 0x3c, 0xc6, 0x1b, 0xf0, 0x9b,
		0x0e, 0xf9, 0x03, 0x33, 0x3b, 0xa9, 0x61, 0x38, 0x97, 0x06, 0x0a, 0x04, 0x51, 0x1d, 0xfa, 0x9f,
		0xb1, 0xd4, 0xd8, 0xe2, 0x8a, 0x7d, 0xb9, 0xda, 0x1d, 0x7b, 0xb3, 0xde, 0x4c, 0x66, 0x49, 0x41,
		0xb4, 0xef, 0x5b, 0xcb, 0x3e, 0x92, 0xe2, 0x11, 0x23, 0xe9, 0x51, 0xcf, 0x6f, 0x8f, 0x18, 0x8e
	};
    // clang-format on

    printf("\nexpanded key next to expected\n");
    // print each byte of expanded key next to expected_expanded_key in an 16x11
    // grid
    for (int i = 0; i < 176; i++) {
      printf("%02x ", expanded_key[i]);
      if (i % 16 == 15) {
        printf("\t");
        for (int j = i - 15; j <= i; j++) {
          printf("%02x ", expected_expanded_key[j]);
        }
        printf("\n");
      }
    }

    assert(memcmp(expanded_key, expected_expanded_key,
                  sizeof(expected_expanded_key)) == 0);
  }

  // test encrypt and decryption
  // clang-format off
  {
  const uint8_t key[16] = {0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6,
                     0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c};

  const uint8_t cleartext[16] = "my name is jeff";

		printf("\nbefore encrypt\n");
		printf("cleartext: %s\n", cleartext);

	printf("cleartext (hex):\t");
    for (int i = 0; i < 16; i++) {
      printf("0x%02x ", cleartext[i]);
    }
    printf("\n");

    aes_128_block_t ciphertext = {0};
    aes_128_encrypt_block(cleartext, ciphertext, key);

    // print ciphertext
	printf("ciphertext (hex):\t");
    for (int i = 0; i < 16; i++) {
      printf("0x%02x ", ciphertext[i]);
    }
    printf("\n");

    // decrypt
    aes_128_block_t decrypted;
    aes_128_decrypt_block(ciphertext, decrypted, key);

    // print decrypted
	printf("decrypted (hex):\t");
    for (int i = 0; i < 16; i++) {
      printf("0x%02x ", decrypted[i]);
    }
			printf("\n");

    // compare decrypted to cleartext
    assert(memcmp(decrypted, cleartext, sizeof(decrypted)) == 0);

// print sizeof ciphertext
		//
// FIX: then \0 byte gets discarded so that is why printf will print 31 chars when printing ciphertext
		ciphertext[16] = '\0'; // this cuts off the last byte of ciphertext, which is wrong
	printf("sizeof ciphertext: %lu\n", sizeof(ciphertext));
	printf("sizeof decrypted: %lu\n", sizeof(decrypted));
	printf("sizeof cleartext: %lu\n", sizeof(cleartext));

    // clang-format on

    // write ciphertext to file
    FILE *fp;
    fp = fopen("ciphertext.txt", "w");
    fprintf(fp, "%s", ciphertext);
    fclose(fp);

    printf("\nciphertext (text):\t%16s\n", ciphertext);
    printf("decrypted (text):\t%s\n", decrypted);
    printf("\naes_decrypt test passed\n");
  }

  return 0;
}
