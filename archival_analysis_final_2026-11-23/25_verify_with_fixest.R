# Independent check of the main regressions with fixest (R), from the frozen tables only.
# Usage: Rscript 25_verify_with_fixest.R <this folder>
# The Python scripts use their own estimator (common.Fit: fixed effects removed by alternating projections, county-clustered
# sandwich x G/(G-1)). This script rebuilds each model's data from the frozen files with separate code and estimates it with
# fixest::feols. Writes outputs/verification_fixest.csv; 26_verification_report.py compares it with the Python outputs.
args <- commandArgs(trailingOnly = TRUE)
here <- if (length(args)) args[1] else "."
suppressPackageStartupMessages(library(fixest))
setFixest_nthreads(4)
rd <- function(f) read.csv(file.path(here, "frozen", f), stringsAsFactors = FALSE, colClasses = c(gmap_id = "character"))
s <- read.csv(file.path(here, "frozen/restaurants.csv"), stringsAsFactors = FALSE, colClasses = c(county_fips = "character", state_fips = "character"))
for (v in c("wpme", "me_national", "me_original", "american")) s[[v]] <- s[[v]] == "True"
s <- s[!is.na(s$trump_share), ]
s$Z <- (s$trump_share - 0.4) / 0.1
ev_ssc <- ssc(adj = FALSE, cluster.adj = TRUE)          # matches the event models: sandwich x G/(G-1)
out <- list()
add <- function(model, term, fit, name, nobs_ = NULL) {
  ct <- coeftable(fit)
  out[[length(out) + 1]] <<- data.frame(model = model, term = term, est = ct[name, 1], se = ct[name, 2], p = ct[name, 4], n = if (is.null(nobs_)) nobs(fit) else nobs_)
}
lincom <- function(model, term, fit, w) {               # linear combination with the same clustered covariance and t(G-1)
  b <- coef(fit)[names(w)]; V <- vcov(fit)[names(w), names(w)]
  est <- sum(w * b); se <- sqrt(as.numeric(t(w) %*% V %*% w))
  out[[length(out) + 1]] <<- data.frame(model = model, term = term, est = est, se = se, p = NA, n = nobs(fit))
}

# ---- 1. Label choice (linear probability; state FE; county clusters; small-sample adjustment as in the Python script)
d <- s[(s$wpme | s$me_national) & !is.na(s$n_reviews) & complete.cases(s[, c("log_pop", "log_density", "mena", "college", "foreign")]), ]
d$y <- as.numeric(d$wpme)
lc_ssc <- ssc(adj = TRUE, fixef.K = "full", cluster.adj = TRUE)
f <- feols(y ~ Z | state_fips, d, cluster = ~county_fips, ssc = lc_ssc);                                        add("label choice: state FE only", "Trump share per 10 pts", f, "Z")
f <- feols(y ~ Z + log_pop + log_density | state_fips, d, cluster = ~county_fips, ssc = lc_ssc);                add("label choice: + population, density", "Trump share per 10 pts", f, "Z")
f <- feols(y ~ Z + log_pop + log_density + mena + college + foreign | state_fips, d, cluster = ~county_fips, ssc = lc_ssc)
add("label choice: + college, foreign-born", "Trump share per 10 pts", f, "Z"); add("label choice: + college, foreign-born", "Middle Eastern ancestry per 1 pt", f, "mena")

# ---- 2. Events: WPME-minus-ME gap, each event and pooled
ev <- rd("event_cells.csv.gz")
g <- s[s$wpme | s$me_national, c("gmap_id", "county_fips", "Z", "wpme")]
ev <- merge(ev[ev$kind == "event", ], g, by = "gmap_id")
ev$W <- as.numeric(ev$wpme)
did <- function(c, label, fe) {
  c <- c[c$bin <= 0, ]
  c$WP <- c$W * (c$bin >= 0); c$WPZ <- c$WP * c$Z
  f <- feols(as.formula(paste("mean ~ WP + WPZ |", fe)), c, cluster = ~county_fips, ssc = ev_ssc)
  add(label, "WPME x After x Trump share", f, "WPZ")
}
for (nm in c("2016 election", "Travel ban")) {
  c <- ev[ev$event == nm, ]; c$cb <- paste(c$county_fips, c$bin)
  did(c, paste0("event gap: ", nm), "gmap_id + cb")
}
st <- ev[ev$event %in% c("2016 election", "Travel ban"), ]
st$rid <- paste(st$gmap_id, st$event); st$cbe <- paste(st$county_fips, st$bin, st$event)
did(st, "event gap: pooled election and travel ban", "rid + cbe")

# ---- 3. Which group moves (American-first reference), shared timeline
tl <- rd("timeline_cells.csv.gz")
g3 <- s[s$wpme | s$me_national | s$american, c("gmap_id", "county_fips", "Z", "wpme", "me_national")]
t3 <- merge(tl, g3, by = "gmap_id")
t3$cb <- paste(t3$county_fips, t3$bin)
t3$WPg <- as.numeric(t3$wpme); t3$MEg <- as.numeric(t3$me_national & !t3$wpme)
for (gn in c("MEg", "WPg")) for (k in c("E", "B")) {
  t3[[paste0(gn, k)]] <- t3[[gn]] * (t3$bin == ifelse(k == "E", 100, 200))
  t3[[paste0(gn, k, "Z")]] <- t3[[paste0(gn, k)]] * t3$Z
}
f3 <- feols(mean ~ MEgE + MEgEZ + MEgB + MEgBZ + WPgE + WPgEZ + WPgB + WPgBZ | gmap_id + cb, t3, cluster = ~county_fips, ssc = ev_ssc)
add("which group moves", "ME x after election x Trump share", f3, "MEgEZ"); add("which group moves", "ME x after travel ban x Trump share", f3, "MEgBZ")
add("which group moves", "WPME x after election x Trump share", f3, "WPgEZ"); add("which group moves", "WPME x after travel ban x Trump share", f3, "WPgBZ")
lincom("which group moves", "ME: average of the two events", f3, c(MEgEZ = .5, MEgBZ = .5))
lincom("which group moves", "WPME: average of the two events", f3, c(WPgEZ = .5, WPgBZ = .5))
lincom("which group moves", "ME: change at 60% Trump share after travel ban", f3, c(MEgB = 1, MEgBZ = 2))
lincom("which group moves", "WPME: change at 60% Trump share after travel ban", f3, c(WPgB = 1, WPgBZ = 2))

# ---- 4. Each group over time (figure 7 model): period 4 (the last pre-election period) is the reference
tt <- merge(rd("story_timeline_cells_3group.csv.gz"), g3, by = "gmap_id")
tt$cb <- paste(tt$county_fips, tt$period)
tt$ME <- as.numeric(tt$me_national & !tt$wpme); tt$WP <- as.numeric(tt$wpme)
tt$per <- factor(tt$period); tt$MEZ <- tt$ME * tt$Z; tt$WPZ <- tt$WP * tt$Z
f4 <- feols(mean ~ i(per, ME, ref = "4") + i(per, MEZ, ref = "4") + i(per, WP, ref = "4") + i(per, WPZ, ref = "4") | gmap_id + cb, tt, cluster = ~county_fips, ssc = ev_ssc)
pick <- function(p, tag) paste0("per::", p, ":", tag)
for (grp in c("ME", "WP")) for (p in c(5, 7)) {
  w <- c(); w[pick(p, paste0(grp, "Z"))] <- 1
  for (q in 0:3) w[pick(q, paste0(grp, "Z"))] <- -1 / 5
  lincom("each group over time", paste0(ifelse(grp == "ME", "ME", "WPME"), ": period ", ifelse(p == 5, "after election", "after travel ban"), " vs pre-election average"), f4, w)
}

# ---- 5. Star breakdown: share of one-star reviews
sc <- merge(rd("star_cells.csv.gz"), g3, by = "gmap_id")
sc$n <- sc$n1 + sc$n2 + sc$n3 + sc$n4 + sc$n5; sc$s1 <- sc$n1 / sc$n
sc$cb <- paste(sc$county_fips, sc$bin); sc$post <- as.numeric(sc$bin >= 100)
sc$MEp <- as.numeric(sc$me_national & !sc$wpme) * sc$post; sc$WPp <- as.numeric(sc$wpme) * sc$post
sc$MEpZ <- sc$MEp * sc$Z; sc$WPpZ <- sc$WPp * sc$Z
f5 <- feols(s1 ~ MEp + MEpZ + WPp + WPpZ | gmap_id + cb, sc, cluster = ~county_fips, ssc = ev_ssc)
add("star breakdown: share 1-star", "ME x After x Trump share", f5, "MEpZ"); add("star breakdown: share 1-star", "WPME x After x Trump share", f5, "WPpZ")

# ---- 6. Reviewer leniency: rating relative to the reviewer's usual (cells written by 19_star_breakdown_leniency.py)
lp <- file.path(here, "frozen/leniency_cells.csv.gz")
if (file.exists(lp)) {
  lc <- merge(read.csv(lp, stringsAsFactors = FALSE, colClasses = c(gmap_id = "character")), g3, by = "gmap_id")
  lc$cb <- paste(lc$county_fips, lc$bin)
  for (gn in c("ME", "WP")) for (k in c("e", "b")) {
    base <- if (gn == "ME") as.numeric(lc$me_national & !lc$wpme) else as.numeric(lc$wpme)
    lc[[paste0(gn, k)]] <- base * (lc$bin == ifelse(k == "e", 100, 200)); lc[[paste0(gn, k, "Z")]] <- lc[[paste0(gn, k)]] * lc$Z
  }
  f6 <- feols(rel_mean ~ MEe + MEeZ + MEb + MEbZ + WPe + WPeZ + WPb + WPbZ | gmap_id + cb, lc, cluster = ~county_fips, ssc = ev_ssc)
  add("leniency: rating relative to reviewer's usual", "ME x after travel ban x Trump share", f6, "MEbZ")
  add("leniency: rating relative to reviewer's usual", "ME x after election x Trump share", f6, "MEeZ")
  add("leniency: rating relative to reviewer's usual", "WPME x after travel ban x Trump share", f6, "WPbZ")
}
res <- do.call(rbind, out)
# ---- 7. Robustness of the lead estimate (ME x after travel ban x Trump share, three-group model)
t3$state <- substr(t3$county_fips, 1, 2)
fml <- mean ~ MEgE + MEgEZ + MEgB + MEgBZ + WPgE + WPgEZ + WPgB + WPgBZ | gmap_id + cb
rb <- list()
radd <- function(label, f) for (tm in c("MEgBZ", "MEgEZ", "WPgBZ")) {
  ct <- coeftable(f); rb[[length(rb) + 1]] <<- data.frame(variant = label, term = tm, est = ct[tm, 1], se = ct[tm, 2], p = ct[tm, 4], n = nobs(f))
}
radd("as reported (each restaurant-period equal weight; county clusters)", f3)
radd("weighted by number of reviews in the cell", feols(fml, t3, weights = ~n, cluster = ~county_fips, ssc = ev_ssc))
radd("clustered by state", feols(fml, t3, cluster = ~state, ssc = ev_ssc))
radd("cells with 3 or more reviews", feols(fml, t3[t3$n >= 3, ], cluster = ~county_fips, ssc = ev_ssc))
radd("restaurant and period FE only (no county-by-period FE)", feols(mean ~ MEgE + MEgEZ + MEgB + MEgBZ + WPgE + WPgEZ + WPgB + WPgBZ + I((bin == 100) * Z) + I((bin == 200) * Z) | gmap_id + bin, t3, cluster = ~county_fips, ssc = ev_ssc))
radd("state-by-period FE instead of county-by-period", feols(mean ~ MEgE + MEgEZ + MEgB + MEgBZ + WPgE + WPgEZ + WPgB + WPgBZ + I((bin == 100) * Z) + I((bin == 200) * Z) | gmap_id + state^bin, t3, cluster = ~county_fips, ssc = ev_ssc))
t3o <- merge(tl, s[s$wpme | s$me_original | s$american, c("gmap_id", "county_fips", "Z", "wpme", "me_original")], by = "gmap_id")
t3o$cb <- paste(t3o$county_fips, t3o$bin); t3o$WPg <- as.numeric(t3o$wpme); t3o$MEg <- as.numeric(t3o$me_original & !t3o$wpme)
for (gn in c("MEg", "WPg")) for (k in c("E", "B")) { t3o[[paste0(gn, k)]] <- t3o[[gn]] * (t3o$bin == ifelse(k == "E", 100, 200)); t3o[[paste0(gn, k, "Z")]] <- t3o[[paste0(gn, k)]] * t3o$Z }
radd("original 20-category ME list", feols(fml, t3o, cluster = ~county_fips, ssc = ev_ssc))
rb <- do.call(rbind, rb)
# by restaurant size: reviews in the 210 pre-election days, thirds of the ME/WPME distribution
pre <- aggregate(n ~ gmap_id, t3[t3$bin < 0, ], sum); names(pre)[2] <- "pre_n"
t3 <- merge(t3, pre, by = "gmap_id", all.x = TRUE); t3$pre_n[is.na(t3$pre_n)] <- 0
foc <- unique(t3[t3$MEg == 1 | t3$WPg == 1, c("gmap_id", "pre_n")]); q <- quantile(foc$pre_n, c(1/3, 2/3))
sz <- list()
for (lab in c("small", "medium", "large")) {
  keep <- if (lab == "small") t3$pre_n <= q[1] else if (lab == "medium") t3$pre_n > q[1] & t3$pre_n <= q[2] else t3$pre_n > q[2]
  d <- t3[keep, ]; ct <- coeftable(feols(fml, d, cluster = ~county_fips, ssc = ev_ssc))
  sz[[lab]] <- data.frame(size = lab, pre_reviews = if (lab == "small") sprintf("%d or fewer", q[1]) else if (lab == "medium") sprintf("%d to %d", q[1] + 1, q[2]) else sprintf("more than %d", q[2]),
                          me_restaurants = length(unique(d$gmap_id[d$MEg == 1])), est = ct["MEgBZ", 1], se = ct["MEgBZ", 2], p = ct["MEgBZ", 4])
}
write.csv(do.call(rbind, sz), file.path(here, "outputs/verification_by_size.csv"), row.names = FALSE)
write.csv(rb, file.path(here, "outputs/verification_robustness.csv"), row.names = FALSE)
print(rb, digits = 3, row.names = FALSE)
write.csv(res, file.path(here, "outputs/verification_fixest.csv"), row.names = FALSE)
print(res, digits = 4, row.names = FALSE)
