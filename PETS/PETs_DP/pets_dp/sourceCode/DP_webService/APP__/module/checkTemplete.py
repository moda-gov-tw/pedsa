#!/usr/bin/python
# -*- coding: utf-8 -*-

#from configparser import ConfigParser

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser as ConfigParser


def getUserRule(file_):
    # get user rule from local
    # format in file:

    '''
    [setting]
    # if autoGen is True, for those value which is not defined below [rule] will replace by autoGenValue
    autoGen = False
    autoGenValue = others

    [information]
    # rule = valueCount;rawData;udfValue;*
    rule_1 = 15;Spain;Europe;*
    rule_2 = 54;Singapore;Asia;*

    ps: If there is two same rule, ex: rule_2 = 54;Singapore;Asia;*  
                                       rule_2 = 54;Singapore;Europe;*
        then, the last one rule_2 will be get.
    '''
  
    '''
    config = ConfigParser.ConfigParser()
    with codecs.open(file_, encoding="utf-8-sig" ) as f:
      config.readfp(f) 
      autoGen = config.get('setting', 'autoGen')
      autoGenValue = config.get('setting', 'autoGenValue')
    '''


    '''
    config = ConfigParser.ConfigParser()
    config.readfp(codecs.open(file_, "r", "utf-8-sig"))
    autoGen = config.get('setting', 'autoGen')
    autoGenValue = config.get('setting', 'autoGenValue')
    '''

    try:
        parser = ConfigParser()
        #config.read(file_,encoding='utf-8')
        parser.read(file_, encoding="utf-8-sig")
        autoGen = parser.get('setting', 'autoGen')
        autoGenValue = parser.get('setting', 'autoGenValue')
        level = parser.get('setting', 'level')
    #except ConfigParser.NoSectionError as e:
    except ConfigParser as e:
        return 0,str(e),None

    index_ = 0
    rules = ''
    # iterate rules to get all rules
    while True:
        index_ += 1
        tmp = 'rule_' + str(index_)
        try:
            rules = rules + parser.get('information', tmp) + '^'

        #except ConfigParser.NoSectionError as e:
        except ConfigParser as e:
            return 0,str(e),None

        except:
            rules = rules[:-1]
            index_ -= 1
            break

    #return autoGen, autoGenValue, rules
    return autoGen, autoGenValue, level, rules


def getReplacePath(path_,level):
    #retrun string
    level = int(level)

    paths = path_.split('^') # list of string
    pathIndex = [i for i in range(len(paths))] # list of string of string
    nodes = [path.split(';') for path in paths] # list of list

    # check if valueCounts is existed
    for node in nodes:
        try:
            node[0] = int(node[0])
        except:
            return ('checkTemplete_error_valueCounts_is_not_existed: {} in {}'.format(node[0],';'.join(node)))

    # check if raw value is multi-defined (every raw values has only one father)
    ruleLeafNode = [node[1] for node in nodes]
    distinctRuleLeafNode = list(set(ruleLeafNode))
    for leafNode in ruleLeafNode:
        if leafNode in distinctRuleLeafNode:
            distinctRuleLeafNode.remove(leafNode)
        else:
            return ('checkTemplete_error_multi-defined: %s'%leafNode)

    # check if root is * 
    for i in range(len(nodes)):
        if nodes[i][-1] != '*':
            return ('checkTemplete_error_root_is_not_*: %s'%paths[i])

    # check generalize level (movements)
    length = [len(listOfNodes)-1 for listOfNodes in nodes] # list of int

    # check if level set too high
    if max(length) <= level:
        return ('checkTemplete_error_level_is_out_of_range: %s'%level)

    # calculate steps
    lastMovement = max(length) - level
    if lastMovement <= 0:
        lastMovement = 1

    movements = [len_-lastMovement for len_ in length] # list of int
    for i in range(len(movements)):
        if movements[i] < 0:
            movements[i]  = 0

    # create replacment dict
    replaceDict_path = ''
    for i in range(len(pathIndex)):
        replaceDict_path += nodes[i][1]
        replaceDict_path += ':'
        replaceDict_path += nodes[i][1+int(movements[i])]
        replaceDict_path += ';'

    #_logger.debug('replaceDict_path: ',str(replaceDict_path))
    return replaceDict_path[:-1]
