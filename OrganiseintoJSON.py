import re
import json

with open("processed_output.json", "r") as f:
    page_data = json.load(f)

all_questions = []
answers_text = ""
found_answers = False

graph_keywords = [
    "graph that best fits", 
    "Choose the graph", 
    "Which graph", 
    "best fits the statement"
]

def is_graph_question(question_text, lines, image_paths):
    if not image_paths or len(image_paths) < 2:
        return False
    has_graph_keywords = any(kw.lower() in question_text.lower() for kw in graph_keywords)
    has_no_text_options = not any(re.match(r'^([A-Z])\)', line) for line in lines[1:])
    return has_graph_keywords and has_no_text_options


#  Extract questions
for page in page_data: 
    page_num = page["page"]
    raw_text = page["text_chunks"][0]["content"]
    
    if "Answers" in raw_text:
        split_parts = raw_text.split("Answers")
        raw_text = split_parts[0]
        answers_text += split_parts[1] if len(split_parts) > 1 else ""
        found_answers = True
    elif found_answers:
        # After Answers section starts, accumulate remaining answer content
        answers_text += "\n" + raw_text

    # Process only question section
    if not found_answers:
        pattern = r'(\d+)\.\s*(.+?)(?=\n\d+\.\s|\Z)'
        matches = re.findall(pattern, raw_text, re.DOTALL)

        for qid, qblock in matches:
            image_paths = [img["path"] for img in page.get("images", [])]

            lines = [line.strip() for line in qblock.strip().split('\n') if line.strip()]
            question_text = lines[0]
            options = []
            if is_graph_question(question_text, lines, image_paths):
                keys = ["A", "B", "C", "D"][:len(image_paths)]
                options = [{"key": k, "image": path} for k, path in zip(keys, image_paths)]
            else:
                options = []
                for line in lines[1:]:
                    
                    match = re.match(r'^([A-Z])\)\s+(.*)', line)
                    if match:
                        key, text = match.groups()
                        options.append({"key": key, "text": text})


            question_type = "single_choice" if len(options) > 1 else "true_false"

            all_questions.append({
                "question_id": f"{page_num}_{qid}",
                "question_type": question_type,
                "question_text": question_text,
                "image": image_paths,
                "options": options
            })

# STEP 2: Parse answers
answer_pattern = r'(\d+)\.\s*(.*?)\nThe correct answer is:\s*([A-Z])\.?\s*(.*?)\n(.*?)(?=\n\d+\.\s|© BBC|\Z)'
matches = re.findall(answer_pattern, answers_text, re.DOTALL)
from fuzzywuzzy import fuzz

def normalize(text):
    return re.sub(r'\s+', ' ', text.strip().lower())

for qid, answer_qtext, key, summary, explanation in matches:
    explanation_text = summary.strip()
    if explanation:
        explanation_text += " " + explanation.strip()

    normalized_answer = normalize(answer_qtext)

    best_score = 0
    best_q = None

    for q in all_questions:
        normalized_q = normalize(q["question_text"])
        score = fuzz.token_set_ratio(normalized_answer, normalized_q)
        if score > best_score:
            best_score = score
            best_q = q

    if best_score >= 80: 
        best_q.update({
            "correct_answer": key,
            "answer_explanation": explanation_text.strip()
        })


# Save to JSON
with open("questions.json", "w") as f:
    json.dump(all_questions, f, indent=2)

print(" Questions extracted and saved to questions.json")
