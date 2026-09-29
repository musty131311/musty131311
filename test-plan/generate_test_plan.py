"""Generate the SufiSupportHub manual test plan & checklist PDF.

Run: python3 test-plan/generate_test_plan.py   (needs: pip install reportlab)
Output: test-plan/SufiSupportHub_Manual_Test_Plan.pdf
Test content lives in test_cases.py.
"""
import datetime
import os
import sys
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    CondPageBreak,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from test_cases import ACCESS_MATRIX, ACCESS_ROLES, CODE_REVIEW_FINDINGS, MODULES  # noqa: E402

OUT = os.path.join(HERE, "SufiSupportHub_Manual_Test_Plan.pdf")
SITE = "https://sufisupporthub.com"
REPO = "github.com/musty131311/sufi-support-hub"
SOURCE_COMMIT = "8f67f89"
FIX_PR = "PR #1 (branch claude/fix-code-review-findings)"
VERSION = "1.1"
TODAY = datetime.date.today().strftime("%d %B %Y")

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
pdfmetrics.registerFont(TTFont("DejaVu", os.path.join(FONT_DIR, "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFontFamily("DejaVu", normal="DejaVu", bold="DejaVu-Bold",
                              italic="DejaVu", boldItalic="DejaVu-Bold")

GREEN = colors.HexColor("#1F5E4A")
LIGHT = colors.HexColor("#E8F1EC")
AMBER = colors.HexColor("#FFF4DB")
GREY = colors.HexColor("#6B7280")
LINE = colors.HexColor("#B8C7BF")

ss = getSampleStyleSheet()
BODY = ParagraphStyle("body", parent=ss["Normal"], fontName="DejaVu", fontSize=9, leading=12.5)
SMALL = ParagraphStyle("small", parent=BODY, fontSize=7.4, leading=9.4)
SMALL_B = ParagraphStyle("smallb", parent=SMALL, fontName="DejaVu-Bold", textColor=colors.white)
SMALL_C = ParagraphStyle("smallc", parent=SMALL, alignment=TA_CENTER)
H1 = ParagraphStyle("h1", parent=BODY, fontName="DejaVu-Bold", fontSize=15, leading=19,
                    textColor=GREEN, spaceBefore=6, spaceAfter=6)
H2 = ParagraphStyle("h2", parent=BODY, fontName="DejaVu-Bold", fontSize=11.5, leading=15,
                    textColor=GREEN, spaceBefore=8, spaceAfter=4)
TITLE = ParagraphStyle("title", parent=BODY, fontName="DejaVu-Bold", fontSize=26, leading=32,
                       textColor=GREEN, alignment=TA_CENTER)
SUB = ParagraphStyle("sub", parent=BODY, fontSize=12, leading=16, alignment=TA_CENTER, textColor=GREY)
BULLET = ParagraphStyle("bullet", parent=BODY, leftIndent=12, bulletIndent=2)

BOX = "☐"
RESULT_CELL = f"{BOX} Pass<br/>{BOX} Fail<br/>{BOX} N/A"


def p(text, style=BODY):
    return Paragraph(text, style)


def bullets(items):
    return [Paragraph(i, BULLET, bulletText="•") for i in items]


def grid(rows, widths, header=True, zebra=True):
    t = Table(rows, colWidths=widths, repeatRows=1 if header else 0)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]
    if header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), GREEN))
    if zebra:
        for r in range(1 if header else 0, len(rows)):
            if r % 2 == 0:
                style.append(("BACKGROUND", (0, r), (-1, r), LIGHT))
    t.setStyle(TableStyle(style))
    return t


def hdr(cells):
    return [p(c, SMALL_B) for c in cells]


def on_page(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFont("DejaVu", 7.5)
    canvas.setFillColor(GREY)
    canvas.drawString(14 * mm, h - 9 * mm, f"SufiSupportHub — Manual Test Plan & Checklist v{VERSION}")
    canvas.drawRightString(w - 14 * mm, h - 9 * mm, SITE)
    canvas.setStrokeColor(LINE)
    canvas.line(14 * mm, h - 10.5 * mm, w - 14 * mm, h - 10.5 * mm)
    canvas.drawString(14 * mm, 8 * mm, "Tester: ____________________   Date: ____________   Build/Release: ____________")
    canvas.drawRightString(w - 14 * mm, 8 * mm, f"Page {doc.page}")
    canvas.restoreState()


def total_cases():
    return sum(len(m["cases"]) for m in MODULES)


def cover(story):
    story += [Spacer(1, 45 * mm),
              p("Sufi Support Hub", TITLE), Spacer(1, 4 * mm),
              p("Cumulative Manual Test Plan &amp; Checklist",
                ParagraphStyle("t2", parent=TITLE, fontSize=17, leading=22)),
              Spacer(1, 8 * mm),
              p(f"Production site: {SITE}", SUB),
              p(f"Source repository: {REPO} (commit {SOURCE_COMMIT} + fixes in {FIX_PR})", SUB),
              Spacer(1, 12 * mm)]
    info = [
        ["Document version", VERSION],
        ["Generated", TODAY],
        ["Coverage", f"{len(MODULES)} modules · {total_cases()} test cases · role-access matrix · "
                     f"{sum(1 for f in CODE_REVIEW_FINDINGS if f[2].startswith('Fixed'))} code-review findings fixed, "
                     f"{sum(1 for f in CODE_REVIEW_FINDINGS if not f[2].startswith('Fixed'))} open"],
        ["Test type", "Manual — functional, role/jurisdiction, security, performance, compatibility, accessibility"],
        ["Environment under test", "Production (sufisupporthub.com) and/or staging"],
        ["Prepared by", "________________________________"],
        ["Approved by", "________________________________"],
    ]
    story.append(grid([[p(f"<b>{a}</b>"), p(b)] for a, b in info], [50 * mm, 125 * mm],
                      header=False, zebra=False))
    story.append(Spacer(1, 10 * mm))
    story.append(p("<b>Contents</b>"))
    story += bullets([
        "1. Introduction &amp; scope", "2. Test approach, roles, environments, data, criteria",
        "3. Feature map (every feature found in the source code)",
        "4. Code-review findings and fix status",
        "5. Role &amp; jurisdiction access matrix",
        "6. Detailed test cases (per module)", "7. Release smoke-test checklist",
        "8. Execution summary", "9. Defect log", "10. Test-cycle sign-off",
    ])
    story.append(PageBreak())


def intro(story):
    story.append(p("1. Introduction", H1))
    story.append(p("1.1 Purpose", H2))
    story.append(p(
        "This plan defines how to manually verify every feature of Sufi Support Hub as deployed to "
        f"{SITE}. It was written from the application source code ({REPO}, a Laravel 12 app), so every "
        "page, form, role and workflow in the code has test cases. It is cumulative: run the full plan "
        "for a major release, run the smoke checklist (Section 7) on every deployment, and add new cases "
        "in the blank rows whenever a feature is added."))
    story.append(p("1.2 System overview", H2))
    story += bullets([
        "<b>Public website</b>: homepage, “Join the Movement” registration, Join a Chapter, poster "
        "generator, news, leadership/team, sitemap.",
        "<b>Admin panel (/admin)</b>: a 5-level hierarchy (National → State → Zonal → LGA → "
        "Cluster), each seeing only its own jurisdiction. It covers signups, members and promotion, admins, "
        "polling agents, parties, elections and candidates, news, team, result review, the live situation "
        "room, trash and the activity log.",
        "<b>Polling-agent portal (/agent)</b>: a separate login. Agents report election results and upload "
        "scoresheets for their assigned polling units.",
    ])
    story.append(p("1.3 Scope", H2))
    story.append(p("<b>In scope:</b> all of the above, plus hosting/HTTPS, security headers, performance, "
                   "mobile/browser compatibility, accessibility, SEO and deployment/backup checks."))
    story.append(p("<b>Out of scope:</b> automated PHPUnit tests (already run by CI on every deploy), load "
                   "testing beyond the manual spot-checks here, and third-party sites (govote.ng, social networks)."))

    story.append(p("2. Test Approach", H1))
    story.append(p("2.1 Test types", H2))
    story += bullets([
        "<b>Smoke</b>: about 20-minute critical-path check after every deployment (Section 7).",
        "<b>Functional</b>: positive, negative and boundary cases per module (Section 6).",
        "<b>Role &amp; jurisdiction</b>: the same URLs tried with every role (Section 5 + module RB).",
        "<b>Election-day rehearsal</b>: agents submit and admins review simultaneously (modules RS, RV, SR, PF).",
        "<b>Non-functional</b>: security, performance, compatibility, accessibility, SEO.",
        "<b>Regression</b>: all High-priority cases, plus every module touched by the release.",
    ])
    story.append(p("2.2 Test accounts needed", H2))
    roles = [
        hdr(["Role", "What it can do", "Login URL", "Test account (fill in)"]),
        [p("Visitor"), p("Public pages, registration, chapter join, poster"), p("—"), p("n/a")],
        [p("National admin"), p("Everything, including national content, activity log and all trash"), p("/admin/login"), p("")],
        [p("State admin"), p("One state: members, admins below, agents, results"), p("/admin/login"), p("")],
        [p("Zonal admin"), p("One senatorial zone within a state"), p("/admin/login"), p("")],
        [p("LGA admin"), p("One LGA"), p("/admin/login"), p("")],
        [p("Cluster admin"), p("Hand-picked polling units only"), p("/admin/login"), p("")],
        [p("Polling agent"), p("Report results for own assigned units"), p("/agent/login"), p("")],
        [p("2nd-state admin"), p("For cross-jurisdiction (negative) checks"), p("/admin/login"), p("")],
    ]
    story.append(grid(roles, [30 * mm, 75 * mm, 27 * mm, 50 * mm]))
    story.append(p("2.3 Test environments", H2))
    env = [
        hdr(["Platform", "Browsers / devices", "Done"]),
        [p("Desktop Windows 10/11"), p("Chrome, Edge, Firefox (latest)"), p(BOX)],
        [p("Desktop macOS"), p("Safari, Chrome (latest)"), p(BOX)],
        [p("Android phone"), p("Chrome on a low/mid-range device, on a slow 3G/4G network (agents in the field)"), p(BOX)],
        [p("iPhone"), p("Safari (latest iOS and one version back)"), p(BOX)],
        [p("Tablet"), p("iPad or Android tablet, portrait and landscape"), p(BOX)],
        [p("Large screen"), p("1920 px / TV or projector for the situation room"), p(BOX)],
    ]
    story.append(grid(env, [40 * mm, 125 * mm, 17 * mm]))
    story.append(p("2.4 Test data", H2))
    story += bullets([
        "Use email aliases you can read (e.g. name+ssh01@gmail.com). Prefix every test name with “TEST”.",
        "Never use real members’ personal data. Delete test records after the cycle (module OP).",
        "Have ready: a JPG/PNG portrait photo, a PDF scoresheet, a file over 10 MB, a file over 2 MB, a GIF, "
        "a .php file renamed to .jpg, text of 300+ characters, emoji and Hausa/Arabic text, and "
        "&lt;script&gt;alert(1)&lt;/script&gt;.",
        "Pick one test state (e.g. Kano) with a Zonal, LGA and Cluster chain, plus a second state for negative checks.",
        "Result submission tests need at least one ACTIVE election with ACTIVE candidates for the test unit.",
        "If testing on production, agree a window, then flag/remove test results so they never affect real totals.",
    ])
    story.append(p("2.5 Entry &amp; exit criteria", H2))
    story.append(p("<b>Entry:</b> build deployed and GitHub Actions green, site reachable, all test accounts ready."))
    story.append(p("<b>Exit:</b> 100% of H cases executed; no open Critical/High defects; at least 95% of executed "
                   "cases passed; remaining issues accepted in the sign-off (Section 10)."))
    story.append(p("2.6 Severity definitions", H2))
    sev = [
        hdr(["Severity", "Meaning", "Example in this app"]),
        [p("Critical"), p("Data breach, wrong election totals, site down, or no workaround."),
         p("A State admin sees another state’s results, or party totals are wrong in the situation room.")],
        [p("High"), p("Core feature broken."), p("Agent cannot submit results. Registration fails.")],
        [p("Medium"), p("Feature partly works, workaround exists."), p("A filter on Members is ignored.")],
        [p("Low"), p("Cosmetic or text issue."), p("Typo, misaligned icon, dead footer link.")],
    ]
    story.append(grid(sev, [22 * mm, 70 * mm, 90 * mm]))
    story.append(p("Test case priority: <b>H</b> = must pass for release; <b>M</b> = should pass; <b>L</b> = nice to have."))
    story.append(p("2.7 How to execute", H2))
    story += bullets([
        "Follow the steps exactly and compare with the expected result.",
        f"Tick {BOX} Pass, {BOX} Fail or {BOX} N/A. Never leave a row blank.",
        "On failure, log it in Section 9 and write the Defect ID in the Notes column. Attach a screenshot or screen recording.",
        "Rows marked NOTE describe behaviour seen in the code that may be unintended. Confirm with the product owner.",
        f"Cases marked [Fixed in PR #1] check a fix from {FIX_PR}. They only pass once that PR is merged and deployed; "
        "before then, expect the old behaviour.",
    ])
    story.append(PageBreak())


def feature_map(story):
    story.append(p("3. Feature Map (from the source code)", H1))
    story.append(p("Every user-facing feature found in the repository, with where it lives and who uses it. "
                   "Tick “Covered” once its module has been fully executed in this cycle."))
    rows = [hdr(["Covered", "Feature", "URL / route", "Who", "Module"])]
    for mod in MODULES:
        for feat, url, who in mod.get("features", []):
            rows.append([p(BOX, SMALL_C), p(escape(feat), SMALL), p(escape(url), SMALL), p(escape(who), SMALL), p(mod["code"], SMALL)])
    story.append(grid(rows, [14 * mm, 70 * mm, 50 * mm, 32 * mm, 16 * mm]))
    story.append(PageBreak())


def findings(story):
    story.append(p("4. Code-Review Findings and Fix Status", H1))
    story.append(p(f"Issues found while reading the source code for this plan. Those marked fixed were "
                   f"corrected in {FIX_PR}. Once it is merged and deployed, run the listed retest cases and "
                   "tick \u201cVerified\u201d. Open items need a decision from the project owner."))
    rows = [hdr(["#", "Module", "Finding", "Status", "Retest case / decision needed", "Verified"])]
    open_rows = []
    for i, (mod, text, status, retest) in enumerate(CODE_REVIEW_FINDINGS, 1):
        rows.append([p(str(i), SMALL), p(mod, SMALL), p(escape(text), SMALL), p(f"<b>{escape(status)}</b>", SMALL),
                     p(escape(retest), SMALL), p(f"{BOX} Yes<br/>{BOX} No", SMALL)])
        if not status.startswith("Fixed"):
            open_rows.append(i)
    t = grid(rows, [8 * mm, 14 * mm, 76 * mm, 24 * mm, 42 * mm, 18 * mm], zebra=False)
    t.setStyle(TableStyle([("BACKGROUND", (0, r), (-1, r), AMBER) for r in open_rows]))
    story.append(t)
    story.append(Spacer(1, 3))
    story.append(p("Shaded rows are still open.", SMALL))
    story.append(PageBreak())


def access_matrix(story):
    story.append(p("5. Role &amp; Jurisdiction Access Matrix", H1))
    story.append(p("Open each URL directly in the address bar while logged in as each role. Write ✓ when the "
                   "actual result matches the expected one, ✗ when it does not."))
    story.append(p("<b>Key:</b> A = allowed · own = allowed, but shows only that role’s own jurisdiction "
                   "· own* = own admins/agents only, no content types · empty = page opens but list is "
                   "empty · 403 = Forbidden · L = redirected to the login page for that area.", SMALL))
    story.append(Spacer(1, 3))
    rows = [hdr(["URL"] + ACCESS_ROLES)]
    for url, expected in ACCESS_MATRIX:
        rows.append([p(escape(url), SMALL)] + [p(f"<b>{e}</b><br/>{BOX}", SMALL_C) for e in expected])
    story.append(grid(rows, [56 * mm] + [18 * mm] * len(ACCESS_ROLES)))
    story.append(PageBreak())


def modules(story):
    story.append(p("6. Detailed Test Cases", H1))
    widths = [13 * mm, 62 * mm, 55 * mm, 8 * mm, 19 * mm, 25 * mm]
    for mod in MODULES:
        head = [p(escape(f"{mod['code']}. {mod['title']}"), H2)]
        if mod.get("pre"):
            head.append(p(f"<i>Preconditions:</i> {escape(mod['pre'])}", SMALL))
        head.append(Spacer(1, 2))
        rows = [hdr(["ID", "Test scenario &amp; steps", "Expected result", "Pri", "Result", "Notes / Defect ID"])]
        for i, (scen, exp, pri) in enumerate(mod["cases"], 1):
            rows.append([p(f"{mod['code']}-{i:02d}", SMALL), p(escape(scen), SMALL), p(escape(exp), SMALL),
                         p(pri, SMALL), p(RESULT_CELL, SMALL), p("", SMALL)])
        for j in range(2):  # blank rows for cases added later
            rows.append([p(f"{mod['code']}-{len(mod['cases']) + j + 1:02d}", SMALL), p("", SMALL), p("", SMALL),
                         p("", SMALL), p(RESULT_CELL, SMALL), p("", SMALL)])
        # Start a new page if fewer than ~4 rows fit, so a heading is never orphaned.
        story.append(CondPageBreak(60 * mm))
        story += head
        story.append(grid(rows, widths))
        story.append(Spacer(1, 5 * mm))
    story.append(PageBreak())


SMOKE = [
    "https://sufisupporthub.com loads (http redirects to https). No console errors or broken images.",
    "Top nav, “View All News”, “View Full Team” and the /join-chapter and /poster links all open.",
    "Homepage modal: register a TEST user (state → LGA → ward → unit cascade works). Success shown.",
    "/join-chapter: submit a TEST member. Green success message.",
    "/poster: upload a photo, add a name, generate and download a PNG.",
    "/news and one article open. /team opens. /sitemap.xml is valid.",
    "Admin login (National) works. The dashboard counts are sensible.",
    "Admin > Signups shows the TEST registration and chapter member just created.",
    "Admin > News: create an inactive TEST item, then delete it (moves to Trash).",
    "Admin > Result Review and Situation Room open for the active election with no errors.",
    "State admin login shows only their state’s data (spot-check Members and Results).",
    "Non-National admin gets 403 on /admin/news.",
    "Agent login works and the dashboard lists only the assigned units.",
    "Agent report form opens for an assigned unit (submit only in an agreed test window/unit).",
    "Agent gets 403 on another unit’s report URL.",
    "Logout works for both admin and agent.",
    "/.env, /composer.json and /deploy-hook.php (without the token) are NOT readable.",
    "Security headers are present (DevTools → Network → response headers).",
    "Homepage, modal, agent portal and situation room checked on one Android phone and one iPhone.",
    "Test records created during the smoke test have been removed or flagged.",
]


def smoke(story):
    story.append(p("7. Release Smoke-Test Checklist (every deployment)", H1))
    story.append(p("Target: under 20 minutes. Any failure blocks the release until triaged."))
    rows = [hdr(["#", "Check", "Pass", "Fail", "Notes"])]
    for i, s in enumerate(SMOKE, 1):
        rows.append([p(str(i), SMALL), p(escape(s), SMALL), p(BOX, SMALL_C), p(BOX, SMALL_C), p("", SMALL)])
    story.append(grid(rows, [8 * mm, 112 * mm, 10 * mm, 10 * mm, 42 * mm]))
    story.append(PageBreak())


def summary(story):
    story.append(p("8. Execution Summary", H1))
    story.append(p("Fill in at the end of each test cycle."))
    rows = [hdr(["Module", "Title", "Cases", "H", "Pass", "Fail", "N/A", "Tester"])]
    for mod in MODULES:
        n = len(mod["cases"])
        h = sum(1 for c in mod["cases"] if c[2] == "H")
        rows.append([p(mod["code"], SMALL), p(escape(mod["title"]), SMALL), p(str(n), SMALL), p(str(h), SMALL)]
                    + [p("", SMALL)] * 4)
    total_h = sum(1 for m in MODULES for c in m["cases"] if c[2] == "H")
    rows.append([p("<b>Total</b>", SMALL), p("", SMALL), p(f"<b>{total_cases()}</b>", SMALL),
                 p(f"<b>{total_h}</b>", SMALL)] + [p("", SMALL)] * 4)
    story.append(grid(rows, [14 * mm, 70 * mm, 13 * mm, 10 * mm, 14 * mm, 14 * mm, 14 * mm, 33 * mm]))
    story.append(PageBreak())


def defects(story):
    story.append(p("9. Defect Log", H1))
    story.append(p("One row per failure. Keep screenshots/videos in a shared folder named by Defect ID."))
    rows = [hdr(["Defect ID", "Test case", "Summary / steps to reproduce", "Severity", "Role / device",
                 "Status", "Retest"])]
    for _ in range(22):
        rows.append([p("", SMALL)] * 6 + [p(f"{BOX} OK", SMALL)])
    t = grid(rows, [17 * mm, 17 * mm, 66 * mm, 16 * mm, 26 * mm, 18 * mm, 16 * mm])
    t.setStyle(TableStyle([("MINROWHEIGHT", (0, 1), (-1, -1), 20)]))
    story.append(t)
    story.append(Spacer(1, 4 * mm))
    story.append(p("<b>Status:</b> New → In progress → Fixed → Retest passed / Reopened → Closed. "
                   "<b>Every report needs:</b> URL, role/account, exact steps, expected vs actual, screenshot, "
                   "date/time, browser and device.", SMALL))
    story.append(PageBreak())


def signoff(story):
    story.append(p("10. Test-Cycle Sign-off", H1))
    rows = [
        ["Release / commit", ""], ["Test cycle dates", ""], ["Environment(s)", ""],
        ["Cases executed / total", f"______ / {total_cases()}"], ["Passed / Failed / N/A", ""],
        ["Open defects (Critical / High / Medium / Low)", ""], ["Known issues accepted for release", ""],
    ]
    story.append(grid([[p(f"<b>{a}</b>"), p(b)] for a, b in rows], [75 * mm, 107 * mm], header=False, zebra=False))
    story.append(Spacer(1, 6 * mm))
    story.append(p(f"Release decision:  {BOX} GO    {BOX} GO with known issues    {BOX} NO-GO"))
    story.append(Spacer(1, 8 * mm))
    sig = [hdr(["Role", "Name", "Signature", "Date"])]
    for r in ["QA / Tester", "Developer", "Project owner", "Operations / Hosting"]:
        sig.append([p(r), p(""), p(""), p("")])
    t = grid(sig, [45 * mm, 52 * mm, 50 * mm, 35 * mm], zebra=False)
    t.setStyle(TableStyle([("MINROWHEIGHT", (0, 1), (-1, -1), 24)]))
    story.append(t)


def main():
    doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=14 * mm, rightMargin=14 * mm,
                            topMargin=15 * mm, bottomMargin=14 * mm,
                            title="Sufi Support Hub — Manual Test Plan & Checklist",
                            author="Sufi Support Hub QA", subject=f"Manual test plan for {SITE}")
    story = []
    cover(story)
    intro(story)
    feature_map(story)
    findings(story)
    access_matrix(story)
    modules(story)
    smoke(story)
    summary(story)
    defects(story)
    signoff(story)
    doc.build(story, onFirstPage=lambda c, d: None, onLaterPages=on_page)
    print(f"Wrote {OUT}: {len(MODULES)} modules, {total_cases()} test cases")


if __name__ == "__main__":
    main()
