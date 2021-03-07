import numpy as np
import scipy.linalg as lin

STRIKE = 1

A = [[1, 1.1], [1, 1/1.1]]

def construct_underlying(period = 52, call_put='call'):
    price_tree = [[1]]
    i = 1
    while i <= period:
        u, d = i, 0
        next_layer_price = []
        while d <= i:
            p = 1 * pow(1.1, u) * pow(1/1.1, d)
            next_layer_price.append(p)               
            u -= 1
            d += 1
        price_tree.append(next_layer_price)
        i += 1
    return price_tree

def construct_upswing(price_tree, period=52, previous_upswing=None, call_put='call'):
    num_exercise = 0
    exercise_time = {}
    exercise_time[period] = []
    indifferent_time = {}
    indifferent_time[period] = []
    tree = [[]]
    i = 1
    while i <= period:
        tree.append([])
        i += 1
    for price in price_tree[period]:
        if call_put == 'call':
            option_exercise = price - STRIKE
        else:
            option_exercise = STRIKE - price
        tree[period].append(max(option_exercise, 0))
        if round(option_exercise, 5) > 0:
            exercise_time[period].append(round(price, 5))
        elif round(option_exercise, 5) == 0:
            indifferent_time[period].append(round(price, 5))

    for j in range(period - 1, -1, -1):
        k = 0
        while k <= j:
            if previous_upswing is None:
                if call_put == 'call':
                    exercise = price_tree[j][k] - STRIKE
                else:
                    exercise = STRIKE - price_tree[j][k]
            else:
                payoff = np.array([previous_upswing[j+1][k], previous_upswing[j+1][k+1]])
                theta = lin.solve(A, payoff)
                if call_put == 'call':
                    exercise = price_tree[j][k] - STRIKE + theta.dot([1, 1])
                else:
                    exercise = STRIKE - price_tree[j][k] + theta.dot([1, 1])
            payoff = np.array([tree[j+1][k], tree[j+1][k+1]])
            theta = lin.solve(A, payoff)
            not_exercise = theta.dot([1, 1])

            price_pt = round(pow(1.1, j-k) * pow(1/1.1, k), 5)
            if round(exercise, 5) > round(not_exercise, 5):
                if j not in exercise_time.keys():
                    exercise_time[j] = [price_pt]
                else:
                    exercise_time[j].append(price_pt)
                tree[j].append(exercise)
            else:
                if round(exercise, 5) == round(not_exercise, 5):
                    if j not in indifferent_time.keys():
                        indifferent_time[j] = [price_pt]
                    else:
                        indifferent_time[j].append(price_pt)
                tree[j].append(not_exercise)
            k += 1
    return tree, exercise_time, indifferent_time

if __name__ == "__main__":
    price_tree = construct_underlying()
    tree_1, exercise_1, indifferent_time1 = construct_upswing(price_tree)
    tree_2, exercise_2, indifferent_time2 = construct_upswing(price_tree, previous_upswing=tree_1)
    tree_3, exercise_3, indifferent_time3 = construct_upswing(price_tree, previous_upswing=tree_2)
    tree_4, exercise_4, indifferent_time4 = construct_upswing(price_tree, previous_upswing=tree_3)
    price_tree_p = construct_underlying(call_put='put')
    tree_1_p, exercise_1_p, indifferent_time1p = construct_upswing(price_tree_p, call_put='put')
    tree_2_p, exercise_2_p, indifferent_time2p = construct_upswing(price_tree_p, previous_upswing=tree_1_p, call_put='put')
    tree_3_p, exercise_3_p, indifferent_time3p = construct_upswing(price_tree_p, previous_upswing=tree_2_p, call_put='put')
    tree_4_p, exercise_4_p, indifferent_time4p = construct_upswing(price_tree_p, previous_upswing=tree_3_p, call_put='put')
    print(exercise_4_p)
    print(exercise_4)
    print(tree_4_p[0][0])
    print(tree_4[0][0])
    
    