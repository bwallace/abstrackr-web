
import desolver
import numpy

class MySolver(desolver.DESolver):
    def error_func(self, indiv, *args):
	print indiv
	print type(indiv)
        # inverse exponential with offset, y = a * exp(b/x) + c
        predicted = indiv[0] * numpy.exp(indiv[1] / args[0]) + indiv[2]

        # sum of squared error
        error = predicted - args[1]
        return numpy.sum(error*error)


class TestDesolver():
    def setUp(self):
        self.xData = numpy.array([5.357, 9.861, 5.457, 5.936, 6.161, 6.731])
        self.yData = numpy.array([0.376, 7.104, 0.489, 1.049, 1.327, 2.077])

    def test_basic(self):

        #solver = desolver.DESolver([(-100,100)]*3, 30, 600,
        solver = MySolver([(-100,100)]*3, 30, 600,
                          method = desolver.DE_RAND_1,
                          args=[self.xData,self.yData], scale=0.8, crossover_prob=0.9,
                          goal_error=.01, polish=False, verbose=False,
                          use_pp = False, pp_modules=['numpy'])

        assert(solver.best_error <= .01)
