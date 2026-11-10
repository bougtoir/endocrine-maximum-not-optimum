% Gate A cross-implementation driver: runs the frozen upstream Sorensen MATLAB autocode (RK4, Tdelta=0.1)
% for one protocol and writes TIME, GlucPV [mM], InsuPV [pM], Cgon [pM]. Usage: octave run_upstream.m <protocol> <outcsv>
args = argv(); protocol = args{1}; outcsv = args{2};
SorensenInitializeParvals; SorensenInitializeStateVars;
% optional 3rd arg 'nocap': lift the AutoTester ForceVars bound (VARMAX=1000, indexed v+1) on the IV infusion variables
if numel(args) >= 3 && strcmp(args{3}, 'nocap'), VARMAX(54:55) = 1e9; end
switch protocol
  case 'ivgtt'   % upstream default: 64.81 mmol/min, TimeIVG -3..0
  case 'ivitt'
    GammaIVGin = 0; GammaIVIin = 2800*6.944/3; TimeIVI = 0; TimeIVIend = 3; Tend = 180;
  case 'civii'
    GammaIVGin = 0; GammaIVIin = 17.5*6.944; TimeIVI = 0; TimeIVIend = 150; Tend = 330;
  case 'fasting'
    GammaIVGin = 0;
end
TIME = Tzero:Tdelta:Tend;
nTimes = length(TIME);
STATEVARS = zeros(nTimes,nDepVars);
STATEVARS(1,:) = CurrentY;

% 20190709 Andrea De Gaetano, Marcello Pompa: Runge Kutta 4
% NOTE: this MATLAB implementation of RK4 uses vector assignments and therefore does NOT replicate exactly the corresponding C++ RK routine.
% By vector-assigning the increments to the (differentially-defined) Ys, the intermediate and final computation of the derivatives of one Y depend
% on the intermediate and final values of the other Ys. Conversely, when using loops, the intermediate and final computation of the derivatives of
% one Y depend on the interval INITIAL values of the other Ys, same as in C++. This last arrangement is consistent with the fact that the algebraic
% variables too are updated only after the computation of all the differential variables and that therefore the algebraic variable values used
% during all of the intermediate computations are the interval initial values.
% For smooth functions the differences in the implementations ought to be minimal. In case of differences, the C++ version is the logically
% consistent one. In any case, for non-smooth functions a variable-step integrator such as Runge-Kutta-Fehlberg ought to be used.

fprintf(1,'\n.');
Time = TIME(1);
for (tk=1:(nTimes-1))
   CurrentY0 = CurrentY;

   SorensenCurrentY2NamedVars;
   SorensenComputeDerivatives;
   dY1 = out1;

   Time = TIME(tk) + Tdelta/2;
   CurrentY = CurrentY0 + Tdelta/2 * dY1;
   SorensenCurrentY2NamedVars;
   SorensenComputeDerivatives;
   dY2 = out1;

   CurrentY = CurrentY0 + Tdelta/2 * dY2;
   SorensenCurrentY2NamedVars;
   SorensenComputeDerivatives;
   dY3 = out1;

   Time = TIME(tk+1);
   CurrentY = CurrentY0 + Tdelta * dY3;
   SorensenCurrentY2NamedVars;
   SorensenComputeDerivatives;
   dY4 = out1;

   CurrentY = CurrentY0 + Tdelta * (dY1/6 + dY2/3 + dY3/3 + dY4/6);
   SorensenForceVars;
   SorensenCurrentY2NamedVars; % needed to do the next computations
   SorensenComputeDiracs;
   SorensenNamedVars2CurrentY; % rebuild CurrentY
   SorensenForceVars;
   SorensenCurrentY2NamedVars; % needed to do the next computations
   SorensenComputeAlgebraic;
   SorensenNamedVars2CurrentY; % rebuild CurrentY
   SorensenForceVars;
   STATEVARS(tk+1,:) = CurrentY;
   fprintf(1,'.'); if (mod(tk,50)==0) fprintf(1,'\n'); end  % show progress
end
iC = 47; csvwrite(outcsv, [TIME(:) STATEVARS(:,9) STATEVARS(:,32) STATEVARS(:,iC)]);
