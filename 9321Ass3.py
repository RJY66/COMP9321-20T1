# python version 3.7.2
# sklearn version 0.0
# pandas version 1.0.3
# numpy version 1.18.3
# scipy version 1.4.1

import pandas as pd
from sklearn import ensemble
from sklearn import neighbors
from sklearn.metrics import *
import numpy as np
import sys
import ast
from scipy.stats import pearsonr


param_len = len(sys.argv)
if param_len != 3:
    print('Invalid number of parameters!')
    sys.exit()

raw_data_train = pd.read_csv(sys.argv[1])
raw_data_test = pd.read_csv(sys.argv[2])
# do with training data
raw_train_x = raw_data_train[['budget', 'runtime', 'release_date', 'original_language', 'cast', 'crew', 'production_companies', 'production_countries', 'keywords', 'genres']]
train_x_LR = pd.DataFrame()
train_x_LR['budget'] = raw_train_x['budget']
train_x_LR['runtime'] = raw_train_x['runtime']

# do with release date, only focus on month of release date
result_date = []
for i in raw_train_x['release_date']:
    if len(i) > 0:
        l = i.split('-')
        if len(l) == 3:
            # get month
            result = int(l[1])
            result_date.append(result)
    # do with missing value
    else:
        result = 0
        result_date.append(result)
train_x_LR['release_date'] = result_date

# do with language, label them with natural numbers
language_set = set()
language_no_map = dict()
a = 0
result_lan = []
language = []
for i in raw_train_x['original_language']:
    if len(i) > 0:
        language_set.add(i)
        language.append(i)
    # do with missing value
    else:
        language_set.add('Unknown')
        language.append('Unknown')
for k in sorted(language_set):
    language_no_map[k] = a
    a += 1
for j in language:
    result_lan.append(language_no_map[j])
train_x_LR['original_language'] = result_lan

# do with production company, label them with natural numbers
company_name = []
company_name_set = set()
company_name_map = dict()
b = 0
result_cn = []
for i in raw_train_x['production_companies']:
    result = ast.literal_eval(i)
    if len(result) > 0:
        # only get first company if there are multiple
        company_name.append(result[0]['name'])
        company_name_set.add(result[0]['name'])
    # do with missing value
    else:
        company_name.append('Unknown')
        company_name_set.add('Unknown')
for j in sorted(company_name_set):
    company_name_map[j] = b
    b += 1
for k in company_name:
    result_cn.append(company_name_map[k])
train_x_LR['production_companies'] = result_cn

# do with production country, label them with natural numbers
country = []
country_set = set()
c = 0
result_cou = []
country_map = dict()
for i in raw_train_x['production_countries']:
    result = ast.literal_eval(i)
    if len(result) > 0:
        # only get first country if there are multiple
        country.append(result[0]['name'])
        country_set.add(result[0]['name'])
    # do with missing value
    else:
        country_set.add('Unknown')
        country.append('Unknown')
for j in sorted(country_set):
    country_map[j] = c
    c += 1
for k in country:
    result_cou.append(country_map[k])
train_x_LR['production_countries'] = result_cou

# do with cast, label them with natural numbers
# add a column about number of cast of each movie
cast = []
cast_set = set()
cast_map = {}
d = 0
result_c = []
num_cast = []
for i in raw_train_x['cast']:
    result = ast.literal_eval(i)
    if len(result) > 0:
        # only get first cast if there are multiple
        cast.append(result[0]['name'])
        cast_set.add(result[0]['name'])
        num_cast.append(len(result))
    # do with missing value
    else:
        cast.append('Unknown')
        cast_set.add('Unknown')
        num_cast.append(0)
for j in sorted(cast_set):
    cast_map[j] = d
    d += 1
for k in cast:
    result_c.append(cast_map[k])
train_x_LR['cast'] = result_c
train_x_LR['nb_cast'] = num_cast

# do with crew, label them with natural numbers
# add a column about number of crew of each movie
dir = []
dir_set = set()
e = 0
result_d = []
dir_map = dict()
num_crew = []
for i in raw_train_x['crew']:
    result = ast.literal_eval(i)
    if len(result) > 0:
        num_crew.append(len(result))
        for m in result:
            # only focus on firstly-founded director of each movie
            if m['job'] == 'Director':
                dir.append(m['name'])
                dir_set.add(m['name'])
                break
    # do with missing value
    else:
        num_crew.append(0)
        dir_set.add('Unknown')
        dir.append('Unknown')
for j in sorted(dir_set):
    dir_map[j] = e
    e += 1
for k in dir:
    result_d.append(dir_map[k])
train_x_LR['crew'] = result_d
train_x_LR['nb_crew'] = num_crew

# do with keywords, label them in natural numbers
keywords_map = {}
keywords = []
keywords_set = set()
result_k = []
f = 0
for i in raw_train_x['keywords']:
    result = ast.literal_eval(i)
    if len(result) > 0:
        # only focus on first keyword
        keywords.append(result[0]['name'])
        keywords_set.add(result[0]['name'])
    # do with missing value
    else:
        keywords_set.add("Unknown")
        keywords.append("Unknown")
for j in sorted(keywords_set):
    keywords_map[j] = f
    f += 1
for k in keywords:
    result_k.append(keywords_map[k])
train_x_LR['keywords'] = result_k
train_x_LR = np.array(train_x_LR, dtype='float')

# do with train x of classification model
train_x_Cla = pd.DataFrame()
train_x_Cla['budget'] = raw_train_x['budget']
train_x_Cla['runtime'] = raw_train_x['runtime']
train_x_Cla = np.array(train_x_Cla, dtype='int')

train_y_LR = np.array(raw_data_train['revenue'], dtype='float')
train_y_Cla = np.array(raw_data_train['rating'], dtype='int')

########################### do with test data ######################################################
raw_test_x = raw_data_test[['budget', 'runtime', 'release_date', 'original_language',  'cast', 'crew', 'production_companies', 'production_countries', 'keywords', 'genres']]
test_x_LR = pd.DataFrame()
test_x_LR['budget'] = raw_test_x['budget']
test_x_LR['runtime'] = raw_test_x['runtime']

# do with release date
result_date2 = []
for i in raw_test_x['release_date']:
    if len(i) > 0:
        result = int(i.split('-')[1])
        result_date2.append(result)
    else:
        result = 0
        result_date2.append(result)
test_x_LR['release_date'] = result_date2

# do with language
language_set2 = set()
result_lan2 = []
language2 = []
for i in raw_test_x['original_language']:
    if len(i) > 0:
        language_set2.add(i)
        language2.append(i)
    else:
        language2.append('Unknown')
        language_set2.add('Unknown')
v = max(language_no_map.values())
# add language in test but not in training set into language number map.
# add at tail of original dict
differ_lan = sorted(language_set2 - language_set)
for m in range(len(differ_lan)):
    language_no_map[differ_lan[m]] = v + m + 1
for j in language2:
    result_lan2.append(language_no_map[j])
test_x_LR['original_language'] = result_lan2

# do with production company
company_name2 = []
company_name_set2 = set()
result_cn2 = []
for i in raw_test_x['production_companies']:
    result = ast.literal_eval(i)
    if len(result) > 0:
        company_name2.append(result[0]['name'])
        company_name_set2.add(result[0]['name'])
    else:
        company_name2.append('Unknown')
        company_name_set2.add('Unknown')
x = max(company_name_map.values())
differ_com = sorted(company_name_set2 - company_name_set)
for m in range(len(differ_com)):
    company_name_map[differ_com[m]] = x + m + 1
for k in company_name2:
    result_cn2.append(company_name_map[k])
test_x_LR['production_companies'] = result_cn2

# do with production country
country2 = []
country_set2 = set()
result_cou2 = []
for i in raw_test_x['production_countries']:
    result = ast.literal_eval(i)
    if len(result) > 0:
        country2.append(result[0]['name'])
        country_set2.add(result[0]['name'])
    else:
        country_set2.add('Unknown')
        country2.append('Unknown')
o = max(country_map.values())
differ_cou = sorted(country_set2 - country_set)
for m in range(len(differ_cou)):
    country_map[differ_cou[m]] = o + m + 1
for k in country2:
    result_cou2.append(country_map[k])
test_x_LR['production_countries'] = result_cou2

# do with cast
cast2 = []
cast_set2 = set()
result_c2 = []
num_cast2 = []
for i in raw_test_x['cast']:
    result = ast.literal_eval(i)
    if len(result) > 0:
        num_cast2.append(len(result))
        cast2.append(result[0]['name'])
        cast_set2.add(result[0]['name'])
    else:
        num_cast2.append(0)
        cast2.append('Unknown')
        cast_set2.add('Unknown')
differ_ca = sorted(cast_set2 - cast_set)
t = max(cast_map.values())
for m in range(len(differ_ca)):
    cast_map[differ_ca[m]] = t + m + 1
for k in cast2:
    result_c2.append(cast_map[k])
test_x_LR['cast'] = result_c2
test_x_LR['nb_cast'] = num_cast2

# do with crew
dir2 = []
dir_set2 = set()
result_d2 = []
num_crew2 = []
for i in raw_test_x['crew']:
    result = ast.literal_eval(i)
    if len(result) > 0:
        num_crew2.append(len(result))
        for m in result:
            if m['job'] == 'Director':
                dir2.append(m['name'])
                dir_set2.add(m['name'])
                break
    else:
        num_crew2.append(0)
        dir_set2.add('Unknown')
        dir2.append('Unknown')
differ_cw = sorted(dir_set2 - dir_set)
q = max(dir_map.values())
for m in range(len(differ_cw)):
    dir_map[differ_cw[m]] = q + m + 1
for k in dir2:
    result_d2.append(dir_map[k])
test_x_LR['crew'] = result_d2
test_x_LR['nb_crew'] = num_crew2

# do with keywords
keywords2 = []
keywords_set2 = set()
result_k2 = []
for i in raw_test_x['keywords']:
    result = ast.literal_eval(i)
    if len(result) > 0:
        keywords2.append(result[0]['name'])
        keywords_set2.add(result[0]['name'])
    else:
        keywords_set2.add("Unknown")
        keywords2.append("Unknown")
differ_k = sorted(keywords_set2 - keywords_set)
r = max(keywords_map.values())
for m in range(len(differ_k)):
    keywords_map[differ_k[m]] = r + m + 1
for k in keywords2:
    result_k2.append(keywords_map[k])
test_x_LR['keywords'] = result_k2
test_x_LR = np.array(test_x_LR, dtype='float')

test_x_Cla = pd.DataFrame()
test_x_Cla['budget'] = raw_test_x['budget']
test_x_Cla['runtime'] = raw_test_x['runtime']
test_x_Cla = np.array(test_x_Cla, dtype='int')

test_y_LR = np.array(raw_data_test['revenue'], dtype='float')
test_y_Cla = np.array(raw_data_test['rating'], dtype='int')

# GradientBoosting Regressor
model_regressor = ensemble.GradientBoostingRegressor(n_estimators=1288)
model_regressor.fit(train_x_LR, train_y_LR)
predict_y_LR = model_regressor.predict(test_x_LR)
predict_y_LR = np.array(predict_y_LR, dtype='float')

# related metrics calculation
msr = mean_squared_error(predict_y_LR, test_y_LR)
pearsonr_v = pearsonr(predict_y_LR, test_y_LR)
df1 = pd.DataFrame()
df1['zid'] = ['z5195715']
df1['MSR'] = [int(msr)]
df1['correlation'] = [round(pearsonr_v[0], 3)]
filename1 = "z5195715.PART1.summary.csv"
df1.to_csv(filename1, index=False)
print("Successfully generate: " + filename1)

df2 = pd.DataFrame()
df2['movie_id'] = raw_data_test['movie_id']
df2['predicted_revenue'] = predict_y_LR.astype('int')
filename2 = 'z5195715.PART1.output.csv'
df2.to_csv(filename2, index=False)
print('Successfully generate: ' + filename2)

# KNN classifier
model_classifier = neighbors.KNeighborsClassifier(9)
model_classifier.fit(train_x_Cla, train_y_Cla)
predict_y_Cla = model_classifier.predict(test_x_Cla)
predict_y_Cla = np.array(predict_y_Cla, dtype='int')

# related metrics calculation
ave_precision = precision_score(y_true=test_y_Cla, y_pred=predict_y_Cla, average='macro')
ave_recall = recall_score(y_true=test_y_Cla, y_pred=predict_y_Cla, average='macro')
accuracy = accuracy_score(y_true=test_y_Cla, y_pred=predict_y_Cla)
df3 = pd.DataFrame()
df3['zid'] = ['z5195715']
df3['average_precision'] = [round(ave_precision, 2)]
df3['average_recall'] = [round(ave_recall, 2)]
df3['accuracy'] = [round(accuracy, 2)]
filename3 = 'z5195715.PART2.summary.csv'
df3.to_csv(filename3, index=False)
print("Successfully generate: " + filename3)

df4 = pd.DataFrame()
df4['movie_id'] = raw_data_test['movie_id']
df4['predicted_rating'] = predict_y_Cla
filename4 = "z5195715.PART2.output.csv"
df4.to_csv(filename4, index=False)
print("Successfully generate: " + filename4)
