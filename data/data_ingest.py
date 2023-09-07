import pandas as pd
import re

def process_markdown_file(file_path):
    with open(file_path, "r") as f:
        data = f.read()

    # Split the data using the h1: pattern
    sections = re.split(r'(?=h1:)', data.strip())

    rows = []
    for section in sections:
        row = {}
        lines = section.strip().split('\n')
        is_text = False
        text_content = []
        for line in lines:
            if line.startswith("h1:"):
                row["h1"] = line.split("h1:")[1].strip()
            elif line.startswith("h2:"):
                row["h2"] = line.split("h2:")[1].strip()
            elif line.startswith("h3:"):
                row["h3"] = line.split("h3:")[1].strip()
            elif line.startswith("PageNumber:"):
                row["pagenumber"] = line.split("PageNumber:")[1].strip()
            elif line.startswith("PageBlueBox:"):
                row["pagebluebox"] = line.split("PageBlueBox:")[1].strip()
            elif line.startswith("SectionCont:"):
                row["sectioncont"] = line.split("SectionCont:")[1].strip()
                is_text = True
            elif is_text:
                text_content.append(line)
        row["text"] = "\n".join(text_content).strip()
        rows.append(row)

    return pd.DataFrame(rows)

def concatenate_and_filter(dfs:list):
    concatenated_df = pd.concat(dfs, axis=0)
    _concatenated_df= concatenated_df[concatenated_df['text'].astype(str).str.strip() != '']
    _concatenated_df.drop_duplicates(inplace=True)
    return _concatenated_df

def split_dataframe_on_condition(df):
    condition = df['pagebluebox'].str.startswith('True')
    df_sections = df[~condition]
    df_bluebox = df[condition]
    return df_sections, df_bluebox


def clean_content_string(content_string):

    abbreviation_map= {
        "AMS ": "Arbetsmarknadsstyrelsen",
        "AT ": "arbetstillstånd",
        "AV ": "arbetsvisering",
        "BT ": "bosättningstillstånd",
        "DO ": "Ombudsmannen mot etnisk diskriminering (från 2009 Diskrimineringsombudsmannen)",
        "EES ": "Europeiska ekonomiska samarbetsområdet",
        "EFTA ": "Europeiska frihandelssammanslutningen",
        "EG ": "Europeiska gemenskapen",
        "EU ": "Europeiska unionen",
        "hm ": "hyllmeter",
        "IAESTE ": "The International Association for the Exchange of Students for Technical Experience",
        "PUT ": "permanent uppehållstillstånd",
        "RA ": "Riksarkivet",
        "SCB ": "Statistiska centralbyrån",
        "SFS ": "Svensk författningssamling",
        "SIV ": "Statens invandrarverk",
        "SOU ": "Statens offentliga utredningar",
        "SUK ": "Statens utlänningskommission",
        "UD ": "Utrikesdepartementet",
        "UNRRA ": "United Nations Relief and Rehabilitation Administration",
        "UT ": "uppehållstillstånd",
        "UV ": "uppehållsvisering",
        "YK ": "yngre kommittéer",
        "ÄK ": "äldre kommittéer"
    }
    # Strip the content
    content_string = content_string.strip()

    # Replace word breaks that occur at line endings
    pattern = r'(\w+)-\n(\w+)'
    replacement = r'\1\2'
    content_string = re.sub(pattern, replacement, content_string)

    # Replace newlines with spaces
    content_string = content_string.replace('\n', ' ')

    # Replace abbreviations
    for abb, full_form in abbreviation_map.items():
        content_string = content_string.replace(abb, full_form)

    return content_string


def sort_and_join_text(df, column_name):
    df_sorted = df.sort_values(by='pagenumber')
    df_sorted['joined_text'] = df_sorted.groupby(column_name)['text'].transform(lambda x: ' '.join(x))
    df_sorted.loc[df_sorted[column_name] == "None", 'joined_text'] = df_sorted.loc[df_sorted[column_name] == "None", 'text'].values
    return df_sorted

def process_bluebox_column(df):
    df['pagebluebox'] = df['pagebluebox'].str.replace(' ', '')
    df[['boolean_value', 'pagebluebox']] = df['pagebluebox'].str.split(',', expand=True)
    df.drop('boolean_value', axis=1, inplace=True)
    return df

def convert_columns_to_dtype(df, columns, dtype):
    for column in columns:
        df[column] = df[column].astype(dtype)
    return df

def save_df_to_json(df, filename):
    df.to_json(filename, orient='records', lines=True, force_ascii=False)


if __name__ == "__main__":

    # Using the function to process the markdown files
    df_invandring = process_markdown_file("/mock_files/kallor_till_invandring_v2.md")
    df_invandring_150 = process_markdown_file("/mock_files/kallor_till_invandring_150_2_v2.md")

    concatenated_df = concatenate_and_filter([df_invandring, df_invandring_150])

    df_sections, df_bluebox = split_dataframe_on_condition(concatenated_df)

    df_sections['text'] = df_sections['text'].apply(lambda df: clean_content_string(df))

    df_sections_sorted = sort_and_join_text(df_sections, 'pagebluebox')
    df_bluebox = process_bluebox_column(df_bluebox)
    df_bluebox_sorted = sort_and_join_text(df_bluebox, 'pagebluebox')

    columns_to_convert = ['pagebluebox', 'joined_text']
    new_dtype = "str"

    df_sections_sorted = convert_columns_to_dtype(df_sections_sorted, columns_to_convert, new_dtype)
    df_bluebox_sorted = convert_columns_to_dtype(df_bluebox_sorted, columns_to_convert, new_dtype)

    save_df_to_json(df_sections_sorted, 'invandring_section_v9.json')
    save_df_to_json(df_bluebox_sorted, 'invandring_blue_boxes_v9.json')
