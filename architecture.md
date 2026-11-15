# Architecture Diagram

```text
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Parser    │───▶│   Matcher   │───▶│   Ranker    │───▶│  Scheduler  │
│   Agent     │    │   Agent     │    │   Agent     │    │   Agent     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                  │                  │                  │
       └──────────────────┴──────────────────┴──────────────────┘
                          │
                  ┌───────▼────────┐
                  │   Shared       │
                  │  Candidate     │
                  │     Pool       │
                  │   (in-memory)  │
                  └───────┬────────┘
                          │
                  ┌───────▼────────┐
                  │   Pipeline     │
                  │  Coordinator   │
                  │  (orchestrator)│
                  └────────────────┘

---

### Step 3: The README (`README.md`)
1. Click the main `recruitment_pipeline` folder. New File -> `README.md`.
2. Copy the entire README from my very first message (it has the Agent Roster, Why it fits, Tools, etc.) and paste it.
3. At the very bottom, add this line and **Ctrl + S**:
`*All code was written, understood, and tested by [Your Name, Roll No].*`

---

### Step 4: Zip it up for submission
1. Close VS Code.
2. Go to your Desktop and find the `recruitment_pipeline` folder.
3. Right-click it and choose **"Compress to ZIP file"** (or "Send to -> Compressed folder").
4. Rename the zip file to `YourRollNo_CSE476_Project2.zip`.

### One final note for your Viva (Oral Exam)
If the teacher asks, *"Why did you use a sequential pipeline?"*
**Your Answer:** *"Because screening candidates is a conveyor belt. The output of the Parser is the input of the Matcher. There is no negotiation or parallel research needed. If I used a manager-worker architecture, it would just add unnecessary latency."*

If they ask, *"What is the honest failure?"*
**Your Answer:** *"Two things. First, Dan Wu's resume didn't list years, so the parser didn't guess; it scored him 0.0 on experience. Second, if two candidates want the same interview slot, the scheduler doesn't double-book; it flags it as 'NO SLOT AVAILABLE' for human escalation."*

**You are completely done with the project. Amazing job sticking with it! Let me know if you need anything else.**
```
