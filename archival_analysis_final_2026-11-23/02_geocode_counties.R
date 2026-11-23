# Step 2 (from raw). Assign each sample restaurant to a county (2018 Census cartographic boundaries) and export county land area.
# Usage: Rscript 02_geocode_counties.R <project root> <this folder>
args <- commandArgs(trailingOnly = TRUE)
root <- args[1]; here <- args[2]
suppressPackageStartupMessages(library(sf))
tmp <- file.path(tempdir(), "county_shp")
unzip(file.path(root, "analysis/2025-08-18-rohan/lat to fips/cb_2018_us_county_500k.zip"), exdir = tmp)
counties <- st_read(file.path(tmp, "cb_2018_us_county_500k/cb_2018_us_county_500k.shp"), quiet = TRUE)
write.csv(st_drop_geometry(counties)[, c("GEOID", "ALAND")], file.path(here, "inputs/census/county_land_area.csv"), row.names = FALSE)
d <- read.csv(file.path(here, "built/sample_restaurants.csv"), stringsAsFactors = FALSE)[, c("gmap_id", "latitude", "longitude")]
d$latitude <- as.numeric(d$latitude); d$longitude <- as.numeric(d$longitude)
ok <- !is.na(d$latitude) & !is.na(d$longitude)
pts <- st_transform(st_as_sf(d[ok, ], coords = c("longitude", "latitude"), crs = 4326), st_crs(counties))
sf_use_s2(FALSE)
j <- suppressMessages(suppressWarnings(st_join(pts, counties[, "GEOID"], join = st_intersects, left = TRUE)))
j <- j[!duplicated(j$gmap_id), ]
write.csv(data.frame(gmap_id = j$gmap_id, county_fips = j$GEOID, stringsAsFactors = FALSE), file.path(here, "built/county_fips.csv"), row.names = FALSE)
cat("restaurants:", nrow(d), " assigned a county:", sum(!is.na(j$GEOID)), "\n")
