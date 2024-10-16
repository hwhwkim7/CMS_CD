library(ggplot2)
library(patchwork)
library(export)

file_path <- '/Users/kimhyewon/Library/CloudStorage/GoogleDrive-hwhwkim7@gmail.com/내 드라이브/UNIST/ORC/CMS_CD/output/'
datum <- read.csv(file=paste0(file_path,"compare_real.csv"), sep=',', header=TRUE)

pplot <- function(measure, measure_tit) {
  # 데이터 프레임을 사용하여 그래프 그리기
  ggplot(datum, aes(x = alpha, y = measure, color = data, group = alpha, shape=data)) +
    geom_line(size=3) +  # 꺾은선 그래프 그리기
    geom_point(size=8) + # 데이터 포인트 표시
    labs(x = "Alpha", y = measure_tit) +
    theme_minimal() +
    theme(
      text = element_text(size = 30),       # 전체 글자 크기 키우기
      panel.grid = element_blank(),       # 그리드 제거
      panel.border = element_rect(color = "black", fill = NA, size = 1))  # 검은색 테두리 추가
}

p1 <- pplot(datum$nmi, 'NMI')
print(p1)
print(combined_plot)
graph2ppt(file=paste0(file_path, "case3_real.pptx"), width=62.5, height=12.5)
