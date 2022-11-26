CONTIKI_PROJECT = receiver
all: $(CONTIKI_PROJECT)

# CFLAGS += -02 # we want binary to be as small as possible

CONTIKI = ../..
# TARGET_LIBFILES += -lm
MAKE_NET = MAKE_NET_NULLNET

MODULES += os/services/simple-energest

include $(CONTIKI)/Makefile.include
