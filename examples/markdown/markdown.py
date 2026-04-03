from typy.builder import DocumentBuilder
from typy.markup import Markdown
from typy.templates import BasicTemplate

body = Markdown("""
## Results

The analysis shows a **significant improvement** in performance.

| Metric | Before | After |
|--------|--------|-------|
| Latency | 120ms | 45ms |
| Throughput | 1000 | 3200 |

### Key Takeaways

- Latency dropped by more than **60%**
- Throughput increased by **3×**

> These results were measured under identical load conditions.

For full details see the [source code](https://github.com/mgoulao/typy).
""")

template = BasicTemplate(
    title="Performance Report",
    date="2024-01-01",
    author="Jane Doe",
    body=body,
)

DocumentBuilder().add_template(template).save_pdf("markdown.pdf")
