## Script Name: fund_analysis.R
## Author: Jingkai Sun
## Email Address: jingkai.sun20@imperial.ac.uk

options(warn=-1)
suppressMessages(library(ggplot2))
suppressMessages(library(dplyr))
suppressMessages(require(tidyverse))
suppressMessages(require(Cairo))
suppressMessages(require(showtext))
rm(list = ls())

setwd("~/Documents/CPIC/fund_stimulation/code/")

# 模式1
rolling1 <- read.csv("../result/rolling1yrs.csv")
rolling2 <- read.csv("../result/rolling2yrs.csv")
rolling3 <- read.csv("../result/rolling3yrs.csv")
# rolling4 <- read.csv("../result/rolling4yrs.csv")

rolling1$period <- rep("3yrs", nrow(rolling1))
rolling2$period <- rep("6yrs", nrow(rolling2))
rolling3$period <- rep("9yrs", nrow(rolling3))
# rolling4$period <- rep("12yrs", nrow(rolling4))

# 总表
marginTable <- rbind(rolling1, rolling2, rolling3)
# rm(rolling1_m2, rolling2_m2, rolling3_m2, rolling4_m2, rolling1, rolling2, rolling3, rolling4)

# glimpse(marginTable)
marginTable$ret_exc <- round(marginTable$ret_exc, 5)
marginTable$ret_exc2 <- round(marginTable$ret_exc2, 5)
marginTable$ret_exc3 <- round(marginTable$ret_exc3, 5)
marginTable$ret_emean <- round(marginTable$ret_emean, 5)
marginTable$ret_emean2 <- round(marginTable$ret_emean2, 5)
marginTable$ret_emean3 <- round(marginTable$ret_emean3, 5)

# marginTable$year_continuous <- apply(marginTable, 1, function(x){ return(as.integer( strsplit(x[1], "-", fixed = T)[[1]][1]) ) })

############################# 画图 ###############################

plot_curve <- function(period = "3yrs", title = "3种算法在各个不同股票上的业绩报酬曲线", y_axis = "ret_emean"){
  
  if (y_axis == "margin"){
    gathered_d <- marginTable %>% gather(algo, values, -year, -account_code, -mode, -E_end, 
                                         -excess_return, -upper_limit, -acc_return, -Emean_return, 
                                         -ret_exc, -ret_exc2, -ret_exc3,
                                         -ret_emean, -ret_emean2, -ret_emean3, -period, -year2)
    func2 <- function(x){
      if (x[17] == "return_margin") return("算法A")
      if (x[17] == "return_margin2") return("算法B")
      if (x[17] == "return_margin3") return("算法C")
    }
  } else if (y_axis == "ret_exc") {
    gathered_d <- marginTable %>% gather(algo, values, -year, -account_code, -mode, -E_end, 
                                         -excess_return, -upper_limit, -acc_return, -Emean_return, 
                                         -return_margin, -return_margin2, -return_margin3,
                                         -ret_emean, -ret_emean2, -ret_emean3, -period, -year2)
    func2 <- function(x){
      if (x[17] == "ret_exc") return("算法A")
      if (x[17] == "ret_exc2") return("算法B")
      if (x[17] == "ret_exc3") return("算法C")
    }
  } else if (y_axis == "ret_emean"){
    gathered_d <- marginTable %>% gather(algo, values, -year, -account_code, -mode, -E_end, 
                                         -excess_return, -upper_limit, -acc_return, -Emean_return, 
                                         -return_margin, -return_margin2, -return_margin3,
                                         -ret_exc, -ret_exc2, -ret_exc3, -period, -year2)
    func2 <- function(x){
      if (x[17] == "ret_emean") return("算法A")
      if (x[17] == "ret_emean2") return("算法B")
      if (x[17] == "ret_emean3") return("算法C")
    }
  }

  
  d <- gathered_d[(gathered_d$period == period),]
  
  func <- function(x){
    if (x[3] == "mode1") return("加仓减仓各10%")
    if (x[3] == "mode2") return("加仓50%减仓30%")
  }
  
  d$mode_ch <- apply(d, 1, func)
  d$业绩报酬算法 <- apply(d, 1, func2)
  
  showtext_auto()
  
  p <- ggplot(data = d, aes(x = year2, y = values, color = 业绩报酬算法)) + 
    geom_line() +
    geom_point() +
    facet_grid(account_code ~ mode_ch, scales = "free") + 
    theme(legend.position = "bottom",
          axis.title = element_text(size = 11, face = "bold"),
          plot.title = element_text(size = 14, face = "bold")) +
    labs(title = title, x = "年份", y = "业绩报酬(元)")
  
  return(p)
}

met <- data.frame(method = c("margin", "ret_exc", "ret_emean"), method_ch = c("业绩报酬", "业绩报酬/超额收益", "业绩报酬/平均资金占用"))

for (year in c(3, 6, 9)){
  for (i in 1:nrow(met)){
    cairo_pdf(paste("../result/ts_curve", year, "_", met[i, 1] ,".pdf", sep = ""))
    print(plot_curve(period = paste(year,"yrs", sep = ""), title = paste("3种算法在各个不同股票上的", met[i, 2] ,"（", year, "年期滚动）", sep = ""), y_axis = paste(met[i, 1])))
    dev.off()
  }
}

############## 业绩提成比例分布稳定，方差小 #######################

mean_sd <- function(mode, period){
  d <- marginTable[(marginTable$mode == mode) & (marginTable$period == period),]
  means <- as.double(sapply(d[(d$mode == mode),][12:14], mean, na.rm = TRUE))
  sds <- as.double(sapply(d[(d$mode == mode),][12:14], sd, na.rm = TRUE))
  return(list(means, sds))
}

ret_mean <- c(mean_sd("mode1", "3yrs")[[1]], mean_sd("mode1", "6yrs")[[1]], mean_sd("mode1", "9yrs")[[1]],
              mean_sd("mode2", "3yrs")[[1]], mean_sd("mode2", "6yrs")[[1]], mean_sd("mode2", "9yrs")[[1]],
              mean_sd("mode1", "3yrs")[[2]], mean_sd("mode1", "6yrs")[[2]], mean_sd("mode1", "9yrs")[[2]],
              mean_sd("mode2", "3yrs")[[2]], mean_sd("mode2", "6yrs")[[2]], mean_sd("mode2", "9yrs")[[2]])

algo <- c(rep(c("A", "B", "C"), 3),
          rep(c("A", "B", "C"), 3),
          rep(c("A", "B", "C"), 3),
          rep(c("A", "B", "C"), 3))

duration <- c(rep("3年期", 3), rep("6年期", 3), rep("9年期", 3),
              rep("3年期", 3), rep("6年期", 3), rep("9年期", 3),
              rep("3年期", 3), rep("6年期", 3), rep("9年期", 3),
              rep("3年期", 3), rep("6年期", 3), rep("9年期", 3))

fund_code <- c(rep("加仓减仓各10%", 9), rep("加仓50%减仓30%", 9),
          rep("加仓减仓各10%", 9), rep("加仓50%减仓30%", 9))

type_value <- c(rep("均值", 18), rep("标准差", 18))

means_sds <- data.frame(模式 = fund_code, duration = duration, algo = algo, ret_mean = ret_mean, type_value = type_value)

cairo_pdf("../result/mean_sd.pdf")
showtext_auto()
ggplot(data = means_sds, aes(x = algo, y = ret_mean, fill = 模式),) +
  geom_histogram(stat = "identity", position = "dodge") +
  geom_text(aes(label=round(ret_mean, 2)), position=position_dodge(1), vjust = 0.5, colour="black", size = 2.5) +
  facet_grid(duration ~ type_value) +
  xlab("3种业绩报酬算法") +
  ylab("业绩报酬/超额收益平均值") +
  theme(axis.title = element_text(size = 13, face = "bold"),
        axis.text = element_text(size = 12),
        # text = element_text(family='STKaiti'),
        legend.position = "bottom")
dev.off()

############## 超额收益<0时，有业绩报酬的概率 #####################

neg_margin <- function(year = 3, algo = "A", mode = 2){
  neg <- subset(marginTable, excess_return < 0)
  sub <- neg[(neg$period == paste(year,"yrs",sep = "")) & (neg$mode == paste("mode",mode,sep="")),]
  if (algo == 'A') { posibility <- nrow(subset(sub, return_margin != 0)) / nrow(sub) }
  if (algo == 'B') { posibility <- nrow(subset(sub, return_margin2 != 0)) / nrow(sub)} 
  if (algo == 'C') { posibility <- nrow(subset(sub, return_margin3 != 0)) / nrow(sub)}
  return(round(posibility, 3) * 100)
}

# 3年期：算法A-模式1, # 3年期：算法B-模式1, # 3年期：算法C-模式1: 
possiblility <- c(neg_margin(3, "A", 1), neg_margin(3, "B", 1), neg_margin(3, "C", 1),
          neg_margin(3, "A", 2), neg_margin(3, "B", 2), neg_margin(3, "C", 2),
          neg_margin(6, "A", 1), neg_margin(6, "B", 1), neg_margin(6, "C", 1),
          neg_margin(6, "A", 2), neg_margin(6, "B", 2), neg_margin(6, "C", 2),
          neg_margin(9, "A", 1), neg_margin(9, "B", 1), neg_margin(9, "C", 1),
          neg_margin(9, "A", 2), neg_margin(9, "B", 2), neg_margin(9, "C", 2))

algo <- c(rep(c("算法A", "算法B", "算法C"), 2),
          rep(c("算法A", "算法B", "算法C"), 2),
          rep(c("算法A", "算法B", "算法C"), 2))

mode <- c(rep("加仓减仓各10%", 3), rep("加仓50%减仓30%", 3),
          rep("加仓减仓各10%", 3), rep("加仓50%减仓30%", 3),
          rep("加仓减仓各10%", 3), rep("加仓50%减仓30%", 3))

duration <- factor(c(rep("3年期", 6),
              rep("6年期", 6),
              rep("9年期", 6)), level = c("3年期", "6年期", "9年期"))

req1 <- data.frame(duration = duration, 模式 = mode, algo = algo, possiblility = possiblility)

CairoPDF("../result/neg_margin.pdf")
showtext_auto()
ggplot(data = req1, aes(x = algo, y = possiblility, fill = 模式),) +
  geom_histogram(stat = "identity", position = "dodge") +
  facet_grid(duration ~.) +
  geom_text(aes(label=possiblility), position=position_dodge(1), vjust = 0.5, colour="black", size = 4) +
  labs(title = "超额收益<0时，有业绩报酬的概率", x = "3种业绩报酬算法", y = "百分比(%)") +
  theme(axis.title = element_text(size = 11, face = "bold"),
        axis.text = element_text(size = 10),
        plot.title = element_text(hjust = 0.5),
        legend.position = "bottom")
dev.off()

############## 超额收益>0时，业绩报酬/超额收益>10%的概率 #####################

posi_margin <- function(year = 3, ret_exc = "B", mode = 1) {
  posi <- subset(marginTable, excess_return > 0)
  sub <- posi[(posi$period == paste(year, "yrs",sep = "")) & (posi$mode == paste("mode",mode,sep="")),]
  if (ret_exc == 'A') { posibility <- nrow(subset(sub, ret_exc > 0.100)) / nrow(sub) }
  if (ret_exc == 'B') { posibility <- nrow(subset(sub, ret_exc2 > 0.100)) / nrow(sub)} 
  if (ret_exc == 'C') { posibility <- nrow(subset(sub, ret_exc3 > 0.100)) / nrow(sub)}
  return(round(posibility, 3) * 100)
}

### Debug ###
posi <- subset(marginTable, excess_return > 0)
# sub <- posi[(posi$period == "9yrs") & (posi$mode == "mode2") & (posi$account_code == "163402.OF"),]
sub <- posi[(posi$period == "9yrs") & (posi$mode == "mode2"),]
d <- subset(sub, ret_exc3 > 0.100)
nrow(subset(sub, ret_exc3 > 0.100))
nrow(sub)
if (ret_exc == 'A') { posibility <- nrow(subset(sub, ret_exc > 0.100)) / nrow(sub) }
if (ret_exc == 'B') { posibility <- nrow(subset(sub, ret_exc2 > 0.100)) / nrow(sub)} 
if (ret_exc == 'C') { posibility <- nrow(subset(sub, ret_exc3 > 0.100)) / nrow(sub)}
### Debug ###

possiblility <- c(posi_margin(3, "A", 1), posi_margin(3, "B", 1), posi_margin(3, "C", 1),
                 posi_margin(3, "A", 2), posi_margin(3, "B", 2), posi_margin(3, "C", 2),
                 posi_margin(6, "A", 1), posi_margin(6, "B", 1), posi_margin(6, "C", 1),
                 posi_margin(6, "A", 2), posi_margin(6, "B", 2), posi_margin(6, "C", 2),
                 posi_margin(9, "A", 1), posi_margin(9, "B", 1), posi_margin(9, "C", 1),
                 posi_margin(9, "A", 2), posi_margin(9, "B", 2), posi_margin(9, "C", 2))

algo <- c(rep(c("算法A", "算法B", "算法C"), 2),
          rep(c("算法A", "算法B", "算法C"), 2),
          rep(c("算法A", "算法B", "算法C"), 2))

mode <- c(rep("加仓减仓各10%", 3), rep("加仓50%减仓30%", 3),
          rep("加仓减仓各10%", 3), rep("加仓50%减仓30%", 3),
          rep("加仓减仓各10%", 3), rep("加仓50%减仓30%", 3))

duration <- factor(c(rep("3年期", 6),
                     rep("6年期", 6),
                     rep("9年期", 6)), 
                   level = c("3年期", "6年期", "9年期"))

req2 <- data.frame(duration = duration, 模式 = mode, algo = algo, possiblility = possiblility)

CairoPDF("../result/posi_margin.pdf")
showtext_auto()
ggplot(data = req2, aes(x = algo, y = possiblility, fill = 模式),) +
  geom_histogram(stat = "identity", position = "dodge") +
  facet_grid(duration ~.) +
  geom_text(aes(label=possiblility), position=position_dodge(1), vjust = 0.5, colour="black", size = 4) +
  ylab("百分比(%)") +
  labs(title = "业绩报酬/超额收益>10%的概率", x = "算法", y = "百分比(%)") + 
  theme(axis.title = element_text(size = 11, face = "bold"),
        axis.text = element_text(size = 10),
        text = element_text(family='Kai'),
        plot.title = element_text(hjust = 0.5),
        legend.position = "bottom")
dev.off()

############## 短期对比 #####################

possiblility <- c(neg_margin(3, "A", 1), neg_margin(3, "B", 1), neg_margin(3, "C", 1),
                  neg_margin(3, "A", 2), neg_margin(3, "B", 2), neg_margin(3, "C", 2),
                  posi_margin(3, "A", 1), posi_margin(3, "B", 1), posi_margin(3, "C", 1),
                  posi_margin(3, "A", 2), posi_margin(3, "B", 2), posi_margin(3, "C", 2))

algo <- c(rep(c("算法A", "算法B", "算法C"), 2),
          rep(c("算法A", "算法B", "算法C"), 2))

mode <- c(rep("加仓减仓各10%", 3), rep("加仓50%减仓30%", 3),
          rep("加仓减仓各10%", 3), rep("加仓50%减仓30%", 3))


requirement <- c(rep("超额收益为负时，有业绩报酬的概率", 6),
                rep("业绩报酬/超额收益>10%的概率", 6))

short_term <- data.frame(requirement = requirement,
                         模式 = mode,
                         algo = algo,
                         possiblility = possiblility)

CairoPDF("../result/compare.pdf")
showtext_auto()
ggplot(data = short_term, aes(x = algo, y = possiblility, fill = 模式),) +
  geom_histogram(stat = "identity", position = "dodge") +
  facet_grid(requirement ~.) +
  geom_text(aes(label=possiblility), position=position_dodge(1), vjust = 0.5, colour="black", size = 4) +
  # theme_classic() +
  xlab("3种业绩报酬算法") +
  ylab("概率百分比（%）") +
  labs(title = "短期三种算法在不同指标下优劣势比较") +
  theme(axis.title = element_text(size = 11, face = "bold"),
        axis.text = element_text(size = 10),
        plot.title = element_text(hjust = 0.5, face = "bold", size = 12),
        legend.position = "bottom")
dev.off()

############## 长期业绩报酬比例要低 #####################

# marginTable$ABdelta <- marginTable$return_margin - marginTable$return_margin2
marginTable$ABdelta <- marginTable$ret_emean - marginTable$ret_emean2
# marginTable$ABdelta <- marginTable$ret_exc - marginTable$ret_exc2

# AB_compare <- function(mode, period){
#   A_better <- nrow(marginTable[(marginTable$mode == mode) & 
#                                  (marginTable$period == period) & 
#                                  (marginTable$ABdelta < 0),]) / nrow(marginTable[(marginTable$mode == mode) & (marginTable$period == period),])
#   
#   B_better <- nrow(marginTable[(marginTable$mode == mode) & 
#                                  (marginTable$period == period) & 
#                                  (marginTable$ABdelta > 0),]) / nrow(marginTable[(marginTable$mode == mode) & (marginTable$period == period),])
#   return(c(round(A_better, 3) * 100, round(B_better, 3) * 100))
# }

Delta <- function(x, num){
  minIdx <- which.min(x[1:num])
  minSort <- sort(x[1:num], decreasing = F)
  # x[num + minIdx] <- 0
  for (i in 2:num){
    delta <- minSort[i] - minSort[1]
    x[match(minSort[i],x) + num] <- x[match(minSort[i],x) + num] + delta
  }
  return(c(x[(num+1):(num+4)]))
}

best_fit_count <- function(x, num, threshold){
  for (i in 1:num){
    if (x[i] <= threshold) {x[i + num] <- x[i + num] + 1}
  }
  return(c(x[(num+1):(num+4)]))
}

marginTable$deltaA <- 0
marginTable$deltaB <- 0
marginTable$deltaC <- 0

marginTable[21:23] <- t(apply(cbind(marginTable[4:6], marginTable[21:23]), 1, FUN = Delta, num = 3))

marginTable$Abest <- 0
marginTable$Bbest <- 0
marginTable$Cbest <- 0

marginTable[24:26] <- t(apply(marginTable[21:26], 1, FUN = best_fit_count, num = 3, threshold = 0))

ABC_compare <- function(mode, period)
{
  d <- marginTable[(marginTable$mode == mode) & (marginTable$period == period),]
  AbestProb <- sum(d$Abest) / nrow(d)
  BbestProb <- sum(d$Bbest) / nrow(d)
  CbestProb <- sum(d$Cbest) / nrow(d)
  return(list(round(AbestProb, 3) * 100, 
              round(BbestProb, 3) * 100, 
              round(CbestProb, 3) * 100))
}

# ABC_compare("mode1", "3yrs")
# ABC_compare("mode2", "3yrs")

winner_posi <- c(ABC_compare("mode1", "3yrs")[[1]], ABC_compare("mode1", "3yrs")[[2]], ABC_compare("mode1", "3yrs")[[3]],
                 ABC_compare("mode2", "3yrs")[[1]], ABC_compare("mode2", "3yrs")[[2]], ABC_compare("mode2", "3yrs")[[3]],
                 ABC_compare("mode1", "6yrs")[[1]], ABC_compare("mode1", "6yrs")[[2]], ABC_compare("mode1", "6yrs")[[3]],
                 ABC_compare("mode2", "6yrs")[[1]], ABC_compare("mode2", "6yrs")[[2]], ABC_compare("mode2", "6yrs")[[3]],
                 ABC_compare("mode1", "9yrs")[[1]], ABC_compare("mode1", "9yrs")[[2]], ABC_compare("mode1", "9yrs")[[3]],
                 ABC_compare("mode2", "9yrs")[[1]], ABC_compare("mode2", "9yrs")[[2]], ABC_compare("mode2", "9yrs")[[3]])

winner <- c(rep(c("算法A最优概率", "算法B最优概率", "算法C最优概率"), 6))

模式 <- c(rep("加仓减仓各10%", 3), 
          rep("加仓50%减仓30%", 3), 
          rep("加仓减仓各10%", 3),
          rep("加仓50%减仓30%", 3), 
          rep("加仓减仓各10%", 3), 
          rep("加仓50%减仓30%", 3))

period <- factor(c(rep("三年期", 6), 
                   rep("六年期", 6), 
                   rep("九年期", 6)), level = c("三年期", "六年期", "九年期"))

df <- data.frame(period = period, 模式 = 模式, 算法最优概率 = winner, winner_posi = winner_posi)

CairoPDF("../result/winner_prob.pdf")
showtext_auto()
ggplot(data = df, aes(x = period, y = winner_posi, fill = 算法最优概率),) +
  geom_histogram(stat = "identity", position = "dodge") +
  facet_grid(模式 ~.) +
  geom_text(aes(label=winner_posi), position=position_dodge(1), vjust = 0.5, colour="black", size = 4) +
  xlab("滚动年限") +
  ylab("概率百分比（%）") +
  labs(title = "短期三种算法在不同指标下优劣势比较") +
  theme(axis.title = element_text(size = 11, face = "bold"),
        axis.text = element_text(size = 10),
        plot.title = element_text(hjust = 0.5, face = "bold", size = 12),
        legend.position = "bottom")
dev.off()

