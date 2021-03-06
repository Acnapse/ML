'''
# Лабораторная работа №2 по курсу "Машинное обучение"

Выполнила работу: Матакова М. В. \
Группа: М8О-308Б-17

## Условие

1. Необходимо реализовать алгоритмы машинного обучения. 
2. Применить данные алгоритмы на наборы данных, подготовленных в первой лабораторной работе. 
3. Провести анализ полученных моделей, вычислить метрики классификатора
4. Произвести тюнинг параметров в случае необходимости. 
5. Сравнить полученные результаты с моделями реализованными в scikit-learn. Аналогично построить метрики классификации. 
6. Показать, что полученные модели не переобучились. 
7. Также необходимо сделать выводы о применимости данных моделей к вашей задаче.

Алгоритмы (с учетом варианта):
* Логическая регрессия
* KNN
* Дерево решений
* Random forest

## Загрузка и преобразование данных
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn import tree
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn import preprocessing
from sklearn.metrics import precision_score
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier

"""Загружаем датасет"""

data = pd.read_csv('chocolate.csv')

"""Замени старые названия колонок на более понятные и простые"""

new_columns = {
    'CompanyÂ\n(Maker-if known)': 'company',
    'Specific Bean\nOrigin or Bar Name': 'bar_origin',
    'REF': 'review_update_value',
    'Review \nDate': 'review_pub_date',
    'Cocoa Percent': 'cocoa_percentage',
    'Company\nLocation': 'company_location',
    'Rating': 'rating',
    'Bean Type': 'bean_type',
    'Broad Bean\nOrigin': 'bean_origin'
}
data = data.rename(new_columns, axis='columns')
data.head().T

"""Убираем знак %"""

def clean(el):
    return np.float32(el.split("%")[0])

data.cocoa_percentage = data.cocoa_percentage.apply(lambda el: clean(el))

"""Также необходимо заменить все пустые клетки (в данном случае это символ Â) на np.nan"""

for col in data.columns:
    if data[col].dtype == 'O':
        data[col] = data[col].apply(lambda l: np.nan if l == 'Â ' else l)

"""## Подготовка данных

Разобьем данные на тестовую и обучающую выборки.
"""

X = data.drop(['company'], axis = 1)
y = data['rating']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=7)

"""## Логическая регрессия"""

def normalize(X):
    mins = np.min(X, axis = 0) 
    maxs = np.max(X, axis = 0) 
    rng = maxs - mins 
    norm_X = 1 - ((maxs - X)/rng) 
    return norm_X
def logistic_func(beta, X):
    return 1.0/(1 + np.exp(-np.dot(X, beta.T))) 

def log_gradient(beta, X, y):
    first_calc = logistic_func(beta, X) - y.reshape(X.shape[0], -1) 
    final_calc = np.dot(first_calc.T, X) 
    return final_calc 

def cost_func(beta, X, y): 
    log_func_v = logistic_func(beta, X) 
    y = np.squeeze(y) 
    step1 = y * np.log(log_func_v) 
    step2 = (1 - y) * np.log(1 - log_func_v) 
    final = -step1 - step2 
    return np.mean(final) 

def grad_desc(X, y, beta, lr=.01, converge_change=.001): 
    cost = cost_func(beta, X, y) 
    change_cost = 1
    while(change_cost > converge_change): 
        old_cost = cost 
        beta = beta - (lr * log_gradient(beta, X, y)) 
        cost = cost_func(beta, X, y) 
        change_cost = old_cost - cost
    return beta

def pred_values(beta, X): 
    pred_prob = logistic_func(beta, X) 
    pred_value = np.where(pred_prob >= .5, 1, 0) 
    return np.squeeze(pred_value)

"""### Результат собственной реализации"""

X = normalize(X)
X_train, X_test, y_train, y_test = train_test_split(
     X, y,stratify=y, test_size=0.1)
beta = np.matrix(np.zeros(X.shape[1]))
beta = grad_desc(X_train.values, y_train.values, beta)

print("train precision: " + str(precision_score(y_train, pred_values(beta, X_train), average='weighted')))
print("test precision: " + str(precision_score(y_test, pred_values(beta, X_test), average='weighted')))

"""### Результат Scikit-learn"""

clf = LogisticRegression()
clf.fit(X_train, y_train)
print("train precision: " + str(precision_score(y_train, clf.predict(X_train), average='weighted')))
print("test precision: " + str(precision_score(y_test, clf.predict(X_test), average='weighted')))

"""## KNN"""

def SquareEuclidDistance(a,b):
    d = 0
    for i in range(a.shape[0]):
        d += (a[i] - b[i]) * (a[i] - b[i])
    return d

def KNN(X_train, Y_train, X_test):
    Y_test = np.ones(X_test.shape[0])
    for j in range(X_test.shape[0]):
        Q = np.zeros(Y_train.max() + 1)
        for i in range(X_train.shape[0]):
            Q[Y_train[i]] += 1/SquareEuclidDistance(X_test[j,:], X_train[i,:])
        Y_test[j] = np.argmax(Q)
    return Y_test

"""### Результат собственной реализации"""

print("train precision: " + str(precision_score(y_test, KNN(X_test.values, y_test.values, X_test.values), average='weighted')))
print("test precision: " + str(precision_score(y_test, KNN(X_train.values, y_train.values, X_test.values), average='weighted')))

"""### Результат Scikit-learn"""

clf = KNeighborsClassifier()
clf.fit(X_train, y_train)
print("train precision: " + str(precision_score(y_train, clf.predict(X_train), average='weighted')))
print("test precision: " + str(precision_score(y_test, clf.predict(X_test), average='weighted')))

"""## Дерево решений"""

class Node:
    def __init__(self, predicted_class):
        self.predicted_class = predicted_class
        self.feature_index = 0
        self.threshold = 0
        self.left = None
        self.right = None


class DecisionTreeClassifier:
    def __init__(self, max_depth=None):
        self.max_depth = max_depth
        self.feature_prun = 0.1

    def fit(self, X, y, random_feature = False):
        self.n_classes_ = len(set(y))
        self.n_features_ = X.shape[1]
        self.tree_ = self._grow_tree(X, y, random_feature)

    def predict(self, X):
        return [self._predict(inputs) for inputs in X]

    def _best_split(self, X, y,random_feature):
        m = y.size
        if m <= 1:
            return None, None
        num_parent = [np.sum(y == c) for c in range(self.n_classes_)]
        best_gini = 1.0 - sum((n / m) ** 2 for n in num_parent)
        best_idx, best_thr = None, None
        for idx in range(self.n_features_):
            if(np.random.randint(0, 11) <= self.feature_prun*10):
                continue
            thresholds, classes = zip(*sorted(zip(X[:, idx], y)))
            num_left = [0] * self.n_classes_
            num_right = num_parent.copy()
            for i in range(1, m):
                c = classes[i - 1]
                num_left[c] += 1
                num_right[c] -= 1
                gini_left = 1.0 - sum(
                    (num_left[x] / i) ** 2 for x in range(self.n_classes_)
                )
                gini_right = 1.0 - sum(
                    (num_right[x] / (m - i)) ** 2 for x in range(self.n_classes_)
                )
                gini = (i * gini_left + (m - i) * gini_right) / m
                if thresholds[i] == thresholds[i - 1]:
                    continue
                if gini < best_gini:
                    best_gini = gini
                    best_idx = idx
                    best_thr = (thresholds[i] + thresholds[i - 1]) / 2
        return best_idx, best_thr

    def _grow_tree(self, X, y,random_feature, depth=0):
        num_samples_per_class = [np.sum(y == i) for i in range(self.n_classes_)]
        predicted_class = np.argmax(num_samples_per_class)
        node = Node(predicted_class=predicted_class)
        if depth < self.max_depth:
            idx, thr = self._best_split(X, y,random_feature)
            if idx is not None:
                indices_left = X[:, idx] < thr
                X_left, y_left = X[indices_left], y[indices_left]
                X_right, y_right = X[~indices_left], y[~indices_left]
                node.feature_index = idx
                node.threshold = thr
                node.left = self._grow_tree(X_left, y_left,random_feature, depth + 1)
                node.right = self._grow_tree(X_right, y_right,random_feature, depth + 1)
        return node

    def _predict(self, inputs):
        node = self.tree_
        while node.left:
            if inputs[node.feature_index] < node.threshold:
                node = node.left
            else:
                node = node.right
        return node.predicted_class

"""### Результат собственной реализации"""

clf = DecisionTreeClassifier(max_depth=10)
clf.fit(X_train.values, y_train.values)
print("train precision: " + str(precision_score(y_train, clf.predict(X_train.values), average='weighted')))
print("test precision: " + str(precision_score(y_test, clf.predict(X_test.values), average='weighted')))

"""### Результат Scikit-learn"""

clf = tree.DecisionTreeClassifier()
clf = clf.fit(X_train, y_train)
print("train precision: " + str(precision_score(y_train, clf.predict(X_train), average='weighted')))
print("test precision: " + str(precision_score(y_test, clf.predict(X_test), average='weighted')))

"""## Random Forest"""

def RandomForest(size, Max_depth):
    head = [None] * size
    for i in range(size):
        head[i] = DecisionTreeClassifier(max_depth=Max_depth)
    return head
def fit(forest, X_train, y_train):
    for i in range(len(forest)):
        subset = np.zeros(X_train.shape)
        labels = np.zeros(y_train.shape).astype(int)
        for j in range(X_train.shape[0]):
            index = np.random.randint(0, X_train.shape[0])
            subset[j] = X_train.values[index]
            labels[j] = y_train.values[index]
        forest[i].fit(X_train.values, y_train.values,random_feature = True)
def predict(forest, X):
    Q = np.zeros([X.shape[0], 2])
    for i in range(len(forest)):
        pred = forest[i].predict(X.values)
        for j in range(len(pred)):
            Q[j, pred[j]] += 1
    pred = np.zeros([X.shape[0]])
    for i in range(X.shape[0]):
        pred[i] = np.argmax(Q[i,:])
    return pred

"""### Результат собственной реализации"""

clf = RandomForest(10, 4)
fit(clf, X_train, y_train)
print("train precision: " + str(precision_score(y_train, predict(clf,X_train), average='weighted')))
print("test precision: " + str(precision_score(y_test, predict(clf,X_test), average='weighted')))

"""### Результат Scikit-learn"""

clf = RandomForestClassifier(max_depth=4)
clf.fit(X_train, y_train)
print("train precision: " + str(precision_score(y_train, clf.predict(X_train), average='weighted')))
print("test precision: " + str(precision_score(y_test, clf.predict(X_test), average='weighted')))
