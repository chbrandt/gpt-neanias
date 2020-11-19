#!/bin/bash

# Run
function run() {
  # Search
  npt search ode mars/mro/ctx/edr '[-1,1,358,2]' --output search.geojson --contains
  # Download
  npt download search.geojson upstream --output download.geojson
  # Reduce
  npt process download.geojson reduced --docker-isis isis3 --tmpdir ./tmp --output reduced.geojson
}
