import openai
import requests
import pandas as pd
import io
import os, requests, json

def extract_key_terms(
    discharge_summary: str,
    diagnoses: str = None,
    model: str = "gpt-3.5-turbo"
) -> dict:
    """
    Uses the OpenAI ChatCompletion API to extract key search terms
    from a patient discharge summary. Returns a dictionary with 'summary'
    and 'conditions'.
    """
    system_content = (
        "You are a helpful assistant and your task is to help search relevant clinical trials "
        "for a given patient description. Please first summarize the main medical problems "
        "of the patient. Then generate up to 10 key conditions for searching relevant clinical "
        "trials for this patient. The key condition list should be ranked by priority. Avoid using the percentage sign when generating key conditions."
        "Please output only a JSON dict formatted as Dict{'summary': Str(summary), 'conditions': List[Str(condition)]}."
    )
    user_content = (
        f"Here is the patient description:\n\n{discharge_summary.strip()}\n\n"
        "If relevant, known diagnoses:\n"
        f"{diagnoses if diagnoses else 'None'}\n\n"
        "Extract the main medical problems and your top conditions for clinical-trial search."
    )

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content}
    ]

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.0,
        n=1
    )
    
    content = response.choices[0].message.content.strip()
    # The content will be a JSON-like string, so we need to parse it
    try:
        return eval(content)  # Convert the string to a dictionary
    except Exception as e:
        return {"error": str(e)}

def build_ctgov_query(
    base_url: str,
    parsed_terms: dict,
    page_size: int = 10,
    max_results: int = None,
    output_format: str = "csv"
) -> str:
    """
    Build the query string for the clinicaltrials.gov API endpoint.
    """
    query_params = []
    query_params.append(
        "filter.overallStatus=NOT_YET_RECRUITING%7CENROLLING_BY_INVITATION%7CRECRUITING%7CAVAILABLE"
    )
    query_params.append("sort=%40relevance")
    conditions_list = parsed_terms.get("conditions", [])
    if conditions_list:
        cond_expr = " OR ".join(conditions_list)
        query_params.append(f"query.cond={cond_expr.replace(' ', '+')}")
    interventions_list = parsed_terms.get("interventions", [])
    if interventions_list:
        intr_expr = " OR ".join(interventions_list)
        query_params.append(f"query.intr={intr_expr.replace(' ', '+')}")
    outcomes_list = parsed_terms.get("outcomes", [])
    if outcomes_list:
        outc_expr = " OR ".join(outcomes_list)
        query_params.append(f"query.outc={outc_expr.replace(' ', '+')}")
    other_terms_list = parsed_terms.get("other_terms", [])
    if other_terms_list:
        terms_expr = " OR ".join(other_terms_list)
        query_params.append(f"query.term={terms_expr.replace(' ', '+')}")
    query_params.append(f"pageSize={page_size}")
    query_params.append(f"format={output_format}")

    query_string = "&".join(query_params)
    full_url = f"{base_url}/studies?{query_string}"
    return full_url

def query_and_save_results(query_url: str, suffix: str = ""):
    """
    Given a query URL, this function will query clinicaltrials.gov and display
    the results in the console or save to a file.
    """
    print("Querying clinicaltrials.gov...")
    response = requests.get(query_url)
    if response.status_code == 200:
        content_type = response.headers.get('Content-Type', '')
        if 'csv' in content_type.lower():
            csv_content = io.StringIO(response.text)
            df = pd.read_csv(csv_content)
            # Save as CSV or print to console
            df.to_csv(f"clinical_trials_results{suffix}.csv", index=False)
            print(f"Results saved as clinical_trials_results{suffix}.csv")
        elif 'json' in content_type.lower():
            data = response.json()
            # Optionally save the JSON as a file or print it
            with open(f"clinical_trials_results{suffix}.json", 'w') as json_file:
                json.dump(data, json_file, indent=4)
            print(f"Results saved as clinical_trials_results{suffix}.json")
        else:
            print(f"Unsupported Content-Type: {content_type}")
    else:
        print(f"Request failed with status code: {response.status_code}")
