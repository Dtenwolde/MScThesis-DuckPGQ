require(ggplot2)
require(dplyr)
require(tidyr)
require(scales) # For the percent_format() function
require(stringr)

test_results_shortest<- read.csv('/home/daniel/Documents/ldbc_snb_bi/duckdb/benchmark/timings-shortest-path-query13.csv')
test_results_shortest$algorithm <- "Shortest_path"

test_results_cheapest <- read.csv('/home/daniel/Documents/ldbc_snb_bi/duckdb/benchmark/timings-cheapest-path-q13.csv')
test_results_cheapest$algorithm <- "Cheapest_path"

test_results <- rbind(test_results_shortest, test_results_cheapest)

test_results <- read.csv('/home/daniel/Documents/ldbc_snb_bi/duckdb/benchmark/timings-cheapest-path-q13.csv')
test_results$sf <- as.factor(test_results$sf)
test_results$query <- as.factor(test_results$query)
test_results$lanes <- as.factor(test_results$lanes)
test_results$threads <- as.factor(test_results$threads)
test_results$algorithm <- as.factor(test_results$algorithm)

test_results <- subset(test_results, select = -c(date))

grouped_results <- test_results %>%
  group_by(sf, query, lanes, threads, workload) %>%
  summarise_all(mean)

long_results <- grouped_results %>% pivot_longer(cols = ends_with("timing"), names_to = "timing", values_to = "value")

query_execution <- ggplot(long_results, aes(fill = timing, y = value, x = sf)) +
  geom_bar(position = "dodge", stat = "identity") +
  theme_classic(base_size = 18) +
  facet_wrap(. ~ sf, scales = "free") +
  labs(y = "Average query execution time per phase (s)",
       x = "Scale factor",
       title = "Average query execution time per phase per scale factor (query 20)")

thread_results <- long_results[long_results$timing == 'total_parameter_timing' & long_results$lanes == 1024,]

thread_execution <- ggplot(thread_results, aes(y = threads, x = value)) +
  geom_line(aes(color = sf)) +
  geom_point(aes(color = sf)) +
  theme_classic() +
  facet_wrap(. ~ sf, scales = "free") +
  scale_x_log10()
thread_execution

# grouped_results_boxplot <- test_results %>% group_by(sf, query, lanes, threads, workload) %>% summarise_all(mean)

grouped_results_boxplot <- test_results %>% pivot_longer(cols = ends_with("timing"), names_to = "timing", values_to = "value")
thread_results_boxplot <- grouped_results_boxplot[grouped_results_boxplot$timing == 'total_parameter_timing' & grouped_results_boxplot$lanes == 1024,]
lane_results_boxplot <- grouped_results_boxplot[grouped_results_boxplot$timing == 'total_parameter_timing' & grouped_results_boxplot$threads == 8,]


thread_execution_boxplot <- ggplot(thread_results_boxplot, aes(y = threads, x = value)) +
  geom_boxplot() +
  theme_classic(base_size = 18) +
  facet_wrap(. ~ sf, scales = "free") +
  labs(y = "Average query execution time per number of threads (s)",
       x = "Execution time in seconds",
       title = "Average query execution time per thread split on scale factor (query 20)")

thread_execution_boxplot

lane_execution_boxplot <- ggplot(lane_results_boxplot, aes(y = lanes, x = value)) +
  geom_boxplot() +
  theme_classic(base_size = 18) +
  facet_wrap(. ~ sf, scales = "free") +
  labs(y = "Average query execution time per number of lanes",
       x = "Execution time in seconds",
       title = "Average query execution time per lane split on scale factor (query 20)")

lane_execution_boxplot

facet_labeller <- function(variable, value) {
  return (paste("SF", value))
}

create_plots_per_query <- function(long_results, q, w, a) {
  all_parameter_results <- long_results %>% filter(query == q, workload == w)
  time_edge_plot <- ggplot(all_parameter_results %>% filter(lanes == 1024, timing == 'total_timing', threads==96), aes(x = edges, y = value/paths, label = sf)) +
    geom_point() +
    # geom_text() +
    geom_line() +
      theme(axis.text=element_text(size=18),
        axis.title=element_text(size=14,face="bold")) +
    geom_text(hjust = 1.1, vjust = 0, size = 7) +
    theme_classic(base_size = 18) +
    scale_x_continuous(trans = 'log10') +
    scale_y_continuous(trans = 'log10') +
    theme(axis.text=element_text(size=16)) +
    annotation_logticks(sides = 'lb') +
    labs(y = "Total execution time in seconds (log10)",
         x = "Number of edges (log10)",
         subtitle = paste0(a, " path"),
         title = paste0("Average query execution time per path (", str_to_title(w), " Query ", q, ")"))

  filename <- paste0(q, w, "timeedgeplot.jpg")
  ggsave(plot = time_edge_plot, filename=filename, path = getwd(), width = 5, height = 4, device='jpg', dpi=300)

  all_parameter_barplot <- ggplot(all_parameter_results %>% filter(lanes == 1024 & threads == 96,
                                                                   !timing %in% c("average_parameter_timing", "total_timing")),
                                  aes(fill = timing, x = sf, y = value)) +
    geom_bar(position="dodge", stat = "identity") +
    theme_classic(base_size = 18) +
      theme(axis.text=element_text(size=18),
        axis.title=element_text(size=14,face="bold")) +
    facet_wrap(. ~ sf, scales = 'free', labeller = facet_labeller, ncol=2) +
    labs(y = "Execution time in seconds", fill = "Timing Categories", subtitle = paste0(a, " path"), title = paste0("Execution time per category (", str_to_title(w), " Query ", q, ")")) +
    scale_fill_brewer(name = "Query Timings", labels = c("Creating CSR", "Other", "Path-finding", "Precomputing", "Gathering results", "Finding path options"), palette = "RdYlBu") +
    theme(axis.text.x = element_blank(), axis.ticks.x = element_blank(), axis.title.x = element_blank())
  total_timings <- all_parameter_results %>% filter(lanes == 1024 & threads == 96, timing == "total_timing")
  timings_relative <- all_parameter_results %>%
    filter(lanes == 1024 & threads == 96, !timing %in% c("average_parameter_timing", "total_timing")) %>%
    group_by(timing) %>%
    mutate(relative = value / total_timings$value)

  filename <- paste0(q, w, "timeedgeplot.jpg")
  ggsave(plot = time_edge_plot, filename=filename, path = getwd(), width = 5, height = 4, device='jpg', dpi=300)


  barplot_relative <- ggplot(timings_relative, aes(x = sf, y = relative, fill = timing)) +
    geom_bar(stat = "identity") +
    theme_classic(base_size = 18) +
      theme(axis.text=element_text(size=14),
        axis.title=element_text(size=14,face="bold")) +
    facet_wrap(. ~ sf, scales = "free", labeller = facet_labeller, ncol=3) +
    labs(y = "Relative Execution time %", fill = "Timing Categories", subtitle = paste0(a, " path"), title = paste0("Relative execution time per category (", str_to_title(w), " Query ", q, ")")) +
    scale_fill_brewer(name = "Query Timings", labels = c("Creating CSR", "Other", "Path-finding", "Precomputing", "Gathering results", "Finding path options"), palette = "RdYlBu") +
    scale_y_continuous(labels = percent) +
    theme(axis.text.x = element_blank(), axis.ticks.x = element_blank(), axis.title.x = element_blank())
  plot_list <- list("lineplot" = time_edge_plot, "barplot" = all_parameter_barplot, "barplot_relative" = barplot_relative)
  return(plot_list)
}


plots_13 <- create_plots_per_query(long_results %>% filter(sf >= 30), 13, "interactive", "Cheapest")

plots_13[1]
plots_13[2]
plots_13[3]

csr_timing <- ggplot(long_results %>% filter(lanes == 1024 & threads == 96,
                                                                   timing == 'csr_timing'),
                                  aes(x = edges + vertices, y = value, label=sf)) +
  geom_point() +
  # geom_smooth(method = "lm", se = FALSE) +
    theme_classic(base_size = 18) +
  theme(axis.text=element_text(size=18),
        axis.title=element_text(size=14,face="bold")) +
    scale_y_continuous(trans = 'log10') +
      scale_x_continuous(trans = 'log10') +
  annotation_logticks(sides = 'lb') +
      geom_text(hjust = 1.1, vjust = 0, size = 7) +
    labs(y = "Execution time in seconds (log10)", x="Number of vertices + edges (log10)",  fill = "Timing Categories", title = paste0("Execution time for CSR creation"))
    # scale_fill_brewer(name = "Query Timings", labels = c("Creating CSR", "Other", "Path-finding", "Precomputing", "Gathering results", "Finding path options"), palette = "RdYlBu") +
    # theme(axis.text.x = element_blank(), axis.ticks.x = element_blank(), axis.title.x = element_blank())

csr_timing

plots_20 <- create_plots_per_query(long_results, 20, "bi")

plots_20[1]
plots_20[2]
plots_20[3]


time_edge_plot <- ggplot(long_results %>% filter(lanes == 1024, timing == 'total_timing', threads==96), aes(x = edges, y = value, label = sf, shape=algorithm)) +
  geom_point(size = 3) +
  geom_line() +
  geom_text(hjust = 1.1, vjust = 0, size = 7) +
  theme_classic(base_size = 18) +
    scale_x_continuous(trans = 'log10') +
    scale_y_continuous(trans = 'log10') +
    theme(axis.text=element_text(size=16)) +
    annotation_logticks(sides = 'lb') +
    labs(y = "Total execution time in seconds (log10)",
         x = "Number of edges (log10)",
         title = "Average query execution time (Interactive Query 13)",
         shape = "Algorithm")

time_edge_plot

filtered_results <- long_results %>% filter(timing == 'total_timing', threads==96)
wide_results <- filtered_results %>% pivot_wider(names_from=algorithm, values_from=value)

wide_results %>% summarise(Cheapest_path / Shortest_path)
# all_parameter_results_13 <- long_results %>% filter(query == 13, workload == "interactive")
# all_parameter_plot_13 <- ggplot(all_parameter_results_13 %>% filter(lanes == 1024 & threads == 8, timing == 'total_timing'), aes(x = edges, y = value)) +
#   geom_point() +
#   geom_line() +
#   theme_classic(base_size = 18) +
#   scale_x_continuous(trans = 'log10') +
#   scale_y_continuous(trans = 'log10') +
#   # facet_wrap(query ~ .) +
#   annotation_logticks(sides = 'lb') +
#   labs(y = "Total execution time in seconds (log10)",
#        x = "Number of edges (log10)",
#        title = "Average query execution time  (Interactive Query 13)")
#
#
# all_parameter_plot_13
#
#
# all_parameter_13_barplot <- ggplot(all_parameter_results_13 %>% filter(lanes == 1024 & threads == 8, !timing %in% c("average_parameter_timing", "total_timing")), aes(fill = timing, x = sf, y = value)) +
#   geom_bar(stat = "identity") +
#   theme_classic(base_size = 18) +
#   facet_wrap(. ~ sf, scales = 'free') +
#   labs(x = "Scale Factor", y = "Execution time in seconds", fill = "Timing Categories") +
#   scale_fill_brewer(name = "Query Timings", labels = c("CSR", "Path-finding", "Precompute", "Finding path options"), palette = "RdYlBu")
# # scale_y_continuous(labels = percent_format(), limits=c(0,1)) +
#
# all_parameter_13_barplot
#
# total_timings <- all_parameter_results_13 %>% filter(lanes == 1024 & threads == 8, timing == "total_timing")
# timings_relative <- all_parameter_results_13 %>%
#   filter(lanes == 1024 & threads == 8, !timing %in% c("average_parameter_timing", "total_timing")) %>%
#   group_by(timing) %>%
#   mutate(relative = value / total_timings$value * 100)
#
# all_parameter_13_barplot_relative <- ggplot(timings_relative, aes(x = sf, y = relative, fill = timing)) +
#   geom_bar(stat = "identity") +
#   theme_classic(base_size = 18) +
#   facet_wrap(. ~ sf, scales = "free") +
#   labs(x = "Scale Factor", y = "Relative Execution time %", fill = "Timing Categories") +
#   scale_fill_brewer(name = "Query Timings", labels = c("Creating CSR", "Path-finding", "Precomputing", "Gathering results", "Finding path options", "Other"), palette = "RdYlBu")
# all_parameter_13_barplot_relative


# all_parameter_results_summarized <- all_parameter_results_13 %>%
#   group_by_all() %>%
#   summarise_all(mean)
# all_parameter_barplot <- ggplot(all_parameter_results_summarized, aes(y = value, x = sf)) +
#   geom_bar(stat = 'identity') +
#   theme_classic() +
# facet_wrap(. ~ sf, scales = "free") +
# scale_y_log10()
# all_parameter_barplot

lanes_execution <- ggplot(lanes_results, aes(y = lanes, x = value)) +
  geom_line(group = 1) +
  geom_point(aes(color = sf)) +
  theme_classic() +
  facet_wrap(. ~ sf, scales = "free") +
  scale_x_log10()
lanes_execution




