CONTIKI_PROJECT = enc
all: $(CONTIKI_PROJECT)

CONTIKI = ../..
TARGET_LIBFILES += -lm
MAKE_NET = MAKE_NET_NULLNET
include $(CONTIKI)/Makefile.include