#
# The superbitRF module as telemetry downlink/uplink
#
#
ap.CFLAGS += -DUSE_$(MODEM_PORT)
ap.CFLAGS += -D$(MODEM_PORT)_BAUD=$(MODEM_BAUD)

ap.CFLAGS += -DDOWNLINK -DPERIODIC_TELEMETRY -DDOWNLINK_DEVICE=superbitrf
ap.CFLAGS += -DDOWNLINK_TRANSPORT=pprz_tp -DDATALINK=SUPERBITRF
ap.CFLAGS += -DDefaultPeriodic='&telemetry_Main'
#ap.CFLAGS += -DUSE_SUPERBITRF -DUSE_SPI2 -DUSE_SPI_SLAVE2

ap.srcs += peripherals/cyrf6936.c
ap.srcs += subsystems/datalink/downlink.c subsystems/datalink/superbitrf.c subsystems/datalink/pprz_transport.c subsystems/datalink/telemetry.c
ap.srcs += $(SRC_FIRMWARE)/datalink.c $(SRC_FIRMWARE)/rotorcraft_telemetry.c
