import openai
import requests
import pandas as pd
import io
import os, requests, json

def evaluate_criteria(
    patient_summary: str,
    inclusion_criteria: list,
    exclusion_criteria: list,
    model: str = "gpt-3.5-turbo"
) -> dict:
    """
    Passes the patient's summary and the list of inclusion/exclusion criteria to OpenAI,
    returning a structured response indicating for each criterion whether it's met or not.

    :param patient_summary: A text description of the patient's relevant data (demographics, labs, diagnoses, etc.)
    :param inclusion_criteria: A list of bullet-point strings for inclusion criteria.
    :param exclusion_criteria: A list of bullet-point strings for exclusion criteria.
    :param model: The name of the OpenAI model to use (default: gpt-3.5-turbo).
    :return: A dictionary with 'inclusion_results' and 'exclusion_results',
             each a list of objects like {"criterion": str, "met": bool, "reason": str}.
    """

    # Convert lists into bullet points for the prompt
    inclusion_text = "\n".join(f"- {c}" for c in inclusion_criteria)
    exclusion_text = "\n".join(f"- {c}" for c in exclusion_criteria)

    # System instruction: how we want the assistant to behave
    system_prompt = (
        "You are a helpful assistant that determines patient eligibility for a clinical trial. "
        "You have a patient's summary and a trial's inclusion/exclusion criteria. "
        "For each criterion, decide if the patient meets it (TRUE/FALSE/UNKNOWN) and briefly explain why."
        "If there is no mention or indication of a criteria being met in the patient summary, it should be UNKNOWN."
        "Additionally, if a criterion involves the patient providing consent or patient willingness (e.g., 'Patient has provided informed consent'), "
        "you should automatically assume it is met."
    )

    user_prompt = (
        f"Patient summary:\n{patient_summary}\n\n"
        "Inclusion Criteria:\n"
        f"{inclusion_text}\n\n"
        "Exclusion Criteria:\n"
        f"{exclusion_text}\n\n"
        "For each inclusion and exclusion criterion, respond with **valid JSON** only in this format:\n"
        "{\n"
        "  \"inclusion_results\": [\n"
        "    {\"criterion\": \"<inclusion bullet>\", \"met\": \"true\"/\"false\"/\"unknown\", \"reason\": \"<short explanation>\"},\n"
        "    ...\n"
        "  ],\n"
        "  \"exclusion_results\": [\n"
        "    {\"criterion\": \"<exclusion bullet>\", \"met\": \"true\"/\"false\"/\"unknown\", \"reason\": \"<short explanation>\"},\n"
        "    ...\n"
        "  ]\n"
        "}\n"
        "Important: each value for \"met\" should be a string: \"true\", \"false\", or \"unknown\".\n"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    response = openai.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.0,
        n=1
    )

    # Attempt to parse JSON from the assistant's reply
    raw_reply = response.choices[0].message.content.strip()
    try:
        parsed = json.loads(raw_reply)
    except json.JSONDecodeError:
        # If parsing fails
        parsed = {
            "inclusion_results": [],
            "exclusion_results": [],
            "error": f"Could not parse as JSON: {raw_reply}"
        }

    return parsed

def find_trial_id(trial_ids):
    """
    Retrieves study data for one or more NCT Ids (trial_ids) from
    the clinicaltrials.gov v2 API and returns the JSON response,
    all wrapped under a top-level 'studies' key.

    :param trial_ids: A single NCT trial ID (str) or a list of them (list[str]).
                      E.g., "NCT06609772" or ["NCT06609772", "NCT04076449"]
    :return: Dict with a "studies" key. Each element in "studies" is
             the JSON for a single trial.
    """
    # If a single string is passed, convert to a list for uniform handling.
    if isinstance(trial_ids, str):
        trial_ids = [trial_ids]

    base_url = "https://clinicaltrials.gov/api/v2/studies/"

    all_studies = []

    for tid in trial_ids:
        params = {
            "format": "json",
            "markupFormat": "markdown"
        }
        endpoint = f"{base_url}{tid}"

        try:
            response = requests.get(endpoint, params=params)

            if response.status_code == 200:
                data = response.json()

                # Ensure we always output a list under 'studies'.
                if "studies" not in data:
                    data = {
                        "studies": [data]
                    }

                # Append each study from the response
                all_studies.extend(data["studies"])

            else:
                # Put an error object in the list so we don't lose track of
                # which trial had a problem.
                all_studies.append({
                    "nctId": tid,
                    "error": f"Unexpected status code: {response.status_code}",
                    "detail": response.text
                })

        except requests.RequestException as e:
            # If there’s a connection error or other request-related error,
            # store an error object in place of the study.
            all_studies.append({
                "nctId": tid,
                "error": str(e)
            })

    return {"studies": all_studies}

def get_score(trial_data):
    # defined custom scoring
    inclusion_scores = {'true': 1, 'false': 0, 'unknown': 0.5}
    exclusion_scores = {'true': 0, 'false': 1, 'unknown': 0.5}
    inclusion_results = trial_data.get("inclusion_results", [])
    exclusion_results = trial_data.get("exclusion_results", [])

    # extract total inclusion and exclusion scores
    total_inclusion = sum(inclusion_scores[item["met"]] for item in inclusion_results)
    total_exclusion = sum(exclusion_scores[item["met"]] for item in exclusion_results)

    # extract unmet criteria score for tie breakers
    # double check this logic
    unmet_inclusion = sum(1 for item in inclusion_results if item["met"].lower() == "false")
    unmet_exclusion = sum(1 for item in exclusion_results if item["met"].lower() == "true")

    total_unmet = unmet_inclusion + unmet_exclusion
    num_criteria = len(inclusion_results) + len(exclusion_results)
    total_score = (total_inclusion + total_exclusion) / num_criteria

    return total_inclusion, total_exclusion, total_unmet, total_score

def rank_trials(json_data):
    trial_scores = []

    # data is api response
    # calculate scores using helper function above
    for trial_id, trial_data in json_data.items():
        total_inclusion, total_exclusion, total_unmet, total_score = get_score(trial_data)

        # this is what is output to dataframe/user or what whatever info we want to output
        trial_info = {
            "trial_id": trial_id,
            "inclusion_score": total_inclusion,
            "exclusion_score": total_exclusion,
            "unmet_criteria": total_unmet,
            "total_score": total_score * 100
        }
        trial_scores.append(trial_info)

    # sort the trials by score and unmet criteria to rank
    sorted_trials = sorted(trial_scores, key = lambda x: (-x["total_score"], x["unmet_criteria"]))

    # apply to original data in json format and add the total score
    ranked_data = {}
    for i, trial in enumerate(sorted_trials):
        trial_id = trial["trial_id"]

        ranked_data[trial_id] = json_data[trial_id].copy()

        ranked_data[trial_id]["ranking"] = {
            "rank": i + 1,
            "total_score": trial["total_score"]
        }

    return ranked_data

def get_results(json_data):
    ranked_trials = rank_trials(json_data)

    return ranked_trials

def evaluate_patient_eligibility_for_studies(
    patient_summary: str,
    ctgov_data: dict,
    model: str = "gpt-3.5-turbo"
) -> dict:
    """
    Loops through a JSON object from clinicaltrials.gov v2.
    Extracts eligibility criteria for each study, and uses OpenAI
    to check if the patient meets them.

    :param patient_summary: Text describing the patient (medical history, labs, etc.).
    :param ctgov_data: The JSON data from clinicaltrials.gov, e.g. data['studies'] array.
    :param model: The OpenAI model name.
    :return: A dict keyed by NCTId or study index, each with the parsed evaluation.
    """
    results = {}

    # The 'studies' list from the clinicaltrials.gov v2 JSON
    # often is in 'ctgov_data["studies"]'
    if "studies" not in ctgov_data:
        print("No 'studies' key found in data. Returning empty.")
        return results
    for study in ctgov_data["studies"]:
        # Typically the NCTId is in identificationModule
        # e.g., study["protocolSection"]["identificationModule"]["nctId"]
        try:
            nct_id = study["protocolSection"]["identificationModule"]["nctId"]
            print(nct_id)
        except KeyError:
            nct_id = "UNKNOWN"

        # Extract eligibility text
        # Usually: study["protocolSection"]["eligibilityModule"]["eligibilityCriteria"]
        # This is often a single string with both Inclusion and Exclusion criteria.
        try:
            eligibility_text = study["protocolSection"]["eligibilityModule"]["eligibilityCriteria"]
            print(eligibility_text)
        except KeyError:
            print(f"No eligibilityModule found for {nct_id}, skipping.")
            continue

        inclusion_bullets = []
        exclusion_bullets = []

        # A naive split that tries to separate by "Inclusion" or "Exclusion" headings:
        lines = eligibility_text.splitlines()
        current_section = None
        for ln in lines:
            line_stripped = ln.strip()
            if not line_stripped:
                continue
            # Check for headings
            lower_line = line_stripped.lower()
            if "inclusion criteria" in lower_line:
                current_section = "inclusion"
                continue
            elif "exclusion criteria" in lower_line:
                current_section = "exclusion"
                continue

            # If line starts with a bullet or something, we treat it as a bullet
            if current_section == "inclusion":
                inclusion_bullets.append(line_stripped)
            elif current_section == "exclusion":
                exclusion_bullets.append(line_stripped)

        # Now pass to the function that calls OpenAI
        print("\nEvaluating criteria...")
        eligibility_result = evaluate_criteria(
            patient_summary=patient_summary,
            inclusion_criteria=inclusion_bullets,
            exclusion_criteria=exclusion_bullets,
            model=model
        )
        print(f"Finished evaluating criteria for {nct_id}\n")
        results[nct_id] = eligibility_result

    # Add rankings to JSON file
    results = get_results(results)
    return results

def get_study_by_nct(ctgov_json: dict, nct_id: str):
    """
    Return the first study in ctgov_json['studies'] whose
    identificationModule.nctId matches `nct_id` (case‑insensitive).
    """
    if not ctgov_json or "studies" not in ctgov_json:
        return None

    for study in ctgov_json["studies"]:
        try:
            sid = study["protocolSection"]["identificationModule"]["nctId"]
            if sid.lower() == nct_id.lower():
                return study
        except KeyError:
            continue
    return None