#include "pkcs_7_padding.h"
#include <stdio.h>

void pkcs_7_pad(block_t block, uint8_t N) {
	assert(N <= BLOCK_SIZE);
	printf("N: %d\n", N);
	memset(block + (BLOCK_SIZE - N), N, N);
}

pkcs_7_unpad_result_t pkcs_7_unpad(const uint8_t* data, uint32_t data_len) {
	const uint8_t N = data[data_len - 1];
	assert(N <= BLOCK_SIZE); 
	printf("\ndata: %p\n", data);
	printf("N: %d\n", N);
	printf("BLOCK_SIZE: %d\n", BLOCK_SIZE);

	pkcs_7_unpad_result_t result = {
		.where_padding_starts = data + (BLOCK_SIZE - N),
		.N = N,
	};
	printf("\nresult.where_padding_starts: %p\n", result.where_padding_starts);
	return result;
}

