import numpy as np
import csv
import datetime
# split across days for

DATA_DIR = "../../data/production_data"
DATA_DIR_I = "../../data/irradiance_data"


def get_day(reader, start_row):
    start_date = to_date_time(start_row[0])
    start_row[0] = start_date
    rows = [start_row]

    end_row = None
    for row in reader:
        date = to_date_time(row[0])
        row[0] = date
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
    if type(date_str) == str:
        date_str = date_str = date_str[:-6]
        date_time = datetime.datetime.strptime(
            date_str, "%Y-%m-%d %H:%M:%S")
        return date_time
    elif type(date_str) == datetime.datetime:
        return date_str
    else:
        return None


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

    return train_rows, test_rows, title_row


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


def to_vector(row_lists, title_row):

    title_to_index = {title: i for i, title in enumerate(title_row)}

    categorical_rows = set([title_to_index["precipType"]])
    category_maps = {}
    for categorical_row_idx in categorical_rows:
        category_maps[categorical_row_idx] = get_category_map(
            row_lists, categorical_row_idx)

    feature_matrices = []
    target_vectors = []

    for row_list in row_lists:
        feature_rows = []
        targets = []

        for row in row_list:
            target = row[title_to_index["production"]]
            try:
                target_float = float(target)
            except:
                continue
            else:
                if target_float == 0.0:
                    continue
                targets.append(target_float)

            feature_list = []
            # Skip the date and production columns
            for feature_idx in range(len(row)):

                if feature_idx == title_to_index["date"] or feature_idx == title_to_index["production"]:
                    continue

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


def parse_irrediance_row(row, title_to_index, tz_offset):

    ghi = float(row[title_to_index["GHI"]])
    dhi = float(row[title_to_index["DHI"]])
    dni = float(row[title_to_index["DNI"]])

    year = int(row[title_to_index["Year"]])
    month = int(row[title_to_index["Month"]])
    day = int(row[title_to_index["Day"]])
    hour = int(row[title_to_index["Hour"]])
    minute = int(row[title_to_index["Minute"]])

    # Something here to fix time?
    time = datetime.datetime(year, month, day, hour, minute)
    tz_delta = datetime.timedelta(hours=abs(tz_offset))
    time = time - tz_delta

    return [time, ghi, dhi, dni]


def load_irrediance_data(file, tz_offset=7):
    with open(file) as csvfile:
        reader = csv.reader(csvfile)
        title_row = next(reader)
        title_to_index = {title: i for i, title in enumerate(title_row)}

        parsed_rows = []
        for row_1 in reader:
            row_2 = next(reader)  # Get in twos and average

            parsed_row_1 = parse_irrediance_row(
                row_1, title_to_index, tz_offset)

            parsed_row_2 = parse_irrediance_row(
                row_2, title_to_index, tz_offset)

            t1 = parsed_row_1[0]
            t2 = parsed_row_2[0]

            assert(t1.hour == t2.hour)

            ghi = (parsed_row_1[1] + parsed_row_2[1]) / 2
            dhi = (parsed_row_1[2] + parsed_row_2[2]) / 2
            dni = (parsed_row_1[3] + parsed_row_2[3]) / 2
            parsed_rows.append([t1, ghi, dhi, dni])

    return parsed_rows, ["date", "GHI", "DHI", "DNI"]


def join_title_rows(prod_title_row, irr_title_row):
    assert(prod_title_row[0] == "date")
    assert(irr_title_row[0] == "date")

    return prod_title_row + irr_title_row[1:]


def join_irradiance_data(production_rows, irradiance_rows):

    joined_rows = []

    p_start = 0
    for r in irradiance_rows:
        r_date = r[0]
        for i in range(p_start, len(production_rows)):
            p = production_rows[i]
            if r_date == p[0]:
                p_start = i  # Use the fact that these are in sorted order
                joined_rows.append(p + r[1:])
                break

    return joined_rows


def get_irradiance_WPI_data(file_production, file_irradiance, window_size, train_rows, tz_str):
    tz_strs = {"America/Denver": 7,
               "America/Los_Angeles": 8, "America/Phoenix": 7}

    test_rows = window_size - train_rows

    train, test, prod_title_row = split(
        file_production, window_size, train_rows, test_rows)
    irradiance_rows, irr_title_row = load_irrediance_data(
        file_irradiance, tz_strs[tz_str])

    train_joined = join_irradiance_data(train, irradiance_rows)
    test_joined = join_irradiance_data(test, irradiance_rows)
    joined_title_rows = join_title_rows(prod_title_row, irr_title_row)

    X, Y = to_vector([train_joined, test_joined], joined_title_rows)

    return X, Y

# file = f"{DATA_DIR}/103941/combination_data/production_weather_combination.csv"
# file_i = f"{DATA_DIR_I}/113805/irradiance_data.csv"

# train, test, prod_title_row = split(file, 3, 2, 1)
# irradiance_rows, irr_title_row = load_irrediance_data(file_i, 7)

# train_joined = join_irradiance_data(train, irradiance_rows)
# test_joined = join_irradiance_data(test, irradiance_rows)
# joined_title_rows = join_title_rows(prod_title_row, irr_title_row)

# [X_train, X_test], [Y_train, Y_test] = to_vector(
#     [train_joined, test_joined], joined_title_rows)
