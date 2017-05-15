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
 * @file "modules/flight_trim/flight_trim.c"
 * @author Rijesh Augustine
 * This module is designed to allow engaging AUTO2 on the first flight of you aircraft. It will fix a poorly calibrated transmitter and wi.
 */

#include "modules/flight_trim/flight_trim.h"
#include "subsystems/radio_control.h"
#include "inter_mcu.h"

#include "subsystems/datalink/datalink.h"
#include "subsystems/datalink/downlink.h"
#include "subsystems/commands.h"

struct FlightTrim flight_trim;

void flight_trim_init(void)
{
  flight_trim.calib_rc = FALSE;
  flight_trim.trim_ac = FALSE;
}

/*
void send_trim_msg(void)
{
  DOWNLINK_SEND_TRIM_MSG(DefaultChannel, DefaultDevice,
                          &(ap_state->command_roll_trim),
                          &(ap_state->command_pitch_trim),
                          &(ap_state->command_yaw_trim),
                          &(commands[COMMAND_ROLL]),
                          &(commands[COMMAND_PITCH]),
                          &(commands[COMMAND_YAW]));
}
*/
/*
<message name="TRIM_MSG" id="39">
  <field name="roll_t"      type="int16" />
  <field name="pitch_t"       type="int16" />
  <field name="yaw_t"       type="int16" />
  <field name="roll"      type="int16" />
  <field name="pitch"       type="int16" />
  <field name="yaw"       type="int16" />
</message>

*/

void flight_trim_event(void)
{
  if (flight_trim.calib_rc)
  {
    flight_trim_rc();
  }
  if (flight_trim.trim_ac)
  {
    flight_trim_ac();
  }
}
void flight_trim_rc(void)
{
  uint8_t i;
  for (i = 0; i < 5; i++) {
      radio_control.neutrals[i] += -radio_control.values[i];
  }
  flight_trim.calib_rc = FALSE;
}
void flight_trim_ac(void)
{
  ap_state->command_roll_trim = commands[COMMAND_ROLL];
  ap_state->command_pitch_trim = commands[COMMAND_PITCH];
  ap_state->command_yaw_trim = commands[COMMAND_YAW];

  flight_trim.trim_ac = FALSE;
}
