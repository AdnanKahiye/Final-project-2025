import spacy
import pandas as pd

# Load spaCy's multilingual model
nlp = spacy.load("xx_ent_wiki_sm")

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

def process_token(category, token, next_token=None):
    """
    Process a token to extract its numeric value or percentage,
    handling expressions like '20 million' or '60 thousand'.
    """
    multipliers = {
        "million": 1_000_000,
        "thousand": 1_000,
        "billion": 1_000_000_000
    }

    try:
        # Check if token is numeric or percentage
        if "%" in token:
            return float(token.replace("%", ""))
        elif token.replace(",", "").replace("$", "").isdigit():
            return float(token.replace(",", "").replace("$", ""))
        
        # Check for multipliers like "million" or "thousand"
        if next_token and next_token.lower() in multipliers:
            base_value = float(token.replace(",", ""))
            return base_value * multipliers[next_token.lower()]

    except ValueError:
        return None

def extract_financials(text):
    """
    Extract financial entities (revenue, expenses, etc.) using NLP.
    """
    doc = nlp(text)
    results = {"tirada": 1}  # Default quantity is 1 unless specified
    tokens = [token.text.lower() for token in doc]
    processed_values = set()  # Track processed (category, value) pairs
    skip_indices = set()  # Track indices that have already been processed

    for cat, keywords in keyword_categories.items():
        for keyword in keywords:
            keyword_tokens = keyword.split()  # Split multi-word keywords into tokens
            for i in range(len(tokens) - len(keyword_tokens) + 1):
                if tokens[i:i + len(keyword_tokens)] == keyword_tokens:
                    category = cat

                    # Look ahead for numeric values or multipliers
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
                            if next_token and next_token.lower() in {"million", "thousand", "billion"}:
                                skip_indices.add(j + 1)  # Skip the multiplier token
                            break

    return results

def calculate_metrics(financials):
    """
    Calculate financial metrics like profit, loss, and net income percentages.
    """
    tirada = financials.get("tirada", 1)
    qiimaha_soo_iibsiga = financials.get("qiimaha_soo_iibsiga", 0)
    qiimaha_iska_iibinta = financials.get("qiimaha_iska_iibinta", 0)
    kharashaadka = financials.get("kharashaadka", 0)
    dakhliga = financials.get("dakhliga", 0)
    faa_iidada = financials.get("faa'iidada", None)

    results = {}

    # Calculate profit from profit margin
    if faa_iidada and dakhliga:
        faa_iido = dakhliga * (faa_iidada / 100)  # Convert percentage to decimal
        results["faa_iido"] = faa_iido
        results["faa_iidada"] = faa_iidada  # Store percentage directly

    # Calculate profit or loss from buying and selling price
    if qiimaha_soo_iibsiga and qiimaha_iska_iibinta:
        faa_iido_or_khasaaro = qiimaha_iska_iibinta - qiimaha_soo_iibsiga
        if faa_iido_or_khasaaro > 0:
            results["faa'iido"] = faa_iido_or_khasaaro
            results["faa'iidada %"] = (faa_iido_or_khasaaro / qiimaha_soo_iibsiga) * 100
        elif faa_iido_or_khasaaro < 0:
            results["khasaaro"] = -faa_iido_or_khasaaro
            results["khasaaro %"] = (-faa_iido_or_khasaaro / qiimaha_soo_iibsiga) * 100

    # Calculate net profit
    if dakhliga and kharashaadka:
        dakhliga_nadiif = dakhliga - kharashaadka
        results["dakhliga nadiif ah"] = dakhliga_nadiif
        results["dakhliga %"] = (dakhliga_nadiif / dakhliga) * 100 if dakhliga else 0

    return results

# Example Usage
if __name__ == "__main__":
    text = "My revenue was 20 million and expenses were 60 thousand last year."
    financials = extract_financials(text)
    print("Extracted Financials:", financials)

    metrics = calculate_metrics(financials)
    print("Calculated Metrics:", metrics)
