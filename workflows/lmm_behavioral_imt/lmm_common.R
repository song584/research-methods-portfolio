## lmm_common.R -- shared setup for the behavioural LMM scripts
##
## Sourced by lmm_error_rate.R, lmm_rt.R and lmm_rcs.R. Holds the parts that
## are identical across the three outcome measures: package loading, reading
## and coding the long-form table, and turning model output into tables.

suppressPackageStartupMessages({
  library(tidyverse)
  library(lme4)
  library(lmerTest)
  library(broom.mixed)
  library(emmeans)
  library(gridExtra)
  library(grid)
})

## Type III tests are requested from lmerTest below; sum-to-zero contrasts are
## the conventional pairing for them.
options(contrasts = c("contr.sum", "contr.poly"))

HERE    <- getwd()
OUT_DIR <- file.path(HERE, "outputs")
dir.create(OUT_DIR, showWarnings = FALSE)

## Missing responses are stored as 9999 in the source tables.
MISSING_CODE <- 9999

#' Read a long-form behavioural table and code its factors
#'
#' @param path CSV in the layout described in INPUT_FORMAT.md.
#' @param measure_col Column holding the outcome for this analysis.
#' @param scale Multiplier applied to the outcome (100 turns a proportion into
#'   a percentage; 1 leaves reaction times in milliseconds).
#' @return Data frame with `subject`, `stimulus`, `task`, `Gender`, `Age` and
#'   `measure`, with missing outcomes dropped.
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

  ## 1 = male, 2 = female in the source tables.
  dat$Gender <- factor(dat[[sex_col]], levels = c(1, 2), labels = c("M", "F"))

  ## Present only for the measures that separate target from catch trials.
  if ("stimulus" %in% names(dat)) {
    dat$stimulus <- factor(dat$stimulus, levels = c(1, 2),
                           labels = c("Target", "Catch"))
    stopifnot(identical(levels(dat$stimulus), c("Target", "Catch")))
  }

  dat$task <- factor(dat$task, levels = c(1, 2, 3),
                     labels = c("IMT", "DMT", "SMT"))

  stopifnot(identical(levels(dat$task), c("IMT", "DMT", "SMT")))
  stopifnot(identical(levels(dat$Gender), c("M", "F")))
  stopifnot(!anyNA(dat$Gender), !anyNA(dat$task))

  dat
}

#' Round p-value columns and the remaining numeric columns separately
round_mix <- function(df, p_cols, other_digits = 3, p_digits = 4) {
  df %>%
    dplyr::mutate(dplyr::across(
      dplyr::where(is.numeric),
      ~ if (dplyr::cur_column() %in% p_cols) round(., p_digits) else round(., other_digits)
    ))
}

#' Type III ANOVA with partial eta squared
#'
#' Partial eta squared is derived from the F ratio and its degrees of freedom,
#' eta2_p = (F * df1) / (F * df1 + df2).
type3_anova <- function(model) {
  anova(model, type = 3) %>%
    as.data.frame() %>%
    tibble::rownames_to_column("Effect") %>%
    dplyr::mutate(
      partial_eta2 = (`F value` * NumDF) / ((`F value` * NumDF) + DenDF)
    ) %>%
    round_mix(p_cols = "Pr(>F)")
}

#' Fixed-effect estimates with 95% confidence intervals
fixed_effects <- function(model) {
  broom.mixed::tidy(model, effects = "fixed", conf.int = TRUE, conf.level = .95) %>%
    dplyr::select(term, estimate, std.error, conf.low, conf.high,
                  df, statistic, p.value) %>%
    dplyr::rename(t = statistic, p = p.value) %>%
    round_mix(p_cols = "p")
}

#' Estimated marginal means as a data frame
marginal_means <- function(emm) {
  emm %>%
    as.data.frame() %>%
    dplyr::rename(EM = emmean, CI_lower = lower.CL, CI_upper = upper.CL) %>%
    round_mix(p_cols = character())
}

#' Pairwise contrasts, uncorrected
pairwise <- function(emm) {
  pairs(emm, adjust = "none") %>%
    as.data.frame() %>%
    dplyr::rename(t = t.ratio, p = p.value) %>%
    round_mix(p_cols = "p")
}

#' One titled table for the PDF report
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

#' Write one table per page of a PDF report
write_report <- function(tables, titles, file, base = 9) {
  grobs <- Map(make_tbl, titles, tables, MoreArgs = list(base = base))
  pdf(file, width = 8.5, height = 11)
  on.exit(dev.off(), add = TRUE)
  for (i in seq_along(grobs)) {
    gridExtra::grid.arrange(grobs[[i]], ncol = 1, newpage = i > 1)
  }
  invisible(file)
}

#' Save a table to outputs/ and report where it went
save_table <- function(df, name) {
  path <- file.path(OUT_DIR, name)
  readr::write_csv(df, path)
  message("wrote ", path)
  invisible(path)
}
