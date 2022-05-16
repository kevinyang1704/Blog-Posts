"""
Title:  Support Figures
Author: Matteo Courthoud
Date:   24/03/2022
"""

import numpy as np
import scipy as sp
import pandas as pd
from scipy.stats import norm
import statsmodels.api as sm
import statsmodels.formula.api as smf

import gif
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns


def plot_test(mu0=0, mu1=3, sigma=1, alpha=0.05, n=100):
    """Plot statistical hypothesis test"""
    s = np.sqrt(sigma**2 / n)
    x = np.linspace(mu0 - 4*s, mu1 + 4*s, 1000)
    pdf1 = norm(mu0, s).pdf(x)
    pdf2 = norm(mu1, s).pdf(x)
    cv = mu0 + norm.ppf(1 - alpha) * s
    power = norm.cdf(np.abs(mu1 - cv) / s)

    # Plot Distributions
    plt.plot(x, pdf1, label=f'Distribution under H0: μ={mu0}');
    plt.plot(x, pdf2, label=f'Distribution under H1: μ={mu1}');

    # Plot areas
    plt.fill_between(x[x>=cv], pdf1[x>=cv], color='r', alpha=0.4, label=f'Significance: α={alpha:.2f}')
    plt.fill_between(x[x<=cv], pdf2[x<=cv], color='g', alpha=0.4, label=f'β={1-power:.2f}')

    # Vertical lines
    plt.vlines(cv, ymin=0, ymax=plt.ylim()[1], color='k', label=f'Critical Value: {cv:.2f}')
    plt.vlines(mu0, ymin=0, ymax=max(pdf1), color='k', lw=1, ls='--', label=None)
    plt.vlines(mu1, ymin=0, ymax=max(pdf2), color='k', lw=1, ls='--', label=None)

    # Other
    plt.legend(bbox_to_anchor=(1.04,0.5), loc="center left");
    plt.title("Hypothesis Testing");


def make_cmap(color1, color2, K):
    C1 = np.array(mpl.colors.to_rgb(color1))
    C2 = np.array(mpl.colors.to_rgb(color2))
    return [(K-1-k)/(K-1) * C1 + k/(K-1) * C2  for k in range(K)]


@gif.frame
def dynamic_plot(k, K, A, B, x, y, e, cmap, xname, yname):
    
    k_ = min(max(k, 0), K-1)
    y_hat_ = A[k_] + B[k_] * x
    y_ = y_hat_ + e
    
    # Initialize figure
    fig = plt.figure()
    gs = fig.add_gridspec(1, 3, hspace=0, wspace=0, width_ratios=[1,5,1])
    (ax1, ax2, ax3) = gs.subplots(sharey='row')

    # First plot
    ax1.scatter(x*0, y)
    ax1.get_xaxis().set_visible(False)
    ax1.set_ylabel(yname)

    # Second plot
    ax2.scatter(x, y_, color=cmap[k_]);
    ax2.plot(x, y_hat_, c='r');
    ax2.vlines(x, np.minimum(y_, y_hat_), np.maximum(y_, y_hat_), linestyle='--', color='k', alpha=0.5, linewidth=1);
    ax2.set_xlabel(xname)
    ax2.set_title(f"Orthogonal projection of {yname} on {xname}")

    # Third plot
    ax3.scatter(x*0, e, c='g');
    ax3.get_xaxis().set_visible(False);
    sd = np.std(y)*0.3
    ax3.set_ylim(min(min(e), min(y)) - sd, max(max(e), max(y)) + sd);
    

def gif_projection(x, y, df, gifname, K=50):
    
    # Fit model
    X = df[x].values
    Y = df[y].values
    model = sm.OLS(Y, sm.add_constant(X)).fit()
    a,b = model.params
    e = model.resid
    
    # Setup
    A = np.linspace(a, 0, K)
    B = np.linspace(b, 0, K)
    cmap = make_cmap('b', 'g', K)
    
    # Make frames
    frames = []
    for k in range(-20, K+20):
        frames.append(dynamic_plot(k, K, A, B, X, Y, e, cmap, x, y))
        
    # Gif from frames
    gif.save(frames, gifname, duration=3, unit="s", between="startend")