import csv
import json
import os
import requests
import logging
from langchain.chat_models import ChatOllama
from langchain.schema import SystemMessage, HumanMessage
from itertools import islice

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("goal_assist_eval.log"), logging.StreamHandler()],
)

# Initialize Ollama
llm = ChatOllama(model="llama3")

# API endpoint
url = "https://rainforest.betterworks.com/accelerators/llm/goal-writing-assist"

# Input/output files
input_file = "test.csv"
output_file = "test_with_output.csv"

# Request headers
headers = {
    "Authorization": "Token 48068f86-d505-4efc-98f3-22722e878e18",
    "Content-Type": "application/json",
    "Referer": "https://rainforest.betterworks.com/haven/goals/create?ver=a34511e4766fab88b52953bbbcab68e8c4bcf750",
    "X-CSRFToken": "T1HyW0RKqDJ8ndiZJgIx6nuVR8isHjZEac4LS8h3yFqzJhQKTVqatWtslfmpwCnm",
    "Cookie": "csrftoken=rlxn6iAticRBweIVkPSNxJ9HEhe7ZtyS; sessionid=yhn4fhtk9tagicaq1y3ypcuyhbkjfkc2",
}

# Evaluation tracking
total = 0
pass_count = 0

with open(input_file, newline="", encoding="utf-8") as infile, open(
    output_file, mode="w", newline="", encoding="utf-8"
) as outfile:

    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames + ["output", "evaluation", "evaluation_status"]
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    outfile.flush()
    os.fsync(outfile.fileno())

    for idx, row in enumerate(reader, 1):

        name = row["name"]
        type_ = row["type"]
        parent = row.get("parent", "").strip()

        if type_.lower() == "milestone":
            has_parent = True
            parents = [{"id": "test", "name": parent, "type": "goal"}]
            [parent] if parent else []
        else:
            has_parent = False
            parents = []
        payload = {"name": name, "type": type_, "parents": parents}
        total += 1

        logging.info(
            f"[{idx}] Processing {type_.upper()} - {name} with parent: {parents}"
        )

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            generated_output = data.get("output", "")
            row["output"] = generated_output
            logging.info(f"[{idx}] ✅ Goal Assist output received.")

            # Ollama evaluation prompt
            eval_prompt = f"""
You are a QA assistant evaluating AI-generated text for goal or milestone creation in the Haven platform.

Your task is to validate whether the following {type_} meets the organizational writing standards and assistive guidelines.

Text:
\"{generated_output}\"

Validation criteria:

If the type is **goal**, ensure the following:
- The goal starts with a dynamic (action-oriented) verb.
- The goal is between 3 and 12 words. But not mandatory.
- The goal includes a clear context of what is to be achieved, optionally using custom organizational terms.
- If no metrics are provided, suggest an appropriate metric placeholder.

If the type is **milestone**, ensure the following:
- The milestone is actionable and specific (clearly describes an action to be taken).
- At least one measurable metric is defined or implied (e.g., survey results, version release, number of users).
- If no metric is given, suggest a suitable placeholder metric.
- The milestone logically supports or aligns with its parent goal (considering the context provided by the goal).

Provide a clear pass/fail judgment with up to 50-character bullet points explaining the result. If any metrics are missing, suggest an appropriate placeholder.
"""

            messages = [
                SystemMessage(
                    content="You are a QA evaluator for goal-writing assist."
                ),
                HumanMessage(content=eval_prompt),
            ]
            eval_result = llm(messages)
            evaluation_text = eval_result.content.strip()
            row["evaluation"] = evaluation_text

            # Determine PASS/FAIL from content
            if "PASS" in evaluation_text.upper():
                row["evaluation_status"] = "PASS"
                pass_count += 1
                logging.info(f"[{idx}] ✅ PASS")
            else:
                row["evaluation_status"] = "FAIL"
                logging.warning(f"[{idx}] ⚠️ FAIL")

        except Exception as e:
            error_msg = str(e)
            row["output"] = f"Error: {error_msg}"
            row["evaluation"] = "Evaluation skipped due to error."
            row["evaluation_status"] = "SKIPPED"
            logging.error(f"[{idx}] ❌ Error occurred: {error_msg}")

        # Write and flush
        writer.writerow(row)
        outfile.flush()
        os.fsync(outfile.fileno())

# Final summary
pass_rate = (pass_count / total) * 100 if total else 0
logging.info(f"✅ Evaluation completed: {pass_count}/{total} passed ({pass_rate:.2f}%)")
logging.info(f"📄 Results saved to {output_file}")
