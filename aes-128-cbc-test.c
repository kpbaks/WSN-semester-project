#include "aes-128-cbc.h"
#include "aes.h"
#include "pkcs_7_padding.h"

#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
  // read a filepath from the command line
  if (argc != 2) {
    printf("usage: %s <filepath>\n", argv[0]);
    return 1;
  }
  char *filepath = argv[1];

  // read ./tux.png into a uint8_t array
  FILE *fp = fopen(filepath, "rb");
  assert(fp != NULL);
  fseek(fp, 0, SEEK_END);
  long fsize = ftell(fp);
  fseek(fp, 0, SEEK_SET); // same as rewind(f);
  printf("fsize: %ld\n", fsize);
  // if fsize is not a multiple of BLOCK_SIZE, then we need to pad it
  // with PKCS#7 padding
  // if fsize is a multiple of BLOCK_SIZE, then we need to add an extra block of
  // size BLOCK_SIZE to the end of the file, and pad it with PKCS#7 padding
  uint32_t padded_fsize = fsize + (BLOCK_SIZE - (fsize % BLOCK_SIZE));
  uint8_t *tux = malloc(padded_fsize);
  assert(tux != NULL);
  fread(tux, fsize, 1, fp);
  fclose(fp);

  // pad tux with PKCS#7 padding
  uint8_t N = padded_fsize - fsize;
  printf("N: %d\n", N);
  pkcs_7_pad(tux + padded_fsize - 16, N);

  // print last 16 bytes of tux
  for (uint32_t i = padded_fsize - 16; i < padded_fsize; i++) {
    printf("%02x ", tux[i]);
  }

  printf("\n");

  // encrypt ./tux.png
  uint8_t *encrypted_tux = malloc(padded_fsize);
  assert(encrypted_tux != NULL);

  aes_128_key_t key = {0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
                       0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f};

  aes_128_block_t iv = {0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
                        0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f};

  aes_128_cbc_encrypt(key, tux, encrypted_tux, padded_fsize, iv);

  // write encrypted ./tux.png to ./encrypted_cbc_tux.png

  // prepend "encrypted_cbc_" to the filepath
  char *encrypted_filepath_prefix = "encrypted_cbc_";
  char *encrypted_filepath =
      malloc(strlen(encrypted_filepath_prefix) + strlen(filepath) + 1);
  assert(encrypted_filepath != NULL);
  strcpy(encrypted_filepath, encrypted_filepath_prefix);
  strcat(encrypted_filepath, filepath);

  fp = fopen(encrypted_filepath, "wb");
  assert(fp != NULL);
  fwrite(encrypted_tux, padded_fsize, 1, fp);
  fclose(fp);

  // decrypt ./encrypted_cbc_tux.png
  uint8_t *decrypted_tux = malloc(padded_fsize);
  assert(decrypted_tux != NULL);

  // data |> pad |> encrypt |> decrypt |> unpad

  aes_128_cbc_decrypt(key, encrypted_tux, decrypted_tux, padded_fsize, iv);

  // unpad decrypted_tux
  pkcs_7_unpad_result_t result = pkcs_7_unpad(decrypted_tux, padded_fsize);
  assert(result.N == N);

  char *decrypted_filepath_prefix = "decrypted_cbc_";
  char *decrypted_filepath =
      malloc(strlen(decrypted_filepath_prefix) + strlen(filepath) + 1);
  assert(decrypted_filepath != NULL);
  strcpy(decrypted_filepath, decrypted_filepath_prefix);
  strcat(decrypted_filepath, filepath);

  // write decrypted decrypted_tux to ./decrypted_cbc_tux.png
  fp = fopen(decrypted_filepath, "wb");
  assert(fp != NULL);
  fwrite(decrypted_tux, fsize, 1, fp);
  fclose(fp);

  // compare tux and decrypted_tux
  assert(memcmp(tux, decrypted_tux, fsize) == 0);
  printf("%s and %s are the same (AES-128-CBC)\n", filepath,
         decrypted_filepath);

  return 0;
}
