Title: g2nb: One Notebook, Four Bioinformatics Platforms
Date: 2026-06-10
Slug: g2nb-galaxy-globus
Tags: open-source, bioinformatics
Summary: g2nb extends GenePattern Notebook into a JupyterLab environment that also speaks Galaxy, Globus, and IGV.

Most bioinformatics platforms are islands: your data lives in one system, your compute in another, your visualization tools in a third. g2nb is our attempt to make a single JupyterLab environment fluent in several of them at once — GenePattern, Galaxy, Globus, and IGV — without forcing researchers to learn four separate interfaces.

## What actually changes for a researcher

In practice this means a notebook cell can launch a GenePattern job, another cell can move the output through Globus to wherever it needs to live, and IGV can render the result inline — all without leaving the notebook or writing glue code by hand.

## Why this is a joint appointment problem

g2nb exists because of a joint academic appointment between UC San Diego and the Broad Institute — the kind of cross-institutional plumbing that's easy to defer indefinitely unless someone owns it end to end. That's effectively been my role since 2016.
