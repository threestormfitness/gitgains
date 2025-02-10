You are an expert system that converts strength-training “loading modules” into structured data. 

A “loading module” is a set/rep scheme (often with progression, regression, or periodization strategies) that can be plugged into a strength or hypertrophy program. 

**Your task**: Read the source material below and produce a JSON object capturing the module’s key parameters. If an item is not explicitly stated, use your best judgment to fill in reasonable defaults or mark it as "open," "varies," "N/A," or "no," depending on context.  

**Important**:  
1. Keep answers concise.  
2. If the source material is ambiguous, do your best to interpret it.  
3. When in doubt, use "N/A," "open," or "varies."  
4. Use "yes" or "no" for simple presence/absence fields unless “varies” makes more sense (e.g., “train_to_failure,” “drop_sets,” etc.).  
5. Round `avg_time_session` to the nearest 1 minute by following the rules for set/rest durations (see details below).  
6. For `id` and `name`, see naming guidelines below to keep them somewhat systematic and informative.  

Below are the fields to populate **in the exact order** shown. Return only valid JSON (no extra commentary).  

---

### Field List & Guidelines

1. **id**  
   - A short, systematic identifier for the loading module.  
   - Suggestion: combine or abbreviate any known author/program name, a main characteristic (e.g., “531,” “EDT,” “DropSets”), and maybe the approximate time or an incremental index.  
   - Example: `"wendler531_45min_cycle"` or `"gzcl_przone_varies"`.  
   - If truly unknown, you can do `"custom_loading_mod_01"` or similar.

2. **name**  
   - A user-friendly but still systematic title.  
   - Include:  
     - Author or program name if known,  
     - Key rep or loading characteristic,  
     - Approx. time per session if relevant.  
   - Example: `"Wendler’s 5/3/1 — 4-Week Progression (45 min per session)"`.  

3. **author_source**  
   - Name of the known author, origin, or “N/A” if unknown.  
   - E.g., `"Jim Wendler"`, `"from GZCL"`, `"n/a"`.  

4. **cycle_duration**  
   - How many sessions (or weeks) in the recommended cycle.  
   - If unspecified, use `"open"`.  
   - If it depends on performance, use `"varies"`.  

5. **total_sets**  
   - Total sets per session or per exercise as stated in the module.  
   - If it can change, use `"varies"`.  
   - If it’s a time-block approach (e.g., EDT 15-min PR zone) and not a fixed set count, also use `"varies"`.  

6. **reps**  
   - One of: `"varies"`, `1-5`, `6-10`, `11-15`, `15+`, or a range if specifically stated.  

7. **intensity_unit**  
   - One of: `"RIR"`, `"RPE"`, `"%"`, `"other"`, or `"N/A"` if no explicit loading parameter is mentioned.  

8. **intensity_range**  
   - The range of intensity across the module.  
   - If not stated, estimate using standard 1RM references, or `"N/A"` if truly unknown.  
   - Examples: `"70-85% 1RM"`, `"RPE 7-9"`, `"N/A"`.  

9. **avg_time_session**  
   - Total time (minutes) to complete the module, rounded to the nearest 1 minute.  
   - **Calculation rules** (simplified):  
     - Each standard set: 30–45 seconds.  
     - Each explosive (e.g., plyo <5 reps) set: 15–25 seconds.  
     - Rest for heavy sets (≤5 reps): 3–5 min.  
     - Rest for sets ≥6 reps: 90–120 sec.  
     - If rest is “as little as possible,” assume 15 sec.  
     - If sets/rest durations are explicitly stated, use those.  
     - Take the average of these ranges.  
     - Do not factor in warmups in the calculation
     - If the source material discusses assistance, auxiliary, or accessory work, or any other part of the workout is not directly part of the loading module, do not factor it into the calculation

10. **time_per_session_breakdown**  
   - Show how you arrived at avg_time_session.  
   - E.g., `"3 sets x 30-45s each + 90s rest between = ~8-10 min total"`.  

11. **amrap**  
   - `"yes"` if it has AMRAP sets; else `"no"` or `"varies"` if partial instructions exist.  

12. **timed**  
   - `"yes"` if sets are done for time (e.g., 30s on/30s off); else `"no"`.  

13. **emom**  
   - `"yes"` if it specifies every-minute-on-the-minute structure; else `"no"`.  

14. **train_to_failure**  
   - `"yes"` if instructions say “to failure,” AMRAP to failure, 0 RIR, or similar.  
   - `"varies"` if it might happen depending on progression.  
   - `"no"` otherwise.  

15. **superset_type**  
   - One of:  
     - `"N/A"` (no explicit superset),  
     - `"antagonist"`,  
     - `"compound"` (giant set),  
     - `"circuit"` (3+ exercises in a sequence),  
     - `"complex"` (same equipment, no rack-down),  
     - or `"open"` if unclear.  

16. **spec_movement**  
   - List the specific movement(s) if the module is speically designed for one (e.g., “bench press,” “squat”),  
   - Otherwise `"open"`.  

17. **autoregulated**  
   - `"yes"` if it includes an autoregulation mechanism (e.g., APRE, 531 Joker sets);  
   - `"no"` otherwise.  

18. **drop_sets**  
   - `"yes"` if drop sets are mentioned;  
   - `"no"` otherwise.  

19. **rest_pause**  
   - `"yes"` if rest-pause sets are used (e.g., DoggCrapp style);  
   - `"no"` otherwise.  

20. **cluster**  
   - `"yes"` if cluster sets are used (e.g., 2 reps, rest 20s, 2 reps, rest 20s...);  
   - `"no"` otherwise.  

21. **tempo_spec**  
   - `"yes"` if specific tempo instructions are included (e.g., triphasic, heavy negatives);  
   - `"no"` otherwise.  

22. **wave_sets**  
   - `"yes"` if wave-loading or ratchet-loading is used (e.g., 3/2/1 waves);  
   - `"no"` otherwise.  

23. **ladder_sets**  
   - One of: `"ascending"`, `"descending"`, `"pyramid"`, or `"n/a"` if no ladder.  

24. **density_sets**  
   - `"yes"` if it uses density training (EDT, HDL, etc.);  
   - `"no"` otherwise.  

25. **straight_sets**  
   - `"yes"` if the module is characterized by straightforward sets (3×10, 5×5, etc.) with consistent rest/loading;  
   - `"no"` if it explicitly uses drop sets, wave sets, etc.  

26. **contrast_sets**  
   - `"yes"` if contrasting intensities/tempos in the same set (e.g., heavy + plyometric);  
   - `"no"` otherwise.  

27. **total_rep_target**  
   - A fixed total rep target, often to complete as fast as possible (e.g., “100 push-ups”).  
   - If none stated, `"n/a"`.  

28. **deload**  
   - `"yes"` if a deload strategy is strongly recommended;  
   - `"no"` otherwise.  

29. **overview_and_execution**  
   - A concise explanation (for a novice) of how to run the module.  
   - Include key progressions, regressions, or cycle details from the source.  
   - Omit generic safety or health disclaimers—just the module details.  

30. **example_application**  
   - Show a brief, realistic example with actual numbers (if relevant).  
   - E.g., how an intermediate lifter might run a 4-week cycle.  

31. **important_notes**  
   - Key “must-do” guidelines or distinct rules for success.  
   - Summarize the author’s unique instructions or special tips.  

32. **volume_metrics**  
   - Provide total volume details: sets × reps or general range.  
   - Exclude warm-ups or assistance.  
   - If it varies by week, describe the range (e.g., “3–6 sets of 2–6 reps over the cycle”).  

---

### Source Material

[PASTE YOUR LOADING MODULE TEXT HERE — the excerpt from an article/program/document that describes the sets, reps, rest, progression, etc.]

---

**Instructions**:  
1. Read the “Source Material.”  
2. Map every detail you can into the JSON fields above, in the exact order.  
3. Use `"yes"`, `"no"`, `"varies"`, or `"n/a"` as needed.  
4. Return **only** the JSON object (no extra text).

**That’s it!** End your answer with the complete JSON object.
