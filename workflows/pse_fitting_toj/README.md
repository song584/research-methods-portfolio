# PSE 피팅 분석 (시간순서판단 / TOJ)

시간순서판단(TOJ) 과제에서 참가자별·조건별 **PSE(주관적 동시점, Point of Subjective Equality)** 를 심리측정함수 피팅으로 추정하고, 그 결과를 정리·시각화하는 코드입니다.

입력은 조건별 반응 집계표(`numpos.csv`) 하나이며, **원자료 전처리는 포함하지 않습니다**(데이터마다 형식이 달라 각자 준비).

## 폴더 구조

```
.
├── README.md
├── INPUT_FORMAT.md         입력 파일(numpos.csv) 형식 명세
├── numpos_example.csv      입력 예시(템플릿)
├── fit_pse.m               numpos.csv → 누적정규 피팅 → PSE   (MATLAB + Palamedes)
├── goodness_of_fit.m       피팅 적합도 평가 (bootstrap)        (MATLAB + Palamedes)
├── after_pse_analysis.py   PSE 정리·요약표·막대그래프          (Python)
└── outputs/                실행 결과 + 입력 numpos.csv 를 두는 곳
```

## 입력

피팅의 입력은 **`numpos.csv`** 하나입니다 — 각 (참가자 × 조건)마다 7개 자극수준에서의 "양성 반응" 개수(NumPos)를 담은 표.

- 형식 명세: **[`INPUT_FORMAT.md`](./INPUT_FORMAT.md)**
- 예시/템플릿: **[`numpos_example.csv`](./numpos_example.csv)**
- 두는 곳: `outputs/numpos.csv` (또는 `fit_pse.m` 의 `in_csv` 경로 수정)

> 원자료 → `numpos.csv` 전처리는 이 저장소에 포함돼 있지 않습니다. 본인 데이터를 위 형식으로만 맞추면 됩니다.

## 요구사항

- **MATLAB + [Palamedes toolbox](http://www.palamedestoolbox.org)** — 피팅
- **Python** (pandas, numpy, matplotlib, seaborn, openpyxl) — 그래프

## 실행

1. 입력 `numpos.csv` 를 `outputs/` 에 둔다.
2. MATLAB 에서 Palamedes 경로 추가: `addpath(genpath('<Palamedes 경로>'))`
3. 피팅: `run fit_pse.m` → `outputs/pse_results.csv`
4. 적합도: `run goodness_of_fit.m` → `outputs/pdev_results.csv`
5. 이후 분석: `python after_pse_analysis.py` → `outputs/summary_pse.xlsx`, `outputs/figures/*.png`

> 빠른 테스트: `numpos_example.csv` 를 `outputs/numpos.csv` 로 복사한 뒤 3번 실행.

## 피팅 설정 (`fit_pse.m`)

```matlab
StimLevels  = [-42 -28 -14 0 14 28 42];   % 자극수준(ms); numpos.csv 의 k1..k7 순서와 대응
OutOfNum    = [20 20 20 20 20 20 20];      % 수준당 시행 수
PF          = @PAL_CumulativeNormal;       % 누적정규
paramsFree  = [1 1 0 0];                    % 역치·기울기만 자유, 추측률 0 / 실수율 0.01 고정
searchGrid.alpha = -42:0.1:42;
searchGrid.beta  = 10.^(-2.5:0.001:1.5);
```

PSE 는 `PAL_CumulativeNormal([alpha beta 0 0.01], 0.5, 'inverse')` 로 구합니다.
**StimLevels 의 부호가 PSE 부호 규약을 결정**합니다 — 결과 부호가 기대와 반대면 StimLevels 부호를 뒤집으세요.

## 출력 / 결과 정리

- `pse_results.csv` — 참가자 × 조건별 `alpha, beta, LL, exitflag, PSE`
- `pdev_results.csv` — 적합도 `pDev` (작을수록 적합 불량; 예: `< .05` 면 제외 검토)
- `after_pse_analysis.py` — PSE 를 정리해 요약표/그래프 생성. 상단 옵션으로 정리 기준 조절:
  - `PSE_ABS_LIMIT`, `DROP_NONFINITE` — 자극범위 밖·`Inf`·`NaN` 등 실패한 피팅 제외
  - `EXCEPT_NONE`, `EXCLUDE_PARTICIPANTS` — 기저선/특정 참가자 제외

## 연구 맥락

이 워크플로가 나온 연구의 배경과 역할은 프로젝트 페이지에 정리돼 있습니다:

```text
projects/temporal_order_judgment_pse/
```

원자료, 전처리, 실험 프로그램은 포함하지 않습니다. 입력 형식만 맞추면 다른
데이터에도 그대로 쓸 수 있습니다.
