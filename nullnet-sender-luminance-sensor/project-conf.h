#define ENERGEST_CONF_ON 1
#undef AES_128_CONF
#define AES_128_CONF cc2420_aes_128_driver // hardware AES
// #define AES_128_CONF aes_128_driver // software AES

// defaults to 60 seconds see os/services/simple-energest/simple-energest.h
#define SIMPLE_ENERGEST_CONF_PERIOD (30 * CLOCK_SECOND) // seconds (seen here:
// https://github.com/contiki-ng/contiki-ng/blob/0c43bf4ffdf40806a30d6e57b750f7371f3371b6/examples/libs/simple-energest/example.c#L52)
