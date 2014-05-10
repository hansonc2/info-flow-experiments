import unittest, time, re
import sys
import math

# common, ad and ad_vector classes
import adVector, ad, common

# for statistical test, plots
import random
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime, timedelta

# for Porter Stemming and removing stop-words
from nltk.corpus import stopwords 

## feature selection
from sklearn.svm import LinearSVC
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.linear_model import RandomizedLogisticRegression

## CV
from sklearn import cross_validation

## Classification
from sklearn.neighbors import KNeighborsClassifier
from sklearn import svm
from sklearn.linear_model import LogisticRegression

# Permutation test
from itertools import combinations as comb
from itertools import product


########### CHOICES FOR THE AD-COMPARISON, AD-IDENTIFICATION #############

# Choices for what to uniquely identify an ad with
URL = 1
TITLE_URL = 2
TITLE_BODY = 3
CHOICE = URL

# Choices for measure of similarity
JACCARD = 1
COSINE = 2
SIM_CHOICE = COSINE

# Choices for assigning weight to the vector
NUM = 1
LOG_NUM = 2
SCALED_NUM = 3 # not implemented
W_CHOICE = NUM


########### HELPER CLASSES AND FUNCTIONS #############


########### FUNCTIONS TO CARRY OUT ANALYSIS #############

#------------- for Ad Set Comparison ---------------#

def ad_sim(ads1, ads2):
	if(SIM_CHOICE == JACCARD):
		return jaccard_index(ads1, ads2)
	elif(SIM_CHOICE == COSINE):
		return ad_cosine_sim(ads1, ads2)
	else:
		print("Illegal SIM_CHOICE")
		raw_input("Press Enter to Exit")
		sys.exit()

def jaccard_index(ads1, ads2):
	ad_union = ads1.union(ads2)
	ad_int = ads1.intersect(ads2)
# 	ad_int.tot_intersect(ads1, ads2)
	return (float(ad_int.size())/float(ad_union.size()))

def ad_cosine_sim(ads1, ads2):
	ad_union = ads1.union(ads2)
	vec1 = []
	vec2 = []
	for ad in ad_union.data:
		vec1.append(ads1.ad_weight(ad, W_CHOICE))
		vec2.append(ads2.ad_weight(ad, W_CHOICE))
	return cosine_sim(vec1, vec2)
	

#------------- for Vector Operations ---------------#

def cosine_sim(vec1, vec2):		# cosine similarity of two vectors
	return (dot_prod(vec1, vec2)/(vec_mag(vec1)*vec_mag(vec2)))

def vec_mag(vec):				# magnitude of a vector
	sum = 0.0
	for i in vec:
		sum = sum + i*i
	return math.sqrt(sum)

def dot_prod(vec1, vec2):		# dot product of two vectors
	sum = 0.0
	if(len(vec1) != len(vec2)):
		print("Dot product doesnt exist")
		sys.exit()
	for i in range(0, len(vec1)):
		sum = sum + vec1[i]*vec2[i]
	return sum

#------------- to convert Ad Vectors to feature vectors ---------------#

def word_vectors(list):
	ad_union = adVector.AdVector()
	for ads in list:
		ad_union = ad_union.union(ads)
	words = ad_union.advec_to_words()
	stemmed_words = common.stem_low_wvec(words)
	filtered_words = [w for w in stemmed_words if not w in stopwords.words('english')]
	word_v = common.unique_words(filtered_words)
	word_v = common.strip_vec(word_v)
	wv_list = []
	labels = []
	for ads in list:
		wv_list.append(ads.gen_word_vec(word_v, W_CHOICE))
		labels.append(ads.label)
	return wv_list, labels, word_v						## Returns word_v as feature

def ad_vectors(list):
	ad_union = adVector.AdVector()
	for ads in list:
		ad_union = ad_union.union(ads)
	av_list = []
	labels = []
	for ads in list:
		av_list.append(ad_union.gen_ad_vec(ads))
		labels.append(ads.label)
	return av_list, labels, ad_union					## Returns entire ad as feature

def temp_ad_vectors(list):
	ad_union = adVector.AdVector()
	for ads in list:
		ad_union.union(ads, ad_union)
# 	ad_union.display('title')
	tav_list = []
	for ads in list:
		tav_list.append(ad_union.gen_temp_ad_vec(ads))
	return tav_list, ad_union


#------------- functions to plot figures from a list of feature vectors ---------------#

def histogramPlots(list):
	a, b = ad_vectors(list)
	obs = np.array(a)
	l = []
	colors = ['b', 'r', 'g', 'm', 'k']							# Can plot upto 5 different colors
	for i in range(0, len(list)):
		l.append([int(i) for i in obs[i]])
	pos = np.arange(1, len(obs[0])+1)
	width = 0.5     # gives histogram aspect to the bar diagram
	gridLineWidth=0.1
	fig, ax = plt.subplots()
	ax.xaxis.grid(True, zorder=0)
	ax.yaxis.grid(True, zorder=0)
	for i in range(0, len(list)):
		lbl = "ads"+str(i)
		plt.bar(pos, l[i], width, color=colors[i], alpha=0.5, label = lbl)
	#plt.xticks(pos+width/2., obs[0], rotation='vertical')		# useful only for categories
	#plt.axis([-1, len(obs[2]), 0, len(ran1)/2+10])
	plt.legend()
	plt.show()
	
def temporalPlots(list):
	obs = np.array(temp_ad_vectors(list))
	#obs = np.array(ad_temp_category(list))
	print obs[0]
	dates = []
	colors = ['r.', 'b.', 'g.', 'm.', 'k.']
	for j in range(0, len(list)):
		dates.append(matplotlib.dates.date2num([list[j].data[i].time for i in range(0, len(list[j].data))]))
	pos = np.arange(len(obs[0]))
	gridLineWidth=0.1
	fig, ax = plt.subplots()
	ax.xaxis.grid(True, zorder=0)
	ax.yaxis.grid(True, zorder=0)
	for i in range(0, len(list)):
		lbl = "ads"+str(i)
		obs[i] = [j+1 for j in obs[i]]
		plt.plot(obs[i], dates[i], colors[i], alpha=0.5, label = lbl)
# 		plt.xticks(pos+width/2., obs[2], rotation='vertical')		# useful only for categories
	#plt.axis([-1, 500, 0, 700])
	plt.legend()
	plt.show()
	
#------------- functions for Statistics and Statistical Tests ---------------#

def stat_prc(adv, ass, keywords):				# prc statistic, which doesn't give very good results		
	presence = []
	for i in range(0, len(adv)):
		if(adv[i].freq_contains(keywords) > 0):
			presence.append(1)
		else:
			presence.append(0)
	ct,cu=0,0
	for i in range(0, len(adv)):
		if(str(i) in ass[0:len(ass)/2]):
			ct += presence[i]
		else:
			cu += presence[i]
	return (ct-cu)

def stat_kw(adv, ass, keywords):				# keyword_diff based statistic
	advm, advf = vec_for_stats(adv, ass)
	return (advm.freq_contains(keywords) - advf.freq_contains(keywords))
	
def stat_sim(adv, ass, keywords):				# cosine similarity based statistic
	advm, advf = vec_for_stats(adv, ass)
	return -ad_sim(advm, advf)

def permutationTest(adv, ass, keywords, stat):
	if(stat == 'coss'):
		Tobs = stat_sim(adv, ass, keywords)
	elif(stat == 'kw'):
		Tobs = stat_kw(adv, ass, keywords)
	elif(stat == 'prc'):
		Tobs = stat_prc(adv, ass, keywords)
	#print "Tobs="+str(Tobs)
	under = 0
	org_ass = ass
	for count, per in enumerate(comb(ass, len(ass)/2), 1):
		new_ass = list(per)+list(set(ass)-set(per))
		if(stat == 'coss'):
			Tpi = stat_sim(adv, new_ass, keywords)
		elif(stat == 'kw'):
			Tpi = stat_kw(adv, new_ass, keywords)
		elif(stat == 'prc'):
			Tpi = stat_prc(adv, new_ass, keywords)
		#print "Tpi="+str(Tpi)
		if round(Tobs, 10) <= round(Tpi, 10):
			under += 1
	return (1.0*under) / (1.0*count)


def vec_for_stats(adv, ass):					# aggregates the control group and experiment group into single ad vectors
	advm = adVector.AdVector()
	advf = adVector.AdVector()
	for i in range(0, len(adv)):
		if(str(i) in ass[0:len(ass)/2]):
			#print "c"+str(i)
			advm.add_vec(adv[i])
		else:
			#print "t"+str(i)
			advf.add_vec(adv[i])
	return (advm, advf)
	
def table_22(adv, ass, keywords):				# creates 2x2 contingency table using keywords
	advm, advf = vec_for_stats(adv, ass)
	kt = advm.freq_contains(keywords)
	ku = advf.freq_contains(keywords)
	nt = advm.size() - kt
	nu = advf.size() - ku
	return [kt, nt, ku, nu]

def testWrapper(adv, ass, keywords, type):
	if(not type == 'chi'):
		s = datetime.now()
		try:
			res = permutationTest(adv, ass, keywords, type)
		except:
			res = 100
		e = datetime.now()
	else:
		s = datetime.now()
		vec = table_22(adv, ass, keywords)
		try:
			chi2, p, dof, ex = stats.chi2_contingency(vec, correction=True)
			res = p
		except:
			res = 100
# 		print vec
# 		print chi2, p, ex
		e = datetime.now()
	return common.round_figures(res, 6), e-s
	
def printCounts(index, adv, ass):				# returns detailed counts of #ads within a round
	advm, advf = vec_for_stats(adv, ass)
	sys.stdout.write("%s\t AD_t size=%s uniq=%s, AD_u size=%s uniq=%s \n" %(index, advm.size(), 
							advm.unique().size(), advf.size(), advf.unique().size()))
	for i in range(0, len(ass)):
		sys.stdout.write("%s \t" %(adv[i].size()))
	print("")

def printNewsMetrics(unit):
	adv = unit['adv']
	ass = unit['ass']
	xvfbfails = unit['xf']
	breakouts = unit['break']
	loadtimes = unit['loadtimes']
	reloads = unit['reloads']
	errors = unit['errors']
 			

#------------- functions for Machine Learning Analyses ---------------#

def getVectorsFromRun(adv, ass, featChoice):			# returns observation vector from a round
	if featChoice == 'word':
		X, labels, feat = np.array(word_vectors(adv))
	elif featChoice == 'ad':
		X, labels, feat = np.array(ad_vectors(adv))
	y = [0]*len(ass)
	for i in ass[0:len(ass)/2]:
		y[int(i)] = 1
	print y
	X = np.array(X)
	y = np.array(y)
	return X, y, feat

def getVectorsFromExp(advdicts, featChoice):			# returns observation vector from a list of rounds
	n = len(advdicts[0]['ass'])
	list = []
	y = []
	sys.stdout.write("Creating feature vectors")
 	sys.stdout.write("-->>")
 	sys.stdout.flush()
	for advdict in advdicts:
		list.extend(advdict['adv'])
	if(featChoice == 'words'):
		X, labels, feat = word_vectors(list)
	elif(featChoice == 'ads'):
		X, labels, feat = ad_vectors(list)
	if(labels[0] == ''):
		for advdict in advdicts:
			ass = advdict['ass']
			y1 = [0]*len(ass)
			for i in ass[0:len(ass)/2]:
				y1[int(i)] = 1
			y.extend(y1)
	else:
		y = [int(i) for i in labels]
	X = [X[i:i+n] for i in range(0,len(X),n)]
	y = [y[i:i+n] for i in range(0,len(y),n)]
# 	print feat[0].title, feat[0].url
	print "Complete"
	return np.array(X), np.array(y), feat	

def trainTest(algos, X, y, splittype, splitfrac, nfolds, list, ptest, chi2, verbose=False):
	
	### Split data into training and testing data based on splittype

	if(splittype == 'rand'):
		rs1 = cross_validation.ShuffleSplit(len(X), n_iter=1, test_size=splitfrac)
		for train, test in rs1:
			if(verbose):
				print test, train
			X_train, y_train, X_test, y_test = X[train], y[train], X[test], y[test]
	elif(splittype == 'timed'):
		split = int((1.-splitfrac)*len(X))
		X_train, y_train, X_test, y_test = X[:split], y[:split], X[split:], y[split:]
	else:
		raw_input("Split type ERROR")	
		
	### Model selection via cross-validation from training data
	
	max_score = 0
	for algo in algos.keys():
		score, mPar, clf = crossVal_algo(nfolds, algo, algos[algo], X_train, y_train, splittype, splitfrac, list)
		if(verbose):
			print score, mPar, clf
		if(score > max_score):
			max_clf = clf
			max_score = score
	if(verbose):
		try:
			print max_score, max_clf, max_clf.coef_.shape			# for linear kernel
		except:
			print max_score, max_clf, max_clf.dual_coef_.shape		# for rbf kernel
	if(ptest==1):
		oXtest, oytest = X_test, y_test	
	if(list==1):
		X_test = np.array([item for sublist in X_test for item in sublist])
		y_test = np.array([item for sublist in y_test for item in sublist])	
		X_train = np.array([item for sublist in X_train for item in sublist])
		y_train = np.array([item for sublist in y_train for item in sublist])
		
	### Fit model to training data and compute test accuracy
	
	np.set_printoptions(threshold=sys.maxint)
	max_clf.fit(X_train, y_train)
	if(verbose):
		print "train-size: ", len(y_train)
		print "test-size: ", len(y_test)
	print "test-score: ", max_clf.score(X_test, y_test)
	if(ptest==1):
		print "p-value: ", blockPTest(oXtest, oytest, max_clf)
# 		for i in range(0,len(oXtest)):
# 			print MLpTest(oXtest[i], oytest[i], clf)
	
	if(chi2==1):
		cont_table = genContTable(X_test, y_test, max_clf)
		print cont_table
		chi2, p, dof, ex = stats.chi2_contingency(cont_table, correction=True)
		print chi2, p, dof, ex
		print ("Chi-Square = "+str(chi2))
		print ("p-value = "+str(p))
			
	return max_clf

def featureSelection(X,y,feat,treatnames,featChoice,splittype,splitfrac,nfolds,nfeat,list):

	algos = {	
				'logit':{'C':np.logspace(-5.0, 15.0, num=21, base=2), 'penalty':['l1']},
# 				'svc':{'C':np.logspace(-5.0, 15.0, num=21, base=2)}		
			}

	clf = trainTest(algos, X, y, splittype, splitfrac, nfolds, list, ptest=0, chi2=0)
	
# 	maxC = clf.get_params()['C']
# 	
# 	if(list==1):
# 		X = np.array([item for sublist in X for item in sublist])
# 		y = np.array([item for sublist in y for item in sublist])	
# 		
# 	randLog = RandomizedLogisticRegression(C=maxC).fit(X,y)
# 	indices = np.where(randLog.get_support())[0]
# 	print randLog.all_scores_
# 	print indices
# 	raw_input("wait")
# 	for i in indices:
# 		print i
# 		feat.choose_by_index(i).printStuff(10, 10, 10)
# 	raw_input("Write randlogreg!!")
	
	printTopKFeatures(X, y, feat, treatnames, featChoice, clf, nfeat, list)
	
# 	clf = trainTest(algos, X, y, splittype, splitfrac, nfolds, list, ptest=0, chi2=0)
# 	ua,uind=np.unique(clf.coef_[0],return_inverse=True)
# 	count=np.bincount(uind)
# 	print ua, count
# 	print "no. of non-zero coefficients: ", len(clf.coef_[0])-count[np.where(ua==0)[0]][0]	
# 	for k in range(1, 50):
# 		topk1 = np.argsort(clf.coef_[0])[::-1][:k]
# 		topk0 = np.argsort(clf.coef_[0])[:k]
# 		kX = X[:,:,np.append(topk1,topk0)]
# 		print k, "\t", 
# 		CVPtest(kX, y, feat, splittype, splitfrac, nfolds, list, ptest=0, chi2=0)


def CVPtest(X, y, feat, splittype, splitfrac, nfolds, list, ptest=1, chi2=1, verbose=False):				# main function, calls cross_validation, then runs chi2

	algos = {	
				'logit':{'C':np.logspace(-5.0, 15.0, num=21, base=2), 'penalty':['l1', 'l2']},
# 				'kNN':{'k':np.arange(1,20,2), 'p':[1,2,3]}, 
# 				'polySVM':{'C':np.logspace(-5.0, 15.0, num=21, base=2), 'degree':[1,2,3,4]},
# 				'rbfSVM':{'C':np.logspace(-5.0, 15.0, num=21, base=2), 'gamma':np.logspace(-15.0, 3.0, num=19, base=2)}
				
			}
	clf = trainTest(algos, X, y, splittype, splitfrac, nfolds, list, ptest=ptest, chi2=chi2, verbose=verbose)


def printTopKFeatures(X, y, feat, treatnames, featChoice, max_clf, k, list):		# prints top k features from max_clf+some numbers
	if(list==1):
		X = np.array([item for sublist in X for item in sublist])
		y = np.array([item for sublist in y for item in sublist])
	A = np.array([0.]*len(X[0]))
	B = np.array([0.]*len(X[0]))
	for i in range(len(X)):
		if(y[i] == 1):
			A = A + X[i]
		elif(y[i] == 0):
			B = B + X[i]
	n_classes = max_clf.coef_.shape[0]
	if(n_classes == 1):
		topk1 = np.argsort(max_clf.coef_[0])[::-1][:k]
		print "\nFeatures for class %s:" %(str(treatnames[1]))
		for i in topk1:
			if(featChoice == 'ads'):
				feat.choose_by_index(i).printStuff(max_clf.coef_[0][i], A[i], B[i])
			elif(featChoice == 'words'):
				print feat[i]
		topk0 = np.argsort(max_clf.coef_[0])[:k]
		print "\n\nFeatures for class %s:" %(str(treatnames[0]))
		for i in topk0:
			if(featChoice == 'ads'):
				feat.choose_by_index(i).printStuff(max_clf.coef_[0][i], A[i], B[i])
			elif(featChoice == 'words'):
				print feat[i]
	else:
		for i in range(0,n_classes):
			topk = np.argsort(max_clf.coef_[i])[::-1][:k]
			print "Features for class %s:" %(str(treatnames[i]))
			for j in topk:
				if(featChoice == 'ads'):
					feat.choose_by_index(j).display()
				elif(featChoice == 'words'):
					print feat[j]
			print "coefs: ", max_clf.coef_[i][topk]
	

def crossVal_algo(k, algo, params, X, y, splittype, splitfrac, list, verbose=False):				# performs cross_validation
	if(splittype=='rand'):
		rs2 = cross_validation.ShuffleSplit(len(X), n_iter=k, test_size=splitfrac)
	elif(splittype=='timed'):
		rs2 = cross_validation.KFold(n=len(X), n_folds=k)
	max, max_params = 0, {}
	par = []
	for param in params.keys():
		par.append(params[param])
	for p in product(*par):
		if(verbose):
 			print "val=", p
		score = 0.0
		for train, test in rs2:
			X_train, y_train, X_test, y_test = X[train], y[train], X[test], y[test]
			if(list==1):
				X_train = np.array([item for sublist in X_train for item in sublist])
				y_train = np.array([item for sublist in y_train for item in sublist])
				X_test = np.array([item for sublist in X_test for item in sublist])
				y_test = np.array([item for sublist in y_test for item in sublist])
			#print X_train.shape, y_train.shape, X_test.shape, y_test.shape
			if(algo == 'svc'):
				clf = LinearSVC(C=p[params.keys().index('C')],
					penalty="l1", dual=False)				## Larger C increases model complexity
			if(algo=='kNN'):
				clf = KNeighborsClassifier(n_neighbors=p[params.keys().index('k')], 
					warn_on_equidistant=False, p=p[params.keys().index('p')])
			if(algo=='linearSVM'):
				clf = svm.SVC(kernel='linear', C=p[params.keys().index('C')])
			if(algo=='polySVM'):
				clf = svm.SVC(kernel='poly', degree = p[params.keys().index('degree')], 
					C=p[params.keys().index('C')])
			if(algo=='rbfSVM'):
				clf = svm.SVC(kernel='rbf', gamma = p[params.keys().index('gamma')], 
					C=p[params.keys().index('C')])			## a smaller gamma gives a decision boundary with a smoother curvature
			if(algo=='logit'):
				clf = LogisticRegression(penalty=p[params.keys().index('penalty')], dual=False, 
					C=p[params.keys().index('C')])
			clf.fit(X_train, y_train)
			score += clf.score(X_test, y_test)
		score /= k
		if(verbose):
 			print score
		if score>max:
			max = score
			max_params = p
			classifier = clf
	return max, max_params, classifier

def stat_ML(X_test, y_test, clf):
	g1 = [X_test[i] for i in range(0,len(X_test)) if y_test[i]==1]
	g2 = [X_test[i] for i in range(0,len(X_test)) if y_test[i]==0]		# CAn REduce RUN TIME by 50%!!!
	return sum(clf.predict(g1)) - sum(clf.predict(g2))

def stat_CC(ypred, ylabel):
	if(ypred.shape != ylabel.shape):
		raw_input("ypred, ylabel not of same shape!")
		print "Exiting..."
		sys.exit(0)
	blocks = ypred.shape[0]
	blockSize = ypred.shape[1]
	CC = 0
	for i in range(0,blocks):
		for j in range(0, blockSize):
			if(ypred[i][j]==ylabel[i][j]):
				CC += 1
	return CC

def getPerm(ylabel):
	blocks = ylabel.shape[0]
	yret = ylabel
	for i in range(0,blocks):
		random.shuffle(yret[i])
	return yret
	

def blockPTest(oXtest, oytest, clf, iterations=10000):				# block permutation test
	blockSize = oXtest.shape[1]
	blocks = oXtest.shape[0]
	ypred = np.array([[-1]*blockSize]*blocks)
	for i in range(0,blocks):
		ypred[i] = clf.predict(oXtest[i])
	Tobs = stat_CC(ypred, oytest)
	print 'Tobs: ', Tobs
# 	raw_input("w")
	under = 0
	for i in range(0,iterations):
		yperm = getPerm(oytest)
# 		print yperm
		Tpi = stat_CC(ypred, yperm)
# 		print Tpi
		if round(Tobs, 10) <= round(Tpi, 10):
			under += 1
# 	print (1.0*under) / (1.0*iterations)
	return (1.0*under) / (1.0*iterations)

def MLpTest(X_test, y_test, clf):									# permutation test
	Tobs = stat_ML(X_test, y_test, clf)
# 	print Tobs
	under = 0
	a = list(common.perm_unique(y_test))
	for new_y_test in a:
		Tpi = stat_ML(X_test, np.array(new_y_test), clf)			# No need to compute this. prediction X_test doesnt change
# 		print new_y_test
# 		print "Tpi="+str(Tpi)
		if round(Tobs, 10) <= round(Tpi, 10):
			under += 1
	return (1.0*under) / (1.0*len(a))

def genContTable(X, y, clf):										# generates contingency table
	try:
		n_classes = clf.coef_.shape[0]								# for linear classifiers
	except:
		n_classes = clf.dual_coef_.shape[0]							# for rbf classifiers
	if(n_classes == 1):
		cont_tab = [[0]*2]*2
	else:
		cont_tab = [[0]*n_classes]*n_classes
	cont_tab = np.array(cont_tab)
	print cont_tab.shape
	y_pred = clf.predict(X)
	if(not len(y_pred) == len(y)):
		raw_input("Dimension error!")
	for i in range(0,len(y)):											
																	#				y=0			y=1
		cont_tab[y_pred[i]][y[i]] = cont_tab[y_pred[i]][y[i]]+1		#	y_pred=0	tab[0,0]	tab[0,1]
																	#	y_pred=1	tab[1,0]	tab[1,1]
	return cont_tab

def MLAnalysis(collection, featChoice='ads', splitfrac=0.1, splittype='timed'):
	par_adv = collection[0]
	treatnames = collection[1]
	splittype = 'timed' #'timed'/'rand'
	X,y,feat = getVectorsFromExp(par_adv, featChoice)
	print X.shape
	print sum(sum(sum(X)))
	print y.shape
	ua,uind=np.unique(y,return_inverse=True)
	count=np.bincount(uind)
	print ua, count
	featureSelection(X,y,feat,treatnames,featChoice,splittype,splitfrac,nfolds=10,nfeat=5,list=1)
	print "CVPtest"
	CVPtest(X, y, feat, splittype, splitfrac, nfolds=10, ptest=1, chi2=0, list=1, verbose=True)


def applyLabels2AdVecs(adv, ass, samples, treatments):
	size = samples/treatments
	for i in range(0, treatments):
		for j in range(0, size):
			adv[int(ass[i*size+j])].setLabel(i)

def get_ads_from_log(log_file, old=False):
	treatnames = []
	fo = open(log_file, "r")
	line = fo.readline()
	chunks = re.split("\|\|", line)
	if(old):
		gmarker = 'g'
		treatments = 2
		treatnames = ['0', '1']
		samples = len(chunks)-1
	else:
		gmarker = 'assign'
		treatments = int(chunks[2])
		samples = int(chunks[1])
		line = fo.readline()
		chunks = re.split("\|\|", line)
		for i in range(1, len(chunks)):
			treatnames.append(chunks[i].strip())
		print treatnames
		print treatments
	assert treatments == len(treatnames)
	fo.close()
	adv = []
	for i in range(0, samples):
 		adv.append(adVector.AdVector())
 	loadtimes = [timedelta(minutes=0)]*samples
 	reloads = [0]*samples
 	errors = [0]*samples
 	xvfbfails = []
 	breakout = False
 	par_adv = []
 	ass = []
		
	fo = open(log_file, "r")
	r = 0	
	sys.stdout.write("Scanning ads")
	for line in fo:
		chunks = re.split("\|\|", line)
		chunks[len(chunks)-1] = chunks[len(chunks)-1].rstrip()
		if(chunks[0] == gmarker and r==0):
			r += 1
			ass = chunks[2:]
			if(old):	
				ass = chunks[1:]
			assert len(ass) == samples
			applyLabels2AdVecs(adv, ass, samples, treatments)
 			#print ass
 		elif(chunks[0] == gmarker and r >0 ):
 			r += 1
 			par_adv.append({'adv':adv, 'ass':ass, 'xf':xvfbfails, 
 						'break':breakout, 'loadtimes':loadtimes, 'reloads':reloads, 'errors':errors})
 			sys.stdout.write(".")
			sys.stdout.flush()
			adv = []
			for i in range(0, samples):
 				adv.append(adVector.AdVector())
 			loadtimes = [timedelta(minutes=0)]*samples
			reloads = [0]*samples
			errors = [0]*samples
 			xvfbfails = []
 			breakout = False
			ass = chunks[2:]
			if(old):	
				ass = chunks[1:]
			assert len(ass) == samples
			applyLabels2AdVecs(adv, ass, samples, treatments)
 		elif(chunks[0] == 'Xvfbfailure'):
 			xtreat, xid = chunks[1], chunks[2]
 			xvfbfails.append(xtreat)
 		elif(chunks[1] == 'breakingout'):
 			breakout = True
 		elif(chunks[1] == 'loadtime'):
 			t = (datetime.strptime(chunks[2], "%H:%M:%S.%f"))
 			delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
 			id = int(chunks[3])
 			loadtimes[id] += delta
 		elif(chunks[1] == 'reload'):
 			id = int(chunks[2])
 			reloads[id] += 1
 		elif(chunks[1] == 'errorcollecting'):
 			id = int(chunks[2])
 			errors[id] += 1 		
		elif(chunks[0] == 'ad'):
			ind_ad = ad.Ad({'Time':datetime.strptime(chunks[3], "%Y-%m-%d %H:%M:%S.%f"), 'Title':chunks[4], 
					'URL': chunks[5], 'Body': chunks[6].rstrip(), 'cat': "", 'label':chunks[2]})
# 			ind_ad.display()
			adv[int(chunks[1])].add(ind_ad)
		else:				# only to analyze old log files
			try:
				ind_ad = ad.Ad({'Time':datetime.strptime(chunks[2], "%Y-%m-%d %H:%M:%S.%f"), 'Title':chunks[3], 
						'URL': chunks[4], 'Body': chunks[5].rstrip(), 'cat': "", 'label':chunks[1]})
# 	 			ind_ad = ad.Ad({'Time':datetime.strptime(chunks[1], "%Y-%m-%d %H:%M:%S.%f"), 'Title':chunks[2], 
# 	 					'URL': chunks[3], 'Body': chunks[4].rstrip(), 'cat': "", 'label':""})
# 				ind_ad.display()
				adv[int(chunks[0])].add(ind_ad)
			except:
				pass
 	
 	r += 1
 	par_adv.append({'adv':adv, 'ass':ass, 'xf':xvfbfails, 
 			'break':breakout, 'loadtimes':loadtimes, 'reloads':reloads, 'errors':errors})
 	sys.stdout.write(".Scanning complete\n")
 	sys.stdout.flush()
 	return [par_adv, treatnames]	