'''
	Byron C Wallace
	Tufts Medical Center: Computational and Analytic Evidence Sythensis 
	tuftscaes.org/curious_snake
	Curious Snake: Active Learning in Python
	results_reporter.py
	---
	
	This module is for aggregating and reporting the output of experimental runs. It uses pylab
	to generate the standard 'learning curves' for each of the learners.
'''

import os
import pdb
try:
    import matplotlib.pyplot as plt
    import pylab
except:
    print '''whoops, results_reporter module can't load pylab library. you can still run your experiments -- 
                data will be written out to files -- but I can't plot your results. '''
    
def post_runs_report(base_path, learner_labels, n, metrics = ["num_labels", "accuracy", "sensitivity", "specificity"]):    
    '''
    Call this method when the analysis finishes. It:
        1) Averages the n runs
        2) Plots the results for each metric in metric and saves these to the 
        base_path directory. Note: Requires pylab! 
    '''        
    print "averaging results..."
    averages = avg_results(base_path, learner_labels, n, metrics) 
    print "done."
    
    # note that we skip the number of labels
    for metric in metrics[1:]:
        plot_metric_for_learners(averages, metric, output_path = os.path.join(base_path, metric) + ".pdf")
    
    print "plots generated"
    
    
def report_yield_burdens(base_path, learner_labels,  n):
    metrics = ["num_labels", "yield", "burden"]
    averages, all_runs =  avg_results(base_path, learner_labels, n, metrics) 
    x_labels = averages[averages.keys()[0]]['num_labels'] 
    num_steps = len(averages[learner_labels[0]]["yield"])
    for learner in averages.keys():
        print learner
        plot_yield_burden_curves(learner, x_labels,  num_steps, all_runs,  averages, base_path)    
        
        
def plot_metric_for_learners(results, metric, legend_loc = "lower right", x_key = "num_labels", 
                            output_path = None, show_plot = True):
    '''
    Uses pylab to generate a learning plot (number of labels v. metric of interest) for each of the learners.
    '''
    learner_names = results.keys()
    learner_names.sort()
    
    # we build a list of the lines plotted (the plot routine returns a line)
    # we need these for the legend.
    lines = []
    # clear the canvass
    pylab.clf()
    
    for learner in learner_names:
        lines.append(pylab.plot(results[learner]["num_labels"], results[learner][metric], 'o-'))
    
    pylab.legend(lines, learner_names, legend_loc, shadow = True)
    pylab.xlabel("Number of Labels")
    pylab.ylabel(metric)
    
    # if an output path was passed in, save the plot to it
    if output_path is not None:
        pylab.savefig(output_path, format="pdf")
    
    if show_plot:
        pylab.show()
    

  
def plot_yield_burden_curves(learner, x_labels, num_steps, all_runs, yields_and_burdens, out_dir):
    pylab.clf()
    total_N = max(x_labels)
    plot_em_all_for_learner(all_runs[learner], total_N, x_labels, num_steps, color="b")
    
    #
    # Now plot the averages
    # 
    plt.plot(x_labels, yields_and_burdens[learner]["yield"], linewidth=2.0, color="b")
    plt.axis([0, total_N, -.05, 1.05])
    plt.ylabel("Yield", {'color' : 'b'})
    
    
    ax_left = pylab.subplot(111)
    ax_right = pylab.twinx()
    plot_em_all_for_learner(all_runs[learner], total_N, x_labels, num_steps, color="r", metric="burden")
    plt.plot(x_labels, yields_and_burdens[learner]["burden"], linewidth=2.0, color="r")
    plt.ylabel("Burden", {'color' : 'r'})
    
    plt.axis([0, total_N, -.05, 1.05])
    pylab.savefig(os.path.join(out_dir, "%s.pdf" % learner), format="pdf")
    
    
   
def plot_em_all_for_learner(runs_for_learner, total_N, xs, num_steps, metric = "yield", color="r", 
                                            name=None, average=None, clear_after=False):
    print total_N
    for run in runs_for_learner:
        plt.plot(xs, run[metric], color=color, alpha=0.3)

    plt.axis([0, total_N, 0, 1.05])
    plt.xlabel("Number of Labels")
    plt.ylabel("Yield" if metric=="yield" else "Burden")
    

def plot_metric_for_learners(results, metric, legend_loc = "lower right", x_key = "num_labels", output_path = None,
                                            show_plot = False, line_styles = ['_', '-'], linewidths = [1.5, 1.5], markers = ['+' , 'o'], colors = ["r", "b"]):
    learner_names = results.keys()
    learner_names.sort()
    pretty_learner_names = ["SIMPLE", "PAL (agg.)"]
    # we build a list of the lines plotted (the plot routine returns a line)
    # we need these for the legend.
    lines = []
    # clear the canvass
    pylab.clf()

    
    for i, learner in enumerate(learner_names):
        #lines.append(pylab.plot(results[learner]["num_labels"], results[learner][metric], linewidth=linewidths[i], color=colors[i]))
        lines.append(plt.plot(results[learner]["num_labels"], results[learner][metric], linewidth=linewidths[i], color=colors[i]))
    plt.axis([0, 4751, 0, 1.05])
    plt.xlabel("Number of Labels")
    plt.ylabel("Yield" if metric=="yields" else "Burden")
    pylab.legend(lines, pretty_learner_names, legend_loc, shadow = False)
    
    # if an output path was passed in, save the plot to it
    if output_path is not None:
        pylab.savefig(output_path, format="pdf")
    
    if show_plot:
        pylab.show()
                   
def average(x):
    return float(sum(x)) / float(len(x))

def _parse_results_file(fpath, has_header=False):
    return_mat = []
    offset = 1 if has_header else 0
    for l in open(fpath, 'r').readlines()[offset:]:
        return_mat.append([eval(s) for s in l.replace("\n", "").split(",")])
    return return_mat
    
def avg_results(base_path, learner_names, n, metrics=["tps", "tns", "fps", "fns", "size", "accuracy", "sensitivity", "specificity", "U19"], size_index=0,\
                    has_header=False, ext=".txt"):
    '''
    This method aggregates the results from the files output during the active learing simulation, building
    averaged time curves for each of the metrics and returning these in a dictionary.
    
 
    n -- number of runs, i.e., number of files   
    '''
    averaged_results_for_learners = {}
    all_runs_for_learners = {}
    headers= None
    for learner in learner_names:
        running_totals, sizes, num_steps = None, None, None
        all_runs = []
        for run in range(n):
            cur_learner_file = os.path.join(base_path, learner + "_" + str(run) + "%s"%ext)
            if headers is None and has_header:
                headers = open(cur_learner_file).readline().split(",")
                metrics = headers
                print "using headers for metrics: %s" % metrics
            else:
                headers = metrics
            print cur_learner_file
            cur_run_results = _parse_results_file(cur_learner_file, has_header=has_header)
            if running_totals is None:
                # on the first pass through, we build an initial zero matrix to store our averages. we do this
                # here because we know how many steps there were (the length, or number of rows, of the first 
                #`cur_run_results' file)
                num_steps = len(cur_run_results)
                running_totals = []
                for step_i in range(num_steps):
                    running_totals.append([0.0 for metric in range(len(metrics))])
                sizes = [0.0 for step_i in range(num_steps)]

            # also keep track of individual runs for each metric
            cur_run_metrics = []
            for metric in range(len(metrics)):
                cur_run_metrics.append([])
                
            
            for step_index in range(num_steps):
                for metric_index in range(len(metrics)):
                    running_totals[step_index][metric_index] += float(cur_run_results[step_index][metric_index])
                    cur_run_metrics[metric_index].append(cur_run_results[step_index][metric_index])
                if run == 0:
                    # set the sizes on the first pass through (these will be the same for each run)
                    sizes[step_index] = float(cur_run_results[step_index][size_index])
            all_runs.append(dict(zip(metrics, cur_run_metrics)))
        
        
        averages = []
        for metric_i in range(len(metrics)):
            cur_metric_avg = []
            for step_i in range(num_steps):
                cur_metric_avg.append(running_totals[step_i][metric_i] / float(n))
            averages.append(cur_metric_avg)

        averaged_results_for_learners[learner] = dict(zip(metrics, averages))
        all_runs_for_learners[learner] = all_runs
    return (averaged_results_for_learners, all_runs_for_learners)
    