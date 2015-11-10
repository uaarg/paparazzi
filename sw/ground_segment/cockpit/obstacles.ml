(*
 * Copyright (C) 2015 Gautier Hattenberger <gautier.hattenberger@enac.fr>
 *
 * This file is part of paparazzi.
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
 *
 *)

(*open Latlong*)

type obstacle = {
  obstacle_track : MapTrack.track;
  mutable last_update : float
}

(*let obstacles = (string, obstacle) Hashtbl.t*)
let obstacles = Hashtbl.create 1

let new_obstacle = fun id name radius time geomap ->
  let track = new MapTrack.track ~size:200 ~icon:"fixedwing" ~name ~show_carrot:false id geomap in
  let obstacle = { obstacle_track = track; last_update = time } in
  Hashtbl.add obstacles id obstacle

let remove_obstacle = fun id ->
  try
    let obstacle = Hashtbl.find obstacles id in
    obstacle.obstacle_track#destroy ();
    Hashtbl.remove obstacles id
  with _ -> () (* no obstacle *)

let update_obstacle = fun id wgs84 alt time ->
  try
    let obstacle = Hashtbl.find obstacles id in
    obstacle.obstacle_track#move_icon wgs84 0.0 alt 0.0 0.0;
    obstacle.last_update <- time;
  with _ -> () (* no obstacle, add a new one ? *)

let obstacle_exist = fun id ->
  Hashtbl.mem obstacles id

