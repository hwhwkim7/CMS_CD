library(ggplot2)
library(patchwork)
library(export)
library(dplyr)

file_path <- '/Users/kimhyewon/Library/CloudStorage/GoogleDrive-hwhwkim7@gmail.com/내 드라이브/UNIST/ORC/CMS_CD/output/final/'
datum <- read.csv(file=paste0(file_path,"compare_real.csv"), sep=',', header=TRUE)

# exclude_cols <- c("data", "algorithm", "time", "X.com")
# 
# # 남은 열 이름들만 선택 (제외할 열 이름들을 제외한 나머지)
# col_list <- setdiff(colnames(datum), exclude_cols)
# print(col_list)

datum <- datum %>%
  filter(algorithm != "CMS0.1", data != "football", data != "polblogs")

col_list = list('nmi', 'ari', 'nf1')

pplot <- function(datum, measure, measure_tit) {
  ggplot(datum, aes(x = data, y = !!sym(measure_tit), fill = algorithm)) +  # 열 이름을 동적으로 전달
    geom_bar(stat = "identity", position = position_dodge(width = 0.6), width = 0.6) +  # 각 데이터의 algorithm에 대한 막대 그래프
    labs(x = "Data", y = measure_tit) +
    theme_minimal() +
    scale_y_continuous(limits = c(0, 1)) + 
    theme(panel.grid = element_blank(), panel.border = element_rect(color = "black", fill = NA, size = 1),
          axis.ticks = element_line(size = 0.8),  # 눈금 표시선 굵게 설정
          axis.ticks.length = unit(5, "pt"),      # 눈금 표시선 길이 설정
          axis.text = element_text(size = 12))  # 축 눈금 크기 설정)
}

p_list <- list()  # 리스트 초기화
for (col in col_list) {
  gg <- pplot(datum, col, col)  # 여기서 col을 동적으로 pplot에 전달
  
  # ggplot 객체를 별도의 리스트 요소로 추가
  p_list[[length(p_list) + 1]] <- gg
}

# 여러 플롯을 합치는 wrap_plots 사용
combined_plot <- wrap_plots(plotlist = p_list, ncol = length(col_list), nrow = 1)

# 결합된 플롯 출력
print(combined_plot)

# PowerPoint 파일로 저장
graph2ppt(file = paste0(file_path, "figure/case1.pptx"), width=28.7, height=6.3)

