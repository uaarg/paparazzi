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
 * @file "modules/waldo_msg/waldo_msg.c"
 * @author Rijesh Augustine
 * This module is to rpovde a single msg for the waldo imaging software to subscribe to.
 */

#include "modules/waldo_msg/waldo_msg.h"
#include "subsystems/datalink/datalink.h"
#include "subsystems/datalink/downlink.h"
#include "subsystems/imu.h"
#include "state.h" //for estimator and attitude
#include "gps.h"
#include "generated/flight_plan.h"

int countup = 0;
float countupfast = 1.;
float groundalt = (float)GROUND_ALT;
int waldo_msg_freq = 10/WALDO_MSG_FREQ;

void waldo_runner(void)
{
  countup++;
  if (countup == waldo_msg_freq)
  {
    send_waldo_msg();
    #ifdef WALDO_DEBUG_MSG
    send_waldo_debug_msg();
    #endif

    countup = 0;
  }
}

void send_waldo_msg(void)
{
  // populate fields
  struct FloatEulers *att = stateGetNedToBodyEulers_f();
  struct UtmCoor_i utm = utm_int_from_gps(&gps, 0);
  float height = stateGetPositionUtm_f()->alt - groundalt;


  // send msg
  DOWNLINK_SEND_WALDO_MSG(DefaultChannel, DefaultDevice,
                          &(att->phi),
                          &(att->psi),
                          &(att->theta),
                          &gps.fix,
                          &utm.east, &utm.north, &utm.zone,
                          &gps.gspeed,
                          &gps.week,
                          &gps.tow,
                          &height);
}

void send_waldo_debug_msg(void)
{
  // populate fields
  countupfast = 10. + countupfast;
  // send msg
  DOWNLINK_SEND_WALDO_DEBUG_MSG(DefaultChannel, DefaultDevice, &countupfast);
}
