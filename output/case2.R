library(ggplot2)
library(patchwork)
library(export)
library(dplyr)

# file_path <- '/Users/kimhyewon/Library/CloudStorage/GoogleDrive-hwhwkim7@gmail.com/내 드라이브/UNIST/ORC/CMS_CD/output/'
file_path <- "G:/내 드라이브/UNIST/ORC/CMS_CD/output/"
datum <- read.csv(file=paste0(file_path,"result_ds.csv"), sep=',', header=TRUE)
print(datum)

gg <- function(datum, measure) {
  ggplot(subset(datum, grepl(measure, data)), aes(x=alpha, y=time, color=data, group=data, shape=data)) +
    geom_line(size=3) +                     # 라인 그리기
    geom_point(aes(shape=data), size=8) +          # 포인트 추가
    labs(x="Alpha", y="Time", title=measure) + 
    theme_minimal() +
    theme(panel.grid = element_blank(), panel.border = element_rect(color = "black", fill = NA, size = 1),
          axis.ticks = element_line(size = 0.8),  # 눈금 표시선 굵게 설정
          axis.ticks.length = unit(5, "pt"),      # 눈금 표시선 길이 설정
          axis.text = element_text(size = 12))  # 축 눈금 크기 설정)  
}
  
p1 <- gg(datum, "^d_avg")
p2 <- gg(datum, "^d_max")
p3 <- gg(datum, "^mu")
combined_plot <- wrap_plots(plotlist = c(list(p1), list(p2), list(p3)), ncol = 3, nrow = 1)
print(combined_plot)
graph2ppt(file=paste0(file_path, "case2.pptx"), width=62.5, height=12.5)
