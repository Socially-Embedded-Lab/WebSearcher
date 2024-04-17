import WebSearcher as ws
import os
import time
import pickle
import pandas as pd
import tldextract
from urllib.parse import unquote
import datetime
import csv
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import kendalltau
from urllib.parse import urlparse, urlunparse

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
        return "/Users/ormeiri/Desktop/Work/sci-search/parser/data/" + html_date + "-html/html"


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
    # check_url = []
    # for i in se.results:
    #     print(i)
    # print('-------------------')
    serp_rank = 1
    # remove duplicate dictionaries from results
    result_cmpts = process_and_remove_duplicates(se.results)
    # for i in result_cmpts:
    #     print(i)
    for result_dict in result_cmpts:
        # print(result_dict)
        if result_dict['type'] == 'shopping_ads':
            continue
        if result_dict['type'] == 'knowledge':
            try:
                # if result_dict['url'] in check_url:
                #     continue
                # check_url.append(result_dict['url'])
                urls.append((serp_rank, result_dict['url']))
                serp_rank += 1
                continue
            except:
                continue
        try:
            if 'url' not in result_dict.keys():
                for dict_in_urls in result_dict['details']['urls']:
                    # if dict_in_urls['url'] in check_url:
                    #     continue
                    if dict_in_urls['url'] != '' and (
                            dict_in_urls['url'].startswith('http') or dict_in_urls['url'].startswith('https')):
                        # check_url.append(dict_in_urls['url'])
                        urls.append((serp_rank, dict_in_urls['url']))
                        serp_rank += 1
                        continue
            elif result_dict['type'] == 'ad':
                # if result_dict['url'] in check_url:
                #     continue
                if result_dict['url'] != '' and (
                        result_dict['url'].startswith('http') or result_dict['url'].startswith('https')):
                    # check_url.append(result_dict['url'])
                    urls.append((serp_rank, result_dict['url']))
                    serp_rank += 1
                try:
                    for dict_in_urls in result_dict['details']:
                        # if dict_in_urls['url'] in check_url:
                        #     continue
                        if dict_in_urls['url'] != '' and (
                                dict_in_urls['url'].startswith('http') or dict_in_urls['url'].startswith('https')):
                            # check_url.append(dict_in_urls['url'])
                            urls.append((serp_rank, dict_in_urls['url']))
                            serp_rank += 1
                except:
                    pass
                finally:
                    continue
            else:
                # if result_dict['url'] in check_url:
                #     continue
                if result_dict['url'] != '' and (
                        result_dict['url'].startswith('http') or result_dict['url'].startswith('https')):
                    # check_url.append(result_dict['url'])
                    urls.append((serp_rank, result_dict['url']))
                    serp_rank += 1
        except:
            result_dict['serp_rank'] = None
            continue
    for tup in urls:
        if tup[1] == '':
            urls.remove(tup)
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
    if directory_path.endswith(".html"):
        html_files = [directory_path]
    else:
        file_list = os.listdir(directory_path)
        html_files = [file for file in file_list if file.endswith(".html")]

    # html_files = [file for file in html_files if file == '38_Brasilia,Federal District,Brazil_Portuguese.html']

    se = ws.SearchEngine()  # Initialize the SearchEngine

    compare_dict = {}
    for html_file in html_files:
        if directory_path.endswith(".html"):
            html_file = directory_path.split("/")[-1]
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


def process_and_remove_duplicates(list_of_dicts):
    l = list({(v.get('cite', None), v.get('title', None), v.get('url', None)): v for v in list_of_dicts}.values())

    # Remove specified keys from each dictionary
    list_of_dicts = [{k: v for k, v in d.items() if k not in ['cmpt_rank', 'serp_rank', 'serp_id', 'title', 'sub_rank']}
                     for d in l]

    unique_dicts = list({str(i): i for i in list_of_dicts}.values())

    return unique_dicts


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
    # print(ground_truth)
    for l in ground_truth.values():
        relevant_in_ground_truth += len(l)
    check_index_parser = []
    check_index_ground_truth = []
    condition1 = False
    for key, parser_urls in parser_output.items():
        if key in ground_truth:
            ground_truth_urls = ground_truth[key]
            for parser_index, parser_url in enumerate(parser_urls):
                decoded_parser_url = unquote(parser_url[1])
                # condition1 = any(decoded_parser_url == unquote(url) for url in ground_truth_urls)
                for ground_truth_index, url in enumerate(ground_truth_urls):
                    if decoded_parser_url == unquote(url):
                        if ground_truth_index in check_index_ground_truth:
                            continue
                        condition1 = True
                        check_index_ground_truth.append(ground_truth_index)
                        check_index_parser.append(parser_index)
                        break
                    else:
                        condition1 = False
                if condition1:
                    true_positives += 1

            identified_by_parser += len(parser_urls)
    recall = true_positives / relevant_in_ground_truth
    precision = true_positives / identified_by_parser

    # Avoid division by zero if precision and recall are both 0
    if precision + recall == 0:
        f1_score = 0
    else:
        f1_score = 2 * (precision * recall) / (precision + recall)

    return recall, precision, f1_score


def calculate_kendall_tau_with_disagreement(list1, list2):
    # Create a mapping of URL to rank for each list
    rank_map1 = {url: rank for rank, url in list1}
    rank_map2 = {url: rank for rank, url in list2}

    # Combine all URLs from both lists
    all_urls = set(rank_map1.keys()).union(set(rank_map2.keys()))

    # Assign a high rank for missing URLs
    max_rank = len(all_urls)
    ranks1 = [rank_map1.get(url, max_rank) for url in all_urls]
    ranks2 = [rank_map2.get(url, max_rank) for url in all_urls]

    # Calculate Kendall tau coefficient
    tau, _ = kendalltau(ranks1, ranks2)
    return tau


def filter_df_by_country_lang_term_date(df, country, lang, term, date):
    filtered_df = df[
        (df["Country"] == country) & (df["Language"] == lang) & (df["Term_id"] == term) & (df["Date"] == date)]
    return filtered_df


def compare_ground_truth_to_parser_dict(parser_dict, ground_truth_df):
    matching_results = []
    fails = 0
    success = 0
    list_check_index = []
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
                # match_index = next(
                #     (idx for idx, url in enumerate(parser_dict[key]) if decoded_link == unquote(url[1])),
                #     None
                # )
                match_index = None
                # print(parser_dict)
                for idx, url in enumerate(parser_dict[key]):
                    # print(f'decoded_link: {decoded_link}')
                    # print(f'url[1]: {unquote(url[1])}')
                    if decoded_link == unquote(url[1]):
                        if idx in list_check_index:
                            continue
                        match_index = idx
                        list_check_index.append(idx)
                        break
                success += 1
                match_condition = "Fail"
                if link_rank == parser_dict[key][match_index][0]:
                    match_condition = "Match"
                matching_results.append(
                    [match_condition, term_id, country, langs, date, decoded_link, parser_dict[key][match_index][1],
                     link_rank, parser_dict[key][match_index][0]])
            else:
                failed_urls = None
                matching_results.append(
                    ["Failed", term_id, country, langs, date, decoded_link, failed_urls, link_rank, None])
                fails += 1
        else:
            print('I cant find the key in the parser dict')
    return matching_results, success, fails


def remove_subdomain(netloc):
    domain_parts = netloc.split('.')
    if len(domain_parts) > 2:
        domain_parts.pop(0)
    return '.'.join(domain_parts)


def canonicalize_url(url):
    if 'youtube.com' in url.lower():
        return url  # Return YouTube URLs unchanged
    parsed_url = urlparse(url.lower())
    cleaned_netloc = remove_subdomain(parsed_url.netloc)
    return parsed_url.scheme + "://" + cleaned_netloc + parsed_url.path


# Function to compare URLs between two dates
def compare_dates(dict1, dict2):
    unchanged_percentages = []

    for key in set(dict1.keys()).union(dict2.keys()):
        urls1 = set(canonicalize_url(url) for url in dict1.get(key, set()))
        urls2 = set(canonicalize_url(url) for url in dict2.get(key, set()))
        total_urls = 0
        if len(urls1) == 0 or len(urls2) == 0:
            continue
        if len(urls1) >= len(urls2):
            total_urls = len(urls1)
        else:
            total_urls = len(urls2)
        if total_urls > 0:
            unchanged = urls1.intersection(urls2)
            percentage_unchanged = (len(unchanged) / total_urls) * 100
            unchanged_percentages.append(percentage_unchanged)

    # Calculate the average percentage of unchanged URLs
    if unchanged_percentages:
        average_unchanged = sum(unchanged_percentages) / len(unchanged_percentages)
    else:
        average_unchanged = 0

    return average_unchanged


def remove_rank_from_url_list(url_list):
    return [url for rank, url in url_list]


if __name__ == "__main__":
    # start = time.time()
    #
    # html_date = '20230314'
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
    # all_success = 0
    # all_failed = 0
    # all_recall = 0
    # all_precision = 0
    # all_f1 = 0
    # tau_distance = 0
    # html_date = '20220818'
    # data_folder = '/Users/ormeiri/Desktop/Work/sci-search/parser/data for test/data'
    # ground_truth_df = pd.read_csv(
    #     "/Users/ormeiri/Desktop/Work/sci-search/parser/data for test/data for test new.csv")
    # ground_truth_df = ground_truth_df[['Country', 'Language', 'Term_id', 'Date', 'Link', 'Rank']]
    # result_df = pd.DataFrame(
    #     columns=['match', 'term_id', 'country', 'langs', 'date', 'decoded_link', 'matched_url', 'decoded_rank',
    #              'matched_rank'])
    # i = 0
    # dates_recall_precision = {'18.08.2022': [0, 0, 0, 0], '04.12.2022': [0, 0, 0, 0], '14.03.2023': [0, 0, 0, 0]}
    # languages_recall_precision = {'English': [0, 0, 0, 0], 'Arabic': [0, 0, 0, 0], 'Hebrew': [0, 0, 0, 0],
    #                               'Russian': [0, 0, 0, 0], 'French': [0, 0, 0, 0],
    #                               'Spanish': [0, 0, 0, 0], 'Swahili': [0, 0, 0, 0], 'Afrikaans': [0, 0, 0, 0],
    #                               'Indonesian': [0, 0, 0, 0],
    #                               'Farsi': [0, 0, 0, 0], 'Chinese': [0, 0, 0, 0], 'Vietnamese': [0, 0, 0, 0],
    #                               'Korean': [0, 0, 0, 0], 'Ukrainian': [0, 0, 0, 0],
    #                               'Taiwanese': [0, 0, 0, 0], 'Turkish': [0, 0, 0, 0], 'German': [0, 0, 0, 0],
    #                               'Italian': [0, 0, 0, 0], 'Portuguese': [0, 0, 0, 0],
    #                               'Polish': [0, 0, 0, 0], 'Hindi': [0, 0, 0, 0], 'Zulu': [0, 0, 0, 0]}
    # for folder in os.listdir(data_folder):
    #     folder_path = os.path.join(data_folder, folder)
    #     if os.path.isdir(folder_path):
    #         for date in os.listdir(folder_path):
    #             html_path = os.path.join(folder_path, date)
    #             for html_file in os.listdir(html_path):
    #                 # if date != '14.03.2023' or html_file != '66_Warsaw,Masovian Voivodeship,Poland_Polish.html':
    #                 #     continue
    #                 html_file_path = os.path.join(html_path, html_file)
    #                 parser_result = run(html_date, html_file_path, run_parser_flag=True)
    #                 # print(parser_result)
    #                 country = list(parser_result.keys())[0][1]
    #                 language = list(parser_result.keys())[0][2]
    #                 term_id = list(parser_result.keys())[0][0]
    #                 filtered_ground_truth = filter_df_by_country_lang_term_date(ground_truth_df, country, language,
    #                                                                             term_id, date)
    #                 # Convert the filtered ground truth data to a dictionary
    #                 ground_truth = {}
    #                 for index, row in filtered_ground_truth.iterrows():
    #                     key = (row['Term_id'], row['Country'], row['Language'])
    #                     url = row['Link']
    #                     if key not in ground_truth:
    #                         ground_truth[key] = []
    #                     ground_truth[key].append(url)
    #                 ground_truth_with_ranks = {}
    #                 for key, urls in ground_truth.items():
    #                     for index, url in enumerate(urls):
    #                         if key not in ground_truth_with_ranks:
    #                             ground_truth_with_ranks[key] = []
    #                         ground_truth_with_ranks[key] = ground_truth_with_ranks[key] + [(index + 1, url)]
    #                 # Calculate recall and precision for this dataset
    #                 recall, precision, f1 = calculate_recall_precision(parser_result, ground_truth)
    #                 dates_recall_precision[date][0] += recall
    #                 dates_recall_precision[date][1] += precision
    #                 dates_recall_precision[date][2] += f1
    #                 dates_recall_precision[date][3] += 1
    #                 languages_recall_precision[language][0] += recall
    #                 languages_recall_precision[language][1] += precision
    #                 languages_recall_precision[language][2] += f1
    #                 languages_recall_precision[language][3] += 1
    #                 all_recall += recall
    #                 all_precision += precision
    #                 all_f1 += f1
    #                 # calculate kendell tau
    #                 tau_distance += calculate_kendall_tau_with_disagreement(ground_truth_with_ranks[(term_id, country, language)],
    #                                                      parser_result[(term_id, country, language)])
    #                 i += 1
    # for date, values in dates_recall_precision.items():
    #     print(f'Average recall for date {date}: {values[0] / values[3]}')
    #     print(f'Average precision for date {date}: {values[1] / values[3]}')
    #     print(f'Average f1 for date {date}: {values[2] / values[3]}')
    # for lang, values in languages_recall_precision.items():
    #     print(f'Average recall for lang {lang}: {values[0] / values[3]}')
    #     print(f'Average precision for lang {lang}: {values[1] / values[3]}')
    #     print(f'Average f1 for lang {lang}: {values[2] / values[3]}')
    # print(f'Average recall for all data: {all_recall / i}')
    # print(f'Average precision for all data: {all_precision / i}')
    # print(f'Average f1 for all data: {all_f1 / i}')
    # print(f'Average kendall tau distance for all data: {tau_distance / i}')
    #
    # date_results = {}
    # language_results = {}
    #
    # for date, values in dates_recall_precision.items():
    #     date_results[date] = {
    #         'Precision': values[1] / values[3],
    #         'Recall': values[0] / values[3],
    #         'F1 Score': values[2] / values[3]
    #     }
    #
    # for lang, values in languages_recall_precision.items():
    #     language_results[lang] = {
    #         'Precision': values[1] / values[3],
    #         'Recall': values[0] / values[3],
    #         'F1 Score': values[2] / values[3]
    #     }
    #
    # # Convert the dictionaries to DataFrames
    # date_df = pd.DataFrame.from_dict(date_results, orient='index')
    # language_df = pd.DataFrame.from_dict(language_results, orient='index')
    #
    # # Add a 'Category' column to each DataFrame
    # date_df['Category'] = date_df.index
    # language_df['Category'] = language_df.index
    #
    # # Combine both DataFrames into one
    # combined_df = pd.concat([date_df, language_df])
    #
    # # Reorder columns if needed
    # combined_df = combined_df[['Category', 'Precision', 'Recall', 'F1 Score']]
    #
    # # Save to CSV
    # combined_df.to_csv('/Users/ormeiri/Desktop/Work/sci-search/parser/data for test/metrics_by_category.csv', index=False)

    #                 matching_results, success, fails = compare_ground_truth_to_parser_dict(parser_result,
    #                                                                                        filtered_ground_truth)
    #                 for record in matching_results:
    #                     result_df = result_df.append(pd.Series(record, index=result_df.columns), ignore_index=True)
    #
    #                 all_success += success
    #                 all_failed += fails
    # print(f'number of success: {all_success} \n'
    #       f'number of fails: {all_failed}')
    # result_df.to_csv('C:/Users/Or (G)Meiri/Desktop/Work/sci-search/parser/data for test/result_test.csv', index=False)
    # # -------------------------- Create Graph -------------------------------------------------
    # html_date = '20230314'
    # path = 'C:/Users/Or (G)Meiri/Desktop/Work/sci-search/parser/data/20230314-html/htmls_for_graphs'
    # parsed_dict = run(html_date, path, run_parser_flag=True)
    # # Extract Wikipedia ranks from the dictionary
    # rows = []
    # for key, values in parsed_dict.items():
    #     term_id, country, language = key
    #     wikipedia_link_rank = [rank for rank, link in values if "wikipedia" in link.lower()]
    #
    #     if wikipedia_link_rank:
    #         rows.append((term_id,country, language, wikipedia_link_rank[0]))
    #
    # # Create a DataFrame
    # df = pd.DataFrame(rows, columns=['ID', 'Country', 'Language', 'Rank'])
    # df.to_csv('C:/Users/Or (G)Meiri/Desktop/Work/sci-search/parser/data/20230314-html/htmls_for_graphs/wikipedia_ranks.csv', index=False)
    # df = pd.read_csv('C:/Users/Or (G)Meiri/Desktop/Work/sci-search/parser/data/20230314-html/htmls_for_graphs/wikipedia_ranks.csv')
    # # Create a scatter plot
    # filterd_df = df[(df['ID'].isin([42,38,39,58,59])) & (df['Language'].isin(['English', 'Arabic', 'French', 'Spanish']))]
    # plt.figure(figsize=(10, 6))
    # sns.scatterplot(x='Language', y='Rank', hue='ID', data=filterd_df, palette='Set1', s=100)
    #
    # # Customize the plot
    # plt.title('Scatter Plot of Rank by Language and ID')
    # plt.xlabel('Language')
    # plt.ylabel('Rank')
    # plt.grid(True)
    #
    # # Show the plot
    # plt.show()
    ##------------------------------Check pages consistency--------------------------------------
    html_dates = ['20220818', '20221204', '20230314']
    print(f'The current date is: {html_dates[0]}')
    august_dict = run(html_dates[0], run_parser_flag=True)
    # print(f'The dictionary is: {august_dict}')
    print(f'The current date is: {html_dates[1]}')
    december_dict = run(html_dates[1], run_parser_flag=True)
    # print(f'The dictionary is: {december_dict}')
    print(f'The current date is: {html_dates[2]}')
    march_dict = run(html_dates[2], run_parser_flag=True)
    # print(f'The dictionary is: {march_dict}')

    # # Remove rank from tuple
    for key, values in august_dict.items():
        august_dict[key] = sorted(remove_rank_from_url_list(values))
    for key, values in march_dict.items():
        march_dict[key] = sorted(remove_rank_from_url_list(values))
    for key, values in december_dict.items():
        december_dict[key] = sorted(remove_rank_from_url_list(values))

    # # Compare August with December, and December with March
    average_unchanged_august_december = compare_dates(august_dict, december_dict)
    average_unchanged_august_march = compare_dates(august_dict, march_dict)
    average_unchanged_december_march = compare_dates(december_dict, march_dict)
    print(f'Average percentage of unchanged URLs between August and December: {average_unchanged_august_december:.2f}%')
    print(f'Average percentage of unchanged URLs between August and March: {average_unchanged_august_march:.2f}%')
    print(f'Average percentage of unchanged URLs between December and March: {average_unchanged_december_march:.2f}%')
