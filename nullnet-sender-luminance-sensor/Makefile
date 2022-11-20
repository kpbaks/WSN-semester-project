CONTIKI_PROJECT = sender
all: $(CONTIKI_PROJECT)

CONTIKI = ../../..

MAKE_NET = MAKE_NET_NULLNET
# seen here: https://github.com/contiki-ng/contiki-ng/blob/0c43bf4ffdf40806a30d6e57b750f7371f3371b6/examples/libs/simple-energest/example.c#L52
include $(CONTIKI)/Makefile.dir-variables
MODULES += $(CONTIKI_NG_SERVICES_DIR)/simple-energest

# TARGET_LIBFILES += -lm

include $(CONTIKI)/Makefile.include
