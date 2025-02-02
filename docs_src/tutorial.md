# Tutorial

Here we walk through two example calculations found in the `latqcdtools/examples`
directory. The first shows a simple HRG calculation, while the second showcases
a continuum limit extrapolation.

## Hadron resonance gas calculation

The hadron resonance gas (HRG) model, and its implementation in the AnalysisToolbox,
is described in some detail [here](physicsAnalysis/HRG.md). Below is a small code
that highlights some of the features of the AnalysisToolbox. For example
`initialize` simulataneously saves all screen output to the log file `HRG.log`
along with the git commit hash, so you can track down which version of the
AnalysisToolbox you used.

Here is `latqcdtools/examples/main_HRG_simple.py`

```Python
import numpy as np
import latqcdtools.base.logger as logger
from latqcdtools.physics.HRG import HRG
from latqcdtools.base.readWrite import readTable, writeTable
from latqcdtools.base.initialize import initialize, finalize

# Write terminal output to log file. Includes git commit hash.
initialize('HRG.log')

# Pick a temperature range in MeV
T = np.arange(100, 166, 1)

# Read in hadron names, masses, charges, baryon number, strangeness,
# charm, and degeneracy factor. This table is provided with AnalysisToolbox.
QMHRG_table = '../latqcdtools/physics/HRGtables/QM_hadron_list_ext_strange_2020.txt'
hadrons, M, Q, B, S, C, g = readTable(QMHRG_table, usecols=(0,1,2,3,4,5,6),
                                      dtype="U11,f8,i8,i8,i8,i8,i8")
w = np.array([1 if ba==0 else -1 for ba in B])

# Instantiate HRG object.
QMhrg = HRG(M,g,w,B,S,Q,C)

# This computation is vectorized since T is a numpy array.
logger.info('Computing chi2B.')
chi = QMhrg.gen_chi(T, B_order=2, Q_order=0, S_order=0, C_order=0,
                    muB_div_T=0.3, muQ_div_T=0, muS_div_T=0, muC_div_T=0)

# Output T and chi2B as columns in this table.
writeTable("chi2B.txt", T, chi, header=['T [MeV]','chi2B (QMHRG)'])

finalize()
```

In this case we work at fixed $\mu_B/T=0.3$
and compute $\chi_2^B$ as function of temperature. What is needed is as much
relevant input knowledge about hadron bound states as is known; this is
collected by `readTable`. This is a wrapper for `numpy.loadtxt()`, hence you
see you can pass it many of the same keyword arguments. The next line
for each species whether the gas is bosonic or fermionic.

Finally the `HRG` class is instantiated as `QMhrg`, which besides
generic conserved charge cumlants like the one computed with `gen_chi`,
contains many methods for various thermodynamic observables such as the
pressure and entropy.
The results are saved in a table `chi2B.txt`.

## Continuum-limit extrapolation

Suppose we want to perform a continuum-limit extrapolation to
determine the deconfinement transition temperature $T_d$ in pure SU(3). The order
parameter for this phase transition is given by the Polyakov loop, $P$. 
The transition is first-order in the
thermodynamic limit, where $\langle |P|\rangle$ as function of temperature
would jump discontinuously at $T_d$.
At finite volume, this abrupt jump becomes smooth, and $T_d$ is estimated by the
inflection point of the curve.

Here is `latqcdtools/examples/main_continuumExtrapolate.py`

```Python
import numpy as np
import latqcdtools.base.logger as logger
from latqcdtools.base.readWrite import readTable
from latqcdtools.base.printErrorBars import get_err_str
from latqcdtools.base.initialize import initialize, finalize
from latqcdtools.math.num_deriv import diff_deriv
from latqcdtools.math.spline import getSpline
from latqcdtools.statistics.statistics import gaudif
from latqcdtools.statistics.bootstr import bootstr_from_gauss
from latqcdtools.physics.continuumExtrap import continuumExtrapolate
from latqcdtools.physics.constants import r0_phys
from latqcdtools.physics.lattice_params import latticeParams

initialize('cont.log')

Nts         = [6,8,10,12,14,16,18,20]
Tds, Tderrs = [], []

for Nt in Nts:

    T  = []
    Ns = Nt*3

    # Read in Polyakov loop measurements, 
    beta, PM, PE = readTable('ploop/Nt'+str(Nt)+'.txt',usecols=(0,1,2))

    # Create array of temperatures in physical units
    for b in beta:
        lp = latticeParams(Ns, Nt, b, scaleType='r0') 
        T.append( lp.getT() )
    t = np.linspace(T[0],T[-1],1001)

    # Extract Td from inflection point of <|P|> vs T using natural spline
    def getTd(pm):
        spl  = getSpline(T, pm, natural=True)
        dPdT = diff_deriv(t, spl)
        maxIndex = np.argmax(dPdT)
        return t[maxIndex]

    # Error in Td estimate comes from 1000 Gaussian bootstrap samples
    Td, Tde = bootstr_from_gauss(getTd, PM, PE, 1000)
    Tds.append(Td)
    Tderrs.append(Tde)

# Perform O(a^4) continuum-limit extrapolation
result, result_err, chidof = continuumExtrapolate( Nts, Tds, Tderrs, order=2, xtype="Nt",
                                                   show_results=True, plot_results=True )

# Do a Z-test against literature result,  
r0 = r0_phys(year=2014, units="MeVinv")
Tdr0, Tdr0e = r0 * result[0], r0 * result_err[0]
Tdr0_lit, Tdr0_lite = 0.7457, 0.0045
logger.info('q(ours vs. lit) =',gaudif(Tdr0,Tdr0e,Tdr0_lit,Tdr0_lite))

finalize()
```

Above we show how such an extrapolation is achieved with
the AnalysisToolbox, along with error estimation, plotting the results, and
carrying out a statistical comparison with the known literature value.
We assume you already have results for $\langle |P|\rangle$ at various $N_\tau$, which we
read in from tables of the form `Nt6.txt`. 
For each $N_\tau$, this code estimates the inflection point of $\langle |P|\rangle$ as a function 
of $T$ by taking a [derivative](math/calculus.md) using a 
[spline](dataAnalysis/curveFitting.md) to get $T_d(N_\tau)$. 
Temperatures are calculated in MeV with the help of our
[class](physicsAnalysis/latticeParameters.md) that collects ensemble parameters. This 
procedure is wrapped in a user-defined function `getTc`, 
so that errors in the $\langle |P| \rangle$ data can be 
conveniently propagated into the error in $T_d(N_\tau)$
using a Gaussian [bootstrap](dataAnalysis/bootstrap.md). 

Having the `Nts`, `Tds`, and `Tderrs`, we are ready to perform a
continuum-limit extrapolation. This will perform an
extrapolation to second order in $a^2$, i.e. $\mathcal{O}(a^4)$, print the fit
results to screen, and create a plot of the extrapolation for you.
The arrays `result` and `result_err` contain the best fit parameters
along with their errors, with `result[0]` being the continuum value $T_d$.
In the last block we compare our result with $T_d r_0$ from the
[literature](https://journals.aps.org/prd/abstract/10.1103/PhysRevD.91.096002). 
The temperatures calculated in this code implicitly had units of
MeV, hence we need $r_0$ in [physical units](physicsAnalysis/referenceScales.md). 
Finally we call `gaudif` to carry out a Gaussian difference test or
Z-test, which is implemented in our [statistics](dataAnalysis/statistics.md) module.

