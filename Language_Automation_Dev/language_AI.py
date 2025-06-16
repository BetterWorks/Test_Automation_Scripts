import openai
import pandas as pd
import json
import time
from pathlib import Path

openai.api_key = "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"  # or set via env

def evaluate_translations(source_text, translations_dict):
    system_prompt = "You are a Translation Reviewer. ONLY reply with valid JSON. No explanations."

    # Strip to requested languages only
    filtered_translations = translations_dict 

    if not filtered_translations:
        return {}

    prompt = f"""
Evaluate the following translations of a source text. Provide a score from 1 (poor) to 5 (excellent) for each translation, along with a short comment explaining the rating.

Respond ONLY in JSON format like this:
{{
  "lc1": {{
    "score": 4,
    "comment": "Fluent and accurate"
  }},
  "lc2": {{
    "score": 5,
    "comment": "Perfect translation"
  }}
}}

Source: "{source_text}"
Translations:
{json.dumps(filtered_translations, ensure_ascii=False, indent=2)}
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        reply = response.choices[0].message["content"].strip()
        print("🔍 Raw reply from evaluation:\n", reply)

        start = reply.find("{")
        end = reply.rfind("}") + 1
        json_block = reply[start:end]

        return json.loads(json_block)

    except Exception as e:
        print(f"⚠️ Self-evaluation failed: {e}")
        print(f"❗ Raw model reply was:\n{reply if 'reply' in locals() else '[No reply]'}")
        return {}


# Available languages
all_languages = {
    "cs": "Czech", "da": "Danish", "de": "German", "es": "Spanish", "es_419": "Latin American Spanish",
    "fr_CA": "French (Canada)", "fr_FR": "French (France)", "he": "Hebrew", "hi": "Hindi", "hr": "Croatian",
    "hu": "Hungarian", "id": "Indonesian", "it": "Italian", "ja": "Japanese", "ko": "Korean",
    "km": "Khmer", "ms": "Malay",
    "nl": "Dutch", "no": "Norwegian", "pl_PL": "Polish", "pt_BR": "Portuguese (Brazil)",
    "ro": "Romanian", "ru": "Russian", "sk": "Slovak", "sv": "Swedish", "th": "Thai", "tr": "Turkish",
    "uk": "Ukrainian", "vi": "Vietnamese", "zh-Hans": "Chinese (Simplified)", "zh-Hant": "Chinese (Traditional)"
}

print("Available language codes (copy and paste as needed):")
print(", ".join(all_languages.keys()))
print("\nYou can enter these codes comma-separated (e.g., es,fr_FR) or type 'all' for all languages.")

target_language_codes_str = input("Enter the language codes you want to translate into (comma-separated, e.g., es,fr_FR): ").strip()

print(f"User input (stripped): '{target_language_codes_str}'")

if target_language_codes_str == 'all':
    languages = all_languages
    print(f"Translating into all available languages: {', '.join(languages.values())}")
else:
    target_language_codes = target_language_codes_str.split(',')
    print(f"Split language codes (initial): {target_language_codes}")
    languages = {}
    valid_codes_entered = []
    for code in target_language_codes:
        stripped_code = code.strip()
        print(f"Checking stripped and lowercased code: '{stripped_code}'")
        if stripped_code in all_languages:
            languages[stripped_code] = all_languages[stripped_code]
            valid_codes_entered.append(stripped_code)
            print(f"'{stripped_code}' is a valid language.")
        else:
            print(f"Warning: '{stripped_code}' is NOT a valid language code and will be skipped.")

    if not languages:
        print("No valid language codes provided. Exiting.")
        exit()
    print(f"Translating into: {', '.join(languages.values())}")

# Load CSV
df_input = pd.read_csv("msg_input.csv").dropna(subset=["msgid", "source_reference"])

# ---- Batch Translation ----
def translate_batch(entries, target_langs, max_retries=3):
    prompt_data = {}
    for entry in entries:
        if pd.notna(entry.get("msgid_plural", None)):
            prompt_data[entry["msgid"]] = {
                "plural": entry["msgid_plural"]
            }
        else:
            prompt_data[entry["msgid"]] = {}

    prompt = f"""
Translate the following strings into these languages: {', '.join(target_langs.keys())}.
For entries with plural, return keys: "msgstr[0]", "msgstr[1]", ..., otherwise "msgstr".

Format:
{{
    "source text": {{
        "lc1": "translated",
        ...
        "lc2": {{
            "msgstr[0]": "singular",
            "msgstr[1]": "plural"
        }},
        ...
    }},
    ...
}}
Here is the input:
{json.dumps(prompt_data)}

Only return JSON.
"""

    for attempt in range(1, max_retries + 1):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            reply = response.choices[0].message["content"].strip()
            return json.loads(reply)
        except Exception as e:
            print(f"⚠️ Batch attempt {attempt} failed — {e}")
            if attempt < max_retries:
                time.sleep(2 ** (attempt - 1))
            else:
                print("❌ Giving up on batch.")
                return {}

# ---- Processing ----
BATCH_SIZE = 5
new_translated_rows = []

for i in range(0, len(df_input), BATCH_SIZE):
    batch_df = df_input.iloc[i:i+BATCH_SIZE]
    batch_input = batch_df.to_dict(orient="records")
    results = translate_batch(batch_input, languages)

    for _, row in batch_df.iterrows():
        msgid = row["msgid"]
        msgid_plural = row.get("msgid_plural", "")
        source = row["source_reference"]
        translations = results.get(msgid, {})

        flat_result = {
            "msgid": msgid,
            "msgid_plural": msgid_plural if pd.notna(msgid_plural) else "",
            "source_reference": source,
        }
        for code in languages:
            val = translations.get(code, "")
            if isinstance(val, dict):  # plural form
                for key, t in val.items():
                    flat_result[f"{code}_{key}"] = t
            else:
                flat_result[code] = val

        new_translated_rows.append(flat_result)
        # Only evaluate the translations that were selected
        selected_translations = {code: translations.get(code, "") for code in languages if code in translations}

        if selected_translations:
            evaluation = evaluate_translations(msgid, selected_translations)
        else:
            evaluation = {}

        for code in languages:
            val = translations.get(code, "")
            flat_result[f"{code}_score"] = evaluation.get(code, {}).get("score", "")
            flat_result[f"{code}_comment"] = evaluation.get(code, {}).get("comment", "")
            # Check if the score is less than 3
            if flat_result[f"{code}_score"] < 3:
                translate_batch(
                    [{"msgid": msgid, "msgid_plural": msgid_plural}],
                    {code: languages[code]}
                )
                

        

new_output_df = pd.DataFrame(new_translated_rows)

# ---- Save CSV (Overwrite Existing) ----
output_file = "translated_output.csv"
new_output_df.to_csv(output_file, index=False)
print(f"✅ Translations saved to {output_file} (existing file was overwritten).")

user_input = input("Review the translations and it's score, Do You Want to append in .po files? yes/no ").strip()

if user_input.lower() == "yes":
    # ---- Generate .po Blocks ----
    def escape_po(text):
        return text.replace('"', r'\"').replace('\n', '\\n')

    po_languages = {**languages, "en": "Template (POT)"}
    translations_per_lang = {code: [] for code in po_languages}

    for _, row in new_output_df.iterrows():
        source = row["source_reference"]
        msgid = row["msgid"]
        msgid_plural = row["msgid_plural"]

        is_plural = bool(msgid_plural.strip())

        for code in po_languages:
            block = f"\n#: {source}\nmsgid \"{escape_po(msgid)}\"\n"

            if is_plural:
                block += f"msgid_plural \"{escape_po(msgid_plural)}\"\n"
                for i in range(2):
                    key = f"{code}_msgstr[{i}]"
                    value = row.get(key, "")
                    block += f"msgstr[{i}] \"{escape_po(value)}\"\n"
            else:
                value = "" if code == "en" else row.get(code, "")
                block += f"msgstr \"{escape_po(value)}\"\n"

            translations_per_lang[code].append(block)

    # ---- Append to .po Files ----
    for code in po_languages:
        file_name = "en.pot" if code == "en" else f"{code}.po"
        po_path = Path(f"appfiles/translations/{file_name}")

        if not po_path.exists():
            print(f"⚠️ Skipping {file_name} because it doesn't exist.")
            continue

        with open(po_path, "a", encoding="utf-8") as f:
            f.write("\n")
            f.writelines(translations_per_lang[code])

    print("✅ Translations appended to .po files.")

else:
    print("❌ No changes made to .po files.")
