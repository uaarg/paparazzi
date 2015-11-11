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

open Printf

module G = MapCanvas

type obstacles = {
  obsid : string;
  mutable circleshape : GnoCanvas.ellipse;
  mutable last_update : float
}


let obstacles = Hashtbl.create 1

let new_obstacle = fun id wgs84 fillcolor radius time (geomap:MapCanvas.widget) ->
  let gencircle = geomap#circle ~fill_color:fillcolor  ~color:fillcolor wgs84 radius in
  let obstacle = {obsid = id; circleshape = gencircle; last_update = time } in 
  Hashtbl.add obstacles id obstacle

let remove_obstacle = fun id ->
  try
   let obstacle = Hashtbl.find obstacles id in
   obstacle.circleshape#destroy ();
   Hashtbl.remove obstacles id
  with _ -> ()

let update_obstacle = fun id wgs84 fillcolor radius time (geomap:MapCanvas.widget) ->
  try
    let obstacle = Hashtbl.find obstacles id in
    let gencircle = geomap#circle ~fill_color:fillcolor  ~color:fillcolor wgs84 radius in
    obstacle.circleshape#destroy ();
    obstacle.circleshape <- gencircle;
    obstacle.last_update <- time
  with _ -> () 

let obstacle_exist = fun id ->
  Hashtbl.mem obstacles id
