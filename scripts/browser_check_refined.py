"""Desktop/mobile, request freshness and motion checks for the React workspace."""

import argparse
import json
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


def idle(page):
    expect(page.locator("#queue-content")).to_have_attribute("aria-busy", "false")


def no_overflow(page):
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), (
        "Page-level horizontal overflow"
    )


def chart_type(page):
    assert page.locator(".data-chart text").first.evaluate(
        "element => getComputedStyle(element).stroke === 'none'"
    )
    size = page.locator(".data-chart text").first.evaluate(
        "element => { const svg=element.ownerSVGElement;const bounds=svg.getBoundingClientRect();return parseFloat(getComputedStyle(element).fontSize)*Math.min(bounds.width/svg.viewBox.baseVal.width,bounds.height/svg.viewBox.baseVal.height); }"
    )
    assert size >= 11, f"Chart text too small: {size}"


def capture(page, path, full_page=True):
    if full_page:
        page.evaluate("window.scrollTo(0,0); document.activeElement?.blur()")
    page.evaluate("document.fonts.ready")
    # The longest authored transition is a 450ms chart draw. Capture settled
    # frames, rather than a clipped outcome or a scrolled fixed-position rail.
    page.wait_for_timeout(500)
    page.screenshot(path=str(path), full_page=full_page)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8010")
    parser.add_argument("--output", type=Path, default=Path("verification/refinement-browser"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    checks, errors = [], []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 1080}, reduced_motion="no-preference"
        )
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(args.url, wait_until="networkidle")
        expect(page.locator("#buyers [data-buyer]")).to_have_count(50)
        expect(page.locator("#buyer-title")).to_contain_text("Buyer")
        expect(page.locator("#summary")).to_contain_text("Hidden")
        page.keyboard.press("Tab")
        assert page.locator(".skip").evaluate("element => element === document.activeElement")
        page.locator(".skip").evaluate("element => element.blur()")
        checks.append("real experiment loads with hidden outcomes and keyboard skip navigation")
        capture(page, args.output / "desktop-queue.png")
        page.locator("#reveal").click()
        expect(page.locator("#reveal")).to_have_text("Hide outcomes")
        idle(page)
        expect(page.locator("#summary")).to_contain_text("of eligible buyers")
        # Use the real rendered options: this check exercises browser navigation
        # without introducing a separate Node HTTP client/TLS transport.
        dates = page.locator("#date option").evaluate_all(
            "options => options.map(option => option.value)"
        )
        assert len(dates) >= 2
        metadata = page.evaluate(
            "async () => { const response = await fetch('/api/metadata'); "
            "if (!response.ok) throw new Error('Metadata unavailable'); return response.json(); }"
        )
        page.locator("#date").select_option(dates[0])
        expect(page.locator("#summary")).to_contain_text("Hidden")
        idle(page)
        assert page.get_by_role("button", name="Previous historical Monday").is_disabled()
        page.get_by_role("button", name="Next historical Monday").click()
        idle(page)
        assert page.locator("#date").input_value() == dates[1]
        checks.append("explicit reveal, eligible-population context and date reset/steppers work")
        page.locator("#model").select_option("gamma_poisson")
        page.locator("#capacity").select_option("100")
        expect(page.locator("#buyers [data-buyer]")).to_have_count(100)
        second = page.locator("#buyers [data-buyer]").nth(1)
        buyer_id = second.get_attribute("data-buyer")
        second.click()
        expect(page.locator("#buyer-title")).to_have_text(f"Buyer {buyer_id}")
        checks.append("model/capacity switching and current buyer detail stay aligned")
        page.locator("#search").fill("999999")
        expect(page.get_by_role("heading", name="No buyers in this view.")).to_be_visible()
        assert (
            page.locator("#export").get_attribute("href") is not None
        )  # A valid empty export is allowed.
        page.get_by_role("button", name="Clear filters", exact=True).last.click()
        expect(page.locator("#buyers [data-buyer]")).to_have_count(100)
        checks.append("empty search provides explicit clear-filter recovery")

        def fail_queue(route):
            route.abort()

        page.route("**/api/queue?**", fail_queue)
        page.locator("#capacity").select_option("50")
        expect(
            page.get_by_role("heading", name="We couldn’t update the shortlist.")
        ).to_be_visible()
        expect(page.locator("#export")).to_have_attribute("aria-disabled", "true")
        assert page.locator("#export").get_attribute("href") is None
        page.unroute("**/api/queue?**", fail_queue)
        page.get_by_role("button", name="Retry loading", exact=True).click()
        expect(page.locator("#buyers [data-buyer]")).to_have_count(50)
        expect(page.locator("#export")).to_have_attribute("aria-disabled", "false")
        assert "capacity=50" in page.locator("#export").get_attribute("href")
        checks.append("failed queries cannot export stale data; retry restores a matching export")
        with page.expect_download() as downloaded:
            page.locator("#export").click()
        downloaded.value.save_as(str(args.output / "queue.csv"))
        assert (
            "target" not in (args.output / "queue.csv").read_text(encoding="utf-8").splitlines()[0]
        )
        checks.append("exported CSV respects the current query and hidden-outcome state")
        page.get_by_role("button", name="Model evidence", exact=True).click()
        expect(page.locator("#evidence-title")).to_be_visible()
        expect(page.locator("#evidence-title")).to_be_focused()
        expect(page.locator(".evidence-contract")).to_contain_text(
            metadata["models"][metadata["selected_model"]]
        )
        expect(page.locator(".scope-note")).to_contain_text("independently")
        expect(page.locator(".cohort-table")).to_contain_text("Order rate")
        chart_type(page)
        page.locator(".data-chart").first.focus()
        before = page.locator(".chart-readout").inner_text()
        page.keyboard.press("ArrowLeft")
        assert page.locator(".chart-readout").inner_text() != before
        page.locator(".data-chart").first.evaluate("element => element.blur()")
        capture(page, args.output / "desktop-evidence.png")
        checks.append(
            "frozen-model evidence is scoped correctly; charts are readable and keyboard inspectable"
        )
        page.get_by_role("button", name="Method & source", exact=True).click()
        expect(page.locator("#method-title")).to_be_visible()
        expect(page.locator(".source-facts")).to_contain_text("36,553")
        no_overflow(page)
        capture(page, args.output / "desktop-method.png")
        page.go_back()
        expect(page.locator("#evidence-title")).to_be_visible()
        page.get_by_role("button", name="Review queue", exact=True).click()
        expect(page.locator("#buyers [data-buyer]")).to_have_count(50)
        checks.append("source audit, view URLs and browser back navigation work")
        for width in [1560, 1280, 1100, 1024, 768, 390, 360]:
            page.set_viewport_size({"width": width, "height": 1000})
            no_overflow(page)
        page.set_viewport_size({"width": 390, "height": 844})
        capture(page, args.output / "mobile-queue.png")
        page.screenshot(path=str(args.output / "mobile-viewport.png"), full_page=False)
        trigger = page.locator("#buyers [data-buyer]").first
        first_id = trigger.get_attribute("data-buyer")
        trigger.click()
        expect(page.locator(".buyer-sheet")).to_be_visible()
        expect(
            page.get_by_role("button", name="Close buyer profile and return to queue")
        ).to_be_focused()
        expect(page.locator("#buyer-title")).to_have_text(f"Buyer {first_id}")
        page.get_by_role("button", name="Next buyer", exact=True).click()
        expect(page.locator("#buyer-title")).not_to_have_text(f"Buyer {first_id}")
        capture(page, args.output / "mobile-buyer.png", full_page=False)
        for _ in range(7):
            page.keyboard.press("Tab")
            assert page.evaluate(
                "document.querySelector('.buyer-sheet').contains(document.activeElement)"
            )
        page.keyboard.press("Escape")
        expect(page.locator(".buyer-sheet")).to_have_count(0)
        expect(trigger).to_be_focused()
        assert page.evaluate("document.body.style.overflow") != "hidden"
        checks.append(
            "mobile buyer sheet supports paging, trapped focus, Escape and trigger-focus restoration"
        )
        page.get_by_role("button", name="Model evidence", exact=True).click()
        expect(page.locator("#evidence-title")).to_be_visible()
        chart_type(page)
        no_overflow(page)
        capture(page, args.output / "mobile-evidence.png")
        checks.append(
            "all target viewport widths avoid page overflow; mobile evidence remains readable"
        )
        page.set_viewport_size({"width": 1440, "height": 1080})
        page.get_by_role("button", name="Review queue", exact=True).click()
        idle(page)
        page.get_by_role("button", name="Switch to dark theme", exact=True).click()
        assert page.evaluate("document.documentElement.dataset.theme") == "dark"
        no_overflow(page)
        capture(page, args.output / "desktop-dark.png")
        checks.append("explicit dark theme retains the measured data and layout")
        context.close()
        reduced = browser.new_context(
            viewport={"width": 390, "height": 844}, reduced_motion="reduce"
        )
        reduced_page = reduced.new_page()
        reduced_page.on("pageerror", lambda error: errors.append(str(error)))
        reduced_page.goto(args.url, wait_until="networkidle")
        expect(reduced_page.locator("#buyers [data-buyer]")).to_have_count(50)
        reduced_page.locator("#reveal").click()
        expect(reduced_page.locator("#reveal")).to_have_text("Hide outcomes")
        idle(reduced_page)
        assert reduced_page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches")
        moving = reduced_page.evaluate(
            "document.getAnimations().filter(a=>a.playState==='running' && a.effect?.getComputedTiming().duration>1).length"
        )
        assert moving == 0, f"Non-reduced animation still running: {moving}"
        checks.append(
            "reduced-motion preference preserves reveal behavior without spatial animation"
        )
        assert not errors, errors
        reduced.close()
        browser.close()
    result = {"status": "passed", "checks": checks, "javascript_errors": errors}
    (args.output / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
