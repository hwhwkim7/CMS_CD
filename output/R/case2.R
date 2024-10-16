library(ggplot2)
library(patchwork)
library(export)
library(dplyr)

file_path <- '/Users/kimhyewon/Library/CloudStorage/GoogleDrive-hwhwkim7@gmail.com/내 드라이브/UNIST/ORC/CMS_CD/output/'
# file_path <- "G:/내 드라이브/UNIST/ORC/CMS_CD/output/"
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

# alpha 값이 0.1인 데이터만 필터링
filtered_datum <- datum %>%
  filter(alpha == 0.1)

# 새로운 x축 레이블 컬럼 추가 (alpha가 0.1인 데이터만 사용)
filtered_datum <- filtered_datum %>%
  mutate(x_label = case_when(
    grepl("d_avg", data) ~ factor(sub(".*_", "", data), levels = c("10", "20", "30")),
    grepl("d_max", data) ~ factor(sub(".*_", "", data), levels = c("100", "150", "200")),
    grepl("mu", data) ~ factor(sub(".*_", "", data), levels = c("0.1", "0.3", "0.5")),
    TRUE ~ as.character(data)
  ))

# 새로운 데이터 그룹 열 추가 (d_avg, d_max, mu로 구분)
filtered_datum <- filtered_datum %>%
  mutate(group = case_when(
    grepl("d_avg", data) ~ "d_avg",
    grepl("d_max", data) ~ "d_max",
    grepl("mu", data) ~ "mu"
  ))

# x축 레이블 설정 (각 데이터의 구분에 맞게 설정)
filtered_datum <- filtered_datum %>%
  mutate(x_label = case_when(
    grepl("d_avg", data) ~ sub(".*_", "", data),
    grepl("d_max", data) ~ sub(".*_", "", data),
    grepl("mu", data) ~ sub(".*_", "", data)
  ))

gg <- function(filtered_datum, y_measure, y_tit) {
  ggplot(filtered_datum, aes(x=x_label, y=y_measure, color=group, group=group, shape=group)) +
  geom_point(size=5, stroke=2) +    # 포인트 추가 (테두리 포함)
  geom_line(size=1.5) +             # 라인 추가
  facet_wrap(~ group, scales = "free_x", ncol = 3) + # 각 그룹별로 나눠서 그리기 (x축 자유롭게)
  labs(x="Parameter", y=y_tit) + 
    scale_y_continuous(limits = c(250, 310)) + 
  theme_minimal() +
  theme(panel.grid = element_blank(), 
        panel.border = element_rect(color = "black", fill = NA, size = 1),
        axis.ticks = element_line(size = 0.8),  # 눈금 표시선 굵게 설정
        axis.ticks.length = unit(5, "pt"),      # 눈금 표시선 길이 설정
        axis.text = element_text(size = 12))    # 축 눈금 크기 설정
}


  
p1 <- gg(filtered_datum, filtered_datum$time, "Running time (sec)")
print(p1)
p2 <- gg(filtered_datum, filtered_datum$nmi, "NMI")
print(p2)
combined_plot <- wrap_plots(plotlist = c(list(p1), list(p2)), ncol = 1, nrow = 2)
print(combined_plot)
graph2ppt(file=paste0(file_path, "case22.pptx"), width=29.5, height=9.25)
