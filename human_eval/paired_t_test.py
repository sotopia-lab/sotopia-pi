from scipy.stats import ttest_rel, ttest_ind

# Sample data
data1 = [1, 2, 3, 4, 5]
data2 = [4, 3, 4, 6, 5]

# Perform the paired t-test
t_statistic, p_value = ttest_ind(data1, data2)
print(t_statistic, p_value)