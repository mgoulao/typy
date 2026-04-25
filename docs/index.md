# typy

```{raw} html
<section class="typy-hero typy-hero-bg">
	<h1>Build polished PDFs from Python and Markdown</h1>
	<p>typy combines a typed Python API, reusable Typst templates, and a CLI designed for both developers and AI agents.</p>
	<a class="typy-cta" href="getting-started.html">Get started</a>
	<a class="typy-cta secondary" href="cookbook.html">Open cookbook</a>
</section>
```

## Quick start

```bash
typy scaffold report --output data.json
typy render --template report --data data.json --output report.pdf
```

## Explore

```{raw} html
<section class="typy-grid">
	<article class="typy-card">
		<h3>Getting started</h3>
		<p>Install typy and render your first document in minutes.</p>
		<a href="getting-started.html">Read guide</a>
	</article>
	<article class="typy-card">
		<h3>Cookbook</h3>
		<p>11 runnable examples from invoices to presentations and batch generation.</p>
		<a href="cookbook.html">View recipes</a>
	</article>
	<article class="typy-card">
		<h3>Template reference</h3>
		<p>Inspect built-in templates and field schemas for each document type.</p>
		<a href="templates.html">Browse templates</a>
	</article>
	<article class="typy-card">
		<h3>CLI reference</h3>
		<p>Command-by-command guidance and options for automation-friendly usage.</p>
		<a href="cli.html">Open CLI docs</a>
	</article>
	<article class="typy-card">
		<h3>API reference</h3>
		<p>Module-level API pages generated from source and type signatures.</p>
		<a href="api/index.html">Read API</a>
	</article>
	<article class="typy-card">
		<h3>Package format</h3>
		<p>RFC: .typy container structure, manifest v1 schema, versioning policy, and error model.</p>
		<a href="package-format.html">Read RFC</a>
	</article>
	<article class="typy-card">
		<h3>Vertical design systems</h3>
		<p>Domain-specific template families sharing a Typst theme and Python base models — legal vertical ships built-in.</p>
		<a href="design-systems.html">Learn more</a>
	</article>
	<article class="typy-card">
		<h3>LLM resources</h3>
		<p>Machine-oriented entry points and generated llms.txt context files.</p>
		<a href="llm.html">Open LLM page</a>
	</article>
</section>
```

```{toctree}
:maxdepth: 2
:caption: Contents
:hidden:

cookbook
getting-started
templates
design-systems
cli
package-format
api/index
llm
```
