import WebSearcher as ws
import os
import time
import pickle
import pandas as pd
import tldextract
from urllib.parse import unquote
import datetime
import csv

langs_dict = {
    'en': 'English',
    'hw': 'Hebrew',
    'ru': 'Russian',
    'ar': 'Arabic',
}

country_dict_short = {
    'US': 'Washington,District of Columbia,United States',
    'IL': 'Jerusalem District,Israel',
    'RU': 'Moscow,Moscow,Russia',
    'EG': 'Cairo,Cairo Governorate,Egypt',
}

country_dict_long = {'Egypt': 'Cairo,Cairo Governorate,Egypt', 'Israel': 'Jerusalem District,Israel',
                     'United States': 'Washington,District of Columbia,United States',
                     'Russia': 'Moscow,Moscow,Russia', 'Indonesia': 'Central Jakarta,Jakarta,Indonesia',
                     'Japan': 'Tokyo,Tokyo,Japan', 'Taiwan': 'Taipei City,Taiwan',
                     }


# def run_parser(html_date, entered_path=None):
#     if entered_path:
#         directory_path = entered_path
#     else:
#         directory_path = f"C:/Users/Or (G)Meiri/Desktop/Work/sci-search/parser/data/{html_date}-html/html"
#
#     # Get a list of all files in the directory
#     file_list = os.listdir(directory_path)
#
#     # Filter HTML files from the list
#     html_files = [file for file in file_list if file.endswith(".html")]
#
#     # html_files = [file for file in html_files if file == '43_Brasilia,Federal District,Brazil_Portuguese.html']
#
#     se = ws.SearchEngine()
#     vars(se)
#     compare_dict = {}
#     # Iterate over each HTML file and apply the search function
#     for html_file in html_files:
#         file_path = os.path.join(directory_path, html_file)
#         # Split the file name based on underscores
#         key_parts = html_file.split("_")
#         # Remove the file extension from the last part
#         key_parts[-1] = os.path.splitext(key_parts[-1])[0]
#
#         if len(key_parts) > 3:
#             if key_parts and key_parts[0].isdigit():
#                 key_parts.pop(1)
#                 key_parts = [key_parts[0], country_dict_short[key_parts[2]], langs_dict[key_parts[1]]]
#             else:
#                 key_parts.pop(2)
#                 key_parts = [key_parts[2], country_dict_short[key_parts[1]], langs_dict[key_parts[0]]]
#         else:
#             if key_parts[1] in country_dict_long.keys():
#                 temp = key_parts[1]
#                 key_parts[1] = country_dict_long[temp]
#         with open(file_path, "rb") as html_page:
#             html_code = html_page.read()
#         se.search('book')
#         print(html_file)
#         se.html = html_code
#         se.parse_results()
#         urls = []
#         check_url = []
#         serp_rank = 1
#         for dict in se.results:
#             try:
#                 if 'url' not in dict.keys():
#                     for dict_in_urls in dict['details']['urls']:
#                         if dict_in_urls['url'] in check_url:
#                             continue
#                         if dict_in_urls['url'] != '' and (dict_in_urls['url'].startswith('http') or dict_in_urls['url'].startswith('https')):
#                             check_url.append(dict_in_urls['url'])
#                             urls.append((serp_rank, dict_in_urls['url']))
#                 elif dict['type'] == 'ad':
#                     if dict['url'] in check_url:
#                         continue
#                     if dict['url'] != '' and (dict['url'].startswith('http') or dict['url'].startswith('https')):
#                         check_url.append(dict['url'])
#                         urls.append((serp_rank, dict['url']))
#                     try:
#                         for dict_in_urls in dict['details']['urls']:
#                             if dict_in_urls['url'] in check_url:
#                                 continue
#                             if dict_in_urls['url'] != '' and (
#                                     dict_in_urls['url'].startswith('http') or dict_in_urls['url'].startswith('https')):
#                                 check_url.append(dict_in_urls['url'])
#                                 urls.append((serp_rank, dict_in_urls['url']))
#                     except:
#                         pass
#                 else:
#                     if dict['url'] in check_url:
#                         continue
#                     if dict['url'] != '' and (dict['url'].startswith('http') or dict['url'].startswith('https')):
#                         check_url.append(dict['url'])
#                         urls.append((serp_rank, dict['url']))
#                 dict['serp_rank'] = serp_rank
#                 serp_rank += 1
#             except:
#                 dict['serp_rank'] = None
#                 continue
#         compare_dict[tuple(key_parts)] = urls
#     return compare_dict

def get_directory_path(html_date, entered_path=None):
    """
    Get the directory path for HTML files based on the specified date and optional custom path.

    Args:
        html_date (str): The date used to construct the directory path.
        entered_path (str, optional): Custom path to the directory (if provided).

    Returns:
        str: The directory path to HTML files.
    """
    if entered_path:
        return entered_path
    else:
        return f"C:/Users/Or (G)Meiri/Desktop/Work/sci-search/parser/data/{html_date}-html/html"


def parse_html_file(file_path, se):
    """
    Parse an HTML file using a SearchEngine instance and extract relevant URLs.

    Args:
        file_path (str): Path to the HTML file.
        se (SearchEngine): An instance of the SearchEngine class for parsing.

    Returns:
        list: A list of tuples containing (serp_rank, url) for relevant URLs.
    """
    with open(file_path, "rb") as html_page:
        html_code = html_page.read()
    se.search('book')
    se.html = html_code
    se.parse_results()
    urls = []
    check_url = []
    serp_rank = 1
    for result_dict in se.results:
        # print(result_dict)
        if result_dict['type'] == 'shopping_ads':
            continue
        if result_dict['type'] == 'knowledge':
            try:
                if result_dict['url'] in check_url:
                    continue
                check_url.append(result_dict['url'])
                urls.append((serp_rank, result_dict['url']))
                serp_rank += 1
                continue
            except:
                continue
        try:
            if 'url' not in result_dict.keys():
                for dict_in_urls in result_dict['details']['urls']:
                    if dict_in_urls['url'] in check_url:
                        continue
                    if dict_in_urls['url'] != '' and (
                            dict_in_urls['url'].startswith('http') or dict_in_urls['url'].startswith('https')):
                        check_url.append(dict_in_urls['url'])
                        urls.append((serp_rank, dict_in_urls['url']))
                        serp_rank += 1
                        continue
            elif result_dict['type'] == 'ad':
                if result_dict['url'] in check_url:
                    continue
                if result_dict['url'] != '' and (
                        result_dict['url'].startswith('http') or result_dict['url'].startswith('https')):
                    check_url.append(result_dict['url'])
                    urls.append((serp_rank, result_dict['url']))
                    serp_rank += 1
                try:
                    for dict_in_urls in result_dict['details']:
                        if dict_in_urls['url'] in check_url:
                            continue
                        if dict_in_urls['url'] != '' and (
                                dict_in_urls['url'].startswith('http') or dict_in_urls['url'].startswith('https')):
                            check_url.append(dict_in_urls['url'])
                            urls.append((serp_rank, dict_in_urls['url']))
                            serp_rank += 1
                except:
                    pass
                finally:
                    continue
            else:
                if result_dict['url'] in check_url:
                    continue
                if result_dict['url'] != '' and (
                        result_dict['url'].startswith('http') or result_dict['url'].startswith('https')):
                    check_url.append(result_dict['url'])
                    urls.append((serp_rank, result_dict['url']))
                    serp_rank += 1
        except:
            result_dict['serp_rank'] = None
            continue
    return urls


def run_parser(html_date, entered_path=None):
    """
       Run the HTML file parser and collect URLs from multiple HTML files.

       Args:
           html_date (str): The date associated with the HTML files.
           entered_path (str, optional): Custom path to the directory (if provided).

       Returns:
           dict: A dictionary mapping tuple keys (parsed from filenames) to lists of URLs.
       """
    directory_path = get_directory_path(html_date, entered_path)
    if directory_path.endswith("html"):
        html_files = [directory_path]
    else:
        file_list = os.listdir(directory_path)
        html_files = [file for file in file_list if file.endswith(".html")]

    # html_files = [file for file in html_files if file == '70_Berlin,Berlin,Germany_German.html']

    se = ws.SearchEngine()  # Initialize the SearchEngine

    compare_dict = {}
    for html_file in html_files:
        if directory_path.endswith("html"):
            html_file = directory_path.split("\\")[-1]
            file_path = directory_path
        else:
            file_path = os.path.join(directory_path, html_file)
        key_parts = html_file.split("_")
        key_parts[-1] = os.path.splitext(key_parts[-1])[0]

        if len(key_parts) > 3:
            if key_parts and key_parts[0].isdigit():
                key_parts.pop(1)
                key_parts = [key_parts[0], country_dict_short.get(key_parts[2], key_parts[2]),
                             langs_dict.get(key_parts[1], key_parts[1])]
            else:
                key_parts.pop(2)
                key_parts = [key_parts[2], country_dict_short.get(key_parts[1], key_parts[1]),
                             langs_dict.get(key_parts[0], key_parts[0])]
        else:
            if key_parts[1] in country_dict_long:
                temp = key_parts[1]
                key_parts[1] = country_dict_long[temp]
        print(html_file)
        urls = parse_html_file(file_path, se)
        compare_dict[tuple(key_parts)] = urls

    return compare_dict


def check_url_matches(dict_urls, df):
    """
    Checks if URLs in the DataFrame match the URLs in the dictionary.

    Args:
        dict_urls (dict): A dictionary containing URLs for each (term_id, country, langs) keys.
        df (pd.DataFrame): The DataFrame containing rows with term_id, langs, country, and Link columns.

    Returns:
        list: A list of matching results.
        int: The count of successful matches.
        int: The count of failed matches.
    """
    matching_results = []
    fails = 0
    success = 0
    for index, row in df.iterrows():
        term_id = row['term_id']
        langs = row['langs']
        country = row['country']
        link = row['Link']
        link_rank = row['Result number']
        key = (term_id, country, langs)

        if key in dict_urls:
            decoded_link = unquote(link)
            condition1 = any(decoded_link == unquote(url[1]) for url in dict_urls[key])
            condition2 = any(
                tldextract.extract(decoded_link).registered_domain == tldextract.extract(
                    unquote(url[1])).registered_domain
                for url in dict_urls[key] if "youtube" not in decoded_link
            )

            if condition1 or condition2:
                match_index = next(
                    (idx for idx, url in enumerate(dict_urls[key]) if decoded_link == unquote(url[1])
                     or (tldextract.extract(decoded_link).registered_domain == tldextract.extract(
                        url[1]).registered_domain and "youtube" not in decoded_link)),
                    None
                )
                success += 1
                match_condition = "Condition 1" if condition1 else "Condition 2"
                rank_equal = False
                if link_rank == dict_urls[key][match_index][0]:
                    rank_equal = True
                matching_results.append(
                    [match_condition, term_id, country, langs, decoded_link, dict_urls[key][match_index][1],
                     rank_equal])
            else:
                # failed_urls = ", ".join(dict_urls[key])
                failed_urls = None
                matching_results.append(["Failed", term_id, country, langs, decoded_link, failed_urls, False])
                fails += 1
    return matching_results, success, fails


def filter_csv_by_date(csv_filename, target_date):
    """
    Filters rows in a CSV file based on the "Collection date" column.

    Args:
        csv_filename (str): The path to the CSV file.
        target_date (str): The target date to filter rows.

    Returns:
        pd.DataFrame: The filtered DataFrame containing rows matching the target date.
    """
    df = pd.read_csv(csv_filename)
    filtered_df = df[df["Collection date"] == target_date]
    return filtered_df[['term_id', 'Collection date', 'langs', 'country', 'Link', 'Result number']]


def run(html_date, entered_path=None, run_parser_flag=False, save_dict=False):
    if run_parser_flag:
        print('Parser is Running')
        dict = run_parser(html_date, entered_path)
        if save_dict:
            output_file_path = "C:/Users/Or (G)Meiri/Desktop/Work/sci-search/parser/WebSearcher/result.pkl"
            with open(output_file_path, "wb") as output_file:
                pickle.dump(dict, output_file)
    else:
        print('Loading dictionary')
        input_file_path = "C:/Users/Or (G)Meiri/Desktop/Work/sci-search/parser/WebSearcher/result.pkl"
        with open(input_file_path, "rb") as input_file:
            dict = pickle.load(input_file)
    return dict


def save_progress_to_csv(success, fails, extraction_date):
    # Existing CSV file path
    progress_csv = 'C:/Users/Or (G)Meiri/Desktop/Work/sci-search/parser/parser_progress.csv'

    current_date_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Define the row to be added
    row_to_add = [current_date_time, success, fails, extraction_date]

    # Add the row to the existing CSV file
    with open(progress_csv, mode='a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(row_to_add)
    print("Row added to the CSV file successfully.")


def calculate_recall_precision(parser_output, ground_truth):
    true_positives = 0
    identified_by_parser = 0
    relevant_in_ground_truth = 0
    for l in ground_truth.values():
        relevant_in_ground_truth += len(l)

    for key, parser_urls in parser_output.items():
        if key in ground_truth:
            ground_truth_urls = ground_truth[key]
            for parser_url in parser_urls:
                decoded_parser_url = unquote(parser_url[1])
                condition1 = any(decoded_parser_url == unquote(url) for url in ground_truth_urls)
                if condition1:
                    true_positives += 1

            identified_by_parser += len(parser_urls)
    recall = true_positives / relevant_in_ground_truth
    precision = true_positives / identified_by_parser

    return recall, precision


def filter_df_by_country_lang_term_date(df, country, lang, term, date):
    filtered_df = df[
        (df["Country"] == country) & (df["Language"] == lang) & (df["Term_id"] == term) & (df["Date"] == date)]
    return filtered_df


def compare_ground_truth_to_parser_dict(parser_dict, ground_truth_df):
    matching_results = []
    fails = 0
    success = 0
    for index, row in ground_truth_df.iterrows():
        date = row['Date']
        term_id = row['Term_id']
        langs = row['Language']
        country = row['Country']
        link = row['Link']
        link_rank = row['Rank']
        key = (term_id, country, langs)

        if key in parser_dict:
            decoded_link = unquote(link)
            condition1 = any(decoded_link == unquote(url[1]) for url in parser_dict[key])

            if condition1:
                match_index = next(
                    (idx for idx, url in enumerate(parser_dict[key]) if decoded_link == unquote(url[1])),
                    None
                )
                success += 1
                match_condition = "Fail"
                if link_rank == parser_dict[key][match_index][0]:
                    match_condition = "Match"
                matching_results.append(
                    [match_condition, term_id, country, langs, date, decoded_link, parser_dict[key][match_index][1],
                    link_rank, parser_dict[key][match_index][0]])
            else:
                # failed_urls = ", ".join(parser_dict[key])
                failed_urls = None
                matching_results.append(["Failed", term_id, country, langs, date, decoded_link, failed_urls, link_rank, None])
                fails += 1
    return matching_results, success, fails


if __name__ == "__main__":
    # start = time.time()
    #
    # html_date = '20220818'
    # # path = 'C:/Users/Or (G)Meiri/Desktop/Work/sci-search/parser/data/קונספירציות - אנגלית, עברית, רוסית, ערבית, יפנית, סינית, טייוואנית, אינדונזית, קוראנית, ויאטנמית/html/8.8.2022'
    # # path = 'C:/Users/Or (G)Meiri/Desktop/Work/sci-search/parser/data/roniresult1403-20220322T200228Z-001/roniresult1403/result'
    # parsed_dict = run(html_date, run_parser_flag=True)
    # CSV_FILENAME = "C:/Users/Or (G)Meiri/Desktop/Work/sci-search/parser/data/coded_srs.csv"
    # TARGET_DATE = "18.8.2022"
    # # TARGET_DATE = "4.12.2022"
    # # TARGET_DATE = "14.3.2022"
    # # TARGET_DATE = "8.8.2022"
    # # TARGET_DATE = "28.6.2022"
    # # TARGET_DATE = "28.7.2022"
    # df = filter_csv_by_date(CSV_FILENAME, TARGET_DATE)
    #
    # matching_results, success, fails = check_url_matches(parsed_dict, df)
    #
    # columns = ["Condition", "term_id", "country", "langs", "decoded_link", "matched_url", "matched_rank"]
    # matching_results_df = pd.DataFrame(matching_results, columns=columns)
    # matching_results_df.to_csv("C:/Users/Or (G)Meiri/Desktop/Work/sci-search/parser/matching_results_df.csv",
    #                            encoding='utf-8', index=False)
    # Set the display options to show all rows and columns
    # pd.set_option('display.max_rows', None)
    # pd.set_option('display.max_columns', None)
    # print(matching_results_df)
    # print(f"Parser success: {success}")
    # print(f"Parser fails: {fails}")
    # print(f'The program ran {(time.time() - start):.2f} seconds.')
    #
    # save_progress = False
    # if save_progress:
    #     extraction_date = TARGET_DATE
    #     save_progress_to_csv(success, fails, extraction_date)

    # # Recall and Precision of the parser across all data
    # ground_truth_df = pd.read_csv("C:/Users/Or (G)Meiri/Desktop/Work/sci-search/parser/data/coded_srs.csv")
    #
    # dataset_paths = [
    #     ('C:/Users/Or (G)Meiri/Desktop/Work/sci-search/parser/data/roniresult1403-20220322T200228Z-001/roniresult1403'
    #      '/result', '14.3.2022'),
    #     # ('C:/Users/Or (G)Meiri/Desktop/Work/sci-search/parser/data/קונספירציות - אנגלית, עברית, רוסית, ערבית, יפנית, '
    #     #  'סינית, טייוואנית, אינדונזית, קוראנית, ויאטנמית/html/8.8.2022', '8.8.2022'),
    #     # ('C:/Users/Or (G)Meiri/Desktop/Work/sci-search/parser/data/קונספירציות - אנגלית, עברית, רוסית, ערבית, יפנית, '
    #     #  'סינית, טייוואנית, אינדונזית, קוראנית, ויאטנמית/html/28.6.2022', '28.6.2022'),
    #     # ('C:/Users/Or (G)Meiri/Desktop/Work/sci-search/parser/data/קונספירציות - אנגלית, עברית, רוסית, ערבית, יפנית, '
    #     #  'סינית, טייוואנית, אינדונזית, קוראנית, ויאטנמית/html/28.7.2022', '28.7.2022'),
    #     ('C:/Users/Or (G)Meiri/Desktop/Work/sci-search/parser/data/20220818-html/html', '18.8.2022'),
    #     ('C:/Users/Or (G)Meiri/Desktop/Work/sci-search/parser/data/20221204-html/html', '4.12.2022')]
    #
    # for dataset_path, dataset_date in dataset_paths:
    #     # Run your parser and get the output
    #     parser_output = run(dataset_date, dataset_path, run_parser_flag=True)
    #
    #     # Filter the ground truth data based on the dataset date
    #     filtered_ground_truth = ground_truth_df[ground_truth_df['Collection date'] == dataset_date]
    #
    #     # Convert the filtered ground truth data to a dictionary
    #     ground_truth = {}
    #     for index, row in filtered_ground_truth.iterrows():
    #         key = (row['term_id'], row['country'], row['langs'])
    #         url = row['Link']
    #         if key not in ground_truth:
    #             ground_truth[key] = []
    #         ground_truth[key].append(url)
    #     # Calculate recall and precision for this dataset
    #     recall, precision = calculate_recall_precision(parser_output, ground_truth)
    #
    #     print(f"Dataset Date: {dataset_date}")
    #     print("Recall:", recall)
    #     print("Precision:", precision)

    # --------------------------- Check with the ground truth ---------------------------
    all_success = 0
    all_failed = 0
    html_date = '20220818'
    data_folder = 'C:/Users/Or (G)Meiri/Desktop/Work/sci-search/parser/data for test/data'
    ground_truth_df = pd.read_csv(
        "C:/Users/Or (G)Meiri/Desktop/Work/sci-search/parser/data for test/data for test new.csv")
    ground_truth_df = ground_truth_df[['Country', 'Language', 'Term_id', 'Date', 'Link', 'Rank']]
    result_df = pd.DataFrame(
        columns=['match', 'term_id', 'country', 'langs', 'date', 'decoded_link', 'matched_url', 'decoded_rank', 'matched_rank'])
    for folder in os.listdir(data_folder):
        folder_path = os.path.join(data_folder, folder)
        if os.path.isdir(folder_path):
            for date in os.listdir(folder_path):
                html_path = os.path.join(folder_path, date)
                for html_file in os.listdir(html_path):
                    # if date != '04.12.2022' or html_file != '5_Paris,Paris,Ile-de-France,France_French.html':
                    #     continue
                    html_file_path = os.path.join(html_path, html_file)
                    parser_result = run(html_date, html_file_path, run_parser_flag=True)
                    # print(parser_result)
                    country = list(parser_result.keys())[0][1]
                    language = list(parser_result.keys())[0][2]
                    term_id = list(parser_result.keys())[0][0]
                    filtered_ground_truth = filter_df_by_country_lang_term_date(ground_truth_df, country, language,
                                                                                term_id, date)
                    matching_results, success, fails = compare_ground_truth_to_parser_dict(parser_result,
                                                                                           filtered_ground_truth)
                    for record in matching_results:
                        result_df = result_df.append(pd.Series(record, index=result_df.columns), ignore_index=True)

                    all_success += success
                    all_failed += fails
    print(f'number of success: {all_success} \n'
          f'number of fails: {all_failed}')
    result_df.to_csv('C:/Users/Or (G)Meiri/Desktop/Work/sci-search/parser/data for test/result_test.csv', index=False)