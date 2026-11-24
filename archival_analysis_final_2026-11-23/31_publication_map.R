# Publication Figure 2: geography of broad positioning. Usage: Rscript 31_publication_map.R <project root> <this folder>
# One circle per county with 5+ WPME or ME restaurants (national list); area = number of restaurants; fill = share positioned as Mediterranean.
# No title inside the figure (caption in outputs/publication/FIGURE_CAPTIONS.md). Writes PDF (vector) and 600 dpi PNG.
args <- commandArgs(trailingOnly = TRUE)
root <- args[1]; here <- args[2]
suppressPackageStartupMessages({library(sf); library(ggplot2)})
tmp <- file.path(tempdir(), "county_shp")
unzip(file.path(root, "analysis/2025-08-18-rohan/lat to fips/cb_2018_us_county_500k.zip"), exdir = tmp)
cty <- st_read(file.path(tmp, "cb_2018_us_county_500k/cb_2018_us_county_500k.shp"), quiet = TRUE)
cty <- cty[!(cty$STATEFP %in% c("02", "15", "60", "66", "69", "72", "78")), ]
sf_use_s2(FALSE)
states <- suppressMessages(suppressWarnings(aggregate(cty[, "STATEFP"], by = list(STATEFP = cty$STATEFP), FUN = function(x) x[1])))
a <- read.csv(file.path(here, "outputs/desc_map_county_data.csv"), colClasses = c(county_fips = "character"))
a5 <- a[a$n >= 5, ]
cen <- merge(suppressWarnings(st_centroid(cty[, "GEOID"])), a5, by.x = "GEOID", by.y = "county_fips")
p <- ggplot() +
  geom_sf(data = st_transform(states, 5070), fill = "white", color = "#9a9a9a", linewidth = 0.2) +
  geom_sf(data = st_transform(cen[order(-cen$n), ], 5070), aes(size = n, fill = share), shape = 21, color = "black", stroke = 0.25, alpha = 0.92) +
  scale_fill_gradient2(low = "#c8501e", mid = "#f2f2f2", high = "#1f5fae", midpoint = 50, limits = c(0, 100), name = "Positioned as\nMediterranean (%)") +
  scale_size_area(max_size = 9, breaks = c(5, 25, 100, 250), name = "Restaurants") +
  theme_void(base_size = 8, base_family = "sans") +
  theme(legend.title = element_text(size = 8), legend.text = element_text(size = 7.5), legend.position = "right", plot.margin = margin(2, 2, 2, 2),
        legend.key.height = unit(0.35, "cm"), legend.key.width = unit(0.35, "cm"))
dir.create(file.path(here, "outputs/publication"), showWarnings = FALSE)
ggsave(file.path(here, "outputs/publication/figure2_map.pdf"), p, width = 6.5, height = 3.7, device = cairo_pdf)
ggsave(file.path(here, "outputs/publication/figure2_map.png"), p, width = 6.5, height = 3.7, dpi = 600, bg = "white")
cat("counties", nrow(a5), "restaurants", sum(a5$n), "\n")
