import asyncio
import csv
import os
import pandas as pd
import logging
from langdetect import detect, LangDetectException
import inspect
from playwright.async_api import async_playwright

# === Constants ===
SCREENSHOT_DIR = "Regression_AI_Feature_Screenshots"
OUTPUT_CSV = "Regression_AI_Feature.csv"
ERROR_LOG_CSV = "Regression_AI_Feature_Error.csv"
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
def get_screenshot_path(lang, feature, email, suffix=""):
    folder = os.path.join(SCREENSHOT_DIR, lang, feature)
    os.makedirs(folder, exist_ok=True)
    filename = f"{email.replace('@', '_')}{('-' + suffix) if suffix else ''}.png"
    return os.path.join(folder, filename)


async def handle_response(response, email):
    if "/accelerators/llm/assistant/" in response.url:
        if response.status >= 500:
            logging.warning(
                f"🚨 500 Error: {response.status} at {response.url} for {email} details : {response.text}"
            )
            network_errors.append(
                {
                    "email": email,
                    "status": response.status,
                    "url": response.url,
                    "error": response.text,
                }
            )
        if response.status != 200:
            logging.warning(
                f"🚨 {response.status} Error: {response.status} at {response.url} for {email} details : {response}"
            )
            network_errors.append(
                {
                    "email": email,
                    "status": response.status,
                    "url": response.url,
                    "error": response,
                }
            )


async def wait_for_loader_to_disappear(
    page, selector="loading-indicator", timeout=100000
):
    try:
        await page.wait_for_selector(selector, timeout=timeout)
        await page.wait_for_selector(selector, state="detached", timeout=timeout)
    except:
        page.reload()
        await page.wait_for_load_state("domcontentloaded")
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


# # 1. Goal Assist
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
        await page.screenshot(
            path=get_screenshot_path(language, "Goal_Assist", email, "generated"),
            full_page=True,
        )
        goals = await page.wait_for_selector(
            "div.goals-assist-modal", timeout=60000
        ).inner_text()
        await page.screenshot(
            path=get_screenshot_path(language, "Goal_Assist", email, "generated2"),
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
                language, "Feeback_Summary", email, "Feeback_Summary_Generate Button"
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


# 3. Feedback Writing Assist
async def validate_feedback_writing_assist(page, email, lang, language, ai_input):
    try:
        max_retries = 5
        retry_count = 0

        while retry_count < max_retries:
            api_error_occurred = False

            def handle_response(response):
                nonlocal api_error_occurred
                if (
                    "/accelerators/llm/assistant/feedback" in response.url
                    and response.status == 500
                ):
                    api_error_occurred = True

            page.on("response", handle_response)

            # Start of flow (after reload if needed)
            await page.goto(f"{Base_url}/app/#/feedback/give")
            await wait_for_loader_to_disappear(page)

            max_retries = 5
            for retry in range(max_retries):
                await page.click("span.select2-choice.select2-default")
                await page.click("input.select2-input")
                await page.fill("input.select2-input", "bob.wilson7269@pharma.com")
                await page.wait_for_selector("ul.select2-results li", timeout=20000)
                await page.wait_for_timeout(2000)

                dropdown_text = await page.locator("ul.select2-results").inner_text()

                if "Loading failed" in dropdown_text:
                    print(f"Dropdown loading failed. Reloading... Attempt {retry + 1}")
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

            textareas = page.locator("textarea[data-ptor='give-feedback-text-area']")
            await textareas.first.click()
            await textareas.first.fill(ai_input)
            await page.screenshot(
                path=get_screenshot_path(
                    language,
                    "Feedback_Writing",
                    email,
                    "Feedback_Writing_Assist_Fill",
                ),
                full_page=True,
            )
            await page.wait_for_timeout(1000)
            await page.keyboard.press("Tab")
            await page.keyboard.press("Enter")

            await wait_for_loader_to_disappear(page)
            await page.wait_for_selector(
                "div.llm-suggestion-action-button-container", timeout=80000
            )
            ai_text = await page.locator(
                "div.llm-suggestion-text-container"
            ).inner_text()
            await page.wait_for_timeout(3000)
            await page.screenshot(
                path=get_screenshot_path(
                    language,
                    "Feedback_Writing",
                    email,
                    "Feedback_Writing_Assist_Generated_Text",
                ),
                full_page=True,
            )

            # If no API error, exit retry loop
            if not api_error_occurred:
                return {
                    "email": email,
                    "feature": "Feedback Writing Assist",
                    "expected_lang": lang,
                    "status": "✅ SUCCESS",
                    "detected_lang": "unknown",  # Update with actual detected language if available
                    "detected_text": ai_text,
                }

            retry_count += 1
            print(f"API 500 error occurred. Retrying attempt {retry_count}...")
            if api_error_occurred:
                await page.keyboard.press("Enter")
                await wait_for_loader_to_disappear(page)
                await page.wait_for_selector(
                    "div.llm-suggestion-action-button-container", timeout=80000
                )
                ai_text = await page.locator(
                    "div.llm-suggestion-text-container"
                ).inner_text()
                await page.wait_for_timeout(3000)
                await page.screenshot(
                    path=get_screenshot_path(
                        language,
                        "Feedback_Writing",
                        email,
                        "Feedback_Writing_Assist_Generated_Text",
                    ),
                    full_page=True,
                )

        return {
            "email": email,
            "feature": "Feedback Writing Assist",
            "expected_lang": lang,
            "status": "❌ FAIL (API Error after retries)",
            "detected_lang": "unknown",
            "detected_text": "N/A",
        }

    except Exception as e:
        print(f"Unexpected error: {e}")

        # If ai_text was fetched earlier, fallback to that and just log the exception
        if "ai_text" in locals() and ai_text.strip():
            detected = detect(ai_text.strip()) if ai_text.strip() else "unknown"
            status = "✅ PASS" if detected == lang else "❌ FAIL"

            return {
                "email": email,
                "feature": "Feedback Writing Assist",
                "expected_lang": lang,
                "detected_lang": detected,
                "status": status + " ⚠️ (exception after AI fetch)",
                "detected_text": ai_text,
            }

        # If truly failed, return error state
        return {
            "email": email,
            "feature": "Feedback Writing Assist",
            "expected_lang": lang,
            "status": "API ❌ ERROR",
            "detected_lang": "unknown",
            "detected_text": str(e),
        }


# 4. Conversation Assist
async def validate_conversation_assist(page, email, lang, language, ai_input):
    try:
        await page.goto(f"{Base_url}/app/#/conversations")
        await page.wait_for_timeout(1000)
        try:
            await wait_for_loader_to_disappear(page)
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


# === Main Execution ===
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1520, "height": 1080})
        results = []
        last_logged_in_email = None
        page = await context.new_page()

        with open("users.csv", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                email, lang, language, ai_input, supported = (
                    row["email"],
                    row["expected_lang"],
                    row["expected_lang_name"],
                    row["AI_input"],
                    row["supported"],
                )

                # Only process rows where 'supported' column is True
                lang = lang.split("_")[0]
                if supported == "True":
                    page.on(
                        "response",
                        lambda res: asyncio.create_task(handle_response(res, email)),
                    )

                    if email != last_logged_in_email:
                        # Login
                        await page.goto(f"{LOGIN_BASE}{email}", timeout=60000)
                        await page.fill("input#password", PASSWORD, timeout=60000)
                        await page.keyboard.press("Tab")
                        await page.wait_for_timeout(5000)
                        await page.click("button[type='submit']")
                        await page.wait_for_load_state("networkidle")
                        await page.wait_for_timeout(2000)
                        last_logged_in_email = email

                    # Run validations
                    feature_results = []

                    for feature_func in [
                        validate_feedback_summary,
                        run_goal_assist_flow,
                        validate_conversation_assist,
                        validate_feedback_writing_assist,
                    ]:
                        try:
                            params = inspect.signature(feature_func).parameters
                            if "ai_input" in params:
                                result = await feature_func(
                                    page, email, lang, language, ai_input
                                )
                            else:
                                result = await feature_func(page, email, lang, language)
                        except Exception as e:
                            logging.exception(
                                f"💥 Error during {feature_func.__name__} for {email}"
                            )
                            result = {
                                "email": email,
                                "feature": feature_func.__name__.replace(
                                    "validate_", ""
                                )
                                .replace("_", " ")
                                .title(),
                                "expected_lang": lang,
                                "status": "API ❌ ERROR",
                            }
                        feature_results.append(result)

                    results.extend(feature_results)

                    pd.DataFrame(results).to_csv(OUTPUT_CSV, index=False)
                    if network_errors:
                        pd.DataFrame(network_errors).to_csv(ERROR_LOG_CSV, index=False)

                    await page.close()

        await browser.close()
        logging.info(f"✅ All done! Results saved to {OUTPUT_CSV}")


# === Entry ===
try:
    asyncio.run(main())
except Exception as e:
    logging.exception("💥 Script crashed due to unhandled exception")
    print("💥 Script crashed. Check run_log.txt for details.")
