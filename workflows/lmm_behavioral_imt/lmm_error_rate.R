## Error rate across task and stimulus type.
##
## The interaction qualifies the task effect, so the task contrast is also
## reported within each stimulus type.

source("lmm_common.R")

INPUT <- file.path("outputs", "error_rate_long.csv")
TAG   <- "error_rate"

dat <- read_behavioural(INPUT, measure_col = "trans1")

model <- lmer(measure ~ stimulus * task + Gender + Age + (1 | subject),
              data = dat)

anova_tbl <- type3_anova(model)
fixed_tbl <- fixed_effects(model)

emm          <- emmeans(model, ~ task | stimulus)
emmeans_tbl  <- marginal_means(emm)
pairwise_tbl <- pairwise(emm)

## Taken from the full model so that every test uses the same error term.
task_by_stim_tbl <- emmeans::joint_tests(model, by = "stimulus") %>%
  as.data.frame() %>%
  dplyr::filter(`model term` == "task") %>%
  dplyr::transmute(
    Stimulus  = stimulus,
    Effect    = `model term`,
    NumDF     = df1,
    DenDF     = df2,
    `F value` = round(F.ratio, 3),
    `Pr(>F)`  = round(p.value, 4)
  )

save_table(anova_tbl,        paste0("typeIII_anova_", TAG, ".csv"))
save_table(fixed_tbl,        paste0("fixed_effects_", TAG, ".csv"))
save_table(emmeans_tbl,      paste0("emmeans_", TAG, ".csv"))
save_table(pairwise_tbl,     paste0("pairwise_", TAG, ".csv"))
save_table(task_by_stim_tbl, paste0("task_within_stimulus_", TAG, ".csv"))

write_report(
  tables = list(anova_tbl, fixed_tbl, emmeans_tbl, pairwise_tbl, task_by_stim_tbl),
  titles = c(
    "Table 1. Type III ANOVA: error rate",
    "Table 2. Fixed effects: error rate",
    "Table 3. Estimated marginal means: error rate",
    "Table 4. Task pairwise comparisons within stimulus type: error rate",
    "Table 5. Task effect within stimulus type: error rate"
  ),
  file = file.path(OUT_DIR, paste0("lmm_report_", TAG, ".pdf"))
)

print(anova_tbl)
