#ifndef _WSN_PKCS_7_PADDING_H_
#define _WSN_PKCS_7_PADDING_H_

#include <stdint.h>
#include <string.h>
#include <assert.h>


#define BLOCK_SIZE 16

// https://www.rfc-editor.org/rfc/rfc5652#section-6.3

// implemention of PKCS#7 padding and unpadding

typedef uint8_t block_t[BLOCK_SIZE];

typedef struct {
	uint8_t *where_padding_starts;
	uint8_t N;
} pkcs_7_unpad_result_t;

void pkcs_7_pad(block_t block, uint8_t N);
pkcs_7_unpad_result_t pkcs_7_unpad(const uint8_t* data, uint32_t data_len); // returns the length of the unpadded block

#endif // _WSN_PKCS_7_PADDING_H_
