"""Local browser validation; never visits a job site or uses applicant data."""
import os
import shutil

from playwright.sync_api import sync_playwright


def main():
    executable = os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium')
    with sync_playwright() as playwright:
        options = {'headless': True}
        if executable:
            options['executable_path'] = executable
        browser = playwright.chromium.launch(**options)
        try:
            page = browser.new_page()
            page.set_content('<label>Name<input aria-label="Name"></label>')
            page.get_by_label('Name', exact=True).fill('Local smoke fixture')
            assert page.get_by_label('Name', exact=True).input_value() == 'Local smoke fixture'
            print('Local Chromium form smoke check passed; no network requests made.')
        finally:
            browser.close()


if __name__ == '__main__':
    main()
