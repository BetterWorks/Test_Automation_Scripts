import json
import asyncio
import csv
from itertools import islice
import os
import pandas as pd
from datetime import datetime
import logging
from langdetect import detect, LangDetectException
import inspect
from playwright.async_api import async_playwright

# === Constants ===
SCREENSHOT_DIR = "french_Final_screenshots11"
OUTPUT_CSV = "french_Final11.csv"
ERROR_LOG_CSV = "API_Errors11.csv"
PASSWORD = "test@1234"
Base_url = "https://rainforest.betterworks.com"
LOGIN_BASE = f"{Base_url}/app/splash/#/signinemail/"
FEATURE_URL = f"{Base_url}/app/#/feedback/view"

# === Setup ===
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
logging.basicConfig(
    filename="run_log.txt",
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
network_errors = []


# === Helpers ===
def get_screenshot_path(lang, feature, email, suffix="", iteration=1):
    folder = os.path.join(SCREENSHOT_DIR, lang, feature)
    os.makedirs(folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{email.replace('@', '_')}{('-' + suffix) if suffix else ''}_{iteration}_{timestamp}.png"
    return os.path.join(folder, filename)


# At module or function scope
async def handle_response(response, state):
    if "/accelerators/llm/assistant/" in response.url and response.status == 500:
        state["api_error_occurred"] = True
        try:
            text = await response.text()
            try:
                body = json.loads(text)
                state["api_error_response"] = (
                    body.get("error", {}).get("message")
                    or body.get("message")
                    or str(body)
                )
            except json.JSONDecodeError:
                state["api_error_response"] = text.strip()
        except:
            state["api_error_response"] = "Could not read API error body"


async def wait_for_loader_to_disappear(
    page, selector="loading-indicator", timeout=100000
):
    try:
        await page.wait_for_selector(selector, timeout=timeout)
        await page.wait_for_selector(selector, state="detached", timeout=timeout)
    except:
        await page.reload()
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_selector(selector, timeout=timeout)
        await page.wait_for_selector(selector, state="detached", timeout=timeout)


async def wait_AI_loader_to_disappear(
    page, selector="loading-indicator", timeout=100000
):
    try:
        await page.wait_for_selector(selector, timeout=timeout)
        await page.wait_for_selector(selector, state="detached", timeout=timeout)
    except:
        pass


async def try_click_with_loader_handling(page, selector, max_retries=3):
    for attempt in range(max_retries):
        try:
            await wait_for_loader_to_disappear(page)
            await page.click(selector, timeout=60000)
            return
        except:
            await page.reload()
            await page.wait_for_timeout(3000)
    raise Exception(f"Click failed on {selector} after {max_retries} retries.")


async def safe_click(page, selector, retries=3):
    for attempt in range(retries):
        try:
            await page.locator(selector).wait_for(state="visible", timeout=10000)
            await page.click(selector)
            return True
        except:
            await page.wait_for_timeout(2000)
    return False

    # === Feature Functions ===

    # 1. Goal Assist
    async def run_goal_assist_flow(page, email, lang, language):
        try:
            await page.goto(f"{Base_url}/app/#/goal/create")
            await wait_for_loader_to_disappear(page)

            await safe_click(page, "button.goal-assist-button")
            await page.wait_for_timeout(1000)
            await page.screenshot(
                path=get_screenshot_path(language, "Goal_Assist", email, "opened"),
                full_page=True,
            )

            await safe_click(page, "button.lin-bag-reg")
            await page.screenshot(
                path=get_screenshot_path(language, "Goal_Assist", email, "loader"),
                full_page=True,
            )
            await wait_for_loader_to_disappear(page, "div.loading-bar-container")
            await page.wait_for_timeout(60000)
            goals = await page.wait_for_selector(
                "div.goals-assist-modal", timeout=60000
            ).inner_text()
            await page.screenshot(
                path=get_screenshot_path(language, "Goal_Assist", email, "generated"),
                full_page=True,
            )
            detected = detect(goals.strip()) if goals.strip() else "unknown"
            status = "✅ PASS" if detected == lang else "❌ FAIL"
            await page.wait_for_timeout(3000)

            return {
                "email": email,
                "feature": "Goal Assist",
                "expected_lang": lang,
                "detected_lang": detected,
                "status": status,
            }
        except Exception as e:
            return {
                "email": email,
                "feature": "Goal Assist",
                "expected_lang": lang,
                "status": "❌ API ERROR",
            }

    # 2. Feedback Summary
    async def validate_feedback_summary(page, email, lang, language):
        try:
            await page.goto(FEATURE_URL)
            await wait_for_loader_to_disappear(page)

            await safe_click(page, ".feedback-summary-container")

            await safe_click(page, ".summary-year-dropdown .dropdown-toggle")
            await page.wait_for_timeout(1000)
            await page.screenshot(
                path=get_screenshot_path(
                    language, "Feeback_Summary", email, "Feeback_Summary_select_time"
                ),
                full_page=True,
            )

            await page.locator(
                "ul.dropdown-menu li.feedback-summary-year-line-item"
            ).first.click()
            await page.wait_for_timeout(5000)
            await page.screenshot(
                path=get_screenshot_path(
                    language,
                    "Feeback_Summary",
                    email,
                    "Feeback_Summary_Generate Button",
                ),
                full_page=True,
            )

            await safe_click(page, ".regenerate-button")
            await page.screenshot(
                path=get_screenshot_path(
                    language, "Feeback_Summary", email, "Feeback_Summary_loader"
                ),
                full_page=True,
            )
            await wait_for_loader_to_disappear(page)
            content = await page.locator(
                "div.summary-text-container.bottom-border-radius-collapsed"
            ).inner_text()
            await page.wait_for_timeout(100000)
            await page.screenshot(
                path=get_screenshot_path(
                    language, "Feeback_Summary", email, "Feeback_Summary_Generated"
                ),
                full_page=True,
            )
            detected = detect(content.strip()) if content.strip() else "unknown"
            status = "✅ PASS" if detected == lang else "❌ FAIL"
            await page.wait_for_timeout(3000)

            return {
                "email": email,
                "feature": "Feedback Summary",
                "expected_lang": lang,
                "detected_lang": detected,
                "status": status,
            }
        except Exception as e:
            return {
                "email": email,
                "feature": "Feedback Summary",
                "expected_lang": lang,
                "status": "API ❌ ERROR",
            }


async def validate_feedback_writing_assist(page, email, lang, language, rows):
    results = []
    state = {
        "api_error_occurred": False,
        "api_error_response": None,
    }

    # Attach response listener
    page.on("response", lambda r: asyncio.create_task(handle_response(r, state)))
    csv_exists = os.path.exists(OUTPUT_CSV)

    try:
        await page.goto(f"{Base_url}/app/#/feedback/give")
        await wait_for_loader_to_disappear(page)

        max_retries = 5
        for retry in range(max_retries):
            await page.click("span.select2-choice.select2-default")
            await page.fill("input.select2-input", "alyssa harding")
            await page.wait_for_selector("ul.select2-results li", timeout=20000)
            await page.wait_for_timeout(2000)

            dropdown_text = await page.locator("ul.select2-results").inner_text()
            if "Loading failed" in dropdown_text:
                await page.reload()
                await page.wait_for_load_state("domcontentloaded")
                continue

            if retry < 2:
                await page.locator("li.select2-result-selectable").first.click()
            else:
                await page.locator("li.select2-result-selectable").nth(1).click()

            await page.click("button[data-ptor='feedback-give-create-button']")
            await page.wait_for_timeout(1000)

            is_disabled = await page.locator(
                "button[data-ptor='give-feedback-adhoc-modal-start-btn']"
            ).get_attribute("disabled")

            if is_disabled is None:
                break
            else:
                await page.click("span.select2-choice.select2-default")
                if await page.is_visible("li.select2-no-results"):
                    await page.reload()
                    await page.wait_for_load_state("domcontentloaded")
                    continue
                else:
                    await page.keyboard.press("Enter")
                    break

        await page.click("button[data-ptor='give-feedback-adhoc-modal-start-btn']")
        await wait_for_loader_to_disappear(page)

        # Loop through each row
        for iteration, row in enumerate(rows, start=1):
            ai_text = ""
            ai_input = row["AI_input"]
            ai_lang = row["expected_lang"]

            try:
                state["api_error_occurred"] = False
                state["api_error_response"] = None

                textareas = page.locator(
                    "textarea[data-ptor='give-feedback-text-area']"
                )
                await textareas.first.click()
                await textareas.first.fill(ai_input)
                await page.screenshot(
                    path=get_screenshot_path(
                        language,
                        "Feedback_Writing",
                        email,
                        f"Feedback_Writing_Assist_Fill_iter{iteration}",
                    ),
                    full_page=True,
                )
                await page.keyboard.press("Tab")
                regenerate_button = page.locator(
                    "button.llm-action-button[ng-click*='regenerate']"
                )
                if await regenerate_button.is_visible():
                    await regenerate_button.click()
                else:
                    await page.keyboard.press("Enter")
                    await page.wait_for_timeout(1000)

                try:
                    await wait_AI_loader_to_disappear(page)
                    await page.wait_for_selector(
                        "div.llm-suggestion-action-button-container", timeout=80000
                    )

                except Exception:
                    results.append(
                        {
                            "email": email,
                            "feature": "Feedback Writing Assist",
                            "expected_lang": lang,
                            "detected_lang": "unknown",
                            "status": "API ❌ ERROR",
                            "detected_text": state["api_error_response"]
                            or "no suggestion or Error",
                        }
                    )
                await page.wait_for_timeout(5000)
                try:
                    ai_text = await page.locator(
                        "div.llm-suggestion-text-container"
                    ).inner_text()
                except:
                    continue

                await page.screenshot(
                    path=get_screenshot_path(
                        language,
                        "Feedback_Writing",
                        email,
                        f"Feedback_Writing_Generated_iter{iteration}",
                    ),
                    full_page=True,
                )

                detected_lang = (
                    detect(ai_text.strip()) if ai_text.strip() else "unknown"
                )
                detected = (
                    detected_lang.split("_")[0]
                    if "_" in detected_lang
                    else detected_lang
                )
                status = "✅ PASS" if detected == lang else "❌ FAIL"

                results.append(
                    {
                        "email": email,
                        "feature": "Feedback Writing Assist",
                        "expected_lang": lang,
                        "detected_lang": detected,
                        "status": status,
                        "detected_text": ai_text,
                    }
                )

            except Exception as e:
                logging.exception(
                    f"Error during AI input iteration {iteration} for {email}"
                )
                results.append(
                    {
                        "email": email,
                        "feature": "Feedback Writing Assist",
                        "expected_lang": lang,
                        "detected_lang": "unknown",
                        "status": "❌ FAIL (Exception)",
                        "detected_text": str(e),
                    }
                )

    except Exception as e:
        logging.exception(f"💥 Error in feedback writing assist for {email}")
        results.append(
            {
                "email": email,
                "feature": "Feedback Writing Assist",
                "expected_lang": lang,
                "detected_lang": "unknown",
                "status": "💥 Critical Error",
                "detected_text": str(e),
            }
        )

    return results


# 4. Conversation Assist
async def validate_conversation_assist(page, email, lang, language, ai_input):
    try:
        await page.goto(f"{Base_url}/app/#/conversations")
        await page.wait_for_timeout(1000)
        try:
            wait_for_loader_to_disappear(page)
        except:
            pass

        try:

            await page.click("button.conversations-nav-bar-create-button")
            await page.wait_for_timeout(1000)
        except:
            await page.reload()
            await page.wait_for_timeout(3000)
            await page.click("button.conversations-nav-bar-create-button")

        try:
            await page.click("div.select2-container.user-dropdown.dropdown-huge")
            await page.locator("li.select2-result-selectable").first.click()
        except:
            pass
        await page.click(
            "div.select2-container.dropdown-huge.input-form.ng-pristine.ng-untouched.ng-valid.ng-empty span.select2-choice"
        )
        await page.click("li.select2-result-selectable")

        await page.click('button[data-ptor="conversation-adhoc-modal-start-btn"]')
        # await page.screenshot(path=get_screenshot_path(language, "Conversation_Assist", email, "Conversation_Assist_Page"), full_page=True)
        await page.wait_for_timeout(2000)

        textarea = page.locator(
            "textarea[data-ptor='conversations-detail-response-input']"
        )
        await textarea.first.click()
        await textarea.first.fill(ai_input)
        await page.screenshot(
            path=get_screenshot_path(
                language, "Conversation_Assist", email, "Conversation_Assist_Fill"
            ),
            full_page=True,
        )

        await page.locator("span.llm-prompt-title-container").click()
        # await page.screenshot(path=get_screenshot_path(language, "Conversation_Assist", email, "Conversation_Assist_AI_Loader"), full_page=True)
        await wait_for_loader_to_disappear(page)

        ai_text = await page.locator("div.llm-assistant-container").inner_text()
        await page.wait_for_timeout(3000)
        await page.screenshot(
            path=get_screenshot_path(
                language,
                "Conversation_Assist",
                email,
                "Conversation_Assist_AI_Generated",
            ),
            full_page=True,
        )

        # Retry logic for API errors
        max_retries = 5
        retry_count = 0
        api_error_occurred = False

        async def handle_response(response):
            nonlocal api_error_occurred
            if f"{Base_url}/accelerators/llm/assistant/conversation" in response.url:
                if response.status == 500:  # Check for HTTP 500 errors
                    api_error_occurred = True

        # Attach the response handler
        page.on("response", handle_response)

        while retry_count < max_retries:
            api_error_occurred = False

            # Click the button to trigger the API call
            await page.locator("span.llm-prompt-title-container").click()

            # Wait for the loader to disappear
            await wait_for_loader_to_disappear(page)

            # Check if API error occurred
            if api_error_occurred:
                retry_count += 1
                print(f"API error detected. Retrying... Attempt {retry_count}")
                await page.wait_for_timeout(2000)  # Wait before retrying
            else:
                # If no error, break the retry loop
                break
        else:
            # If retries are exhausted, handle failure
            print("API error persisted after maximum retries.")
            return {
                "email": email,
                "feature": "Conversation Assist",
                "status": "❌ FAIL (API Error after retries)",
                "detected_lang": "unknown",
                "detected_text": "N/A",
            }

        # Extract AI-generated text after successful API call
        ai_text = await page.locator("div.llm-assistant-container").inner_text()
        detected = detect(ai_text.strip()) if ai_text.strip() else "unknown"

        # Determine the status
        status = "✅ PASS" if detected == lang else "❌ FAIL"

        # Return the result
        return {
            "email": email,
            "feature": "Conversation Assist",
            "expected_lang": lang,
            "detected_lang": detected,
            "status": status,
            "detected_text": ai_text,
        }
    except Exception as e:
        return {
            "email": email,
            "feature": "Conversation Assist",
            "expected_lang": lang,
            "status": "API ❌ ERROR",
        }


from collections import defaultdict


def group_rows_by_email(path="french_users.csv"):
    email_rows = defaultdict(list)
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in islice(reader, None):
            if row["supported"] == "True":
                email_rows[row["email"]].append(row)
    return email_rows


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1520, "height": 1080})
        results = []
        header_written = False
        network_errors = []

        email_rows = group_rows_by_email("french_users.csv")
        for email, rows in email_rows.items():
            lang = rows[0]["expected_lang"].split("_")[0]
            language = rows[0]["expected_lang_name"]
            page = await context.new_page()
            page.on(
                "response", lambda res: asyncio.create_task(handle_response(res, email))
            )

            # Login once per email
            await page.goto(f"{LOGIN_BASE}{email}", timeout=60000)
            await page.fill("input#password", PASSWORD, timeout=60000)
            await page.keyboard.press("Tab")
            await page.wait_for_timeout(10000)
            await page.click("button[type='submit']")
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(2000)

            feature_results = []

            # Only run once per email, passing all rows
            try:
                result = await validate_feedback_writing_assist(
                    page, email, lang, language, rows
                )

            except Exception as e:
                logging.exception(
                    f"💥 Error during validate_feedback_writing_assist for {email}"
                )
                result = [
                    {
                        "email": email,
                        "feature": "Feedback Writing Assist",
                        "expected_lang": lang,
                        "status": "EXCEPTION ❌",
                        "detected_lang": "unknown",
                        "detected_text": str(e),
                    }
                ]

            feature_results.extend(result)
            results.extend(feature_results)

            # Write after each email to preserve partial results
            # Write results after each email
            df = pd.DataFrame(feature_results)

            # Check if the file exists to decide whether to write the header
            header = not os.path.exists(OUTPUT_CSV)

            # Log the number of results being written
            logging.info(f"Writing {len(feature_results)} results for {email}")

            # Open the file with 'a' mode and write the data
            with open(OUTPUT_CSV, mode="a", newline="") as f:
                df.to_csv(f, header=header, index=False)
                f.flush()  # This forces the data to be written immediately

            # Log the write completion
            logging.info(f"Results written to {OUTPUT_CSV}")

            header_written = True  # After the first write, set this to True

            # Log network errors, if any
            if network_errors:
                with open(ERROR_LOG_CSV, mode="a", newline="") as f:
                    pd.DataFrame(network_errors).to_csv(f, index=False)
                    f.flush()  # Ensure network errors are written immediately

            await page.close()

        await browser.close()
        logging.info(f"✅ All done! Results saved to {OUTPUT_CSV}")


# === Entry ===
try:
    asyncio.run(main())
except Exception as e:
    logging.exception("💥 Script crashed due to unhandled exception")
    print("💥 Script crashed. Check run_log.txt for details.")

    # === Main Execution ===
#     # async def main():
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=False)
#         context = await browser.new_context(viewport={"width": 1520, "height": 1080})
#         results = []

#         with open("french_users.csv", newline="") as f:
#             reader = csv.DictReader(f)
#             for row in islice(reader, 11, None):
#                 email, lang, language, ai_input, supported = (
#                     row["email"],
#                     row["expected_lang"],
#                     row["expected_lang_name"],
#                     row["AI_input"],
#                     row["supported"],
#                 )
#                 iteration = 1

#                 # Only process rows where 'supported' column is True
#                 lang = lang.split("_")[0]
#                 if supported == "True":
#                     if email != last_logged_in_email:
#                         if "page" in locals():
#                             await page.close()

#                         page = await context.new_page()
#                         page.on(
#                             "response",
#                             lambda res: asyncio.create_task(
#                                 handle_response(res, email)
#                             ),
#                         )

#                         # if email != last_logged_in_email:
#                         # Login
#                         await page.goto(f"{LOGIN_BASE}{email}", timeout=60000)
#                         await page.fill("input#password", PASSWORD, timeout=60000)
#                         await page.keyboard.press("Tab")
#                         await page.wait_for_timeout(10000)
#                         await page.click("button[type='submit']")
#                         await page.wait_for_load_state("networkidle")
#                         await page.wait_for_timeout(2000)
#                         last_logged_in_email = email

#                         if email == last_logged_in_email:
#                             ai_input = (
#                                 row["AI_input"]
#                                 if last_ai_input != row["AI_input"]
#                                 else "next_ai_input_value"
#                             )  # Adjust this to get the next row's AI input

#                         # Run validations
#                         feature_results = []

#                         for feature_func in [
#                             # validate_feedback_summary,
#                             # run_goal_assist_flow,
#                             # validate_conversation_assist,
#                             validate_feedback_writing_assist
#                         ]:
#                             iteration += 1
#                             try:
#                                 params = inspect.signature(feature_func).parameters
#                                 if "ai_input" in params:
#                                     result = await feature_func(
#                                         page,
#                                         email,
#                                         lang,
#                                         language,
#                                         ai_input,
#                                         last_logged_in_email,
#                                     )
#                                 else:
#                                     result = await feature_func(
#                                         page, email, lang, language
#                                     )
#                             except Exception as e:
#                                 logging.exception(
#                                     f"💥 Error during {feature_func.__name__} for {email}"
#                                 )
#                                 # result = {
#                                 #     "email": email,
#                                 #     "feature": feature_func.__name__.replace("validate_", "").replace("_", " ").title(),
#                                 #     "expected_lang": lang,
#                                 #     "status": "API ❌ ERROR"
#                                 # }
#                             feature_results.append(result)

#                         results.extend(feature_results)

#                         pd.DataFrame(results).to_csv(OUTPUT_CSV, index=False)
#                         if network_errors:
#                             pd.DataFrame(network_errors).to_csv(
#                                 ERROR_LOG_CSV, index=False
#                             )

#                         await page.close()

#         await browser.close()
#         logging.info(f"✅ All done! Results saved to {OUTPUT_CSV}")
# #     async with async_playwright() as p:
# #         browser = await p.chromium.launch(headless=False)
# #         context = await browser.new_context(viewport={"width": 1520, "height": 1080})
# #         results = []

# #         email_rows = group_rows_by_email("french_users.csv", skip_rows=11)
# #         for email, rows in email_rows.items():
# #             lang = rows[0]["expected_lang"].split("_")[0]
# #             language = rows[0]["expected_lang_name"]
# #             page = await context.new_page()
# #             page.on(
# #                 "response", lambda res: asyncio.create_task(handle_response(res, email))
# #             )

# #             # Login once per email
# #             await page.goto(f"{LOGIN_BASE}{email}", timeout=60000)
# #             await page.fill("input#password", PASSWORD, timeout=60000)
# #             await page.keyboard.press("Tab")
# #             await page.wait_for_timeout(10000)
# #             await page.click("button[type='submit']")
# #             await page.wait_for_load_state("networkidle")
# #             await page.wait_for_timeout(2000)

# #             iteration = 1
# #             feature_results = []
# #             for row in rows:
# #                 lang = row["expected_lang"].split("_")[0]
# #                 language = row["expected_lang_name"]
# #                 ai_input = row["AI_input"]

# #                 for feature_func in [
# #                     # validate_feedback_summary,
# #                     # run_goal_assist_flow,
# #                     # validate_conversation_assist,
# #                     validate_feedback_writing_assist,
# #                 ]:
# #                     iteration += 1
# #                     try:
# #                         params = inspect.signature(feature_func).parameters
# #                         if "ai_input" in params:
# #                             result = await feature_func(
# #                                 page, email, lang, language, ai_input, email
# #                             )
# #                         else:
# #                             result = await feature_func(page, email, lang, language)
# #                     except Exception as e:
# #                         logging.exception(
# #                             f"💥 Error during {feature_func.__name__} for {email}"
# #                         )
# #                         result = {
# #                             "email": email,
# #                             "feature": feature_func.__name__.replace("validate_", "")
# #                             .replace("_", " ")
# #                             .title(),
# #                             "expected_lang": lang,
# #                             "status": "EXCEPTION ❌",
# #                         }
# #                     feature_results.append(result)

# #             results.extend(feature_results)

# #             pd.DataFrame(results).to_csv(OUTPUT_CSV, index=False)
# #             if network_errors:
# #                 pd.DataFrame(network_errors).to_csv(ERROR_LOG_CSV, index=False)

# #             await page.close()

# #         await browser.close()
# #         logging.info(f"✅ All done! Results saved to {OUTPUT_CSV}")


# # === Entry ===
# try:
#     asyncio.run(main())
# except Exception as e:
#     logging.exception("💥 Script crashed due to unhandled exception")
#     print("💥 Script crashed. Check run_log.txt for details.")
