## lmm_rcs.R -- rate correct score across task
##
## Model: measure ~ task + Gender + Age + (1 | subject)
##
## The rate correct score combines accuracy and speed into one value per task,
## so it is defined for target trials only. There is no stimulus factor and
## therefore no interaction term; task is compared directly.
##
## Run: Rscript lmm_rcs.R      (from this folder)

source("lmm_common.R")

INPUT <- file.path("outputs", "rcs_long.csv")
TAG   <- "rcs"

dat <- read_behavioural(INPUT, measure_col = "trans1", scale = 1)

model <- lmer(measure ~ task + Gender + Age + (1 | subject), data = dat)

anova_tbl  <- type3_anova(model)
fixed_tbl  <- fixed_effects(model)

emm          <- emmeans(model, ~ task)
emmeans_tbl  <- marginal_means(emm)
pairwise_tbl <- pairwise(emm)

save_table(anova_tbl,    paste0("typeIII_anova_", TAG, ".csv"))
save_table(fixed_tbl,    paste0("fixed_effects_", TAG, ".csv"))
save_table(emmeans_tbl,  paste0("emmeans_", TAG, ".csv"))
save_table(pairwise_tbl, paste0("pairwise_", TAG, ".csv"))

write_report(
  tables = list(anova_tbl, fixed_tbl, emmeans_tbl, pairwise_tbl),
  titles = c(
    "Table 1. Type III ANOVA: rate correct score",
    "Table 2. Fixed effects: rate correct score",
    "Table 3. Estimated marginal means: rate correct score",
    "Table 4. Task pairwise comparisons: rate correct score"
  ),
  file = file.path(OUT_DIR, paste0("lmm_report_", TAG, ".pdf"))
)

print(anova_tbl)
