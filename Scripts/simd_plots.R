require(tidyr)
require(dplyr)
require(ggplot2)

test_results <- read.csv('/home/daniel/git/SIMD-Batched-Bellman-Ford/experiment_output.csv')

test_results$number_of_edges <- as.factor(test_results$number_of_edges)
test_results$number_of_vertices <- as.factor(test_results$number_of_vertices)
test_results$number_of_sources <- as.factor(test_results$number_of_sources)
# test_results$instruction_set <- as.factor(test_results$instruction_set)

grouped_results <- test_results %>%
  group_by(number_of_edges, number_of_sources, number_of_vertices, instruction_set) %>%
  summarise_all(mean)

long_results <- grouped_results %>% pivot_longer(cols = ends_with("cycles"), names_to = "cycles", values_to = "value")
long_results$cycles <- as.factor(long_results$cycles)



ggplot(long_results, aes(x=number_of_sources, y=value, shape=instruction_set, color=cycles)) +
  geom_point(size = 3.5) +
  geom_line() +
  scale_y_log10() +
  theme_classic(base_size = 16) +
  theme(axis.text=element_text(size=16)) +
  annotation_logticks(sides = 'lb') +
  labs(y = "Number of CPU cycles", x = "Number of lanes", shape="Instruction set", color = "Algorithm version",
       title = "Comparison of CPU cycles Scalar vs. Vectorized - Batched Bellman-Ford",
  subtitle = "Graph containing 1024 vertices and 102400 edges") +
  scale_color_brewer(labels = c("Scalar", "Scalar + Modified", "Auto-vectorized"), palette="Set1")


filtered_grouped_results <- grouped_results %>% filter(instruction_set == " AVX2") %>% summarise(speedup = scalar_cycles / vectorized_cycles)
