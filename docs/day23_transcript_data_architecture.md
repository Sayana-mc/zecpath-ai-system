# Day 23 — transcript data architecture

The root persists screening sessions, transcript segments, and structured
question/answer interactions in SQLite. Session state and candidate/opening
association are checked through the existing application records. Segment
batches validate all inputs before persistence, and sequence numbers must be
strictly increasing from one across the session.

Raw and whitespace-normalized text are stored separately. Timestamp and
confidence fields are optional; timestamps must include timezone information
when supplied, and confidence is bounded from zero to one. Transcript
retrieval returns the session, segments, and interactions under the existing
recruiter authentication boundary.

This is a storage and manual/import data contract only. There is no audio
recording, speech-to-text, speaker diarization, live voice AI, or automated
interviewing integration. No transcript content is scored by this feature.
