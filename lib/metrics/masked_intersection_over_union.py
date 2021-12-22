import torch
from typing import Tuple, Dict, List

from lib.metrics import MaskedScalar
from metrics.intersection_over_union import compute_iou


class MaskedIntersectionOverUnion(MaskedScalar):
    def __init__(self, match_label: bool = False, match_mask: bool = True, reduction: str = "mean",
                 ignore_labels: List[int] = None):
        super().__init__(reduction, ignore_labels)

        self.match_label = match_label
        self.match_mask = match_mask

    def add(self, prediction: torch.Tensor, ground_truth: Tuple[torch.Tensor, Dict[int, torch.Tensor]]) -> None:
        ground_truth, masks = ground_truth

        ones = torch.ones([1], device=ground_truth.device)
        zeros = torch.zeros([1], device=ground_truth.device)

        for label, mask in masks.items():
            if not self._should_label_be_ignored(label):

                if self.match_label:
                    ground_truth_mask = ground_truth == label
                    prediction_mask = prediction == label

                if self.match_mask:
                    ground_truth_mask = mask & ground_truth
                    prediction_mask = mask & prediction

                masked_ground_truth = torch.where(ground_truth_mask, ones, zeros)
                masked_prediction = torch.where(prediction_mask, ones, zeros)
                scalar = self.evaluate_sample(masked_ground_truth, masked_prediction)
                self.values[label].append(scalar)
                self.totals[label] += masked_prediction.numel()

        self._is_valid = False

    def evaluate_sample(self, ground_truth: torch.Tensor, prediction: torch.Tensor) -> float:
        iou = compute_iou(ground_truth, prediction)
        return iou
