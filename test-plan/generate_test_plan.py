"""Generate the SufiSupportHub manual test plan & checklist PDF.

Run: python3 test-plan/generate_test_plan.py
Output: test-plan/SufiSupportHub_Manual_Test_Plan.pdf
"""
import datetime
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from test_cases import MODULES

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "SufiSupportHub_Manual_Test_Plan.pdf")
SITE = "https://sufisupporthub.com"
REPO = "github.com/musty131311/sufi-support-hub"
VERSION = "1.0"
TODAY = datetime.date.today().strftime("%d %B %Y")

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
pdfmetrics.registerFont(TTFont("DejaVu", os.path.join(FONT_DIR, "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFontFamily("DejaVu", normal="DejaVu", bold="DejaVu-Bold",
                              italic="DejaVu", boldItalic="DejaVu-Bold")

GREEN = colors.HexColor("#1F5E4A")
LIGHT = colors.HexColor("#E8F1EC")
GREY = colors.HexColor("#6B7280")
LINE = colors.HexColor("#B8C7BF")

ss = getSampleStyleSheet()
BODY = ParagraphStyle("body", parent=ss["Normal"], fontName="DejaVu", fontSize=9, leading=12.5)
SMALL = ParagraphStyle("small", parent=BODY, fontSize=7.4, leading=9.4)
SMALL_B = ParagraphStyle("smallb", parent=SMALL, fontName="DejaVu-Bold", textColor=colors.white)
H1 = ParagraphStyle("h1", parent=BODY, fontName="DejaVu-Bold", fontSize=15, leading=19,
                    textColor=GREEN, spaceBefore=6, spaceAfter=6)
H2 = ParagraphStyle("h2", parent=BODY, fontName="DejaVu-Bold", fontSize=11.5, leading=15,
                    textColor=GREEN, spaceBefore=8, spaceAfter=4)
TITLE = ParagraphStyle("title", parent=BODY, fontName="DejaVu-Bold", fontSize=26, leading=32,
                       textColor=GREEN, alignment=TA_CENTER)
SUB = ParagraphStyle("sub", parent=BODY, fontSize=12, leading=16, alignment=TA_CENTER, textColor=GREY)
BULLET = ParagraphStyle("bullet", parent=BODY, leftIndent=12, bulletIndent=2)

BOX = "☐"


def p(text, style=BODY):
    return Paragraph(text, style)


def bullets(items):
    return [Paragraph(i, BULLET, bulletText="•") for i in items]


def grid(rows, widths, header=True, zebra=True, font_size=None):
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
        style += [("BACKGROUND", (0, 0), (-1, 0), GREEN)]
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


def on_first(canvas, doc):
    pass


def cover(story):
    story += [Spacer(1, 55 * mm),
              p("SufiSupportHub", TITLE), Spacer(1, 4 * mm),
              p("Cumulative Manual Test Plan &amp; Checklist", ParagraphStyle("t2", parent=TITLE, fontSize=17, leading=22)),
              Spacer(1, 8 * mm),
              p(f"Production site: {SITE}", SUB),
              p(f"Source repository: {REPO}", SUB),
              Spacer(1, 14 * mm)]
    info = [
        ["Document version", VERSION],
        ["Generated", TODAY],
        ["Test type", "Manual — functional, UI, security, performance, compatibility, accessibility"],
        ["Environment under test", "Production (sufisupporthub.com) and/or staging"],
        ["Prepared by", "________________________________"],
        ["Approved by", "________________________________"],
    ]
    story.append(grid([[p(f"<b>{a}</b>"), p(b)] for a, b in info], [55 * mm, 110 * mm],
                      header=False, zebra=False))
    story.append(Spacer(1, 12 * mm))
    story.append(p(
        "<b>How to read this document.</b> Section 3 is a feature inventory: tick every feature the site "
        "actually has, and mark whole modules N/A if a feature does not exist. Sections 5 onward hold "
        "step-by-step test cases. Each module ends with blank rows for anything specific to "
        "SufiSupportHub that the generic cases miss.", SMALL))
    story.append(PageBreak())


def intro(story):
    story.append(p("1. Introduction", H1))
    story.append(p("1.1 Purpose", H2))
    story.append(p(
        "This plan defines how to manually verify that every feature of SufiSupportHub, as deployed to "
        f"{SITE}, works correctly, securely and consistently for every type of user before and after each "
        "release. It is cumulative: every module is re-tested on a full regression cycle, and the smoke "
        "checklist (Section 6) is run on every deployment."))
    story.append(p("1.2 Scope", H2))
    story.append(p("<b>In scope</b>"))
    story += bullets([
        "Hosting, domain, SSL/HTTPS, redirects and error pages.",
        "All public (visitor) pages, navigation, content and contact channels.",
        "User accounts: registration, email verification, login, logout, password reset, profile, deletion.",
        "Core support workflows: support requests/tickets, messaging/chat, knowledge base/resources, "
        "appointments/events, donations/payments and notifications, wherever these exist.",
        "Admin/staff back office: users and roles, request handling, content management, reports, settings.",
        "Cross-cutting: form validation, file uploads, search, security, performance, responsive and "
        "cross-browser behaviour, accessibility, SEO, localisation, privacy and data integrity.",
    ])
    story.append(p("<b>Out of scope</b>"))
    story += bullets([
        "Automated unit/integration tests and load tests beyond the manual spot-checks listed here.",
        "Third-party platforms themselves (payment gateway, email provider). Only our integration with them is tested.",
    ])
    story.append(p("1.3 Objectives", H2))
    story += bullets([
        "Confirm that every user-facing feature behaves as intended for each role.",
        "Find functional, UI, security and data defects before users do.",
        "Give a repeatable, auditable checklist with sign-off for each release.",
    ])

    story.append(p("2. Test Approach", H1))
    story.append(p("2.1 Test levels &amp; types", H2))
    story += bullets([
        "<b>Smoke test</b>: 15-minute critical-path check after every deployment (Section 6).",
        "<b>Functional test</b>: positive, negative and boundary cases per module (Section 5).",
        "<b>Role-based test</b>: repeat protected flows as Visitor, Registered user, Staff/Agent and Admin.",
        "<b>Non-functional test</b>: security, performance, compatibility, accessibility, SEO.",
        "<b>Regression</b>: re-run all High-priority cases plus the modules touched by the change.",
        "<b>Exploratory</b>: 30–60 minute time-boxed sessions per release. Record findings in the defect log.",
    ])
    story.append(p("2.2 User roles to test", H2))
    roles = [
        hdr(["Role", "Description", "Test account (fill in)"]),
        [p("Visitor"), p("Not logged in. Public pages, contact form, sign-up."), p("n/a")],
        [p("Registered user / member"), p("Seeker of support. Submits and tracks requests, manages profile."), p("")],
        [p("Staff / Agent / Volunteer"), p("Handles assigned requests, replies, updates status."), p("")],
        [p("Admin / Super-admin"), p("Full back office: users, roles, content, settings, reports."), p("")],
    ]
    story.append(grid(roles, [40 * mm, 90 * mm, 50 * mm]))
    story.append(p("2.3 Test environments", H2))
    env = [
        hdr(["Platform", "Browsers / devices", "Checked"]),
        [p("Desktop Windows 10/11"), p("Chrome, Edge, Firefox (latest)"), p(BOX)],
        [p("Desktop macOS"), p("Safari, Chrome (latest)"), p(BOX)],
        [p("Android phone"), p("Chrome. Low-end device + slow 3G/4G"), p(BOX)],
        [p("iPhone"), p("Safari (iOS latest and latest‑1)"), p(BOX)],
        [p("Tablet"), p("iPad Safari / Android tablet, portrait + landscape"), p(BOX)],
        [p("Screen sizes"), p("320, 375, 414, 768, 1024, 1366, 1920 px widths"), p(BOX)],
    ]
    story.append(grid(env, [45 * mm, 110 * mm, 25 * mm]))
    story.append(p("2.4 Test data", H2))
    story += bullets([
        "Use dedicated test accounts, one per role, with emails you can access (e.g. Gmail + aliases).",
        "Never use real beneficiaries' personal data. Use clearly fake names (e.g. “TEST User 01”).",
        "For payments, use gateway sandbox/test cards. If only live mode exists, use the smallest amount and refund it.",
        "Prepare upload files: small JPG/PNG/PDF, a file just above the size limit, an .exe renamed to .jpg, "
        "and file names with spaces and non-Latin characters.",
        "Prepare long strings (5,000+ chars), emoji, Arabic/RTL text, HTML/script snippets and SQL-like input.",
        "Delete or clearly label all test data after the cycle (see W-module).",
    ])
    story.append(p("2.5 Entry &amp; exit criteria", H2))
    story.append(p("<b>Entry:</b> build deployed, URL reachable, test accounts ready, release notes available."))
    story.append(p("<b>Exit:</b> 100% of High-priority cases executed; no open Critical/High defects; "
                   "≥ 95% of executed cases passed; known issues documented and accepted in sign-off."))
    story.append(p("2.6 Severity &amp; priority definitions", H2))
    sev = [
        hdr(["Severity", "Meaning", "Example"]),
        [p("Critical"), p("Site down, data loss, security breach, payments broken. No workaround."),
         p("Login fails for everyone; private requests visible to other users.")],
        [p("High"), p("Core feature broken or wrong, workaround hard."), p("Support request cannot be submitted.")],
        [p("Medium"), p("Feature partly works; workaround exists."), p("Filter on admin list ignores date.")],
        [p("Low"), p("Cosmetic or minor text/UI issue."), p("Typo, misaligned icon.")],
    ]
    story.append(grid(sev, [25 * mm, 80 * mm, 75 * mm]))
    story.append(p("Test case priority: <b>H</b> = must pass for release; <b>M</b> = should pass; <b>L</b> = nice to have."))
    story.append(p("2.7 How to execute a test case", H2))
    story += bullets([
        "Read the steps, perform them exactly, and compare against the expected result.",
        f"Tick {BOX} Pass, {BOX} Fail or {BOX} N/A (feature not present). Never leave a row blank.",
        "On failure, log a defect (Section 7), write the defect ID in Notes, and attach a screenshot/video.",
        "Record the browser/device used when a failure is environment-specific.",
    ])
    story.append(PageBreak())


def inventory(story):
    story.append(p("3. Feature Inventory (complete first)", H1))
    story.append(p(
        "Tick each feature that exists on sufisupporthub.com. Any module whose features are all unticked "
        "can be marked N/A as a whole in Section 5. Add missing features in the blank rows. They "
        "then need their own test cases in the related module's blank rows."))
    rows = [hdr(["Exists?", "Feature", "Module", "Notes / URL"])]
    for mod in MODULES:
        for feat in mod.get("features", []):
            rows.append([p(f"{BOX} Yes {BOX} No", SMALL), p(feat, SMALL), p(mod["code"], SMALL), p("", SMALL)])
    for _ in range(6):
        rows.append([p(f"{BOX} Yes {BOX} No", SMALL), p("", SMALL), p("", SMALL), p("", SMALL)])
    story.append(grid(rows, [24 * mm, 85 * mm, 15 * mm, 58 * mm]))
    story.append(PageBreak())


def summary(story):
    story.append(p("4. Execution Summary", H1))
    story.append(p("Fill in after each test cycle."))
    rows = [hdr(["Module", "Title", "Cases", "Pass", "Fail", "N/A", "Blocked", "Tester"])]
    total = 0
    for mod in MODULES:
        n = len(mod["cases"])
        total += n
        rows.append([p(mod["code"], SMALL), p(mod["title"], SMALL), p(str(n), SMALL)] + [p("", SMALL)] * 5)
    rows.append([p("<b>Total</b>", SMALL), p("", SMALL), p(f"<b>{total}</b>", SMALL)] + [p("", SMALL)] * 5)
    story.append(grid(rows, [14 * mm, 62 * mm, 14 * mm, 14 * mm, 14 * mm, 14 * mm, 16 * mm, 34 * mm]))
    story.append(PageBreak())
    return total


def modules(story):
    story.append(p("5. Detailed Test Cases", H1))
    widths = [13 * mm, 62 * mm, 55 * mm, 8 * mm, 19 * mm, 25 * mm]
    result_cell = f"{BOX} Pass<br/>{BOX} Fail<br/>{BOX} N/A"
    for mod in MODULES:
        head = [p(f"{mod['code']}. {mod['title']}", H2)]
        if mod.get("pre"):
            head.append(p(f"<i>Preconditions:</i> {mod['pre']}", SMALL))
        head.append(p(f"{BOX} Entire module N/A (feature not present on site)", SMALL))
        head.append(Spacer(1, 2))
        rows = [hdr(["ID", "Test scenario &amp; steps", "Expected result", "Pri", "Result", "Notes / Defect ID"])]
        for i, (scen, exp, pri) in enumerate(mod["cases"], 1):
            rows.append([p(f"{mod['code']}-{i:02d}", SMALL), p(scen, SMALL), p(exp, SMALL),
                         p(pri, SMALL), p(result_cell, SMALL), p("", SMALL)])
        for j in range(2):
            rows.append([p(f"{mod['code']}-{len(mod['cases']) + j + 1:02d}", SMALL), p("", SMALL), p("", SMALL),
                         p("", SMALL), p(result_cell, SMALL), p("", SMALL)])
        story.append(KeepTogether(head + [grid(rows[:3], widths)]))
        story.append(grid([rows[0]] + rows[3:], widths) if len(rows) > 3 else Spacer(1, 0))
        story.append(Spacer(1, 5 * mm))
    story.append(PageBreak())


SMOKE = [
    "Home page loads over HTTPS in < 3 s with no console errors or broken images.",
    "http:// and www. variants redirect to the canonical https:// URL.",
    "All main navigation and footer links open the correct pages (no 404).",
    "Contact form submits and the message arrives at the admin inbox.",
    "New user can register and receives the verification/welcome email.",
    "Existing user can log in, and log out fully.",
    "Forgot-password email arrives and the reset link works.",
    "User can create a support request/ticket and sees it in “My requests”.",
    "Staff/admin receives notification of the new request and can reply.",
    "User sees the staff reply and status change.",
    "Donation/payment (if present) completes in test mode and a receipt is shown/emailed.",
    "Admin dashboard loads, and user list and request list display data.",
    "Protected pages redirect to login when logged out.",
    "Site renders correctly on one Android and one iPhone device.",
    "Search returns relevant results for a known keyword.",
    "No sensitive data (keys, stack traces) visible on error pages.",
]


def smoke(story):
    story.append(p("6. Release Smoke-Test Checklist (run on every deployment)", H1))
    story.append(p("Target: under 15 minutes. Any failure blocks the release until triaged."))
    rows = [hdr(["#", "Check", "Pass", "Fail", "Notes"])]
    for i, s in enumerate(SMOKE, 1):
        rows.append([p(str(i), SMALL), p(s, SMALL), p(BOX, SMALL), p(BOX, SMALL), p("", SMALL)])
    story.append(grid(rows, [8 * mm, 110 * mm, 11 * mm, 11 * mm, 42 * mm]))
    story.append(PageBreak())


def defects(story):
    story.append(p("7. Defect Log", H1))
    story.append(p("Every failure gets one row. Keep screenshots/videos in a shared folder named by Defect ID."))
    rows = [hdr(["Defect ID", "Test case ID", "Summary / steps to reproduce", "Severity", "Browser / device",
                 "Status", "Retest"])]
    for _ in range(22):
        rows.append([p("", SMALL)] * 4 + [p("", SMALL), p("", SMALL), p(f"{BOX} OK", SMALL)])
    t = grid(rows, [17 * mm, 18 * mm, 65 * mm, 16 * mm, 26 * mm, 18 * mm, 16 * mm])
    t.setStyle(TableStyle([("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
                           ("MINROWHEIGHT", (0, 1), (-1, -1), 20)]))
    story.append(t)
    story.append(Spacer(1, 4 * mm))
    story.append(p("<b>Status values:</b> New → In progress → Fixed → Retest passed / Reopened → Closed. "
                   "<b>Defect report must include:</b> URL, role/account used, exact steps, expected vs actual, "
                   "screenshot/video, date/time, browser + device."))
    story.append(PageBreak())


def signoff(story):
    story.append(p("8. Test Cycle Sign-off", H1))
    rows = [
        ["Release / build", ""], ["Test cycle dates", ""], ["Environment(s)", ""],
        ["Total cases executed", ""], ["Passed / Failed / N/A / Blocked", ""],
        ["Open defects (Critical / High / Medium / Low)", ""], ["Known issues accepted for release", ""],
    ]
    story.append(grid([[p(f"<b>{a}</b>"), p(b)] for a, b in rows], [75 * mm, 105 * mm], header=False, zebra=False))
    story.append(Spacer(1, 6 * mm))
    story.append(p(f"Release decision:  {BOX} GO    {BOX} GO with known issues    {BOX} NO-GO"))
    story.append(Spacer(1, 8 * mm))
    sig = [hdr(["Role", "Name", "Signature", "Date"])]
    for r in ["QA / Tester", "Developer lead", "Project owner", "Admin / Operations"]:
        sig.append([p(r), p(""), p(""), p("")])
    t = grid(sig, [45 * mm, 50 * mm, 50 * mm, 35 * mm], zebra=False)
    t.setStyle(TableStyle([("MINROWHEIGHT", (0, 1), (-1, -1), 24)]))
    story.append(t)


def main():
    doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=14 * mm, rightMargin=14 * mm,
                            topMargin=15 * mm, bottomMargin=14 * mm,
                            title="SufiSupportHub Manual Test Plan & Checklist",
                            author="SufiSupportHub QA", subject=f"Manual test plan for {SITE}")
    story = []
    cover(story)
    intro(story)
    inventory(story)
    total = summary(story)
    modules(story)
    smoke(story)
    defects(story)
    signoff(story)
    doc.build(story, onFirstPage=on_first, onLaterPages=on_page)
    print(f"Wrote {OUT} with {len(MODULES)} modules and {total} test cases")


if __name__ == "__main__":
    main()
