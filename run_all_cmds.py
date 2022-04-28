import os

#####################################
##    Semantic Aspects Selection   ##
#####################################
cmd1 = 'python3 SA_Selection/run_SAs_selection.py'
os.system(cmd1)

###########################################
##    Semantic Similarity Computation    ##
###########################################
cmd2 = 'python3 SS_Calculation/run_SS_calculation_SAs.py'
os.system(cmd2)

##########################################
##    Learning supervised similarity    ##
##########################################

cmd3 = 'python3 Regression/run_make_shuffle_partitions.py'
os.system(cmd3)

cmd4 = 'python3 Regression/run_withPartitions.py'
os.system(cmd4)

#####################
##    Baselines    ##
#####################

cmd5 = 'python3 Regression/run_baselines.py'
os.system(cmd5)