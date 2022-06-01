require(ggplot2)
require(dplyr)
require(tidyr)



test_results <- read.csv('/home/daniel/Documents/ldbc_snb_bi/duckdb/benchmark/timings.csv', sep="|")
test_results$sf <- as.factor(test_results$sf)
test_results$query <- as.factor(test_results$query)
test_results$lanes <- as.factor(test_results$lanes)
test_results$threads <- as.factor(test_results$threads)

test_results <- subset(test_results, select = -c(date, parameter_timing))

grouped_results <- test_results %>% group_by(sf, query, lanes, threads, workload) %>% summarise_all(mean)

long_results <- grouped_results %>% pivot_longer(cols = ends_with("timing"), names_to="timing", values_to="value")

query_execution <- ggplot(long_results, aes(fill=timing, y=value, x=sf)) +
  geom_bar(position="dodge", stat="identity") +
  theme_classic(base_size=18) +
  facet_wrap(. ~ sf, scales = "free") +
  labs(y = "Average query execution time per phase (s)",
     x = "Scale factor",
     title="Average query execution time per phase per scale factor (query 20)")

thread_results <- long_results[long_results$timing == 'total_parameter_timing' & long_results$lanes == 1024,]

thread_execution <- ggplot(thread_results, aes(y=threads, x=value)) +
  geom_line(aes(color=sf)) +
  geom_point(aes(color=sf)) +
  theme_classic() +
  facet_wrap(. ~ sf, scales = "free") +
  scale_x_log10()
thread_execution

# grouped_results_boxplot <- test_results %>% group_by(sf, query, lanes, threads, workload) %>% summarise_all(mean)

grouped_results_boxplot <- test_results %>% pivot_longer(cols = ends_with("timing"), names_to="timing", values_to="value")
thread_results_boxplot <- grouped_results_boxplot[grouped_results_boxplot$timing == 'total_parameter_timing' & grouped_results_boxplot$lanes == 1024,]
lane_results_boxplot <- grouped_results_boxplot[grouped_results_boxplot$timing == 'total_parameter_timing' & grouped_results_boxplot$threads == 8,]


thread_execution_boxplot <- ggplot(thread_results_boxplot, aes(y=threads, x=value)) +
  geom_boxplot() +
  theme_classic(base_size=18) +
  facet_wrap(. ~ sf, scales = "free") +
  labs(y = "Average query execution time per number of threads (s)",
     x = "Execution time in seconds",
     title="Average query execution time per thread split on scale factor (query 20)")

thread_execution_boxplot

lane_execution_boxplot <- ggplot(lane_results_boxplot, aes(y=lanes, x=value)) +
  geom_boxplot() +
  theme_classic(base_size=18) +
  facet_wrap(. ~ sf, scales = "free") +
  labs(y = "Average query execution time per number of lanes",
     x = "Execution time in seconds",
     title="Average query execution time per lane split on scale factor (query 20)")

lane_execution_boxplot



all_parameter_results <- long_results %>% filter(lanes == 1024 & threads == 8, timing == 'total_parameter_timing') %>% group_by_all() %>% summarise_all(mean)
all_parameter_barplot <- ggplot(all_parameter_results, aes(y=value,x=sf)) +
  geom_bar(stat='identity') +
  theme_classic()
  # facet_wrap(. ~ sf, scales = "free") +
  # scale_y_log10()
all_parameter_barplot

lanes_execution <- ggplot(lanes_results, aes(y=lanes, x=value)) +
  geom_line(group=1) +
  geom_point(aes(color=sf)) +
  theme_classic() +
  facet_wrap(. ~ sf, scales = "free") +
  scale_x_log10()
lanes_execution