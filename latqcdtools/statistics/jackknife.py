#
# jackknife.py
#
# H. Sandmeyer, D. Clarke
#
# A parallelized jackknife routine that can handle arbitrary return values of functions.
#

import numpy as np
import math
from latqcdtools.statistics.statistics import std_mean, std_err, meanArgWrapper
import latqcdtools.base.logger as logger
from latqcdtools.base.speedify import DEFAULTTHREADS, parallel_function_eval


def pseudo(mean, mean_i, numb_blocks):
    """ Calculate pseudo values of elements of objects that are not tuple. """
    return numb_blocks * mean - (numb_blocks - 1) * mean_i


def pseudo_val(mean, mean_i, numb_blocks):
    if type(mean) is tuple:
        retvalue = ()
        for i in range(len(mean)):
            retvalue += (pseudo(np.array(mean[i]),
                         np.array(mean_i[i]), numb_blocks),)
        return retvalue
    else:
        return pseudo(np.array(mean), np.array(mean_i), numb_blocks)


class nimbleJack:
    """ Class allowing for parallelization of the jackknife function. """

    def __init__(self, func, data, nblocks, confAxis, return_sample, args, nproc):

        self._func = func
        self._data = np.array(data)
        self._nblocks = nblocks
        self._confAxis = confAxis
        self._return_sample = return_sample
        self._args = args
        self._nproc = nproc

        # If the measurements are accessed by the second index in data, we construct the jackknife  manually to allow
        # different size of sets of measurements. conf_axis==1 is the only case that allows different lengths of data
        # arrays per observable.
        if self._confAxis == 1:
            try:
                self._lengths = [len(self._data[i])
                                 for i in range(len(self._data))]
                self._blocksizes = [math.floor(
                    length / self._nblocks) for length in self._lengths]
                for length in self._lengths:
                    if length < self._nblocks:
                        raise IndexError("More blocks than datapoints!")
            except TypeError:  # if we get an 1D array
                self._confAxis = 0
                self._length = self._data.shape[self._confAxis]
                self._blocksize = math.floor(self._length / self._nblocks)
        else:
            self._length = self._data.shape[self._confAxis]
            self._blocksize = math.floor(self._length / self._nblocks)

        if self._confAxis == 1:
            self._numb_observe = len(self._data)
            used_data = [self._data[i][:self._nblocks * self._blocksizes[i]]
                         for i in range(self._numb_observe)]
            used_data = np.array(used_data)
        else:
            if self._length < self._nblocks:
                logger.TBError(
                    "More blocks than data. length, self._nblocks=", self._length, self._nblocks)
            rolled_data = np.rollaxis(self._data, self._confAxis)
            used_data = np.rollaxis(
                rolled_data[:self._blocksize*self._nblocks], 0, self._confAxis+1)

        # Get initial estimator of the mean
        if self._nblocks == 1:
            ndat = len(self._data)
            idx = np.arange(ndat)
            self._mean = np.mean(self.getJackknifeEstimator1d())
            self._error = np.sqrt(
                (ndat - 1) / ndat * sum((self._func(self._data[idx != i]) - self._mean)**2 for i in range(ndat)))
        else :     
            self._mean = meanArgWrapper(func, used_data, args)
            self._blockval = parallel_function_eval(
                self.getJackknifeEstimator, range(self._nblocks), nproc=self._nproc)
            self._mean = std_mean(self._blockval)
            self._error = std_err(self._blockval)

    def __repr__(self) -> str:
            return "jackknife"

    def getJackknifeEstimator1d(self):
        ndat = len(self._data)
        idx = np.arange(ndat)
        sample = np.array([self._func(self._data[idx != i])
                              for i in range(ndat)])
        return sample

    def getResults1d(self):
        ndat = len(self._data)
        jsamp = self._get_jackknife_estimator_1d()
        jackmean = np.mean(jsamp)
        jackstd = np.sqrt((ndat - 1) * np.sum((jsamp - jackmean)**2))
        return jackmean, jackstd

        
    def getJackknifeEstimator(self, i):
        """ Gets the ith jackknife estimator from throwing away jackknife block i. """
        block_data = []
        if self._confAxis == 1:
            for k in range(self._numb_observe):
                block_data.append(self._data[k][0:i * self._blocksizes[k]])
                block_data[k] = np.concatenate((block_data[k], self._data[k][(i + 1) * self._blocksizes[k]:self._nblocks * self._blocksizes[k]]))
        else:
            # The Jackknife blocks are constructed by rolling the conf axis to the first index. Then the jackknife
            # blocks are built. Aferwards the we roll back
            rolled_data = np.rollaxis(self._data, self._confAxis)
            for j in range(i * self._blocksize):
                block_data.append(rolled_data[j])
            for j in range((i + 1) * self._blocksize, self._nblocks * self._blocksize):
                block_data.append(rolled_data[j])
            block_data = np.rollaxis(
                np.array(block_data), 0, self._confAxis + 1)
        block_data = np.array(block_data)
        mean_i = meanArgWrapper(self._func, block_data, self._args)
        return pseudo_val(self._mean, mean_i, self._nblocks)

    def getResults(self):
        if self._return_sample:
            return self._blockval, self._mean, self._error
        else:
            return self._mean, self._error


def jackknife(func, data, numb_blocks=20, conf_axis=1, return_sample=False, args=(), nproc=DEFAULTTHREADS):
    """Jackknife routine for arbitray functions. This routine creates the jackknife like blocked subsets of data and
    passes them to the function in the same format as in the input data. So the idea is to write a function that
    computes an observable from a given data set. This function can be put into this jackkife routine and will get the
    jackknifed blocked data as input. Based on the output of the function, the jackkife mean and error are computed.
    The function may return multiple observables that are either scalars or numpy objects. You can pass a
    multidimensional object as data, but the jackknife function has to know from which axis blocks should be removed.
    This is controlled by conf_axis (default = 0 for one dimensional arrays and default = 1 for higher order arrays).
    Look into the __init__ function of the nimbleJack class to see in detail how this is implemented.

        Parameters
        ----------
        func : callable
            The function that calculates the observable

        data : array_like
            Input data

        numb_blocks : integer
            Number of jackknife blocks

        conf_axis : integer, optional, default = 0 for dim(data) = 1 and default = 1 for dim(data) >= 2
            Axis that should be resampled

        return_sample : boolean, optional, default = False                                           
            Along with the mean and the error also return the results from the individual samples

        args : array_like or dict, default = ()
            optional arguments to be passed to func. If a dictionary they are passed as **args.

        nproc : integer
            Number of threads to use if you choose to parallelize. nproc=1 turns off parallelization.
    """
    jk = nimbleJack(func, data, numb_blocks, conf_axis,
                    return_sample, args, nproc)
    return jk.getResults()
