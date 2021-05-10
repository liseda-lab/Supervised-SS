from scipy.stats import pearsonr

#####################
##    Functions    ##
#####################

def performance_baselines(list_SS, list_proxy, aspects):
    """
    Compute the correlation for the static baselines.
    :param list_SS: list of lists. Each list represents an entity pair and its elements are the static similarity values (one for each static baseline);
    :param list_proxy: list of proxy values for each entity pair of datasets;
    :param aspects: list of static baselines;
    :return: list of pearson correlation coefficient values for each static baseline.
    """
    corrs_baselines = []
    for i in range(len(aspects)):
        SS_baseline = [SS[i] for SS in list_SS]
        corr = pearsonr(SS_baseline, list_proxy)[0]
        corrs_baselines.append(corr)
    return corrs_baselines
