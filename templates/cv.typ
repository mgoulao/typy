#import "typy.typ": init_typy
#import "typy_data.typ": typy_data

#let typy = init_typy(typy_data)

// ── Page setup ──────────────────────────────────────────────────────────────
#set page(margin: (x: 2cm, y: 1.8cm))
#set text(font: "Linux Libertine", size: 10.5pt, lang: "en")
#set par(leading: 0.65em)

// ── Color palette ────────────────────────────────────────────────────────────
#let accent = rgb("#2563eb")  // blue-600

// ── Helper: thin horizontal rule ─────────────────────────────────────────────
#let hrule = line(length: 100%, stroke: 0.5pt + luma(180))

// ── Section heading ──────────────────────────────────────────────────────────
#let section(title) = {
  v(0.6em)
  text(weight: "bold", size: 11pt, fill: accent, upper(title))
  v(0.2em)
  hrule
  v(0.4em)
}

// ── Entry (experience / education) ───────────────────────────────────────────
#let entry(left-top, right-top, left-bottom, right-bottom, description) = {
  grid(
    columns: (1fr, auto),
    row-gutter: 0.15em,
    text(weight: "semibold", left-top),
    align(right, text(fill: luma(80), right-top)),
    text(style: "italic", left-bottom),
    align(right, text(fill: luma(80), right-bottom)),
  )
  if description != "" {
    v(0.2em)
    text(fill: luma(40), description)
  }
  v(0.5em)
}

// ── Name & contact header ─────────────────────────────────────────────────────
#align(center)[
  #text(size: 22pt, weight: "bold", typy("name", "str"))
]

#let contact = typy("contact", "array")
#let contact-parts = ()

#if contact.email != "" {
  contact-parts.push(contact.email)
}
#if contact.phone != "" {
  contact-parts.push(contact.phone)
}
#if contact.location != "" {
  contact-parts.push(contact.location)
}
#for link in contact.links {
  contact-parts.push(link)
}

#align(center)[
  #text(size: 9.5pt, fill: luma(60), contact-parts.join("  ·  "))
]

#v(0.3em)
#hrule
#v(0.5em)

// ── Summary ──────────────────────────────────────────────────────────────────
#let summary-text = typy("summary", "str")
#if summary-text != "" {
  section("Summary")
  text(summary-text)
  v(0.3em)
}

// ── Experience ───────────────────────────────────────────────────────────────
#let experience-list = typy("experience", "array")
#if experience-list.len() > 0 {
  section("Experience")
  for item in experience-list {
    entry(
      item.title,
      item.start_date + " – " + item.end_date,
      item.company,
      item.location,
      item.description,
    )
  }
}

// ── Education ────────────────────────────────────────────────────────────────
#let education-list = typy("education", "array")
#if education-list.len() > 0 {
  section("Education")
  for item in education-list {
    entry(
      item.degree,
      item.start_date + " – " + item.end_date,
      item.institution,
      item.location,
      item.description,
    )
  }
}

// ── Skills ───────────────────────────────────────────────────────────────────
#let skills-list = typy("skills", "array")
#if skills-list.len() > 0 {
  section("Skills")
  text(skills-list.join(" · "))
  v(0.3em)
}

// ── Languages ────────────────────────────────────────────────────────────────
#let languages-list = typy("languages", "array")
#if languages-list.len() > 0 {
  section("Languages")
  text(languages-list.map(l => l.name + " (" + l.level + ")").join(" · "))
  v(0.3em)
}

// ── Certifications ───────────────────────────────────────────────────────────
#let certifications-list = typy("certifications", "array")
#if certifications-list.len() > 0 {
  section("Certifications")
  for item in certifications-list {
    grid(
      columns: (1fr, auto),
      text(weight: "semibold", item.name) + [ — ] + text(style: "italic", item.issuer),
      align(right, text(fill: luma(80), item.date)),
    )
    v(0.4em)
  }
}
