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
 * @file "modules/waldo_msg/waldo_msg.h"
 * @author Rijesh Augustine
 * This module is to rpovde a single msg for the waldo imaging software to subscribe to.
 */

#ifndef WALDO_MSG_H
#define WALDO_MSG_H

extern void waldo_runner(void);
extern void send_waldo_msg(void);
extern void send_waldo_debug_msg(void);

#endif

#ifndef WALDO_MSG_FREQ
#define WALDO_MSG_FREQ 2
#endif
