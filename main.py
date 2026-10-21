"""PrintHub: PyScript logic. Every feature runs from a browser event."""
from html import escape
from pyscript import document, when

PRICE = {"q-bw": ("Black & white", 1.0), "q-color": ("Colored", 3.0), "q-copy": ("Photocopy", 1.0)}

SERVICES = [
    ("Black & white printing", "₱1.00 / page", "print", "Assignments, reports, and research papers."),
    ("Colored printing", "₱3.00 / page", "print", "Presentations, charts, and project pages."),
    ("Photocopying", "₱1.00 / page", "print", "Copy notes, IDs, and forms."),
    ("Scanning", "Price at counter", "finish", "Turn paper into a file."),
    ("Lamination", "Price at counter", "finish", "Protect certificates and IDs."),
    ("Document binding", "Price at counter", "finish", "Neat covers for reports."),
]

COMPETITORS = {
    "Max Copy Center": ("Sanciangko St.",
        "Many services: digital and press printing, B&W and color photocopying, risograph, posters, books, stickers.",
        "Broad and not focused on students. PrintHub concentrates on school documents."),
    "Seventy Seven Digital Arts": ("138 Mall, Colon St.",
        "Document printing, photocopying, lamination, photo printing, PVC IDs, and online orders.",
        "Serves many customer types. PrintHub is built around college students."),
    "Sebu Printing": ("Palaez St.",
        "Document and photo printing, photocopying, scanning, and lamination.",
        "General printing products. PrintHub specializes in academic printing."),
}

tickets = []


def peso(x):
    return f"₱{x:,.2f}"


def qty(el_id):
    try:
        return max(int(float(document.querySelector(f"#{el_id}").value)), 0)
    except ValueError:
        return 0


def addons():
    boxes = document.querySelectorAll("fieldset input")
    return [b.value for b in boxes if b.checked]


def lines():
    out = []
    for key, (label, price) in PRICE.items():
        n = qty(key)
        if n:
            out.append((label, n, price, n * price))
    return out


# ---------- Live receipt (input events) ----------
@when("input", ".job-in")
def draw_receipt(event=None):
    rows = lines()
    html = ""
    for label, n, price, sub in rows:
        html += f'<div class="rl"><span>{label}<br><small>{n} × {peso(price)}</small></span><span>{peso(sub)}</span></div>'
    for a in addons():
        html += f'<div class="rl"><span>{a}</span><span>at counter</span></div>'
    if not html:
        html = '<p class="rempty">Add pages to start your receipt.</p>'
    document.querySelector("#r-lines").innerHTML = html
    document.querySelector("#r-total").textContent = peso(sum(r[3] for r in rows))
    extra = addons()
    document.querySelector("#r-note").textContent = (
        "Finishing is priced when you arrive." if extra else "Prices: B&W ₱1, color ₱3, copy ₱1 per page.")

# ---------- Dela Cruz Icy Jake -----------
# ---------- Send job send event ----------
@when("submit", "#job-form")
def send_job(event):
    event.preventDefault()
    msg = document.querySelector("#j-msg")
    name = document.querySelector("#j-name").value.strip()
    rows = lines()
    if not name or not (rows or addons()):
        msg.textContent = "Add your name and at least one page count or finishing service."
        msg.className = "msg err"
        return
    n = len(tickets) + 1
    tickets.append({
        "no": f"PH-{n:03d}", "name": name,
        "file": document.querySelector("#j-file").value.strip() or "File at counter",
        "items": [f"{label} × {q}" for label, q, _, _ in rows] + addons(),
        "total": sum(r[3] for r in rows), "done": False})
    msg.textContent = f"Ticket PH-{n:03d} created. Show it at the counter."
    msg.className = "msg ok"
    render_tickets()


def render_tickets():
    box = document.querySelector("#tickets")
    if not tickets:
        box.innerHTML = '<p class="empty">No tickets yet. Send a job above.</p>'
        return
    html = ""
    for t in reversed(tickets):
        state = "Picked up" if t["done"] else "Ready for pickup soon"
        btn = "" if t["done"] else f'<button class="pick" data-no="{t["no"]}">Mark picked up</button>'
        html += (f'<article class="ticket{" done" if t["done"] else ""}"><b class="tno">{t["no"]}</b>'
                 f'<div><strong>{escape(t["name"])}</strong><br><small>{escape(t["file"])}</small>'
                 f'<p>{escape(", ".join(t["items"]))}</p></div>'
                 f'<div class="tr"><b>{peso(t["total"])}</b><small>{state}</small>{btn}</div></article>')
    box.innerHTML = html


@when("click", "#tickets")
def pick_up(event):
    b = event.target
    if b.classList.contains("pick"):
        for t in tickets:
            if t["no"] == b.dataset.no:
                t["done"] = True
        render_tickets()

# ---------- Service filter (click events) ----------
def draw_services(kind="all"):
    html = ""
    for name, price, k, desc in SERVICES:
        if kind in ("all", k):
            html += f'<article class="sv {k}"><h3>{name}</h3><p class="sp">{price}</p><p>{desc}</p></article>'
    document.querySelector("#svc").innerHTML = html


@when("click", ".tab[data-f]")
def filter_services(event):
    for t in document.querySelectorAll(".tab[data-f]"):
        t.classList.remove("on")
    event.target.classList.add("on")
    draw_services(event.target.dataset.f)

# ---------- Alga Daryl ----------
# ---------- Competitor Comparison ----------
def show_comp(name):
    place, strong, gap = COMPETITORS[name]
    document.querySelector("#comp").innerHTML = (
        f'<div><h3>{name}</h3><p class="loc">{place}</p><p><b>Strengths.</b> {strong}</p></div>'
        f'<div class="gap"><h3>Where PrintHub fits</h3><p>{gap}</p></div>')
    for t in document.querySelectorAll("#comp-tabs .tab"):
        t.classList.toggle("on", t.textContent == name)


tabs = document.querySelector("#comp-tabs")
for name in COMPETITORS:
    b = document.createElement("button")
    b.className = "tab"
    b.textContent = name
    tabs.appendChild(b)


@when("click", "#comp-tabs .tab")
def pick_comp(event):
    show_comp(event.target.textContent)


draw_services()
show_comp("Max Copy Center")
draw_receipt()
render_tickets()
