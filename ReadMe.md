Quantitative Framework for Middle Persian Syntax
This repository contains some of the most relevant computational infrastructure, data-driven analysis, and preliminary grammar chapters for the syntax of Zoroastrian Middle Persian. It serves as a technical companion for reviewers and researchers.
📂 Repository Structure
1. Research Notebooks (Jupyter)
These notebooks provide a transparent, step-by-step view of the statistical transformations and visualization logic:
vp_stats.ipynb: Comprehensive data on the Verb Phrase (valency, light-verbs, and serial verbs).
diathesis.ipynb: Analysis of alignment, ergativity, and participant marking.
adverbial_queries.ipynb: Extraction and classification of simple and periphrastic adverbs.
Morphology_queries.ipynb: Large-scale extraction of PoS categories and word-formation patterns.
token-count.ipynb: Baseline metrics for sentence and token counts across the corpus.
2. Preliminary Grammar Chapters
The folder old-sections-inprogress/ contains preliminary drafts of key syntactic sections, expanding on the statistical findings:
Comparative Syntax: Analysis of az and kū constructions and superlative strategies.
Coordination and Ellipsis: Investigation of the "Orphan" relation and non-projectivity in SOV coordination.
3. Data and Baseline
query-stats/: Directory containing raw .csv outputs and baseline metrics generated per text to allow for genre-specific normalization.
The planned scripts.docx: Technical roadmap and research assumptions for the computational pipeline.
🔗 Related Work
This repository is part of a broader study on the transition from synthetic to analytic structures in Middle Persian.
Paper Repository: MiddlePersian-NounPhrase-Classes
Publication: Head Directionality and the Ezafe Marking in Middle Persian Noun Phrase: A Corpus-Based Approach. (Submitted to International Journal of Corpus Linguistics).
DOI: 10.5281/zenodo.19113772
💡 Reproducibility
All scripts and notebooks are designed to be forward-compatible. They are based on the stabilized snapshot of the MPCD (Sept 2024) but are configured to be re-run on new versions of the corpus after text imports or annotation modifications.