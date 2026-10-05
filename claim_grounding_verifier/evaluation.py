"""
Evaluation Metrics & Benchmark Assessment Module
Computes Precision, Recall, Macro-F1, Confusion Matrix, and Abstention Risk-Coverage.
"""

from typing import List, Dict, Any
from .schema import Verdict


class GroundingEvaluator:
    def evaluate(self, y_true: List[Verdict], y_pred: List[Verdict]) -> Dict[str, Any]:
        verdicts = [Verdict.SUPPORTED, Verdict.REFUTED, Verdict.UNVERIFIABLE]
        cm = {v1.value: {v2.value: 0 for v2 in verdicts} for v1 in verdicts}

        for gt, pred in zip(y_true, y_pred):
            cm[gt.value][pred.value] += 1

        per_class_metrics = {}
        f1_scores = []

        for v in verdicts:
            v_str = v.value
            tp = cm[v_str][v_str]
            fp = sum(cm[other][v_str] for other in cm if other != v_str)
            fn = sum(cm[v_str][other] for other in cm[v_str] if other != v_str)

            prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

            per_class_metrics[v_str] = {
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1": round(f1, 4),
                "tp": tp, "fp": fp, "fn": fn
            }
            f1_scores.append(f1)

        macro_f1 = sum(f1_scores) / len(f1_scores)

        # Abstention Metrics
        total = len(y_true)
        abstentions = sum(1 for p in y_pred if p == Verdict.UNVERIFIABLE)
        coverage = (total - abstentions) / total if total > 0 else 0.0

        # Selective Accuracy (accuracy on non-abstained predictions)
        correct_non_abstained = sum(1 for gt, p in zip(y_true, y_pred) if p != Verdict.UNVERIFIABLE and gt == p)
        non_abstained_count = total - abstentions
        selective_acc = correct_non_abstained / non_abstained_count if non_abstained_count > 0 else 0.0

        return {
            "total_samples": total,
            "macro_f1": round(macro_f1, 4),
            "per_class": per_class_metrics,
            "confusion_matrix": cm,
            "coverage": round(coverage, 4),
            "selective_accuracy": round(selective_acc, 4)
        }
