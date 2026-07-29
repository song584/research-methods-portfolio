#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
after_pse_analysis.py  —  [PART 2: PSE 이후 분석]

피팅으로 얻은 PSE 값을 정리·시각화한다 (원본 최상위 Untitled.ipynb 재현).
  - PSE 결과를 long 표로 정리 (참가자 x 자극유형 x 방향조합)
  - 피팅 실패(Inf/NaN/극단값/미수렴) 정리
  - 자극유형 x 방향조합 평균 PSE 요약표 (xlsx)
  - 기저선(none) 대비 차이(diff) 계산
  - 막대그래프 재현 (원본 seaborn barplot 셀들)

입력 우선순위:
  1) outputs/pse_results.csv     (fit_pse.m 의 새 피팅 결과)  — 권장
  2) _original_reference/pses.csv (학위논문 당시 원본 PSE)        — MATLAB 없이 바로 테스트용

실행:  python after_pse_analysis.py
출력:  outputs/summary_pse.xlsx, outputs/pse_long.csv, outputs/figures/*.png
"""

import os
import re
import glob
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

# ----------------------------------------------------------------------
# 정리/제외 옵션  (학위논문은 jamovi 에서 여러 제외본을 만들었음:
#   exceptnone / nojiyeon / yesjuho. 아래 knob 로 동일하게 재현 가능.)
# ----------------------------------------------------------------------
EXCEPT_NONE          = True      # 기저선(none) 조건을 그래프/요약에서 제외할지
EXCLUDE_PARTICIPANTS = []        # 예: ["P12"]  (특정 참가자 제외 예시)
PSE_ABS_LIMIT        = 100.0     # |PSE| 가 이 값 초과면 피팅 실패로 보고 제외 (None=미적용)
DROP_NONFINITE       = True      # Inf/NaN 제외

HERE   = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "outputs")
FIGDIR = os.path.join(OUTDIR, "figures")

STIM_MAP = {0: "none", 1: "arrow", 2: "gaze"}            # 자극유형: 없음/화살표/시선
STIM_KO  = {"none": "없음(기저선)", "arrow": "화살표", "gaze": "시선"}
CONF_KO  = {"BB": "뒤-뒤", "facing": "마주봄", "FF": "앞-앞", "nonfacing": "등돌림"}
LABEL_RE = re.compile(r"^(.+?)([012])(none|BB|facing|FF|nonfacing)$")


def find_korean_font():
    """설치된 한글 폰트 자동 탐색 (NanumGothic/AppleGothic/Malgun Gothic 등)."""
    import matplotlib.font_manager as fm
    have = {f.name for f in fm.fontManager.ttflist}
    for cand in ["NanumGothic", "AppleGothic", "Apple SD Gothic Neo",
                 "Malgun Gothic", "Noto Sans CJK KR", "NanumBarunGothic"]:
        if cand in have:
            return cand
    return None


# ----------------------------------------------------------------------
# 입력 로딩 -> 통일된 long DataFrame [participant, stim_type, confront, pse, exitflag]
# ----------------------------------------------------------------------
def load_long():
    long_csv = os.path.join(OUTDIR, "pse_results.csv")
    wide_csv = os.path.join(HERE, "_original_reference", "pses.csv")

    if os.path.exists(long_csv):
        d = pd.read_csv(long_csv)
        d["stim_type"] = d["stim_type"].map(STIM_MAP)
        d = d.rename(columns={"cond": "confront", "PSE": "pse"})
        if "exitflag" not in d:
            d["exitflag"] = 1
        src = "pse_results.csv (새 피팅)"
        return d[["participant", "stim_type", "confront", "pse", "exitflag"]], src

    # fallback: 원본 wide pses.csv (1행, 컬럼명 PSE<참가자><label>)
    raw = pd.read_csv(wide_csv)
    rows = []
    for col in raw.columns:
        name = col.strip()
        if not name.startswith("PSE"):
            continue
        m = LABEL_RE.match(name[3:])
        if not m:
            continue
        pid, stim, cond = m.group(1), int(m.group(2)), m.group(3)
        rows.append({"participant": pid, "stim_type": STIM_MAP[stim],
                     "confront": cond, "pse": float(raw[col].iloc[0]),
                     "exitflag": 1})
    return pd.DataFrame(rows), "원본 pses.csv (학위논문 PSE)"


def clean(df):
    """피팅 실패/제외 적용. 정리 전후 개수를 함께 반환."""
    n0 = len(df)
    d = df.copy()
    if DROP_NONFINITE:
        d = d[np.isfinite(d["pse"])]
    if PSE_ABS_LIMIT is not None:
        d = d[d["pse"].abs() <= PSE_ABS_LIMIT]
    if "exitflag" in d:
        d = d[d["exitflag"] == 1]
    if EXCLUDE_PARTICIPANTS:
        d = d[~d["participant"].isin(EXCLUDE_PARTICIPANTS)]
    return d.reset_index(drop=True), n0, len(d)


# ----------------------------------------------------------------------
# 분석
# ----------------------------------------------------------------------
def summarize(d):
    """자극유형 x 방향조합 평균/표준편차/표준오차/N 요약."""
    g = (d.groupby(["stim_type", "confront"])["pse"]
           .agg(["mean", "std", "count"]).reset_index())
    g["se"] = g["std"] / np.sqrt(g["count"])
    return g


def diff_from_baseline(d):
    """참가자별 기저선(none) 대비 PSE 차이 (table_logistic_diff 개념)."""
    base = (d[d["stim_type"] == "none"]
            .groupby("participant")["pse"].mean().rename("base"))
    m = d[d["stim_type"] != "none"].merge(base, on="participant", how="left")
    m["pse_diff"] = m["pse"] - m["base"]
    return m


def barplot(d, x, hue, fname, title, korean=False):
    plt.figure(figsize=(7, 5))
    data = d.copy()
    if korean:
        kfont = find_korean_font()
        if kfont is None:
            print("  (한글 폰트 없음 -> 영문 라벨로 출력. 한글 폰트 설치 시 자동 적용)")
            korean = False
        else:
            data["stim_type"] = data["stim_type"].map(lambda s: STIM_KO.get(s, s))
            data["confront"]  = data["confront"].map(lambda s: CONF_KO.get(s, s))
            plt.rcParams["font.family"] = kfont
            plt.rcParams["axes.unicode_minus"] = False
    sns.barplot(x=x, y="pse", hue=hue, data=data,
                errorbar="se", capsize=0.1, palette="Blues", err_kws={"linewidth": 1.2})
    plt.ylabel("PSE (ms)"); plt.title(title); plt.tight_layout()
    plt.savefig(os.path.join(FIGDIR, fname), dpi=120)
    plt.close()


def main():
    os.makedirs(FIGDIR, exist_ok=True)
    df, src = load_long()
    print(f"[입력] {src}  ({len(df)} 행)")

    d, n0, n1 = clean(df)
    print(f"[정리] {n0} -> {n1} 행 (Inf/NaN·|PSE|>{PSE_ABS_LIMIT}·미수렴·제외참가자 제거)")

    plot_d = d[d["stim_type"] != "none"] if EXCEPT_NONE else d

    # 요약표 + long 저장
    summ = summarize(plot_d)
    diff = diff_from_baseline(d)
    d.to_csv(os.path.join(OUTDIR, "pse_long.csv"), index=False)
    with pd.ExcelWriter(os.path.join(OUTDIR, "summary_pse.xlsx")) as xw:
        summ.to_excel(xw, sheet_name="mean_by_condition", index=False)
        diff.to_excel(xw, sheet_name="diff_from_baseline", index=False)
        d.to_excel(xw, sheet_name="pse_long", index=False)

    # 그래프 (원본 셀 6~13 재현)
    barplot(plot_d, "confront", "stim_type", "fig1_pse_by_confront_x_stim.png",
            "PSE by 방향조합 x 자극유형")
    barplot(plot_d, "stim_type", "confront", "fig2_pse_by_stim_x_confront.png",
            "PSE by 자극유형 x 방향조합")
    barplot(plot_d, "stim_type", "confront", "fig3_pse_korean.png",
            "자극 유형별 PSE (방향 조합)", korean=True)

    print("[완료] 요약표/그래프 저장:")
    print(f"   - {os.path.join(OUTDIR,'summary_pse.xlsx')}")
    print(f"   - {os.path.join(OUTDIR,'pse_long.csv')}")
    print(f"   - {FIGDIR}/fig1..3_*.png")
    print("\n조건별 평균 PSE (ms):")
    print(summ.to_string(index=False))


if __name__ == "__main__":
    main()
