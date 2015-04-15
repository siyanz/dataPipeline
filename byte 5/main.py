import httplib2
from apiclient.discovery import build
import urllib
import json
import csv
import matplotlib.pyplot as plt 
import numpy as np
import scipy.stats
from sklearn.naive_bayes import GaussianNB
from sklearn import tree
from sklearn import cross_validation
from sklearn import preprocessing
from sklearn import metrics
from sklearn.dummy import DummyClassifier
import csv

API_KEY = 'AIzaSyDOI185_gTElbbCD1BUgalIiDZ4XeRlXO8'
TABLE_ID = '1V-zsxH7mLEiM6ueBDTLbL3PcPbN_V_HG6W3nA_54'

# open the data stored in a file called "data.json"
try:
    fp = open("data/dogs.json")
    dogs = json.load(fp)
    fp = open("data/cats.json")
    cats = json.load(fp)

# but if that file does not exist, download the data from fusiontables
except IOError:
    service = build('fusiontables', 'v1', developerKey=API_KEY)
    query = "SELECT * FROM " + TABLE_ID + " WHERE  AnimalType = 'DOG'"
    dogs = service.query().sql(sql=query).execute()
    fp = open("data/dogs.json", "w+")
    json.dump(dogs, fp)
    query = "SELECT * FROM " + TABLE_ID + " WHERE  AnimalType = 'CAT'"
    cats = service.query().sql(sql=query).execute()
    fp = open("data/cats.json", "w+")
    json.dump(cats, fp)


#================================================================
# Statistics
#================================================================

# Checking whether a difference is significant
# Are cats returned to owners at the same rate as dogs (H0) 
# or is the difference significant (H1)

# first let's grab the data
n_groups = 2 # cats and dogs
outcome_types = ['Returned to Owner', 'Transferred to Rescue Group', 'Adopted', 'Foster', 'Euthanized']
outcome_labels = ['Owner', 'Rescue Group', 'Adopted', 'Foster', 'Euthanized', 'Other']
age_outcome = ['Infant - Younger than 6 months', 'Youth - Younger than 1 year', 'Older than 1 year', 'Older than 7 years']
age_outcome_labels = ['Young', 'Old', 'Unknown']
cat_outcomes = np.array([0.0,0,0,0,0,0])
dog_outcomes = np.array([0.0,0,0,0,0,0])
dog_young_outcomes = np.array([0.0,0,0,0,0,0])
dog_old_outcomes = np.array([0.0,0,0,0,0,0])
dog_unknown_outcomes = np.array([0.0,0,0,0,0,0])

rows_cats = cats['rows'] # the actual data 
for cat in rows_cats:
    # get the outcome stored for this cat
    value = cat[13]
    try:
        i = outcome_types.index(value)
        # one of outcome_types
        cat_outcomes[i] = cat_outcomes[i] + 1
    except ValueError:
        # everything else
        cat_outcomes[5] = cat_outcomes[5] + 1


rows_dogs = dogs['rows']
for dog in rows_dogs:
    value = dog[13]
    try:
        i = outcome_types.index(value)
        dog_outcomes[i] += 1
    except ValueError:
        dog_outcomes[5] += 1

for dog in rows_dogs:
    value = dog[13]
    age = dog[8]
    try:
        i_age = age_outcome.index(age)
        if i_age <= 1:
            try:
                i = outcome_types.index(value)
                dog_young_outcomes[i] += 1
            except ValueError:
                dog_young_outcomes[5] += 1
        else:
            try:
                i = outcome_types.index(value)
                dog_old_outcomes[i] += 1
            except ValueError:
                dog_old_outcomes[5] += 1
    except ValueError:
        try:
            i = outcome_types.index(value)
            dog_unknown_outcomes[i] += 1
        except ValueError:
            dog_unknown_outcomes[5] += 1
        

# plot the data to see what it looks like
fig, ax = plt.subplots()
index = np.arange(6)
bar_width = 0.2
opacity = 0.4
rects1 = plt.bar(index, dog_young_outcomes, bar_width, alpha=opacity, color='b', label='Young')
rects2 = plt.bar(index+bar_width, dog_old_outcomes, bar_width, alpha=opacity, color='r', label='Old')
rects3 = plt.bar(index+bar_width*2, dog_unknown_outcomes, bar_width, alpha=opacity, color='g', label='Unknown')
plt.ylabel('Number')
plt.title('Number of dogs by age for adopted dogs')
plt.xticks(index + bar_width, outcome_labels)
plt.legend()
plt.tight_layout()
plt.show()

alpha = .05

Observed = np.array([dog_young_outcomes, dog_old_outcomes])
X_2, p, dof, expected= scipy.stats.chi2_contingency(Observed)
print "CHI-squared: ", X_2, "p = ", p



#-----------------------------------------------------#
#--------------------Machine Learning-----------------#
#-----------------------------------------------------#
try:
    fp = open("data/random_dogs_and_cats.json")
    all_data = np.array(json.load(fp))

except IOError:
# make an array of all data about cats and dogs
    all_data = cats['rows'] + dogs['rows']
    # randomize it so the cats aren't all first
    np.random.shuffle(all_data)
    fp = open("data/random_dogs_and-cats.json", "w+")
    json.dump(all_data, fp)
    all_data = np.array(all_data)

features = ['IntakeMonth', 'Breed', 'EstimatedAge', 'Sex', 'SpayNeuter', 
            'Size', 'Color', 'IntakeType', 'IntakeYear', 'OutcomeYear']

out = 'OutcomeType'
cols = cats['columns']
use_data = []
ncols = len(cols)
for i in np.arange(ncols):
    try: 
        # we want to use a column 
        # if its name is in the list of features we want to keep
        features.index(cols[i])
        use_data.append(i)
    except ValueError:
        # and if it matches the name of the column we are predicting
        # ('Outcome') we capture the column index for later
        if cols[i] == out:
            out_index = i

x = all_data[:, use_data]
y = all_data[:, out_index]


y[y=="No Show"] = "Other"
y[y=="Missing Report Expired"] = "Other"
y[y=="Found Report Expired"] = "Other"
y[y=="Lost Report Expired"] = "Other"
y[y=="Released in Field"] = "Other"
y[y==''] = "Other"
y[y=="Died"] = "Other"
y[y=="Disposal"] = "Other"
y[y=="Missing"] = "Other"
y[y=="Trap Neuter/Spay Released"] = "Other"
y[y=="Transferred to Rescue Group"] = "Other"
y[y==u'Foster']="Other"

y[y=="Returned to Owner"] = "Home"
y[y==u'Adopted']="Home"
y[y==u'Euthanized']="Euthanized"
# So for now we have 5 classes total: Other, Foster, Owner, Adopted, Euthanized
Outcomes = ["Euth.", "Home", "Other"]

nrows = len(all_data)
percent = len(x)/5
X_opt = x[:percent, :]
y_opt = y[:percent]
X_rest = x[percent:, :]
y_rest = y[percent:]


X_opt_for_orange = np.insert(X_opt, len(features), y_opt, axis=1)
with open("data/orange_opt.csv", "w+") as csvfile:
    datawriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    datawriter.writerow(features + ["Class"])
    for row in X_opt_for_orange:
        datawriter.writerow(row)

with open("data/orange_rest.csv", "w+") as csvfile:
    datawriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    datawriter.writerow(features + ["Class"])
    for row in X_rest:
        datawriter.writerow(row)


le = preprocessing.LabelEncoder()
labels = []
le
for name in features:
    csvfile = open('data/{0}.csv'.format(name), 'rb')
    datareader = csv.reader(csvfile, delimiter=',')
    for row in datareader:
        labels.append(row[0])
# make a label for empty values too
labels.append(u'')
le.fit(labels)

X = le.transform(x)

nrows = len(all_data)
percent = len(x)/5
X_opt = X[:percent, :]
y_opt = y[:percent]
X_rest = X[percent:, :]
y_rest = y[percent:]

dc = DummyClassifier(strategy='most_frequent',random_state=0)
gnb = GaussianNB()
dt = tree.DecisionTreeClassifier(max_depth=5)

skf = cross_validation.StratifiedKFold(y_rest, 10)
gnb_acc_scores = []
dc_acc_scores = []
dt_acc_scores = []

count = 0
# loop through the folds
for train, test in skf:
    # extract the train and test sets
    X_train, X_test = X_rest[train], X_rest[test]
    y_train, y_test = y_rest[train], y_rest[test]
    
    # train the classifiers
    dc = dc.fit(X_train, y_train)
    gnb = gnb.fit(X_train, y_train)
    dt = dt.fit(X_train, y_train)
    tree.export_graphviz( dt, out_file = 'tree{0}.dot'.format(count), feature_names=features)
    count += 1

    # test the classifiers
    dc_pred = dc.predict(X_test)
    gnb_pred = gnb.predict(X_test)
    dt_pred = dt.predict(X_test)

    # calculate metrics relating how well they did
    dc_accuracy = metrics.accuracy_score(y_test, dc_pred)
    dc_precision, dc_recall, dc_f, dc_support = metrics.precision_recall_fscore_support(y_test, dc_pred)
    gnb_accuracy = metrics.accuracy_score(y_test, gnb_pred)
    gnb_precision, gnb_recall, gnb_f, gnb_support = metrics.precision_recall_fscore_support(y_test, gnb_pred)
    dt_accuracy = metrics.accuracy_score(y_test, dt_pred)
    dt_precision, dt_recall, dt_f, dt_support = metrics.precision_recall_fscore_support(y_test, dt_pred)
    

    # print the results for this fold
    print "Accuracy "
    print "Dummy Cl: %.2f" %  dc_accuracy
    print "Naive Ba: %.2f" %  gnb_accuracy
    print "Decision Tree: % .2f" % dt_accuracy
    print "F Score"
    print "Dummy Cl: %s" % dc_f
    print "Naive Ba: %s" % gnb_f
    print "Decision Tree: %s" % dt_f
    print "Precision", "\t".join(list(Outcomes))
    print "Dummy Cl:", "\t".join("%.2f" % score for score in  dc_precision)
    print "Naive Ba:", "\t".join("%.2f" % score for score in  gnb_precision)
    print "Decision Tree:", "\t".join("%.2f" % score for score in  dt_precision)
    print "Recall   ", "\t".join(list(Outcomes))
    print "Dummy Cl:", "\t".join("%.2f" % score for score in  dc_recall)
    print "Naive Ba:", "\t".join("%.2f" % score for score in  gnb_recall)
    print "Decision Tree", "\t".join("%.2f" % score for score in  dt_recall)

    dc_acc_scores = dc_acc_scores + [dc_accuracy]
    gnb_acc_scores = gnb_acc_scores + [gnb_accuracy]
    dt_acc_scores = dt_acc_scores + [dt_accuracy]

    diff = np.mean(dt_acc_scores) - np.mean(gnb_acc_scores)
    t, prob = scipy.stats.ttest_rel(dt_acc_scores, gnb_acc_scores)

print "============================================="
print " Results of optimization "
print "============================================="
print "Decision Tree accuracy: ", np.mean(dt_acc_scores)
print "Naive Bayes Mean accuracy: ", np.mean(gnb_acc_scores)
print "Accuracy for Decision Tree and Naive Bayes differ by {0}; p<{1}".format(diff, prob)

print "These are good summary scores, but you may also want to" 
print "Look at the details of what is going on inside this"
print "Possibly even without 10 fold cross validation"
print "And look at the confusion matrix and other details"
print "Of where mistakes are being made for developing insight"

print "============================================="
print " Final Results "
print "============================================="
print "When you have finished this assignment you should"
print "train a final classifier using the X_rest and y_rest"
print "using 10-fold cross validation"
print "And you should print out some sort of statistics on how it did"
