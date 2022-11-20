CONTIKI_PROJECT = receiver
all: $(CONTIKI_PROJECT)

CONTIKI = ../..
TARGET_LIBFILES += -lm
MAKE_NET = MAKE_NET_NULLNET

MODULES += os/services/simple-energest

include $(CONTIKI)/Makefile.include
