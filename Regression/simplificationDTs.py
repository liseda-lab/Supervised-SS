import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeRegressor, export_text, _tree


#####################
##    Functions    ##
#####################

def simplify_rule(rule, feature_names):
    """
    Simplify a rule.
    :param rule: string representing a decision rule;
    :param feature_names: list of feature names;
    :return: string representing the simplified rule.
    """
    conditions, prediction = rule.split(': prediction =')
    dic_conditions = {}
    
    for feature in feature_names:
        dic_conditions[feature] = []

    conditions = conditions[1:-1].split(') and (')
    for condition in conditions :
        for feature in feature_names:
            if feature in condition:
                dic_conditions[feature].append(condition)

    new_rule = 'if '
    for feature in dic_conditions:
        conditions = dic_conditions[feature]
        if len(conditions) != 0:
            conditions = dic_conditions[feature]
            big = []
            less = []
            for cond in conditions:
                if '<=' in cond:
                    less.append(float(cond.split('<= ')[1]))
                if '>' in cond:
                    big.append(float(cond.split('> ')[1]))

            if len(big)!=0 and len(less)!=0:
                new_rule = new_rule + '(' + str(max(big)) + ' < ' + feature + ' <= '  +  str(min(less)) +  ') and ' 
            else:
                if len(big) != 0 and len(less) == 0:
                    new_rule = new_rule + '(' + feature + ' > ' + str(max(big)) + ') and '
                
                if len(big) == 0 and len(less) != 0:
                    new_rule = new_rule + '(' + feature + ' <= ' + str(min(less)) + ') and '

    new_rule = new_rule[:-5] + ': prediction =' + prediction
    return new_rule



def tree_to_code(tree, feature_names):
    """
    Transform a decision tree into a set of rules.
    :param tree: tree;
    :param feature_names: list of feature names;
    :return: list of simplified rules;
    """
    tree_ = tree.tree_
    feature_name = [
        feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
        for i in tree_.feature
    ]
    pathto=dict()

    global k
    global rules

    rules = []
    k = 0
    def recurse(node, depth, parent):
        global k
        indent = "  " * depth

        if tree_.feature[node] != _tree.TREE_UNDEFINED:
            name = feature_name[node]
            threshold = tree_.threshold[node]
            s= "({} <= {})".format( name, threshold, node )
            if node == 0:
                pathto[node]=s
            else:
                pathto[node]=pathto[parent]+ ' and ' +s

            recurse(tree_.children_left[node], depth + 1, node)
            s="({} > {})".format( name, threshold)
            if node == 0:
                pathto[node]=s
            else:
                pathto[node]=pathto[parent]+' and ' +s
            recurse(tree_.children_right[node], depth + 1, node)
        else:
            k=k+1
            rule = pathto[parent] + ': prediction = ' +  str(tree_.value[node][0][0])
            simplified_rule = simplify_rule(rule, feature_names)
            rules.append(simplified_rule)

    recurse(0, 1, 0)
    return rules






