# Day 22 — Conversational Question Schema

## Purpose

Defines the contract for conversation-ready question objects used in interactive HR screening sessions and future automated voice screening engines.

---

## 1. Schema Specification

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ConversationalQuestion",
  "type": "object",
  "properties": {
    "question_id": {
      "type": "string",
      "pattern": "^[A-Z0-9_-]+$"
    },
    "role_id": {
      "type": "string",
      "enum": ["DATA_ANALYST", "SOFTWARE_DEVELOPER", "GENERAL_TECH", "GENERAL_NON_TECH"]
    },
    "category": {
      "type": "string",
      "enum": [
        "INTRODUCTION",
        "EDUCATION",
        "EXPERIENCE",
        "SKILLS",
        "LOCATION",
        "SALARY",
        "NOTICE_PERIOD"
      ]
    },
    "question_text": {
      "type": "string",
      "minLength": 5
    },
    "expected_answer_type": {
      "type": "string",
      "enum": [
        "TEXT",
        "NUMBER",
        "YES_NO",
        "SINGLE_CHOICE",
        "MULTIPLE_CHOICE",
        "DATE",
        "DURATION",
        "LOCATION",
        "CURRENCY",
        "NOTICE_PERIOD",
        "SKILL_LIST"
      ]
    },
    "mandatory": {
      "type": "boolean"
    },
    "scoring_importance": {
      "type": "string",
      "enum": ["HIGH", "MEDIUM", "LOW", "INFORMATIONAL"]
    },
    "display_order": {
      "type": "integer",
      "minimum": 1
    },
    "is_active": {
      "type": "boolean",
      "default": true
    },
    "version": {
      "type": "integer",
      "default": 1
    },
    "translations": {
      "type": "object",
      "properties": {
        "en": { "type": "string" },
        "ml": { "type": ["string", "null"] },
        "hi": { "type": ["string", "null"] }
      },
      "required": ["en"]
    }
  },
  "required": [
    "question_id",
    "role_id",
    "category",
    "question_text",
    "expected_answer_type",
    "mandatory",
    "scoring_importance",
    "display_order",
    "translations"
  ]
}
```

