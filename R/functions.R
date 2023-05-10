pull_files <- function(folder){
  file_paths <- list.files(
    folder,
    pattern = "*.csv$",
    full.names = TRUE
  )
  files <- lapply(
    file_paths,
    read.csv
  )
  files <- dplyr::bind_rows(files)
  files$type <- folder
  files <- dplyr::distinct(files)
  return(files)
}


# parse date from audiomoth files
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


