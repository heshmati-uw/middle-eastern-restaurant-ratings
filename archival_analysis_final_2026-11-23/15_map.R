# Descriptive map: where restaurants serving Middle Eastern food position broadly (WPME) versus explicitly (ME).
# Usage: Rscript 15_map.R <project root> <this folder>
# One dot per county with 5+ WPME or ME restaurants (national list); size = number of restaurants; color = share WPME.
args <- commandArgs(trailingOnly = TRUE)
root <- args[1]; here <- args[2]
suppressPackageStartupMessages({library(sf); library(ggplot2)})
tmp <- file.path(tempdir(), "county_shp")
unzip(file.path(root, "analysis/2025-08-18-rohan/lat to fips/cb_2018_us_county_500k.zip"), exdir = tmp)
cty <- st_read(file.path(tmp, "cb_2018_us_county_500k/cb_2018_us_county_500k.shp"), quiet = TRUE)
cty <- cty[!(cty$STATEFP %in% c("02", "15", "60", "66", "69", "72", "78")), ]
sf_use_s2(FALSE)
states <- suppressMessages(suppressWarnings(aggregate(cty[, "STATEFP"], by = list(STATEFP = cty$STATEFP), FUN = function(x) x[1])))
r <- read.csv(file.path(here, "frozen/restaurants.csv"), colClasses = c(county_fips = "character"), stringsAsFactors = FALSE)
r <- r[(r$wpme == "True" | r$me_national == "True") & !is.na(r$trump_share), ]
r$w <- as.numeric(r$wpme == "True")
a <- aggregate(cbind(n = 1, wpme = r$w) ~ county_fips, data = r, FUN = sum)
a$share <- 100 * a$wpme / a$n
a <- merge(a, unique(r[, c("county_fips", "trump_share", "mena")]), by = "county_fips")
write.csv(a, file.path(here, "outputs/desc_map_county_data.csv"), row.names = FALSE)
a5 <- a[a$n >= 5, ]
cen <- suppressWarnings(st_centroid(cty[, "GEOID"]))
cen <- merge(cen, a5, by.x = "GEOID", by.y = "county_fips")
proj <- 5070
p <- ggplot() +
  geom_sf(data = st_transform(states, proj), fill = "#f4f3ef", color = "#c9c7c0", linewidth = 0.25) +
  geom_sf(data = st_transform(cen[order(-cen$n), ], proj), aes(size = n, fill = share), shape = 21, color = "#fcfcfb", stroke = 0.35, alpha = 0.92) +
  scale_fill_gradient2(low = "#eb6834", mid = "#e9e7e1", high = "#2a78d6", midpoint = 50, limits = c(0, 100), name = "Share positioned\nas Mediterranean (%)") +
  scale_size_area(max_size = 13, breaks = c(5, 25, 100, 250), name = "Restaurants") +
  labs(title = "Where restaurants serving Middle Eastern food position broadly",
       subtitle = "Blue: mostly \"Mediterranean\" (WPME). Orange: mostly explicit Middle Eastern labels (ME).",
       caption = paste0("Counties with 5 or more WPME or ME restaurants (", nrow(a5), " counties, ", sum(a5$n), " restaurants). First Google category, 2021.")) +
  theme_void(base_size = 10) +
  theme(plot.background = element_rect(fill = "#fcfcfb", color = NA), plot.title = element_text(face = "bold", size = 12.5, color = "#0b0b0b"),
        plot.subtitle = element_text(size = 9.5, color = "#52514e"), plot.caption = element_text(size = 7.5, color = "#52514e", hjust = 0),
        legend.title = element_text(size = 8.5, color = "#52514e"), legend.text = element_text(size = 8, color = "#52514e"),
        plot.margin = margin(10, 10, 8, 10), legend.position = "right")
ggsave(file.path(here, "outputs/desc_map_wpme_share.png"), p, width = 10.5, height = 6.2, dpi = 150, bg = "#fcfcfb")
cat("counties plotted:", nrow(a5), " restaurants:", sum(a5$n), "\n")
cat("correlation of WPME share with Middle Eastern ancestry share (counties with 5+):", round(cor(a5$share, a5$mena), 2), "; with Trump share:", round(cor(a5$share, a5$trump_share), 2), "\n")
