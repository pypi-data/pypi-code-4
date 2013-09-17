"""
Wrapper all tasks to the same module
"""

from .mad import task_mad
from .tau import task_tau
from .pearson import task_pearson
from .effect_size import task_cohen
from .ttest import task_paired_t
from .mannwhitney import task_mannwhitneyu
from .friedman import task_friedman
from .kappa import task_cohen_kappa
