# 입력 파일 형식 — `numpos.csv`

이 저장소는 **피팅 단계부터** 공개합니다. 전처리 코드는 포함하지 않으며,
대신 피팅 스크립트가 받는 입력 파일(`numpos.csv`)의 형식만 정의합니다.
원자료를 어떤 방식으로 처리하든, 아래 형식의 `numpos.csv` 만 만들면 그대로 피팅됩니다.

예시는 같은 폴더의 [`numpos_example.csv`](./numpos_example.csv) 참고.

---

## 무엇을 만들면 되나

각 **(참가자 × 조건)** 마다, 7개 자극수준(SOA)에서의 **"양성 반응" 개수(NumPos)** 를
센 표입니다. 한 행 = 한 (참가자 × 조건).

## 파일 위치

피팅 스크립트(`fit_pse.m`)는 기본적으로 `outputs/numpos.csv` 를 읽습니다.
본인 파일을 거기에 두거나, 스크립트 상단 `in_csv` 경로를 바꾸세요.

```
% fit_pse.m
in_csv = fullfile(here, 'outputs', 'numpos.csv');
```

## 형식

- CSV, UTF-8, **헤더 1줄 포함**
- 행 수 = 참가자 수 × 조건 수 (예: 16명 × 9조건 = 144행)

| 컬럼 | 타입 | 설명 |
|---|---|---|
| `participant` | 문자열 | 참가자 ID. 결과 파일에 그대로 전달(식별용). |
| `stim_type` | 정수/문자열 | 자극 유형 등 분류 라벨. 결과에 전달(피팅 계산엔 미사용). |
| `cond` | 문자열 | 조건명. 결과에 전달. |
| `label` | 문자열 | 행을 구분하는 고유 라벨(예: `1facing`). 결과에 전달. |
| `k1`~`k7` | 정수 0~20 | 7개 자극수준에서의 **양성 반응 개수(NumPos)**. 스크립트의 `StimLevels` 순서와 동일. |

## `k1`~`k7` 와 자극수준의 대응

`k1`~`k7` 은 피팅 스크립트의 `StimLevels` 벡터와 **같은 순서**로 정렬되어야 합니다.
현재 설정(최종 부호 규약):

```
StimLevels = [-42 -28 -14 0 14 28 42];   % k1 ↔ -42, k2 ↔ -28, ..., k7 ↔ 42 (ms)
OutOfNum   = [20 20 20 20 20 20 20];      % 수준당 시행 수 = 20  -> k 값은 0~20
```

- 자극수준 단위/부호는 본인 실험 규약에 맞추면 됩니다(스크립트의 `StimLevels` 만 일치시키면 됨).
- **양성 반응의 정의**(두 응답 중 어느 쪽을 셀지)에 따라 PSE 부호가 결정됩니다. 일관되게만 세면 됩니다.
- 수준당 시행 수가 20이 아니면 스크립트의 `OutOfNum` 도 함께 바꾸세요.

## 예시 (numpos_example.csv 발췌)

```
participant,stim_type,cond,label,k1,k2,k3,k4,k5,k6,k7
P01_example,0,none,0none,2,5,11,16,18,20,20
P01_example,1,BB,1BB,2,5,10,14,18,19,20
P01_example,1,facing,1facing,2,4,8,12,19,19,20
...
```

(위 예시 값은 형식 설명용 가상 데이터입니다.)

## 출력

`fit_pse.m` 실행 결과는 `outputs/pse_results.csv` 로 저장됩니다:

| 컬럼 | 설명 |
|---|---|
| `participant`, `stim_type`, `cond`, `label` | 입력에서 그대로 전달 |
| `alpha`, `beta` | 피팅된 역치·기울기 |
| `LL`, `exitflag` | 로그우도, 수렴 플래그(1=정상) |
| `PSE` | 주관적 동시점 (`PAL_CumulativeNormal` 역함수, 0.5 교차점) |

## 빠른 테스트

```matlab
% 예시 파일로 동작 확인:
%   numpos_example.csv 를 outputs/numpos.csv 로 복사한 뒤
addpath(genpath('<Palamedes 경로>'))
run fit_pse.m        % -> outputs/pse_results.csv 생성
```
