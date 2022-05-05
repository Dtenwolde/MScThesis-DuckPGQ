library(ggplot2)
library(dplyr)

setwd('/home/daniel/PycharmProjects/MScThesisScripts')

test_results <- read.csv('test_results_optimization_with_connections_remote.csv', header = TRUE, stringsAsFactors = FALSE)
names(test_results) <- c('time', 'optimization', 'sf', 'fraction')

test_results$fraction[test_results$fraction == "1.csv"] <- as.character("1")

by_frac_optimization <- test_results %>% group_by(fraction, optimization, sf) %>% summarise(avg_time = mean(time))

plot <- ggplot(by_frac_optimization, aes(x=fraction, # Main plot
                                y = avg_time, 
                                colour = as.factor(optimization), 
                                group=as.factor(optimization))) +
                
  geom_point() +
  geom_line() +
  facet_wrap(. ~ sf, scales = "free") + # Split on variable
  labs(y = "Average query execution time", 
       x = "Average number of connections",
       title="Comparison between the shared join optimization") +
  scale_colour_discrete(name = "Optimization", labels = c("Disabled", "Enabled")) +
  scale_y_log10() +
  scale_x_log10() +
  theme_classic() 
plot

