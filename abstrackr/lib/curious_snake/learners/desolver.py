#
#
#

import numpy
import scipy.optimize
import sys

# http;//www.parallelpython.com -
# can be single CPU, multi-core SMP, or cluster parallelization
try:
    import pp
    HAS_PP = True
except ImportError:
    HAS_PP = False
    
# # Import Psyco if available
# try:
#     import psyco
#     psyco.full()
# except ImportError:
#     pass #print "psyco not loaded"

# set up the enumerated DE method types
DE_RAND_1 = 0
DE_BEST_1 = 1
DE_BEST_2 = 2
DE_BEST_1_JITTER = 3
DE_LOCAL_TO_BEST_1 = 4

# Functions to set up and control remote worker
def _update_solver(in_solver):
    global solver
    solver = in_solver
    
def _call_error_func(ind):
    global solver
    error = solver.error_func(solver.population[ind,:],*(solver.args))
    return error


class DESolver(object):
    """
    Genetic minimization based on Differential Evolution.
    """

    def __init__(self, param_ranges, population_size, max_generations,
                 method = DE_RAND_1, args=None,
                 scale=0.8, crossover_prob=0.9,
                 goal_error=1e-3, polish=True, verbose=True,
                 use_pp=True, pp_depfuncs=None, pp_modules=None):
        """
        """
        # set the internal vars
        self.param_ranges = param_ranges
        self.num_params = len(self.param_ranges)
        self.population_size = population_size
        self.max_generations = max_generations
        self.method = method
        #self.func = func
        # prepend self to the args
        if args is None:
            args = ()
        self.args = args
        self.scale = scale
        self.crossover_prob = crossover_prob
        self.goal_error = goal_error
        self.polish = polish
        self.verbose = verbose

        # set helper vars
        self.rot_ind = numpy.arange(self.population_size)

        # set status vars
        self.generation = 0

        # set up the population
        # eventually we can allow for unbounded min/max values with None
        self.population = numpy.hstack([numpy.random.uniform(p[0],p[1],
                                                size=[self.population_size,1])
                              for p in param_ranges])
        self.population_errors = numpy.empty(self.population_size)

        # check for pp
        if use_pp and not HAS_PP:
            print "WARNING: PP was not found on your system, so no "\
                  "parallelization will be performed."
            use_pp = False

        if use_pp:
            # auto-detects number of SMP CPU cores (will detect 1 core on
            # single-CPU systems)
            job_server = pp.Server()

            if self.verbose:
                print "Setting up %d pp_cpus" % (job_server.get_ncpus())

            # set up lists of depfuncs and modules
            depfuncs = []
            if not pp_depfuncs is None:
                depfuncs.extend(pp_depfuncs)
            depfuncs = tuple(depfuncs)
            modules = ['desolver']
            if not pp_modules is None:
                modules.extend(pp_modules)
            modules = tuple(modules)

            # give each worker a copy of this object and the required
            # depfuncs and modules
            for i in range(job_server.get_ncpus()):
                job_server.submit(_update_solver,
                                  args=(self,), depfuncs=depfuncs,
                                  modules=modules)
            job_server.wait()

        else:
            job_server = None

        # the rest is now in a try block
        
        # try/finally block is to ensure remote worker processes are
        # killed if they were started
        try:
            # eval the initial population
            self._eval_population(job_server)

            # set the index of the best individual
            best_ind = self.population_errors.argmin()
            self.best_error = self.population_errors[best_ind]
            self.best_individual = numpy.copy(self.population[best_ind,:])
            self.best_generation = self.generation

            if self.verbose:
                print "Best generation: %g" % (self.best_generation)
                print "Best Error: %g" % (self.best_error)
                print "Best Indiv: " + str(self.best_individual)
                print
            
            # now solve
            self._solve(job_server)
        finally:
            # destroy the server if it was started
            if use_pp:
                job_server.destroy()


    def _eval_population(self, job_server=None):
        """
        Evals the provided population, returning the errors from the
        function.
        """
        # see if use job_server
        if self.verbose:
            print "Generation: %d (%d)" % (self.generation,self.max_generations)
            sys.stdout.write('Evaluating population (%d): ' % (self.population_size))
        if not job_server:
            # eval the function for the initial population
            for i in xrange(self.population_size):
                if self.verbose:
                    sys.stdout.write('%d ' % (i))
                    sys.stdout.flush()
                #self.population_errors[i] = self.func(self.population[i,:],*(self.args))
                self.population_errors[i] = self.error_func(self.population[i,:],*(self.args))
        else:
            # update the workers
            for i in range(job_server.get_ncpus()):
                job_server.submit(_update_solver, (self,), (), ())
            job_server.wait()

            # submit the functions to the job server
            jobs = []
            for i in xrange(self.population_size):
                jobs.append(job_server.submit(_call_error_func, (i,), (), ()))
            for i,job in enumerate(jobs):
                if self.verbose:
                    sys.stdout.write('%d ' % (i))
                    sys.stdout.flush()
                error = job()
                self.population_errors[i] = error
                #self.population_errors[i] = job()

        if self.verbose:
            sys.stdout.write('\n')
            sys.stdout.flush()

    def error_func(self, indiv, *args):
        raise NotImplementedError 

    def _evolve_population(self):
        """
        Evolove to new generation of population.
        """
        # save the old population
        self.old_population = self.population.copy()
        self.old_population_errors = self.population_errors.copy()

        # index pointers
        rind = numpy.random.permutation(4)+1

        # shuffle the locations of the individuals
        ind1 = numpy.random.permutation(self.population_size)
        pop1 = self.old_population[ind1,:]
        
        # rotate for remaining indices
        rot = numpy.remainder(self.rot_ind + rind[0], self.population_size)
        ind2 = ind1[rot,:]
        pop2 = self.old_population[ind2,:]

        rot = numpy.remainder(self.rot_ind + rind[1], self.population_size)
        ind3 = ind2[rot,:]
        pop3 = self.old_population[ind3,:]

        rot = numpy.remainder(self.rot_ind + rind[2], self.population_size)
        ind4 = ind3[rot,:]
        pop4 = self.old_population[ind4,:]

        rot = numpy.remainder(self.rot_ind + rind[3], self.population_size)
        ind5 = ind4[rot,:]
        pop5 = self.old_population[ind5,:]
        
        # population filled with best individual
        best_population = self.best_individual[numpy.newaxis,:].repeat(self.population_size,axis=0)

        # figure out the crossover ind
        xold_ind = numpy.random.rand(self.population_size,self.num_params) >= \
            self.crossover_prob

        # get new population based on desired strategy
        # DE/rand/1
        if self.method == DE_RAND_1:
            population = pop3 + self.scale*(pop1 - pop2)
            population_orig = pop3
        # DE/BEST/1
        if self.method == DE_BEST_1:
            population = best_population + self.scale*(pop1 - pop2)
            population_orig = best_population
        # DE/best/2
        elif self.method == DE_BEST_2:
            population = best_population + self.scale * \
                         (pop1 + pop2 - pop3 - pop4)
            population_orig = best_population
        # DE/BEST/1/JITTER
        elif self.method == DE_BEST_1_JITTER:
            population = best_population + (pop1 - pop2) * \
                         ((1.0-0.9999) * \
                          numpy.random.rand(self.population_size,self.num_params) + \
                          self.scale)
            population_orig = best_population
        # DE/LOCAL_TO_BEST/1
        elif self.method == DE_LOCAL_TO_BEST_1:
            population = self.old_population + \
                         self.scale*(best_population - self.old_population) + \
                         self.scale*(pop1 - pop2)
            population_orig = self.old_population
            
        # crossover
        population[xold_ind] = self.old_population[xold_ind]

        # apply the boundary constraints
        for p in xrange(self.num_params):
            # get min and max
            min_val = self.param_ranges[p][0]
            max_val = self.param_ranges[p][1]

            # find where exceeded max
            ind = population[:,p] > max_val
            if ind.sum() > 0:
                # bounce back
                population[ind,p] = max_val + \
                                    numpy.random.rand(ind.sum())*\
                                    (population_orig[ind,p]-max_val)

            # find where below min
            ind = population[:,p] < min_val
            if ind.sum() > 0:
                # bounce back
                population[ind,p] = min_val + \
                                    numpy.random.rand(ind.sum())*\
                                    (population_orig[ind,p]-min_val)

        # set the class members
        self.population = population
        self.population_orig = population

    
    def _solve(self, job_server=None):
        """
        Optimize the parameters of the function.
        """

        # loop over generations
        for g in xrange(1,self.max_generations):
            # set the generation
            self.generation = g

            # update the population
            self._evolve_population()
            
            # evaluate the population
            self._eval_population(job_server)

            # decide what stays
            ind = self.population_errors > self.old_population_errors
            self.population[ind,:] = self.old_population[ind,:]
            self.population_errors[ind] = self.old_population_errors[ind]

            # set the index of the best individual
            best_ind = self.population_errors.argmin()

            # update what is best
            if self.population_errors[best_ind] < self.best_error:
                self.best_error = self.population_errors[best_ind]
                self.best_individual = numpy.copy(self.population[best_ind,:])
                self.best_generation = self.generation

            if self.verbose:
                print "Best generation: %g" % (self.best_generation)
                print "Best Error: %g" % (self.best_error)
                print "Best Indiv: " + str(self.best_individual)
                print
            
            # see if done
            if self.best_error < self.goal_error:
                break

        # see if polish with fmin search after the first generation
        if self.polish:
            if self.verbose:
                print "Polishing best result: %g" % (self.population_errors[best_ind])
                iprint = 1
            else:
                iprint = -1
            # polish with bounded min search
            polished_individual, polished_error, details = \
                                 scipy.optimize.fmin_l_bfgs_b(self.error_func,
                                                              self.population[best_ind,:],
                                                              args=self.args,
                                                              bounds=self.param_ranges,
                                                              approx_grad=True,
                                                              iprint=iprint)
            if self.verbose:
                print "Polished Result: %g" % (polished_error)
                print "Polished Indiv: " + str(polished_individual)
            if polished_error < self.population_errors[best_ind]:
                # it's better, so keep it
                self.population[best_ind,:] = polished_individual
                self.population_errors[best_ind] = polished_error

                # update what is best
                self.best_error = self.population_errors[best_ind]
                self.best_individual = numpy.copy(self.population[best_ind,:])
                

        if job_server:
            self.pp_stats = job_server.get_stats()
