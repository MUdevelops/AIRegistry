# query-rewriter

**Version:** 1.0.0

Lightweight deterministic query rewriting for retrieval workflows.

## Overview

`query-rewriter` normalizes user search text into a cleaner retrieval-ready
query while preserving the original wording and intent.

It is designed for AI and RAG workflows where consistent query preprocessing
is useful before retrieval.

## Features

- Dependency-free
- Deterministic
- No network access
- No external model or API required
- Preserves the user's original query content
- Normalizes whitespace
- Simple Python API

## Installation

Install through AIRegistry:

```bash
ai add query-rewriter@1.0.0