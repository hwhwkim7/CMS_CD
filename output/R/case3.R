library(ggplot2)
library(patchwork)
library(export)

pplot <- function(datum, measure, measure_tit, line_datum) {
  
  # 색상 팔레트 설정 (orc_cd와 louvain_cd 두 개의 색상 생성)
  colors <- scales::hue_pal()(2)
  
  # 기본 그래프 그리기
  p <- ggplot(datum, aes(x = alpha, y = measure, color = data, group = data)) +
    geom_line(size=3) +  # 꺾은선 그래프
    geom_point(size=8) + # 데이터 포인트 표시
    labs(x = "Alpha", y = measure_tit) +
    theme_minimal() +
    theme(
      text = element_text(size = 30),       # 전체 글자 크기 키우기
      panel.grid = element_blank(),         # 그리드 제거
      panel.border = element_rect(color = "black", fill = NA, size = 1),
      axis.ticks = element_line(size = 0.8),  # 눈금 표시선 굵게 설정
      axis.ticks.length = unit(5, "pt"),      # 눈금 표시선 길이 설정
      axis.text = element_text(size = 12)) +  # 축 눈금 크기 설정
    facet_wrap(~data) +  # data별로 그래프 분리
    ylim(0, 1)  # Y축을 0에서 1까지 설정
  
  # 모든 data에서 각 알고리즘에 해당하는 수평선을 그리기
  for (algorithm_value in unique(line_datum$algorithm)) {
    # 해당 알고리즘에 대한 nmi 값 추출
    nmi_values <- line_datum %>%
      filter(algorithm == algorithm_value) %>%
      pull(nmi)
    
    # 색상을 알고리즘에 맞춰 설정
    color <- ifelse(algorithm_value == "orc_cd", colors[1], colors[2])
    
    # 수평선 추가 (모든 데이터에 대해서 동일하게 적용)
    p <- p + geom_hline(yintercept = nmi_values, linetype = "dashed", color = color, size = 1.5)
  }
  
  return(p)
}



file_path <- '/Users/kimhyewon/Library/CloudStorage/GoogleDrive-hwhwkim7@gmail.com/내 드라이브/UNIST/ORC/CMS_CD/output/final/'
datum <- read.csv(file=paste0(file_path,"real_final.csv"), sep=',', header=TRUE)
datum <- datum %>%
  filter(data == "karate" | data == "polbooks")
print(datum)
line_datum <- read.csv(file=paste0(file_path,'compare_real.csv'), sep=',', header=TRUE)
line_datum <- line_datum %>%
  filter(data == "polbooks" | data == 'karate') %>%
  filter(algorithm == 'orc_cd' | algorithm == 'louvain_cd')
print(line_datum)

pplot(datum, datum$nmi, 'NMI', line_datum)
graph2ppt(file=paste0(file_path, "/figure/case3.pptx"), width=28.7, height=6.3)
