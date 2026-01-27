from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from typing import Protocol

from app.quiz.models import QuizQuestion


@dataclass(frozen=True)
class QuestionBankItem:
    question: str
    correct: str
    distractors: list[str]
    explanation: str


class QuizGenerator(Protocol):
    def generate(self, topic: str, difficulty: str, num_questions: int) -> list[QuizQuestion]:
        ...


class DeterministicQuizGenerator:
    def __init__(self) -> None:
        self._bank = {
            "python lists": [
                QuestionBankItem(
                    question="What is the primary purpose of a Python list?",
                    correct="To store an ordered, mutable collection of items.",
                    distractors=[
                        "To store only unique items without order.",
                        "To map keys to values in a fixed structure.",
                        "To define an immutable sequence of characters.",
                    ],
                    explanation="Lists are ordered and mutable, ideal for sequences you need to change.",
                ),
                QuestionBankItem(
                    question="Which list operation appends an item to the end?",
                    correct="list.append(item)",
                    distractors=[
                        "list.extend(item)",
                        "list.insert(item)",
                        "list.add(item)",
                    ],
                    explanation="append adds a single item to the end of a list.",
                ),
                QuestionBankItem(
                    question="What does slicing a list return?",
                    correct="A new list containing the selected elements.",
                    distractors=[
                        "A tuple with the first and last element.",
                        "A view into the original list.",
                        "A generator that yields items lazily.",
                    ],
                    explanation="Slicing returns a new list with the selected items.",
                ),
            ],
            "python dicts": [
                QuestionBankItem(
                    question="What data structure does a Python dict represent?",
                    correct="A mapping of unique keys to values.",
                    distractors=[
                        "An ordered list of duplicate values.",
                        "A fixed-size array of numbers.",
                        "A stack of items with LIFO access.",
                    ],
                    explanation="Dicts map unique keys to values for fast lookup.",
                ),
                QuestionBankItem(
                    question="Which method safely retrieves a value with a default?",
                    correct="dict.get(key, default)",
                    distractors=[
                        "dict.fetch(key, default)",
                        "dict.find(key, default)",
                        "dict.value(key, default)",
                    ],
                    explanation="get returns the default if the key is missing.",
                ),
                QuestionBankItem(
                    question="What happens when you assign an existing key in a dict?",
                    correct="The value is overwritten.",
                    distractors=[
                        "A new key is created with a suffix.",
                        "The assignment is ignored.",
                        "A KeyError is raised.",
                    ],
                    explanation="Keys are unique; assigning replaces the existing value.",
                ),
            ],
            "python functions": [
                QuestionBankItem(
                    question="What does a function return if no return statement is present?",
                    correct="None",
                    distractors=[
                        "False",
                        "0",
                        "An empty string",
                    ],
                    explanation="Python functions return None by default.",
                ),
                QuestionBankItem(
                    question="What is a parameter in a function definition?",
                    correct="A named variable listed in the function signature.",
                    distractors=[
                        "A value passed at call time.",
                        "A type annotation only.",
                        "A required keyword for all functions.",
                    ],
                    explanation="Parameters are variables defined in the function signature.",
                ),
                QuestionBankItem(
                    question="What is the purpose of *args in a function?",
                    correct="To accept a variable number of positional arguments.",
                    distractors=[
                        "To accept only keyword arguments.",
                        "To unpack dictionaries.",
                        "To define default values.",
                    ],
                    explanation="*args captures extra positional arguments.",
                ),
            ],
            "sql basics": [
                QuestionBankItem(
                    question="Which SQL clause filters rows in a SELECT query?",
                    correct="WHERE",
                    distractors=[
                        "ORDER BY",
                        "GROUP BY",
                        "HAVING",
                    ],
                    explanation="WHERE filters rows before grouping or ordering.",
                ),
                QuestionBankItem(
                    question="Which SQL statement inserts new rows?",
                    correct="INSERT INTO",
                    distractors=[
                        "ADD ROW",
                        "CREATE ROW",
                        "APPEND ROW",
                    ],
                    explanation="INSERT INTO adds new rows to a table.",
                ),
                QuestionBankItem(
                    question="What does SELECT * do in SQL?",
                    correct="Returns all columns from the selected tables.",
                    distractors=[
                        "Returns only primary key columns.",
                        "Deletes all rows from the table.",
                        "Returns only aggregated values.",
                    ],
                    explanation="SELECT * retrieves all columns in the result set.",
                ),
            ],
        }

        self._generic_stems = [
            "Which statement about {topic} is correct?",
            "Pick the best answer related to {topic}.",
            "In {topic}, which option fits best?",
            "Choose the correct concept about {topic}.",
            "Which option best describes {topic}?",
        ]
        self._generic_answer_sets = [
            (
                "{topic} has defined rules and common real-world use cases.",
                [
                    "{topic} is only used for styling user interfaces.",
                    "{topic} has no practical applications.",
                    "{topic} is a random string with no structure.",
                ],
            ),
            (
                "{topic} follows consistent patterns that make it predictable.",
                [
                    "{topic} is purely a visual design principle.",
                    "{topic} cannot be learned or practiced.",
                    "{topic} is unrelated to problem solving.",
                ],
            ),
            (
                "{topic} is commonly used to solve problems efficiently.",
                [
                    "{topic} only applies to hardware manufacturing.",
                    "{topic} is a deprecated concept with no usage today.",
                    "{topic} has no defined behavior or purpose.",
                ],
            ),
        ]
        self._generic_explanations = [
            "The correct choice reflects the typical definition and usage.",
            "The correct answer aligns with how the topic is commonly applied.",
            "The correct option matches standard expectations for the topic.",
        ]

    def generate(self, topic: str, difficulty: str, num_questions: int) -> list[QuizQuestion]:
        rng = random.Random(self._stable_seed(topic, difficulty, num_questions))
        if topic in self._bank:
            return self._generate_from_bank(topic, difficulty, num_questions, rng)
        return self._generate_generic(topic, difficulty, num_questions, rng)

    def _generate_from_bank(
        self,
        topic: str,
        difficulty: str,
        num_questions: int,
        rng: random.Random,
    ) -> list[QuizQuestion]:
        bank = list(self._bank[topic])
        rng.shuffle(bank)

        questions: list[QuizQuestion] = []
        for i in range(num_questions):
            item = bank[i % len(bank)]
            choices, answer_index = self._build_choices(item.correct, item.distractors, rng)
            questions.append(
                QuizQuestion(
                    id=i + 1,
                    question=f"{item.question} ({difficulty})",
                    choices=choices,
                    answer_index=answer_index,
                    explanation=item.explanation,
                )
            )
        return questions

    def _generate_generic(
        self,
        topic: str,
        difficulty: str,
        num_questions: int,
        rng: random.Random,
    ) -> list[QuizQuestion]:
        stems = list(self._generic_stems)
        rng.shuffle(stems)

        questions: list[QuizQuestion] = []
        for i in range(num_questions):
            stem = stems[i % len(stems)]
            correct_template, distractors = self._generic_answer_sets[
                i % len(self._generic_answer_sets)
            ]
            correct = correct_template.format(topic=topic)
            distractor_texts = [text.format(topic=topic) for text in distractors]
            choices, answer_index = self._build_choices(correct, distractor_texts, rng)
            explanation = self._generic_explanations[i % len(self._generic_explanations)]
            questions.append(
                QuizQuestion(
                    id=i + 1,
                    question=f"{stem.format(topic=topic)} ({difficulty})",
                    choices=choices,
                    answer_index=answer_index,
                    explanation=explanation,
                )
            )
        return questions

    @staticmethod
    def _stable_seed(topic: str, difficulty: str, num_questions: int) -> int:
        seed_input = f"{topic}|{difficulty}|{num_questions}".encode("utf-8")
        return int(hashlib.sha256(seed_input).hexdigest(), 16)

    @staticmethod
    def _build_choices(
        correct: str,
        distractors: list[str],
        rng: random.Random,
    ) -> tuple[list[str], int]:
        unique_distractors: list[str] = []
        for item in distractors:
            if item != correct and item not in unique_distractors:
                unique_distractors.append(item)

        if len(unique_distractors) < 3:
            fallback = [
                "None of the above.",
                "All of the above.",
                "Not enough information.",
                "Depends on the context.",
            ]
            for item in fallback:
                if item != correct and item not in unique_distractors:
                    unique_distractors.append(item)
                if len(unique_distractors) == 3:
                    break

        choices = [correct] + unique_distractors[:3]
        rng.shuffle(choices)
        return choices, choices.index(correct)
