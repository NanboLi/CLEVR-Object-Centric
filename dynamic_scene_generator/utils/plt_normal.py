import numpy as np

from matplotlib import pyplot as plt


def plot_normal(mu, sigma, color, label, fig=None):
    """Function to plot a Gaussian of given mean and stddev
    
    Args:
        mu: scalar mean
        sigma: scalar standard deviation
        color: matplotlib recognized color
        label: string for legend label
    Returns:
        plots an 8 stddev wide Gaussian
    """
    normcurv = lambda x: np.exp(-0.5*((x - mu)/sigma)**2) / (np.sqrt(2.*np.pi) * sigma)
    xPlot = np.linspace(mu - 4*sigma, mu + 4*sigma, num=int(8.*sigma/0.01));
    yPlot = normcurv(xPlot);
    
    if fig is None:
        plt.plot(xPlot, yPlot, color, label=label)
    else:
        fig.plot(xPlot, yPlot, color, label=label)