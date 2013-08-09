import desolver
import numpy
import curious_snake

def n_at_least_alpha(preds, n, alphas) :
    bool_to_sign = lambda x: 1.0 if x else -1.0
    count = 0
    for i, x_i in enumerate(preds):
        if x_i >= alphas[i]:
            count+=1
    return bool_to_sign(count >= n)
        
class WeightSolver(desolver.DESolver):

    
    def error_func(self, indiv, *args):
        P = args[0]
        beta = args[1]
        n = args[2]
        y = args[3]
        #P_hat = numpy.dot(P, indiv)
        #sign = lambda x: 1.0 if x>0.0 else -1.0
        
        y_hat = [n_at_least_alpha(y_i, n, indiv) for y_i in P]
        
        conf_mat = curious_snake._evaluate_predictions(y_hat, y)
        results = {}
        curious_snake._calculate_metrics(conf_mat, results, verbose=False)
        metric_score = beta * results["sensitivity"] + results["specificity"]
        return 1/metric_score
        

        
    def error_func1(self, indiv, *args):
        P = args[0]
        beta = args[1]
        y = args[2]
        P_hat = numpy.dot(P, indiv)
        sign = lambda x: 1.0 if x>0.0 else -1.0
        y_hat = [sign(y_i) for y_i in P_hat]
        
        conf_mat = curious_snake._evaluate_predictions(y_hat, y)
        results = {}
        curious_snake._calculate_metrics(conf_mat, results, verbose=False)
        metric_score = beta * results["sensitivity"] + results["specificity"]
        return 1/metric_score 