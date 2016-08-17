/*
 * Copyright (C) Rijesh Augustine
 *
 * This file is part of paparazzi
 *
 * paparazzi is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2, or (at your option)
 * any later version.
 *
 * paparazzi is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with paparazzi; see the file COPYING.  If not, see
 * <http://www.gnu.org/licenses/>.
 */
/**
 * @file "modules/flight_trim/flight_trim.h"
 * @author Rijesh Augustine
 * This module is designed to allow engaging AUTO2 on the first flight of you aircraft. It will fix a poorly calibrated transmitter and wi.
 */

#include "std.h"

#ifndef FLIGHT_TRIM_H
#define FLIGHT_TRIM_H

struct FlightTrim {
  bool calib_rc;
  bool trim_ac;
};

extern void flight_trim_init(void);
extern void flight_trim_event(void);
extern void flight_trim_rc(void);
extern void flight_trim_ac(void);
//extern void send_trim_msg(void);

extern struct FlightTrim flight_trim;

#endif
