## Shared setup for the behavioural LMM scripts.

suppressPackageStartupMessages({
  library(tidyverse)
  library(lme4)
  library(lmerTest)
  library(broom.mixed)
  library(emmeans)
  library(gridExtra)
  library(grid)
})

options(contrasts = c("contr.sum", "contr.poly"))

OUT_DIR <- file.path(getwd(), "outputs")
dir.create(OUT_DIR, showWarnings = FALSE)

MISSING_CODE <- 9999

## Read a long-form table and code its factors. `scale` converts the outcome
## if needed, e.g. 100 to turn a proportion into a percentage.
read_behavioural <- function(path, measure_col, scale = 1) {
  dat <- readr::read_csv(path, show_col_types = FALSE)

  sex_col <- intersect(c("Gender", "Sex", "gender", "sex"), names(dat))[1]
  if (is.na(sex_col)) stop("No Gender/Sex column found in ", path)

  dat <- dat %>%
    dplyr::mutate(
      subject = factor(.data$id),
      Age     = as.numeric(.data$Age),
      measure = dplyr::na_if(as.numeric(.data[[measure_col]]), MISSING_CODE) * scale
    ) %>%
    tidyr::drop_na(measure)

  dat$Gender <- factor(dat[[sex_col]], levels = c(1, 2), labels = c("M", "F"))
  dat$task   <- factor(dat$task, levels = c(1, 2, 3), labels = c("IMT", "DMT", "SMT"))

  if ("stimulus" %in% names(dat)) {
    dat$stimulus <- factor(dat$stimulus, levels = c(1, 2),
                           labels = c("Target", "Catch"))
    stopifnot(identical(levels(dat$stimulus), c("Target", "Catch")))
  }

  ## Stop rather than let mis-coded values become NA and drop participants.
  stopifnot(identical(levels(dat$task), c("IMT", "DMT", "SMT")))
  stopifnot(identical(levels(dat$Gender), c("M", "F")))
  stopifnot(!anyNA(dat$Gender), !anyNA(dat$task))

  dat
}

round_mix <- function(df, p_cols, other_digits = 3, p_digits = 4) {
  df %>%
    dplyr::mutate(dplyr::across(
      dplyr::where(is.numeric),
      ~ if (dplyr::cur_column() %in% p_cols) round(., p_digits) else round(., other_digits)
    ))
}

type3_anova <- function(model) {
  anova(model, type = 3) %>%
    as.data.frame() %>%
    tibble::rownames_to_column("Effect") %>%
    dplyr::mutate(
      partial_eta2 = (`F value` * NumDF) / ((`F value` * NumDF) + DenDF)
    ) %>%
    round_mix(p_cols = "Pr(>F)")
}

fixed_effects <- function(model) {
  broom.mixed::tidy(model, effects = "fixed", conf.int = TRUE, conf.level = .95) %>%
    dplyr::select(term, estimate, std.error, conf.low, conf.high,
                  df, statistic, p.value) %>%
    dplyr::rename(t = statistic, p = p.value) %>%
    round_mix(p_cols = "p")
}

marginal_means <- function(emm) {
  emm %>%
    as.data.frame() %>%
    dplyr::rename(EM = emmean, CI_lower = lower.CL, CI_upper = upper.CL) %>%
    round_mix(p_cols = character())
}

pairwise <- function(emm) {
  pairs(emm, adjust = "none") %>%
    as.data.frame() %>%
    dplyr::rename(t = t.ratio, p = p.value) %>%
    round_mix(p_cols = "p")
}

make_tbl <- function(title, df, base = 9) {
  gridExtra::arrangeGrob(
    grid::textGrob(title, x = 0, hjust = 0,
                   gp = grid::gpar(fontsize = 11, fontface = "bold")),
    gridExtra::tableGrob(
      df, rows = NULL,
      theme = gridExtra::ttheme_minimal(base_size = base,
                                        padding = grid::unit(c(1.5, 3), "mm"))
    ),
    ncol = 1,
    heights = grid::unit.c(grid::unit(1, "lines"), grid::unit(1, "null"))
  )
}

write_report <- function(tables, titles, file, base = 9) {
  grobs <- Map(make_tbl, titles, tables, MoreArgs = list(base = base))
  pdf(file, width = 8.5, height = 11)
  on.exit(dev.off(), add = TRUE)
  for (i in seq_along(grobs)) {
    gridExtra::grid.arrange(grobs[[i]], ncol = 1, newpage = i > 1)
  }
  invisible(file)
}

save_table <- function(df, name) {
  path <- file.path(OUT_DIR, name)
  readr::write_csv(df, path)
  message("wrote ", path)
  invisible(path)
}
