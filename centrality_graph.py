#configs
# set some nicer defaults for matplotlib
from matplotlib import rcParams
import matplotlib.pyplot as plt
import numpy as np

#these colors come from colorbrewer2.org. Each is an RGB triplet
dark2_colors = [(0.10588235294117647, 0.6196078431372549, 0.4666666666666667),
                (0.8509803921568627, 0.37254901960784315, 0.00784313725490196),
                (0.4588235294117647, 0.4392156862745098, 0.7019607843137254),
                (0.9058823529411765, 0.1607843137254902, 0.5411764705882353),
                (0.4, 0.6509803921568628, 0.11764705882352941),
                (0.9019607843137255, 0.6705882352941176, 0.00784313725490196),
                (0.6509803921568628, 0.4627450980392157, 0.11372549019607843),
                (0.4, 0.4, 0.4)]

rcParams['figure.figsize'] = (10, 6)
rcParams['figure.dpi'] = 150
rcParams['axes.color_cycle'] = dark2_colors
rcParams['lines.linewidth'] = 2
rcParams['axes.grid'] = False
rcParams['axes.facecolor'] = 'white'
rcParams['font.size'] = 14
rcParams['patch.edgecolor'] = 'none'

def remove_border(axes=None, top=False, right=False, left=True, bottom=True):
    """
    Minimize chartjunk by stripping out unnecessary plot borders and axis ticks
    
    The top/right/left/bottom keywords toggle whether the corresponding plot border is drawn
    """
    ax = axes or plt.gca()
    ax.spines['top'].set_visible(top)
    ax.spines['right'].set_visible(right)
    ax.spines['left'].set_visible(left)
    ax.spines['bottom'].set_visible(bottom)
    
    #turn off all ticks
    ax.yaxis.set_ticks_position('none')
    ax.xaxis.set_ticks_position('none')
    
    #now re-enable visibles
    if top:
        ax.xaxis.tick_top()
    if bottom:
        ax.xaxis.tick_bottom()
    if left:
        ax.yaxis.tick_left()
    if right:
        ax.yaxis.tick_right()

centralities = [{'majority_size': 56, 'dems': 173.65830168949006, 'mean:': 171.60061115807699, 'gop': 169.03992960787392}, {'majority_size': 54, 'dems': 290.60582517917737, 'mean:': 295.696052187725, 'gop': 300.12643495442393}, {'majority_size': 55, 'dems': 167.45103589882862, 'mean:': 169.84287199009148, 'gop': 171.84331672096599}, {'majority_size': 55, 'dems': 186.5895926031653, 'mean:': 193.25792749709882, 'gop': 198.58012500551575}, {'majority_size': 61, 'dems': 112.0988790342671, 'mean:': 107.50918299217808, 'gop': 100.29504256306438}, {'majority_size': 56, 'dems': 87.574454603674425, 'mean:': 84.685387516493222, 'gop': 80.9201835700744}]


years = np.array([1990, 1995, 2000, 2005, 2010, 2013])

plt.figure(figsize=(5,5))
plt.plot(years, [x['dems'] for x in centralities], 'bo', years, [x['gop'] for x in centralities], 'ro', years, [x['mean:'] for x in centralities], 'k--')
##plt.plot(years, [x['dems'] for x in centralities], 'r--')
plt.axis([1989.5, 2013.5, 0, 350])
remove_border(left=False, bottom=False)
plt.title('Senate Centrality Over Time')
plt.show()
