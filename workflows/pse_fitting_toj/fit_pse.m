%% fit_pse.m  --  [PART 1: PSE fitting / Palamedes]
%
% Reads numpos.csv (output of 01_preprocess.py) and, for each
% participant x condition, fits a cumulative-normal psychometric function
% with Palamedes and computes the PSE.
%
% Faithful to the original workflow (hyperparams_input.txt + params_input.txt
% + pse_input.txt), but instead of thousands of auto-generated variable-name
% lines it loops over numpos.csv. Settings are identical to the original.
%
% Requires: MATLAB + Palamedes toolbox  (www.palamedestoolbox.org)
% Run:      in MATLAB, cd to this folder, then  >> run fit_pse.m
% Output:   ../outputs/pse_results.csv
%           (participant, label, alpha, beta, LL, exitflag, PSE)

clear; clc;

%% --- paths ------------------------------------------------------------
here    = fileparts(mfilename('fullpath'));
in_csv  = fullfile(here, 'outputs', 'numpos.csv');
out_csv = fullfile(here, 'outputs', 'pse_results.csv');

% Add Palamedes to the path (same as original hyperparams_input.txt).
% If toolboxdir fails, replace the line below with your own path, e.g.:
%   addpath(genpath('C:\path\to\Palamedes'));
try
    addpath(toolboxdir('Palamedes'));
catch
    warning('toolboxdir(''Palamedes'') failed. Please addpath your Palamedes folder manually.');
end

%% --- fitting settings (identical to original hyperparams_input.txt) ---
StimLevels = [-42 -28 -14 0 14 28 42];   % FINAL sign convention (intermediate pses.csv used [42 28 14 0 -14 -28 -42]; final flips the sign)
OutOfNum   = [20 20 20 20 20 20 20];        % trials per level (all 20, verified in preprocessing)
PF         = @PAL_CumulativeNormal;         % psychometric function (cumulative normal)
paramsFree = [1 1 0 0];                      % [threshold slope guess lapse] -> only first two free
searchGrid.alpha  = -42:0.1:42;             % brute-force grid for threshold (alpha)
searchGrid.beta   = 10.^(-2.5:0.001:1.5);   % grid for slope (beta)
searchGrid.gamma  = 0;                       % guess rate fixed
searchGrid.lambda = 0.01;                    % lapse rate fixed

% To use Weibull instead (reproduces pse_weibull.csv):
%   PF = @PAL_Weibull;   (StimLevels should be positive -- check stimulus transform if needed)

%% --- read input ------------------------------------------------------
T = readtable(in_csv);
K = [T.k1 T.k2 T.k3 T.k4 T.k5 T.k6 T.k7];    % NumPos matrix (rows = conditions)
n = height(T);

alpha = nan(n,1); beta = nan(n,1);
LL = nan(n,1); exitflag = nan(n,1); PSE = nan(n,1);

%% --- loop over participant x condition -------------------------------
fprintf('Fitting %d cells (participant x condition)\n', n);
for i = 1:n
    NumPos = K(i, :);

    % 1) Maximum-likelihood fit (same as PAL_PFML_Fit in params_input.txt)
    [params, ll, ef] = PAL_PFML_Fit(StimLevels, NumPos, OutOfNum, ...
                                    searchGrid, paramsFree, PF);
    alpha(i)    = params(1);
    beta(i)     = params(2);
    LL(i)       = ll;
    exitflag(i) = ef;

    % 2) PSE = stimulus value where the PF equals 0.5 (inverse)
    %    (same as pse_input.txt: gamma=0, lambda=0.01 fixed)
    PSE(i) = PAL_CumulativeNormal([params(1) params(2) 0 0.01], 0.5, 'inverse');

    if mod(i, 20) == 0, fprintf('  %d/%d done\n', i, n); end
end

%% --- save ------------------------------------------------------------
R = table(T.participant, T.stim_type, T.cond, T.label, ...
          alpha, beta, LL, exitflag, PSE, ...
          'VariableNames', {'participant','stim_type','cond','label', ...
                            'alpha','beta','LL','exitflag','PSE'});
writetable(R, out_csv);
fprintf('[done] -> %s  (%d rows)\n', out_csv, height(R));
fprintf('Note: rows with exitflag~=1 or Inf/NaN/extreme PSE are failed fits -> review exclusion in Part 2\n');
