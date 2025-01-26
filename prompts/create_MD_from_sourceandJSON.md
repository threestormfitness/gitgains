You are given two inputs:
1. **JSON Data** describing a strength/loading module (sets, reps, intensity, rest, etc.).
2. **Source Material** with more detailed explanations, background, and guidelines.

**Your Task**: 
Using these two inputs, create a cohesive Markdown (MD) page that presents the module in a “wiki-style” format. The MD page should include the following sections (in this order):

1. **Main Title**  
   - Use the "name" field from the JSON as the title, plus a short descriptor (if appropriate).

2. **Module Details**  
   - Create a table with two columns: **Field** and **Value**.
   - Populate each row using the JSON keys as the “Field” (e.g., id, name, author_source, etc.) and the JSON values as the “Value.”
     - If a particular key is not present or is irrelevant, omit it.
   - The table should look similar to:

     ```
     | Field                          | Value                              |
     |--------------------------------|------------------------------------|
     | **id**                         | `...`                              |
     | **name**                       | `...`                              |
     | ...                            | ...                                |
     ```

3. **Overview and Execution**  
   - Summarize how to perform the module (sets, reps, load, rest intervals, etc.).
   - If the JSON has an "overview_and_execution" field, integrate it here.
   - Incorporate any relevant details from the source material to clarify methodology, progression, or rationale.

4. **Plateau or Stalling Strategies** (if relevant)  
   - If the JSON or source mentions how to handle missed reps, plateaus, or stalling, include a section on recommended strategies.
   - This can be omitted if the module doesn't address stalling.

5. **Example Application**  
   - Include a clear, real-world example of how someone might run this program over days/weeks.  Use strength standards that might apply to an intermediate to advanced 185 lbs male trainee, unless source material suggests a different example
   - Use the JSON’s "example_application" if provided, or adapt from the source text.
   - This should be simple and easy to follow, but provide enough content to help the reader visualize the process through the course of several training sessions (as many as necessary to show what progressions may look like)

6. **Important Notes**  
   - Mention any cautionary points, best practices, or special considerations (e.g., “Don’t train to failure,” “Start at 70% 1RM,” etc.).
   - Use the JSON’s "important_notes" or any similar field.

7. **Volume Metrics**  
   - Present total sets/reps or any volume details from the JSON or source.
   - If no explicit data is provided, either derive it from the sets × reps × exercises or leave it out.

8. **Summary**  
   - Provide a concise wrap-up of why this module is used, who it’s for (e.g., beginner, intermediate), and any final thoughts.
   - You may draw from the source material or your own knowledge (in a minimal, summarizing way).

---

### Formatting Rules

- The entire output **must be in Markdown**.
- Use consistent headings (e.g., `##`, `###`) and subheadings to organize the sections.
- Maintain a clean, readable layout.
- For the **Module Details** table, bold the “Field” names and present values verbatim (unless you need to reformat for clarity).
- If any field from the JSON is repeated or redundant, feel free to merge them, but avoid losing necessary info.
- If the source material conflicts with the JSON, **prioritize the JSON** (unless asked otherwise).

### Example Workflow

1. **Read the JSON** and note all fields (e.g., id, name, reps, intensity, rest intervals, example_application, etc.).
2. **Scan the source material** for additional context: explanation, instructions, or extra detail that can complement or clarify the JSON data.
3. **Write the module in MD** following the structure: title → module details table → overview → stalling → examples → notes → volume → summary.
4. **Ensure final output is a single cohesive document** in Markdown.

**Now, please use this approach to generate the final MD document. If anything is unclear or missing, make a best guess or note the omission.**
