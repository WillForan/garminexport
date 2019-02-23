#!/usr/bin/env Rscript
suppressPackageStartupMessages({
library(dplyr)
library(lubridate)
library(ggplot2)
library(scales)
})

d <- data.table::fread('hrts_tmp.txt',sep="\t")
# format: get column for time only and date only
names(d) <- c('datetime','hr')
d$datetime <- ymd_hms(d$datetime)
d$date <- date(d$datetime); 
d$time <- d$datetime; date(d$time) <- today() # make all days the same

# plot
p <- ggplot(d) +
 aes(x=time, y=date, color=hr) +
 geom_tile() +
 scale_x_datetime(breaks=date_breaks("1 hour"),
                  labels=date_format("%H")) +
 scale_y_date(breaks=date_breaks("7 day"),
              labels=date_format("%a %Y-%m-%d")) +
 scale_color_continuous(low='white',high='red', limits=c(40,150)) +
 theme_bw()

ggsave(p,file="hr.pdf", height=20,width=5)
