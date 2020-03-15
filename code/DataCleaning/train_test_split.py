import numpy as np
import csv
import datetime
# split across days for

DATA_DIR = "../../data/production_data"


def get_day(reader, start_row):
    start_date = to_date_time(start_row[0])
    rows = [start_row]

    end_row = None
    for row in reader:
        date = to_date_time(row[0])
        if date.day > start_date.day or \
                date.month > start_date.month or \
                date.year > start_date.year:
            end_row = row
            break

        else:
            rows.append(row)

    return rows, end_row


def to_date_time(date_str):
    # Timezone string is non-standard, strip it off
    date_str = date_str = date_str[:-6]
    date_time = datetime.datetime.strptime(
        date_str, "%Y-%m-%d %H:%M:%S")

    return date_time


def train_test_split_rows(window_rows, train_number, test_number):
    window_size = len(window_rows)
    assert((train_number + test_number) == window_size)

    indices = set([i for i in range(window_size)])
    idx_choice = np.random.choice(
        window_size, size=train_number, replace=False)
    pick_train = set(idx_choice)
    pick_test = indices.difference(pick_train)

    train_rows = []
    for train_idx in pick_train:
        train_rows.extend(window_rows[train_idx])

    test_rows = []
    for test_idx in pick_test:
        test_rows.extend(window_rows[test_idx])

    return train_rows, test_rows


def split(file, window_size, train_number, test_number):
    assert((train_number + test_number) == window_size)

    with open(file) as csvfile:
        reader = csv.reader(csvfile)
        title_row = next(reader)
        key_to_row_idx = {val: i for i, val in enumerate(title_row)}

        train_rows = []
        test_rows = []

        start_row = next(reader)
        window_index = 0
        window_days = []
        while start_row is not None:

            if window_index > window_size-1:
                new_train_rows, new_test_rows = train_test_split_rows(
                    window_days, train_number, test_number)
                train_rows.extend(new_train_rows)
                test_rows.extend(new_test_rows)
                window_index = 0
                window_days = []
            else:
                day_rows, start_row = get_day(reader, start_row)
                window_days.append(day_rows)
                window_index += 1

        # Just add the leftovers to the train rows
        for day_rows in window_days:
            train_rows.extend(day_rows)

    return train_rows, test_rows


def get_category_map(row_lists, idx=4):

    category_map = {}
    next_idx = 0

    for row_list in row_lists:
        for row in row_list:
            val = row[idx]

            # Includes a "none" category for ""
            if val not in category_map:
                category_map[row[idx]] = next_idx
                next_idx += 1

    return category_map


def to_vector(row_lists):

    categorical_rows = set([4])
    category_maps = {}
    for categorical_row_idx in categorical_rows:
        category_maps[categorical_row_idx] = get_category_map(
            row_lists, categorical_row_idx)
    print(category_maps)

    feature_matrices = []
    target_vectors = []

    for row_list in row_lists:
        feature_rows = []
        targets = []

        for row in row_list:
            target = row[-1]
            try:
                target_float = float(target)
            except:
                continue
            else:    
                if target_float == 0.0:
                    # print("Skipping target")
                    continue
                targets.append(target_float)

            feature_list = []
            # Skip the date and production columns
            for feature_idx in range(1, len(row)-1):

                feature_val = row[feature_idx]

                if feature_idx in categorical_rows:  # categorical feature
                    category_map = category_maps[feature_idx]
                    l = [0] * len(category_map)
                    l[category_map[feature_val]] = 1
                    feature_list.extend(l)
                else:  # Regular (real valued) feature
                    if feature_val == "":
                        feature_list.append(0.0)
                    else:
                        feature_list.append(float(feature_val))

            feature_rows.append(np.array(feature_list))

        feature_matrices.append(np.vstack(feature_rows))
        target_vectors.append(np.array(targets))

    # Some sanity checks:
    assert(feature_matrices[0].shape[0] == len(target_vectors[0]))
    assert(feature_matrices[0].shape[1] == feature_matrices[1].shape[1])

    return feature_matrices, target_vectors


# file = f"{DATA_DIR}/103941/combination_data/production_weather_combination.csv"

# train, test = split(file, 3, 2, 1)

# [X_train, X_test], [Y_train, Y_test] = to_vector([train, test])
