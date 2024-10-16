library(ggplot2)
library(patchwork)
library(export)
library(dplyr)
library(reshape2)

file_path <- '/Users/kimhyewon/Library/CloudStorage/GoogleDrive-hwhwkim7@gmail.com/내 드라이브/UNIST/ORC/CMS_CD/output/final/'
datum <- read.csv(file=paste0(file_path,"scalability.csv"), sep=',', header=TRUE)
print(head(datum))
datum <- datum[, c("data", "time", "orc_time", "alpha")]
datum$number <- as.numeric(gsub("\\D", "", datum$data))
print(datum)
# 데이터 롱 포맷으로 변환 (time과 orc_time을 나란히 그리기 위해)
df_long <- melt(datum, id.vars = c("number", "alpha"), measure.vars = c("time", "orc_time"))
print(df_long)

# ggplot으로 막대 그래프 그리기 (alpha 값에 따라 그래프 나누기)
p1<- ggplot(df_long, aes(x = alpha, y = value, fill = variable)) +
  geom_bar(stat = "identity", position = "dodge") +
  labs(x = "Number", y = "Time (seconds)", fill = "Time Type") +
  facet_wrap(~ factor(number)) +  # alpha 값에 따라 그래프 나눔
  theme_minimal()  +
  theme(panel.grid = element_blank(), panel.border = element_rect(color = "black", fill = NA, size = 0.2),
        axis.ticks = element_line(size = 0.2),  # 눈금 표시선 굵게 설정
        axis.ticks.length = unit(20, "pt"),      # 눈금 표시선 길이 설정
        axis.text = element_text(size = 12))  # 축 눈금 크기 설정)  

print(p1)
# ggplot을 사용한 라인 그래프 (alpha 값에 따라 라인 구분)
p2 <- ggplot(datum, aes(x = number, y = time, color = factor(alpha))) +
  geom_line(size=1) +  # 라인 그래프
  geom_point(size=8) +  # 포인트 추가
  labs(x = "Number", y = "Time (seconds)", color = "Alpha") +  # 라벨 추가
  theme_minimal()  +
  theme(panel.grid = element_blank(), panel.border = element_rect(color = "black", fill = NA, size = 0.2),
        axis.ticks = element_line(size = 0.8),  # 눈금 표시선 굵게 설정
        axis.ticks.length = unit(5, "pt"),      # 눈금 표시선 길이 설정
        axis.text = element_text(size = 12))  # 축 눈금 크기 설정)  

combined_plot <- wrap_plots(plotlist = c(list(p1), list(p2)), ncol = 1, nrow = 2)
print(combined_plot)

# PowerPoint 파일로 저장
graph2ppt(file = paste0(file_path, "figure/case2_bar.pptx"), width=28.7, height=15)

