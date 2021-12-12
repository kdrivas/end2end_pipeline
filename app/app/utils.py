def check_data_in_request(data, valid_columns):
    for col in valid_columns:
        # Check if all the columns exists and if the data contains information 
        # from three periods
        if col not in data or len(data[col]) != 3:
            return False

    return True
