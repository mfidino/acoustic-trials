library(dplyr)
library(bbplot)
library(bdc)

source("./R/functions.R")

# pull_files(): reads in csv outputs stored in folders

# read in output from mixit classifictions
mx <- pull_files("mixit_snips")

# and then the no mixit snips
nmx <- pull_files("no_mixit_snips")

dat <- dplyr::bind_rows(
  list(
    mx,
    nmx
  )
)

# read in noise files
n1 <- read.csv("longshot2.csv")
n2 <- read.csv("longshot3.csv")
n1 <- dplyr::bind_rows(
  n1,n2
)
n1 <- dplyr::distinct(n1)
n1 <- n1[!duplicated(n1$path),]

# fix file names a bit

tmp <- strsplit(
  n1$path,
  "/|\\\\"
)

other_stuff <- sapply(
  tmp,
  function(x){
    jj <- paste0(
      x[1:(length(x)-1)],
      collapse = "/"
    )
    jj <- gsub("\\\\","/", jj)
    return(jj)
  }
)
file <- sapply(
  tmp,
  function(x){
    x[length(x)]
  }

)
tmp <- strsplit(
  file,
  "_"
)
tmp <- lapply(
  tmp,
  function(x){
    x[3] = gsub("\\.wav","", x[3])
    return(x)
  }
)
tmp <- lapply(
  tmp,
  function(x){
    x[3] <- as.character(round(as.numeric(x[3]),2))
    return(x)
  }
)
tmp <- lapply(
  tmp,
  function(x){
    paste0(
      paste0(
        x,
        collapse = "_"
      ),
      ".wav"
    )
  }
)
tmp <- unlist(tmp)
file <- paste0(
  other_stuff,"/",
  tmp
)

n1$path <- file

# and do this with the other files now too
tmp <- strsplit(
  dat$path,
  "/|\\\\"
)

other_stuff <- sapply(
  tmp,
  function(x){
    jj <- paste0(
      x[1:(length(x)-1)],
      collapse = "/"
    )
    jj <- gsub("\\\\","/", jj)
    return(jj)
  }
)
file <- sapply(
  tmp,
  function(x){
    x[length(x)]
  }

)
tmp <- strsplit(
  file,
  "_"
)
tmp <- lapply(
  tmp,
  function(x){
    x[3] = gsub("\\.wav","", x[3])
    return(x)
  }
)
tmp <- lapply(
  tmp,
  function(x){
    x[3] <- as.character(round(as.numeric(x[3]),2))
    return(x)
  }
)
tmp <- lapply(
  tmp,
  function(x){
    paste0(
      paste0(
        x,
        collapse = "_"
      ),
      ".wav"
    )
  }
)
tmp <- unlist(tmp)
file <- paste0(
  other_stuff,"/",
  tmp
)

dat$path <- file

longshot <- dplyr::inner_join(
  dat,
  n1,
  by= "path"
)

# pull the site info from the file path
tmp <- strsplit(
  dat$path,
  "/|\\\\"
)
site_info <- vector("list", length = length(tmp))
pb <- txtProgressBar(max = length(site_info))
for(i in 1:length(site_info)){
  setTxtProgressBar(pb, i)
  len_dat <- length(tmp[[i]])
  if(len_dat %in% c(7,8)){
    site_info[[i]] <- data.frame(
      city = tmp[[i]][len_dat-3],
      site = tmp[[i]][len_dat-2],
      date = parse_date(list(tmp[[i]]), len_dat)
    )
  }
  if(len_dat == 6){
    site_info[[i]] <- data.frame(
      city = tmp[[i]][len_dat-2],
      site = tmp[[i]][len_dat-1],
      date = parse_date(list(tmp[[i]]), len_dat)
    )
  }
}
site_info <- dplyr::bind_rows(site_info)
dat <- dplyr::bind_cols(dat, site_info)

# same for noise
tmp <- strsplit(
  n1$path,
  "/|\\\\"
)
site_info <- vector("list", length = length(tmp))
pb <- txtProgressBar(max = length(site_info))
for(i in 1:length(site_info)){
  setTxtProgressBar(pb, i)
  len_dat <- length(tmp[[i]])
  if(len_dat %in% c(7,8)){
    site_info[[i]] <- data.frame(
      city = tmp[[i]][len_dat-3],
      site = tmp[[i]][len_dat-2],
      date = parse_date(list(tmp[[i]]), len_dat)
    )
  }
  if(len_dat == 6){
    site_info[[i]] <- data.frame(
      city = tmp[[i]][len_dat-2],
      site = tmp[[i]][len_dat-1],
      date = parse_date(list(tmp[[i]]), len_dat)
    )
  }
}
site_info <- dplyr::bind_rows(site_info)
n1 <- dplyr::bind_cols(n1, site_info)
n1$file <- sapply(
  strsplit(
    n1$path,
    "/"
  ),
  function(x){
    x[length(x)]
  }
)
dat$file <-sapply(
  strsplit(
    dat$path,
    "/"
  ),
  function(x){
    x[length(x)]
  }
)
dat <- dplyr::inner_join(
  dat,
  n1[,-1],
  by = c("city","site","date","file")
)

# get family info
sn <- unique(dat$scientific_name)

sp_dat <- bdc::bdc_query_names_taxadb(
  sci_name = sn
)

# add a couple family bits
sp_dat$family[sp_dat$original_search == "Gallinula galeata"] <- "Rallidae"
sp_dat$family[sp_dat$original_search == "Cistothorus stellaris"] <- "Troglodytidae"
sp_dat$family[sp_dat$original_search == "Circus hudsonius"] <- "Accipitridae"
sp_dat$family[sp_dat$original_search == "Mareca strepera"] <- "Anatidae"
sp_dat$family[sp_dat$original_search == "Corthylio calendula"] <- "Regulidae"
sp_dat$family[sp_dat$original_search == "Spatula clypeata"] <- "Anatidae"
# now get the file name
dat <- dplyr::inner_join(
  dat,
  sp_dat[,c("original_search", "family")],
  by = c("scientific_name" = "original_search")
)

# get comparisons for when both mixit and no_mixit find the
#  same species in the same files

# clean up file names a bit

to_query <- dat %>%
  dplyr::group_by(city, site, date, file, common_name, start_time, end_time, family) %>%
  dplyr::summarise(longshot = length(scientific_name)) %>%
  data.frame()

comp_results <- vector("list", length = nrow(to_query))
pb <- txtProgressBar(max = length(comp_results))
for(i in 1:length(comp_results)){
  setTxtProgressBar(pb, i)
  tmp <- dat[
    dat$file == to_query$file[i] &
      dat$site == to_query$site[i] &
      dat$city == to_query$city[i] &
      dat$start_time == to_query$start_time[i] &
      dat$end_time == to_query$end_time[i] &
      dat$common_name == to_query$common_name[i],
  ]
  if(nrow(tmp)>1){
    tmp <- tmp[order(tmp$type),]
    comp_results[[i]] <- data.frame(
      tmp[1,c("city","site","date","common_name","family","mean_dB")],
      max_confidence = max(tmp$confidence),
      diff = tmp$confidence[1] - tmp$confidence[2],
      comparison = "both_ID",
      path = ifelse(
        tmp$confidence[1] >= tmp$confidence[2],
        tmp$path[1],
        tmp$path[2]
      )
    )
  } else {
    comp_results[[i]] <- data.frame(
      tmp[1,c("city","site","date","common_name","family","mean_dB")] ,
      max_confidence = tmp$confidence,
      diff = NA,
      comparison = ifelse(
        tmp$type == "mixit_snips",
        "mixit",
        "no mixit"
      ),
      path = tmp$path
    )
  }
}

comp_results <- dplyr::bind_rows(comp_results)
comp_results <- split(
  comp_results,
  factor(comp_results$comparison)
)
# look at those that both found

hist(
  comp_results$both_ID$diff,
  xlab = "Difference in BirdNET classification accuracy for mixit vs. no mixit seperation",
  main = ""
  )

hist(comp_results$mixit$mean_dB)
hist(comp_results$both_ID$mean_dB)
plot(comp_results$both_ID$diff ~ comp_results$both_ID$mean_dB)

lc <- read.csv("Audiomoth_landcover.csv")
lc$link <- NA

unq_sites <- unique(dat$site)
# link sites
for(i in 1:nrow(lc)){
  tt <- grep(lc$site[i], unq_sites)
  if(length(tt) == 1){
    lc$link[i] <- unq_sites[tt]
  }
  if(length(tt) == 0){
    tt <- agrep(lc$site[i], unq_sites)
    if(length(tt) == 1){
      lc$link[i] <- unq_sites[tt]
    }
  }

}

lc <- lc[!is.na(lc$link),]

windows(6,6)
par(mar = c(6,6,1,1))
bbplot::blank(xlim = c(0,1), ylim = c(80,120), bty = "l")
bbplot::axis_blank(1)
bbplot::axis_blank(2)
bbplot::axis_text(side = 1, line = 0.6,cex = 1.2)
bbplot::axis_text(side = 2, line = 0.6,cex = 1.2, las =2)
bbplot::axis_text("Proportion built area around site",
                  cex = 1.4, line = 2.5, side = 1)
bbplot::axis_text("Average dB across surveys at site",
                  cex = 1.4, line = 3.25, side = 2)

points(
  x = lc$built.area,
  y = lc$mean,
  pch = 21,
  bg = "gray50",
  cex = 1.7
)

m1 <- lm(
  mean ~ built.area,
  data = lc
)

m1 <- lme4::lmer(
  mean ~ built.area + (1|city),
  data = lc
)

mu_sound <- n1 %>%
  dplyr::group_by(site) %>%
  dplyr::summarise(mean = mean(mean_dB))

lc <- dplyr::inner_join(
  lc,
  mu_sound,
  by = c("link" = "site")
)

# look at it by species
both_ID <- comp_results$both_ID
spc <- both_ID %>%
  dplyr::group_by(common_name, family) %>%
  dplyr::summarise(
    n = length(path),
    mu = median(diff),
    sd = sd(diff)
  ) %>%
  dplyr::filter(n>1)

spc <- spc[order(spc$mu, decreasing = TRUE),]
windows(6,9)
tiff(
  "./iuwc_plots/average_improvement_mixit.tiff",
  height = 9,
  width = 6,
  units = "in",
  res = 600,
  compression = "lzw"
)
par(mar = c(6,1,0.5,1))
bbplot::blank(xlim = c(0,0.5), ylim = c(1,152))
bbplot::axis_blank(1)
bbplot::axis_text(side = 1, line = 0.8, cex = 1.2)
bbplot::axis_text("Average improvement in BirdNET accuracy\nwith sound seperation by species",
                  line = 4, cex = 1.5, side = 1)
sp_points <- rev(1:152)

points(
  x = spc$mu,
  y = sp_points,
  cex = 1,
  pch = 21,
  bg = "gray"
)
dev.off()
write.csv(
  spc,
  "./iuwc_plots/average_improvement_mixit_species.csv",
  row.names = FALSE
)
spc[spc$mu>0,]

fpc <- both_ID %>%
  dplyr::group_by(family) %>%
  dplyr::summarise(
    n = length(path),
    mu = median(diff),
    sd = sd(diff),
    nsp = length(unique(common_name))
  ) %>%
  dplyr::filter(n>1) %>%
  dplyr::filter(nsp > 1) %>%
  data.frame()
fpc <- fpc[order(fpc$mu, decreasing = TRUE),]


# look at things only picked up by mixit
mx <- comp_results$mixit

# did no mixit actually miss the species over a 5 minute survey?
tmp <- dplyr::left_join(
  dplyr::distinct(mx[,c("city","site", "date", "common_name", "comparison")]),
  dplyr::distinct(both_ID[,c("city","site", "date", "common_name","comparison")])
)

mx <- dplyr::distinct(
  mx[,c("city","site", "date", "common_name")]
)
mx <- split(
  mx,
  factor(paste0(mx$site, mx$date))
)

bt <- dplyr::distinct(
  both_ID[,c("city","site", "date", "common_name")]
)

bt <- split(
  bt,
  factor(paste0(bt$site, bt$date))
)


both_vec <- vector("list", length = length(mx) )

for(i in 1:length(mx)){

  oo <- which(names(bt) == names(mx)[i] )
  if(length(oo) == 0){
    both_vec[[i]] <- data.frame(
      mx[[i]],
      type = "missed"
    )
  }else{
    both_vec[[i]] <- data.frame(
      mx[[i]]
    )

  }
}



# read in all the possible files

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


