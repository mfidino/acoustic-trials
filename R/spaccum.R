# Create species accumulation curves
library(vegan)
library(dplyr)
library(lubridate)
library(bdc)
library(bbplot)

# reading in current dataset
dat <- read.csv(
  "./mixit_snips/mixit_to_birdnet_classifications.csv"
)

# get all of the files that were processed
all_files <- list.files(
  "D:/uwin_sounds",
  full.names = TRUE
)
# remove some stuff or the time being
all_files <- all_files[-grep("split|TEMP|TEST", all_files)]

flist <- vector("list", length = length(all_files))
for(i in 1:length(all_files)){
  flist[[i]] <- list.files(
    all_files[i],
    recursive = TRUE,
    full.names = TRUE
  )
}

parse_date <- function(x,y){
  year_val <- substr(
    sapply(
      x,
      "[[",
      y
    ),
    1,
    4
  )

  month_val <- substr(
    sapply(
      x,
      "[[",
      y
    ),
    5,
    6
  )

  day_val <- substr(
    sapply(
      x,
      "[[",
      y
    ),
    7,
    8
  )
  return(
    paste0(
      year_val,"-", month_val,"-", day_val
    )
  )

}

all_samples <- vector("list", length = length(flist))
for(i in 1:length(flist)){

  tmp <- strsplit(
    flist[[i]],
    "/"
  )
  if(all(sapply(tmp, length) != 5)){
    next
  }
  all_samples[[i]] <- data.frame(
    city = sapply(
      tmp,"[[", 3
    ),
    site = sapply(
      tmp, "[[", 4
    ),
    date = parse_date(
      tmp,5
    )
  )
}
all_samples <- dplyr::bind_rows(all_samples)
all_samples$site <- gsub(
  " ", "_", all_samples$site
)


# get some of the other info we need here as columns, based on
#  splitting filepatphs

tmp <- strsplit(dat$path,"\\\\")
dat$city <- sapply(
  tmp,
  "[[",
  2
)

dat$site <- sapply(
  tmp,
  "[[",
  3
)

dat$date <- parse_date(
  tmp,5
)

# get species names via bdc
longshot <- bdc::bdc_query_names_taxadb(
  sci_name = unique(dat$scientific_name)
)
my_passers <- longshot$scientificName[
  longshot$order == "Passeriformes"
]

# start summarizing now to get a species accumulation curve
#  for each site
dl <- split(
  dat,
  factor(
    paste0(
      dat$city,"_",dat$site
    )
  )
)



my_cmat <- vector("list", length = length(dl))
names(my_cmat) <- names(dl)
to_go <- rep(FALSE, length(dl))
for(i in 1:length(dl)){
  tmp <- dl[[i]]
  tmp <- tmp[tmp$confidence > 0.9,]
  tmp <- tmp[tmp$scientific_name %in% my_passers,]
  if(nrow(tmp) == 0){
    to_go[i] <- TRUE
    next
  }
  ar <- all_samples[all_samples$site == tmp$site[1],]
  ar <- dplyr::distinct(ar)
  tmp <- dplyr::distinct(
    tmp[,c("common_name", "city", "site", "date", "scientific_name")]
  )
  tmp$count <- 1
  unq_sp <- unique(tmp$common_name)
  ar <- ar[rep(1:nrow(ar), each = length(unq_sp)),]
  ar$common_name <- rep(unq_sp, length(unique(ar$date)))
  tmp <- dplyr::left_join(
    ar,
    tmp,
    by = c("site", "date", "city", "common_name")
  )
  tmp$count[is.na(tmp$count)] <- 0
  my_cmat[[i]] <- matrix(
    tmp$count,
    ncol = length(unq_sp),
    nrow = length(unique(tmp$date)),
    byrow = TRUE
  )
  colnames(my_cmat[[i]]) <- unq_sp
  if(nrow(my_cmat[[i]]) == 1){
    to_go[i] <- TRUE
  }
}
to_go <- which(to_go)

my_cmat <- my_cmat[-to_go]
# create speccaum

results <- vector(
  "list",
  length = length(my_cmat)
)
cs <- names(my_cmat)
for(i in 1:length(results)){
  city <- substr(
    cs[i],1,4
  )
  site <- substr(
    cs[i], 6, nchar(cs[i])
  )
  sp <- vegan::specaccum(
    my_cmat[[i]]#,
    #method = "collector"
  )
  results[[i]] <- data.frame(
    city = city,
    site = site,
    days = sp$sites,
    n = sp$richness
  )
}
results <- dplyr::bind_rows(
  results
)


results <- split(
  results,
  factor(results$city)
)

cityn <- sapply(
  results,
  function(x) max(x$n)
)
for(i in 1:length(results)){
  results[[i]] <- split(
    results[[i]],
    factor(results[[i]]$site)
  )
}

# plot the accumulation curves out
windows(12,6)
m <- matrix(1:8, ncol = 4, nrow = 2)
layout(m)
par(mar = c(1,3,3,1), oma = c(8,8,0.5,0.5), lend = 2)

pnames <- c(
  "Atlanta, GA",
  "Chicago, IL",
  "Iowa City, IA",
  "Jackson, MS",
  "Washington D.C.",
  "Phoenix, AZ",
  "Salt Lake City, UT",
  "Seattle, WA"
)
for(i in 1:length(results)){
  tmp <- results[[i]]
  bbplot::blank(xlim = c(1,10), ylim = c(0, cityn[i]), bty="l")
  bbplot::axis_blank(1,minor = FALSE)
  bbplot::axis_blank(2, minor = FALSE)
  my_pal <- viridisLite::viridis(n = length(tmp))
  bbplot::axis_text(
    text =pnames[i],
    side = 3,
    line = 1
  )
  if(i %in% m[2,]){
    bbplot::axis_text(side = 1, line = 1)
  }

  bbplot::axis_text(side = 2, line = 1, las =2)
  for(j in 1:length(tmp)){
    lines(
      x = tmp[[j]]$days,
      y = tmp[[j]]$n,
      lwd = 8,
      col = scales::alpha(
        my_pal[j],
        alpha = 0.7
      )
    )
  }
  bbplot::axis_text(
    "Days (5 minute recording per day)",
    side = 1,
    outer = TRUE,
    at = 0.5,
    line  =5,
    cex = 2
    )
  bbplot::axis_text(
    "Unique species count",
    side = 2,
    outer = TRUE,
    at = 0.5,
    line  =3,
    cex = 2
  )

}

