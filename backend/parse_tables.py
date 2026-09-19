import os
import re
import sys
import pandas as pd
from dotenv import load_dotenv
from llama_parse import LlamaParse


# Reconfigure stdout to handle UTF-8 symbols like ≤ on Windows console
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Load environment variables
load_dotenv()

def parse_pdf_tables(pdf_path: str):
    """
    Parses a PDF using LlamaParse, extracts all markdown tables,
    and returns them as a list of pandas DataFrames.
    """
    # 1. Initialize LlamaParse
    # LlamaParse preserves tables perfectly in Markdown format when result_type="markdown".
    # parse_mode="parse_page_with_lvm" uses a vision model (LVM) to identify tables accurately.
    api_key = os.getenv("LLAMA_CLOUD_API_KEY")
    if not api_key:
        raise ValueError("LLAMA_CLOUD_API_KEY environment variable is not set. Please check your .env file.")
        
    parser = LlamaParse(
        result_type="markdown",
        tier="agentic",
        version="latest",
        api_key=api_key
    )
    
    print(f"Parsing document: {pdf_path} ... (this might take a moment as it goes to LlamaCloud)")
    json_objs = parser.get_json_result(pdf_path)
    output_dir = "./extracted_images"
# Download embedded images locally
    image_dicts = parser.get_images(json_objs, download_path=output_dir)

    for img in image_dicts:
        image_file_path = img["path"]
        page_number = img.get("page", "Unknown")
        print(f"Extracted image from Page {page_number}: {image_file_path}")
        # Load and parse the document
    documents = parser.load_data(pdf_path)
    
    # Combine content from all pages/nodes
    full_text = "\n\n".join([doc.text for doc in documents])
    
    # 2. Extract markdown tables from the parsed text using regex
    # Markdown tables are bounded by '|' and contain header separator lines like |---| or |:---|
    table_pattern = re.compile(r'((?:^|\n)(?:\|[^\n]+\|\r?\n?)+)')
    tables_found = table_pattern.findall(full_text)
    
    dataframes = []
    table_index = 1
    
    for table_str in tables_found:
        table_clean = table_str.strip()
        
        # Verify it has a markdown table divider (e.g. |---| or |--|--)
        if not re.search(r'\|[\s-]*:?---+:?[\s-]*\|', table_clean):
            continue
            
        print(f"\n--- Found Markdown Table {table_index} ---")
        print(table_clean)
        
        try:
            # Clean and parse the table manually into a DataFrame to avoid version-specific pandas errors
            lines = [line.strip() for line in table_clean.split('\n') if line.strip()]
            
            table_data = []
            for line in lines:
                # Skip the alignment row (e.g. |---| or |:---|:---|)
                if re.match(r'^\|[\s\-\|:]+\|$', line):
                    continue
                
                # Split cells and strip outer pipes
                cells = [cell.strip() for cell in line.split('|')]
                if line.startswith('|'):
                    cells = cells[1:]
                if line.endswith('|'):
                    cells = cells[:-1]
                table_data.append(cells)
                
            if len(table_data) > 0:
                headers = table_data[0]
                rows = table_data[1:]
                
                # Ensure all rows have matching column lengths
                num_cols = len(headers)
                cleaned_rows = []
                for row in rows:
                    if len(row) < num_cols:
                        row = row + [''] * (num_cols - len(row))
                    elif len(row) > num_cols:
                        row = row[:num_cols]
                    cleaned_rows.append(row)
                    
                df = pd.DataFrame(cleaned_rows, columns=headers)
                dataframes.append(df)
                table_index += 1
            else:
                print(f"Table {table_index} is empty or invalid.")
        except NameError as e:
            print("name 'pd' is not defined or name 're' is not defined. Please ensure pandas and re are imported correctly.")
        except TypeError as e:
            print("'NoneType' object has no attribute 'split' or 'float' object has no attribute 'strip'. This may indicate a malformed table or unexpected content.")
        except ValueError as e:
            print(f"Could not parse Table {table_index}: {e}. Empty data passed with no index or Columns must be same length as key.")
            
    return full_text, dataframes

# if __name__ == "__main__":
#     pdf_file = "Documents/Anti_Bribery_Ethical_Conduct_Policy.pdf"
    
#     if os.path.exists(pdf_file):
#         try:
#             text, dfs = parse_pdf_tables(pdf_file)
#             print(f"\nParsing complete. Successfully extracted {len(dfs)} table(s).")
            
#             # Save tables to CSV files
#             for idx, df in enumerate(dfs):
#                 csv_name = f"table_{idx + 1}.csv"
#                 df.to_csv(csv_name, index=False)
#                 print(f"Saved Table {idx + 1} to {csv_name}")
#                 print(df.head())
#         except Exception as e:
#             print(f"Error during execution: {e}")
#     else:
#         print(f"PDF file not found at: {pdf_file}")
