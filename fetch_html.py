import pandas as pd
from scripts.scraper import Scraper
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
from bs4 import BeautifulSoup
import glob
import matplotlib.pyplot as plt
import seaborn as sns


def fetch_html(url, headers):
    try:
        scraper = Scraper(url, headers=headers)
        scraper.fetch()
        return url, scraper.soup
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return url, None


def main_create_csvs():
    df = pd.read_csv('/Users/ormeiri/Desktop/Work/sci-search/parser/data/coded_srs.csv')
    save_interval = 10  # Save after every 10 links
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Connection': 'keep-alive'
    }

    for start_index in tqdm(range(490, len(df), save_interval), desc="Processing batches"):
        end_index = min(start_index + save_interval, len(df))
        batch_df = df.iloc[start_index:end_index].copy()
        batch_df['raw_html'] = [None] * len(batch_df)  # Initialize with None

        # Create a list of URLs for the batch
        url_list = [(row['Link'], headers) for index, row in batch_df.iterrows()]

        with ProcessPoolExecutor() as executor:
            # Submit all tasks to the executor
            future_to_url = {executor.submit(fetch_html, url, headers): url for url, headers in url_list}

            # Process the results as they are completed
            for future in as_completed(future_to_url):
                url, html = future.result()
                if html is not None:
                    index = batch_df[batch_df['Link'] == url].index[0]
                    batch_df.at[index, 'raw_html'] = html

        interim_file = f'/Users/ormeiri/Desktop/Work/sci-search/parser/data/data_with_html/progress_{start_index + 1}.csv'
        batch_df.to_csv(interim_file, index=False)
        print(f"Batch starting at index {start_index + 1} saved.")

    print("Scraping completed.")


def concat_csvs(folder_path):
    """
    Concatenates all CSV files in the specified folder into one DataFrame,
    drops rows with null values in the 'raw_html' column,
    and optionally saves the result to a CSV file.

    Parameters:
    folder_path (str): Path to the folder containing the CSV files.

    Returns:
    pd.DataFrame: The concatenated DataFrame.
    """

    # Use glob to get all CSV files in the folder
    csv_files = glob.glob(f'{folder_path}/*.csv')

    # List to hold DataFrames
    dfs = []

    # Read each CSV file and append to list
    for file in csv_files:
        df = pd.read_csv(file)
        dfs.append(df)

    # Concatenate all DataFrames into one and drop rows with null 'raw_html'
    combined_df = pd.concat(dfs, ignore_index=True)
    combined_df.dropna(subset=['raw_html'], inplace=True)

    return combined_df


# Example function to extract text from paragraph tags
def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    paragraphs = soup.find_all('p')
    text = ' '.join([para.get_text() for para in paragraphs])
    return text


if __name__ == "__main__":
    # main_create_csvs()
    combined_df = concat_csvs('/Users/ormeiri/Desktop/Work/sci-search/parser/data/data_with_html')
    combined_df['extracted_text'] = combined_df['raw_html'].apply(
        lambda html: extract_text_from_html(html) if pd.notnull(html) else '')
    combined_df.rename(columns={'Quality mean פרופורציה_new': 'quality_mean',
                                'Accessibility mean פרופורציה ': 'accessibility_mean',
                                'SSI mean פרופורציה': 'ssi_mean'}, inplace=True)

    # Standardize the category names:
    combined_df['type'] = combined_df['type'].replace({
        'Conspiracy theories': 'Conspiracy Theories',
        'Socio-Scientific Isuues': 'Socio-Scientific Issues'  # Correct the spelling
    })

    # combined_df = pd.read_csv('/Users/ormeiri/Desktop/Work/sci-search/parser/data/combined_data_new.csv')

    # Plotting distributions
    for column in ['quality_mean', 'accessibility_mean']:
        plt.figure()
        sns.histplot(combined_df[column], kde=True)
        if column == 'quality_mean':
            plt.title('Distribution of Quality Mean')
            plt.xlabel('Quality Mean')
        else:
            plt.title('Distribution of Accessibility Mean')
            plt.xlabel('Accessibility Mean')
        plt.ylabel('Frequency')
        plt.show()

    combined_df.dropna(subset=['extracted_text'], inplace=True)
    combined_df.to_csv('/Users/ormeiri/Desktop/Work/sci-search/parser/data/combined_data_new.csv', index=False)
