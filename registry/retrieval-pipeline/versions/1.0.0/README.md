# retrieval-pipeline

**Version:** 1.0.0

Composable retrieval workflow that connects a retriever with a context builder
to produce bounded AI-ready context.

## Overview

`retrieval-pipeline` provides a small orchestration layer for retrieval-based AI
applications.

It separates the workflow into three stages:

```text
User Query
    ↓
Retriever
    ↓
Selected Passages
    ↓
Context Builder
    ↓
AI-ready Context