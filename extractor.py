import spacy
import pandas as pd

# Load spaCy's multilingual model
nlp = spacy.load("xx_ent_wiki_sm")

# Somali number words mapping
somali_numbers = {
    "hal": 1,
    "labo": 2,
    "saddex": 3,
    "afar": 4,
    "shan": 5,
    "lix": 6,
    "todobo": 7,
    "sideed": 8,
    "sagaal": 9,
    "toban": 10,
    "konton": 50,
    "boqol": 100,
    "kun": 1_000
}

# Function to load keywords from a CSV file
def load_keywords_from_csv(file_path):
    df = pd.read_csv(file_path)
    keyword_dict = {}
    for category in df['Category'].unique():
        keyword_dict[category] = df[df['Category'] == category]['Keyword'].tolist()
    return keyword_dict

# Load keywords from the CSV file
file_path = r"C:/Users/hp/Desktop/Django Course/keyword_categories.csv"
keyword_categories = load_keywords_from_csv(file_path)

# Function to process a token and extract numeric values
def process_token(category, token, next_token=None):
    """
    Process a token to extract numeric values, percentages, or values with multipliers like "milyan".
    """
    multipliers = {
        "milyan": 1_000_000,
        "kun": 1_000,
        "bilyan": 1_000_000_000
    }
    try:
        # Handle percentages
        if category in {"faa'iidada", "heerka koboca", "heerka"}:
            if "%" in token:
                return float(token.replace("%", ""))
            elif next_token == "%":
                return float(token)

        # Handle values with multipliers like "milyan" or "kun"
        if next_token and next_token.lower() in multipliers:
            base_value = float(token.replace(",", ""))
            return base_value * multipliers[next_token.lower()]

        # Handle plain numeric values
        return float(token.replace(",", "").replace("$", ""))
    
    except ValueError:
        return None

# Function to calculate quantity from tokens based on Somali number words
def calculate_quantity_from_text(tokens):
    """
    Calculate quantity ('tirada') based on Somali number words in the text.
    """
    quantity = 0  # Start from 0
    for token in tokens:
        if token in somali_numbers:
            quantity += somali_numbers[token]
    return quantity if quantity > 0 else 1  # Default to 1 if no numbers are found

# Function to extract financial data from text
def extract_financials(text):
    """
    Extract financial entities (revenue, expenses, etc.) using NLP.
    """
    doc = nlp(text)
    results = {}
    tokens = [token.text.lower() for token in doc]

    # Calculate 'tirada' based on Somali number words
    results["tirada"] = calculate_quantity_from_text(tokens)

    processed_values = set()  # Track processed (category, value) pairs
    skip_indices = set()  # Track indices that have already been processed

    for cat, keywords in keyword_categories.items():
        for keyword in keywords:
            keyword_tokens = keyword.split()  # Split multi-word keywords into tokens
            for i in range(len(tokens) - len(keyword_tokens) + 1):
                if tokens[i:i + len(keyword_tokens)] == keyword_tokens:
                    category = cat

                    # Look ahead for numeric values or percentages
                    for j in range(i + len(keyword_tokens), len(tokens)):
                        if j in skip_indices:
                            continue  # Skip already processed tokens

                        token_text = tokens[j]
                        next_token = tokens[j + 1] if j + 1 < len(tokens) else None
                        value = process_token(category, token_text, next_token)

                        if value is not None:
                            # Avoid duplicates
                            if (category, value) in processed_values:
                                break

                            # Update results based on category
                            results[category] = results.get(category, 0) + value
                            processed_values.add((category, value))
                            skip_indices.add(j)  # Mark token as processed
                            if next_token == "%":
                                skip_indices.add(j + 1)  # Skip the "%" token
                            break

    return results

# Function to calculate financial metrics
def calculate_metrics(financials):
    """
    Calculate metrics based on extracted financials.
    """
    tirada = financials.get("tirada", 1)
    qiimaha_soo_iibsiga = financials.get("qiimaha_soo_iibsiga", 0)
    qiimaha_iska_iibinta = financials.get("qiimaha_iska_iibinta", 0)
    kharashaadka = financials.get("kharashaadka", 0)
    dakhliga = financials.get("dakhliga", 0)
    faa_iidada = financials.get("faa'iidada", None)
    khasaaradda = financials.get("khasaarada", None)

    results = {}

    # Calculate profit from profit margin
    if faa_iidada and dakhliga:
        faa_iido = dakhliga * (faa_iidada / 100)  # Convert percentage to decimal
        results["faa_iido"] = faa_iido
        results["faa_iidada"] = faa_iidada  # Store percentage directly

    # Calculate profit or loss from buying and selling price
    if qiimaha_soo_iibsiga and qiimaha_iska_iibinta:
        results['kharashaadka'] =qiimaha_soo_iibsiga*tirada
        results['dakhliga'] =qiimaha_iska_iibinta*tirada
        faa_iido_or_khasaaro = qiimaha_iska_iibinta - qiimaha_soo_iibsiga
        if faa_iido_or_khasaaro > 0:
            results["faa'iido"] = faa_iido_or_khasaaro
            results["faa'iidada % "] = (faa_iido_or_khasaaro / qiimaha_soo_iibsiga) * 100
        elif faa_iido_or_khasaaro < 0:
            results["khasaaro"] = -faa_iido_or_khasaaro
            results["khasaaro % :"] = (-faa_iido_or_khasaaro / qiimaha_soo_iibsiga) * 100

    # Calculate net profit
    if dakhliga and kharashaadka:
        dakhliga_nadiif = dakhliga - kharashaadka
        results["dakhliga hadda :"] = dakhliga_nadiif

    return results
