# 행동 데이터 선형혼합모형 (IMT / DMT / SMT)

세 가지 기억 과제(IMT, DMT, SMT)의 행동 수행을 **선형혼합모형(LMM)** 으로
분석하는 코드입니다. 과제와 자극 유형(표적/캐치)을 고정효과로, 연령과 성별을
공변량으로 두고, 참가자마다 임의절편을 둡니다.

입력은 조건별 값이 담긴 long-form 표 하나이며, **원자료 전처리는 포함하지
않습니다**.

## 폴더 구조

```
.
├── README.md
├── INPUT_FORMAT.md              입력 CSV 형식 명세
├── example_error_rate_long.csv  입력 예시(가상 데이터)
├── lmm_common.R                 공통: 패키지·데이터 코딩·표 생성
├── lmm_error_rate.R             오류율   ~ stimulus * task + Gender + Age
├── lmm_rt.R                     반응시간 ~ stimulus * task + Gender + Age
├── lmm_rcs.R                    RCS      ~ task + Gender + Age
└── outputs/                     입력 CSV 를 두고, 결과가 저장되는 곳
```

## 모형

```r
# 오류율 · 반응시간 — 표적/캐치가 모두 있으므로 상호작용 포함
measure ~ stimulus * task + Gender + Age + (1 | subject)

# RCS — 표적 시행에서만 정의되므로 자극 요인 없음
measure ~ task + Gender + Age + (1 | subject)
```

`lme4` 로 적합하고 `lmerTest` 로 Satterthwaite 자유도 기반 **Type III** 검정을
수행합니다. 효과크기는 부분 에타제곱을 F 비로부터 계산합니다.

```
eta2_p = (F * NumDF) / (F * NumDF + DenDF)
```

오류율과 반응시간에서는 상호작용이 과제 효과의 해석을 제약하므로, 과제 효과를
**자극 유형별로** 다시 보고합니다. 이때 자극별로 모형을 나눠 적합하지 않고
`emmeans::joint_tests(model, by = "stimulus")` 로 전체 모형에서 뽑아, 같은 오차항을
쓰도록 했습니다.

## 요구사항

R 과 다음 패키지: `tidyverse`, `lme4`, `lmerTest`, `broom.mixed`, `emmeans`,
`gridExtra`.

```r
install.packages(c("tidyverse", "lme4", "lmerTest",
                   "broom.mixed", "emmeans", "gridExtra"))
```

## 실행

1. 입력 CSV 를 `outputs/` 에 둡니다 — 이름은 [`INPUT_FORMAT.md`](./INPUT_FORMAT.md) 참조.
2. 이 폴더에서 실행합니다.

```bash
Rscript lmm_error_rate.R
Rscript lmm_rt.R
Rscript lmm_rcs.R
```

빠른 확인: `example_error_rate_long.csv` 를 `outputs/error_rate_long.csv` 로
복사한 뒤 `Rscript lmm_error_rate.R`.

## 출력

측정치마다 `outputs/` 에 다음이 생깁니다.

| 파일 | 내용 |
| --- | --- |
| `typeIII_anova_*.csv` | Type III ANOVA + 부분 에타제곱 |
| `fixed_effects_*.csv` | 고정효과 추정치, 95% 신뢰구간, t, p |
| `emmeans_*.csv` | 추정 주변평균과 신뢰구간 |
| `pairwise_*.csv` | 조건 간 쌍비교(보정 없음) |
| `task_within_stimulus_*.csv` | 자극 유형별 과제 omnibus (오류율·반응시간만) |
| `lmm_report_*.pdf` | 위 표들을 한 페이지에 하나씩 담은 보고서 |

## 성별 코딩

입력의 `Gender`(또는 `Sex`)는 **1 = 남성, 2 = 여성** 으로 고정해서 읽습니다.
다른 코딩을 쓰는 자료는 넣기 전에 바꿔야 하며, 코딩이 어긋나면 스크립트가
중단되도록 검사를 넣어 두었습니다.

## 연구 맥락

이 워크플로가 나온 연구는 프로젝트 페이지에 정리돼 있습니다.

```text
projects/adolescent_impulsivity_salience_network/
```

원자료와 참가자 정보는 포함하지 않습니다.
