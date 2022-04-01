library(ggplot2)
library(dplyr)

setwd('/home/daniel/PycharmProjects/MScThesis-Scripts')

test_results <- read.csv('test_results_optimization_with_connections.csv', header = FALSE)
names(test_results) <- c('time', 'optimization', 'sf', 'fraction', 'num_connections')

by_frac_optimization <- test_results %>% group_by(fraction, optimization, sf) %>% summarise(avg_time = mean(time), avg_num_connections = mean(num_connections))

plot <- ggplot(by_frac_optimization, aes(x=avg_num_connections, # Main plot
                                y = avg_time, 
                                colour = as.factor(optimization), 
                                group=as.factor(optimization))) +
                
  geom_point() +
  geom_line() +
  # scale_fill_manual(values = color_table$colors) +
  facet_wrap(. ~ sf, scales = "free") + # Split on variable
  labs(y = "Average query execution time", 
       x = "Average number of connections",
       title="Comparison between the shared join optimization") +
  scale_colour_discrete(name = "Optimization", labels = c("Disabled", "Enabled")) +
  theme_classic() 
  #theme(axis.title.x=element_blank(), # Hide axis label
   #     axis.text.x=element_blank(),
  #      axis.ticks.x=element_blank(),
   #     text = element_text(size=11))

plot

