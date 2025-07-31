# Multimodal PDF Question Extractor

This project provides tools to extract structured question and answer data (including images and graphs) from educational PDF documents, such as those containing quizzes or assessments.

---

##  Components

### 1. `Multimodalextract.py`

- Downloads a PDF file.
- Extracts:
  - Text chunks
  - Embedded images
- Organizes extracted content by page into a structured JSON format for further processing: `processed_output.json`.

### 2. `OrganiseintoJSON.py`

- Parses `processed_output.json`.
- Extracts individual questions and multiple-choice options.
- Detects and structures image-based questions (e.g., graphs).
- Matches and appends answers and explanations using fuzzy matching.
- Final structured output is saved as `questions.json`.


## High-Level Approach & Thought Process

### Objective:
To extract structured questions and answers (including image-based questions like graphs) from a PDF quiz document, and save them in a structured format (`questions.json`) that includes:
- Question text
- Images
- Options (text or image)
- Correct answer and explanation 

---

### Two-Phase Architecture:

#### **Phase 1: Extraction (`Multimodalextract.py`)**
- **Goal:** Break down the PDF into usable components (text chunks, images) and organize them page by page.

##### Steps:
1. **Download the PDF**
   - Assumes a direct URL is available.
   - Downloads once and stores in a `data/` directory.

2. **Open PDF using `PyMuPDF`**
   - Iterates through all pages.

3. **Text Extraction**
   - Extracts the entire page's text and stores it in `.txt` files per page.

4. **Image Extraction**
   - Extracts all embedded images per page.
   - Saves them as PNGs and encodes them to base64 for later use.

5. **Organize Extracted Content**
   - Groups all items (`text`, `images`) by page into a JSON list (`processed_output.json`).

---

#### **Phase 2: Parsing & Structuring (`OrganiseintoJSON.py`)**
- **Goal:** Interpret extracted data to identify structured questions, options, and correct answers.

##### Steps:
1. **Load Processed JSON**
   - Reads `processed_output.json`.

2. **Split Content into Questions**
   - Uses regex patterns to detect numbered questions (e.g., `1.`, `2.`, etc.).
   - Supports multiline question blocks.

3. **Graph/Image-Based Question Detection**
   - Uses keyword matching (e.g., "Which graph", "best fits") to identify visual MCQs.
   - Assumes such questions do not have A/B/C options in text but use images instead.

4. **Text-Based Option Parsing**
   - Uses regex to match standard `A)`, `B)` options.

5. **Answer Matching**
   - Once the "Answers" section is found in the PDF:
     - Splits answer content from the questions.
     - Uses fuzzy string matching (`fuzzywuzzy`) to associate answers with the best matching question text.
     - Adds `correct_answer` and `answer_explanation` to questions.

6. **Save Final Output**
   - Produces a clean `questions.json` file suitable for further use in quiz apps, AI training, etc.

---

## Assumptions Made

1. **Structured Format in PDF**
   - Assumes questions are clearly numbered (`1.`, `2.` ...).
   - Assumes answers appear under a section labeled "Answers".

2. **Graph/Image Question Detection**
   - Assumes these do **not** have A/B/C options in text, but are followed by multiple images.
   - Detects them via keywords (e.g., "Which graph").

4. **Images Belong to Questions on the Same Page**
   - Assumes any images on a page belong to the question(s) on that page.

5. **Fuzzy Matching is Sufficient**
   - Relies on `fuzzywuzzy` with a threshold (80%) to match answer text with question text.

6. ** PDF Has No Tables **
   - Currently ignores any tables or forms as this pdf didn't have any — only text and image content are extracted.




## Requirements

- **Python 3.7+ is required**

Install dependencies using:

```bash
pip install -r requirements.txt
---
```
## Requirements

## Installation

Before running the scripts, install the required dependencies:

```bash
pip install -r requirements.txt
```
---


**Dependencies include:**
- `requests`
- `PyMuPDF`
- `tqdm`
- `fuzzywuzzy`
- `python-Levenshtein` 

---

## How to Run

Run the scripts in the following order:

### 1. Step 1: Run the PDF extractor

```bash
python Multimodalextract.py
```

- Downloads the PDF from a URL.
- Extracts all text and images structured by page.
- Saves output to `data/` and `processed_output.json`.

---

### 2. Step 2: Run the question organizer

```bash
python OrganiseintoJSON.py
```

- Parses and structures questions from the extracted data.
- Matches answers with questions using fuzzy string matching.
- Final output is saved as `questions.json`.

---

## Output Files

- `data/`: Folder containing all extracted text and images.
- `processed_output.json`: Intermediate structured representation of the PDF.
- `questions.json`: Final list of questions, options, answers, and explanations.

---

## Notes

- This is currently configured to process a BBC Skillswise graph quiz PDF.
- Image-based questions are detected automatically via keyword matching.
- Works best with structured PDFs containing clearly numbered questions.


---

## 📂 Example Project Structure

```
.
├── Multimodalextract.py
├── OrganiseintoJSON.py
├── requirements.txt
├── README.md
├── processed_output.json
├── questions.json
└── data/
    ├── images/
    └── text/
```

---
