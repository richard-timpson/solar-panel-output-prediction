import numpy as np
import csv
import datetime
from calendar import isleap
import json
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


def get_total_area(architecture_file):
    sites = {}

    with open(architecture_file) as f:
        rows = csv.reader(f)
        title_row = {s: i for i, s in enumerate(next(rows))}

        for row in rows:
            area = float(row[title_row["width"]]) * \
                float(row[title_row["height"]])
            area /= (100*100)  # To keep the numbers from getting too big

            site_id = int(row[title_row["site_id"]])
            if site_id in sites:
                sites[site_id] += area
            else:
                sites[site_id] = area

    return sites


def append_site_features(X, features):
    # Append the given features to the array of training examples
    # All training examples will be give the same value for the feature
    x_a = np.zeros((X.shape[0], len(features)))
    for i in range(len(features)):
        x_a[:, i] = features[i]

    return np.hstack([X, x_a])


def date_to_feature(date: datetime.datetime):
    day_of_year = date.timetuple().tm_yday
    if isleap(date.year):
        days_in_year = 366
    else:
        days_in_year = 365

    # Use a perioidic function
    day = 1 + np.sin(day_of_year*np.pi / days_in_year)
    hour = 1 + np.sin(date.hour*np.pi / 24)

    return day, hour


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


def build_vector_title_row(title_row, category_maps):
    new_titles = []

    for title_idx, title in enumerate(title_row):

        if title == "production":
            continue

        elif title == "date":
            new_titles.append("day")
            new_titles.append("hour")

        elif title_idx in category_maps:
            category_map = category_maps[title_idx]
            l = [""] * len(category_map)
            for cat_name, name_idx in category_map.items():
                l[name_idx] = f"{title}_{cat_name}"
            new_titles.extend(l)
        else:
            new_titles.append(title)

    return new_titles


def to_vector(row_lists, title_row):

    title_to_index = {title: i for i, title in enumerate(title_row)}

    categorical_rows = set([title_to_index["precipType"]])
    category_maps = {}
    for categorical_row_idx in categorical_rows:
        # category_maps[categorical_row_idx] = get_category_map(
        #     row_lists, categorical_row_idx)
        category_maps[categorical_row_idx] = {
            "": 0, "rain": 1, "snow": 2, "sleet": 3}  # Standardize across all the sites

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

                feature_val = row[feature_idx]
                if feature_idx == title_to_index["production"]:
                    continue
                elif feature_idx == title_to_index["date"]:
                    day, hour = date_to_feature(row[feature_idx])
                    feature_list.append(day)
                    feature_list.append(hour)

                elif feature_idx in categorical_rows:  # categorical feature
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
    new_title_row = build_vector_title_row(title_row, category_maps)

    assert(feature_matrices[0].shape[0] == len(target_vectors[0]))
    assert(feature_matrices[0].shape[1] == feature_matrices[1].shape[1])
    assert(len(new_title_row) == feature_matrices[0].shape[1])

    return feature_matrices, target_vectors, new_title_row


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


def get_production_data(file, window_size, train_rows):
    test_rows = window_size - train_rows

    train, test, prod_title_row = split(
        file, window_size, train_rows, test_rows)

    X, Y, new_title_row = to_vector(
        [train, test], prod_title_row)

    return X, Y, new_title_row


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

    X, Y, new_title_row = to_vector(
        [train_joined, test_joined], joined_title_rows)

    return X, Y, new_title_row


def keep_columns(X, title_row, columns):
    # Remove all columns except for the given list of columns to keep
    columns = set(columns)

    assert(X.shape[1] == len(title_row))

    new_title_row = []
    to_remove = []
    for i, title in enumerate(title_row):
        if title in columns:
            new_title_row.append(title)
        else:
            to_remove.append(i)

    X_new = np.delete(X, to_remove, 1)
    return X_new, new_title_row


def remove_columns(X, title_row, columns):
    # Remove columns given a (textual) list of columns to delete
    columns = set(columns)

    assert(X.shape[1] == len(title_row))

    new_title_row = []
    to_remove = []
    for i, title in enumerate(title_row):
        if title in columns:
            to_remove.append(i)
        else:
            new_title_row.append(title)

    X_new = np.delete(X, to_remove, 1)
    return X_new, new_title_row
