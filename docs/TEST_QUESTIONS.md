# Test Questions — Evaluation Benchmark

Use this list to validate the chatbot after every meaningful change.
Fill in the "Expected" column with the answer you'd consider correct,
based on the actual Rheonics documentation.

**Goal**: 80% pass rate before Phase 1 is considered complete.

---

## Product knowledge (specs)

| # | Question | Expected answer (key facts) | Pass/Fail |
|---|----------|-----------------------------|-----------|
| 1 | What is the viscosity range of the SRD? | 1 to 3,000 cP standard | ⏳ |
| 2 | What is the density accuracy of the SRD? | 0.001 g/cc | ⏳ |
| 3 | What process fluid temperature can the SRD handle? | -40 up to 285 °C | ⏳ |
| 4 | What materials are available for wetted parts? | 316L SS, Hastelloy C22 | ⏳ |
| 5 | What is the ingress protection rating? | IP69K (limited by M12) | ⏳ |

## Communication protocols

| # | Question | Expected | Pass/Fail |
|---|----------|----------|-----------|
| 6 | What digital outputs does the SRD support? | Modbus RTU, Ethernet, USB, HART | ⏳ |
| 7 | Does the SRD support Profinet? | Yes, via Ethernet | ⏳ |
| 8 | What analog output does the SRD have? | 4-20 mA (3 channel) | ⏳ |

## Applications / use cases

| # | Question | Expected | Pass/Fail |
|---|----------|----------|-----------|
| 9 | What is the SRD used for in drilling? | Inline mud density + viscosity | ⏳ |
| 10 | What is CoaguTrack? | Cheese curd firmness monitoring | ⏳ |
| 11 | Can the SRV be used for battery slurry? | Yes, real-time viscosity control | ⏳ |

## Ordering / configuration

| # | Question | Expected | Pass/Fail |
|---|----------|----------|-----------|
| 12 | What are the SRD electronics options? | SME-TRD, SME-TR, SME-DRM | ⏳ |
| 13 | Example order code for standard SRD? | SRD D1 DCAL1 V1 STD E1... | ⏳ |
| 14 | What is the maximum pressure rating? | Up to 500 bar (7500 psi) | ⏳ |

## Accessories

| # | Question | Expected | Pass/Fail |
|---|----------|----------|-----------|
| 15 | What is the STCM? | Smart Thermal Control Module | ⏳ |
| 16 | What temperature range does the STCM cover? | 5 °C to 120 °C | ⏳ |
| 17 | STCM temperature stability? | 0.005 °C | ⏳ |

## Edge cases (should NOT answer, or should ask for context)

| # | Question | Expected behavior | Pass/Fail |
|---|----------|-------------------|-----------|
| 18 | Why isn't my sensor turning on? | Ask for error code / image | ⏳ |
| 19 | How much does an SRV cost? | Decline, outside scope | ⏳ |
| 20 | How does an Emerson viscometer compare? | Decline, not Rheonics product | ⏳ |

---

## Running the test

*(to be filled when backend is ready)*

```powershell
python -m backend.evaluate --questions docs/TEST_QUESTIONS.md
```

## Results log

| Date       | Version | Pass rate | Notes |
|------------|---------|-----------|-------|
| 2026-04-18 | —       | —         | Baseline — no system built yet |
