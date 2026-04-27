def login(page):
    page.goto("https://beta.dazn.com/en-CA/search")

    # Accept cookies (safe handling)
    try:
        page.get_by_role("button", name="Accept").click(timeout=3000)
    except:
        pass

    # Click Sign In
    page.get_by_role("link", name="openbrowse_NavigationHeader_signin").click()

    # Enter Email
    page.locator('[data-test-id="EMAIL"]').fill("adtechca@dazn.com")
    page.locator('[data-test-id="refined-button-signin"]').click()

    # Enter Password
    page.locator('[data-test-id="PASSWORD"]').fill("55555eE")
    page.locator('[data-test-id="refined-button-signin"]').click()

    # Wait for login completion
    page.wait_for_load_state("networkidle")