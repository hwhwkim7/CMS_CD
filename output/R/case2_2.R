library(ggplot2)
library(patchwork)
library(export)

file_path <- '/Users/kimhyewon/Library/CloudStorage/GoogleDrive-hwhwkim7@gmail.com/내 드라이브/UNIST/ORC/CMS_CD/output/'
datum <- read.csv(file=paste0(file_path,"result_scalability.csv"), sep=',', header=TRUE)
print(datum)
alpha_values <- c(0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
datum <- datum[datum$alpha %in% alpha_values, ]
datum <- datum[datum$data != 1000, ]
datum$data <- as.numeric(gsub("scalability_", "", datum$data))
print(datum)

# 그래프 그리기
ggplot(datum, aes(x = as.factor(datum$data), y = time, group = alpha, color = as.factor(alpha), shape = as.factor(alpha))) + 
  geom_line(size=1) +
  geom_point(size=8) +  # 데이터 포인트 강조
  labs(x = "# of Nodes", y = "Running time (sec)", color = "Alpha") +  # X축과 Y축 라벨 변경
  theme_minimal() +
  # coord_cartesian(xlim=c(3990, 4010), ylim = c(13900, 14400)) + 

  theme(
    panel.grid = element_blank(), 
    panel.border = element_rect(color = "black", fill = NA, size = 1),
    axis.ticks = element_line(size = 0.8),  # 눈금 표시선 굵게 설정
    axis.ticks.length = unit(5, "pt"),      # 눈금 표시선 길이 설정
    axis.text = element_text(size = 12)     # 축 눈금 크기 설정
  )



graph2ppt(file=paste0(file_path, "figure/case2.pptx"), width=50, height=10)
