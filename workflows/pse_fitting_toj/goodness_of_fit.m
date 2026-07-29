%% goodness_of_fit.m  --  [PART 2: goodness-of-fit / Palamedes]
%
% Evaluates the goodness-of-fit of the Part-1 fits via bootstrap.
% Reproduces the original pdev_input.txt calls to PAL_PFML_GoodnessOfFit
% (organized as a loop).
%
% Larger pDev = better fit (data consistent with the model). A common rule
% of thumb is pDev < .05 indicates poor fit -> consider excluding that cell.
%
% Requires: MATLAB + Palamedes, and Part-1 outputs (numpos.csv, pse_results.csv)
% Run:      in MATLAB,  >> run goodness_of_fit.m
% Output:   ../outputs/pdev_results.csv
%           (participant, label, Dev, pDev, converged_ratio)

clear; clc;

here     = fileparts(mfilename('fullpath'));
numpos   = fullfile(here, 'outputs', 'numpos.csv');
fitcsv   = fullfile(here, 'outputs', 'pse_results.csv');
out_csv  = fullfile(here, 'outputs', 'pdev_results.csv');

try
    addpath(toolboxdir('Palamedes'));
catch
    warning('Please addpath your Palamedes folder manually.');
end

%% --- settings (same as Part 1 + bootstrap count) ---------------------
StimLevels = [-42 -28 -14 0 14 28 42];   % FINAL sign convention (see fit_pse.m; flipped from intermediate)
OutOfNum   = [20 20 20 20 20 20 20];
PF         = @PAL_CumulativeNormal;
paramsFree = [1 1 0 0];
searchGrid.alpha  = -42:0.1:42;
searchGrid.beta   = 10.^(-2.5:0.001:1.5);
searchGrid.gamma  = 0;
searchGrid.lambda = 0.01;
B = 1000;                                    % bootstrap simulations (same as original)

%% --- read input (NumPos + fitted parameters) -------------------------
Tn = readtable(numpos);
Tf = readtable(fitcsv);
assert(height(Tn) == height(Tf), 'numpos.csv and pse_results.csv row counts differ');
K  = [Tn.k1 Tn.k2 Tn.k3 Tn.k4 Tn.k5 Tn.k6 Tn.k7];
n  = height(Tn);

Dev = nan(n,1); pDev = nan(n,1); convRatio = nan(n,1);

%% --- loop ------------------------------------------------------------
fprintf('Goodness-of-fit: %d cells x B=%d ...\n', n, B);
for i = 1:n
    NumPos       = K(i, :);
    paramsValues = [Tf.alpha(i) Tf.beta(i) 0 0.01];   % Part-1 fit result
    [dev, pdev, ~, converged] = PAL_PFML_GoodnessOfFit( ...
        StimLevels, NumPos, OutOfNum, paramsValues, paramsFree, B, PF, ...
        'searchGrid', searchGrid);
    Dev(i)       = dev;
    pDev(i)      = pdev;
    convRatio(i) = mean(converged == 1);
    fprintf('  %d/%d  pDev=%.3f\n', i, n, pdev);
end

%% --- save ------------------------------------------------------------
R = table(Tf.participant, Tf.label, Dev, pDev, convRatio, ...
          'VariableNames', {'participant','label','Dev','pDev','converged_ratio'});
writetable(R, out_csv);
fprintf('[done] -> %s\n', out_csv);
