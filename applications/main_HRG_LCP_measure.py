# 
# main_HRG_cs2.py
# 
# D. Clarke
#
# Do an HRG calculation of basic observables along a line of constant entropy.
#


import argparse
import numpy as np
from latqcdtools.physics.HRG import HRG, LCP_init_NS0
from latqcdtools.base.utilities import getArgs, find_nearest_idx
from scipy.interpolate import interp1d
from scipy.optimize import fsolve, newton_krylov
from latqcdtools.base.check import rel_check


parser = argparse.ArgumentParser(description='Script to calculate cs2 in HRG.',allow_abbrev=False)
parser.add_argument("--hadron_file", dest="hadron_file", required=True,help="Table with hadron properties.", type=lambda f: open(f))
parser.add_argument("--LCP_file", dest="LCP_file", required=True, help="muB, muQ, and muS chosen to fall along some line of constant physics", type=lambda f: open(f))
parser.add_argument("--snB", dest="snB", required=True, help="fix s/nB to this value", type=float)
parser.add_argument("--r", dest="r", default=0.4, help="r=nQ/nB (RHIC is 0.4, isospin symmetric is 0.5", type=float)


args = getArgs(parser)

showPlots  = False
target_snB = args.snB
LCP_file   = args.LCP_file
r          = args.r


T, muB, muQ, muS = np.loadtxt(args.LCP_file.name, unpack=True, usecols=(0, 1, 2, 3))
muC = 0.


hadrons,M,Q,B,S,C,g = np.loadtxt(args.hadron_file.name,unpack=True,usecols=(0,1,2,3,4,5,6),dtype="U11,f8,i8,i8,i8,i8,i8")
w  = np.array([1 if ba==0 else -1 for ba in B])

QMhrg      = HRG(M,g,w,B,S,Q,C)

s  = QMhrg.S_div_T3(T,mu_B=muB, mu_Q=muQ, mu_S=muS, mu_C=muC)
nB = QMhrg.gen_chi(T, B_order=1, Q_order=0, S_order=0, C_order=0, mu_B=muB, mu_Q=muQ, mu_S=muS, mu_C=muC)

x=muB
y=s/nB

guessIndex=find_nearest_idx(y,target_snB)

yinterp = interp1d(x, y, kind='cubic')
def func(z):
    return yinterp(z) - target_snB
target_muB = fsolve(func,x[guessIndex])[0]


def strangeness_neutral_equations(muQS,mu,t):
    x, y   = muQS
    X1B = QMhrg.gen_chi(t,B_order=1,mu_B=mu,mu_Q=x,mu_S=y)
    X1S = QMhrg.gen_chi(t,S_order=1,mu_B=mu,mu_Q=x,mu_S=y)
    X1Q = QMhrg.gen_chi(t,Q_order=1,mu_B=mu,mu_Q=x,mu_S=y)
    return X1S, X1Q - r*X1B


muQ, muS = LCP_init_NS0
solution = newton_krylov(lambda p: strangeness_neutral_equations(p,target_muB,T[0]), (muQ, muS))
muQ = solution[0]
muS = solution[1]


s  = QMhrg.S_div_T3(T[0],mu_B=target_muB, mu_Q=muQ, mu_S=muS, mu_C=muC)
nB = QMhrg.gen_chi(T[0], B_order=1, Q_order=0, S_order=0, C_order=0, mu_B=target_muB, mu_Q=muQ, mu_S=muS, mu_C=muC)


if not rel_check(target_snB,s/nB,1e-4):
    print("#Strayed from line of constant physics by",100*abs(target_snB-s/nB)/target_snB,"%")

pT4 = QMhrg.P_div_T4(T[0],mu_B=target_muB,mu_S=muS,mu_Q=muQ,mu_C=muC)
eT4 = QMhrg.E_div_T4(T[0],mu_B=target_muB,mu_S=muS,mu_Q=muQ,mu_C=muC)


print('  %.8e  %.8e  %.8e  %.8e'%(T[0],target_muB,pT4,eT4))