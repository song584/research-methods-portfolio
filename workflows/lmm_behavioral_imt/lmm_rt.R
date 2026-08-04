## lmm_rt.R -- reaction time across task and stimulus type
##
## Model: measure ~ stimulus * task + Gender + Age + (1 | subject)
##
## Reaction times are taken from correct responses on target trials and from
## false alarms on catch trials, so the same crossed design as the error-rate
## analysis applies.
##
## Run: Rscript lmm_rt.R      (from this folder)

source("lmm_common.R")

INPUT <- file.path("outputs", "rt_long.csv")
TAG   <- "rt"

dat <- read_behavioural(INPUT, measure_col = "trans1", scale = 1)

model <- lmer(measure ~ stimulus * task + Gender + Age + (1 | subject),
              data = dat)

anova_tbl  <- type3_anova(model)
fixed_tbl  <- fixed_effects(model)

emm          <- emmeans(model, ~ task | stimulus)
emmeans_tbl  <- marginal_means(emm)
pairwise_tbl <- pairwise(emm)

task_by_stim_tbl <- emmeans::joint_tests(model, by = "stimulus") %>%
  as.data.frame() %>%
  dplyr::filter(`model term` == "task") %>%
  dplyr::transmute(
    Stimulus = stimulus,
    Effect   = `model term`,
    NumDF    = df1,
    DenDF    = df2,
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
    "Table 1. Type III ANOVA: reaction time",
    "Table 2. Fixed effects: reaction time",
    "Table 3. Estimated marginal means: reaction time",
    "Table 4. Task pairwise comparisons within stimulus type: reaction time",
    "Table 5. Task effect within stimulus type: reaction time"
  ),
  file = file.path(OUT_DIR, paste0("lmm_report_", TAG, ".pdf"))
)

print(anova_tbl)
