# Copyright 2019 DeepMind Technologies Limited. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Optax: composable gradient processing and optimization, in JAX."""

from optax._src.alias import adabelief
from optax._src.alias import adagrad
from optax._src.alias import adam
from optax._src.alias import adamw
from optax._src.alias import dpsgd
from optax._src.alias import fromage
from optax._src.alias import lamb
from optax._src.alias import noisy_sgd
from optax._src.alias import radam
from optax._src.alias import rmsprop
from optax._src.alias import sgd
from optax._src.alias import sm3
from optax._src.alias import yogi
from optax._src.base import EmptyState
from optax._src.base import GradientTransformation
from optax._src.base import identity
from optax._src.base import OptState
from optax._src.base import Params
from optax._src.base import Schedule
from optax._src.base import TransformInitFn
from optax._src.base import TransformUpdateFn
from optax._src.base import Updates
from optax._src.clipping import adaptive_grad_clip
from optax._src.clipping import AdaptiveGradClipState
from optax._src.clipping import clip
from optax._src.clipping import clip_by_global_norm
from optax._src.clipping import ClipByGlobalNormState
from optax._src.clipping import ClipState
from optax._src.combine import chain
from optax._src.constrain import keep_params_nonnegative
from optax._src.constrain import NonNegativeParamsState
from optax._src.constrain import zero_nans
from optax._src.constrain import ZeroNansState
from optax._src.control_variates import control_delta_method
from optax._src.control_variates import control_variates_jacobians
from optax._src.control_variates import moving_avg_baseline
from optax._src.linear_algebra import global_norm
from optax._src.linear_algebra import matrix_inverse_pth_root
from optax._src.linear_algebra import power_iteration
from optax._src.lookahead import lookahead
from optax._src.lookahead import LookaheadParams
from optax._src.lookahead import LookaheadState
from optax._src.loss import cosine_distance
from optax._src.loss import cosine_similarity
from optax._src.loss import huber_loss
from optax._src.loss import l2_loss
from optax._src.loss import sigmoid_binary_cross_entropy
from optax._src.loss import smooth_labels
from optax._src.loss import softmax_cross_entropy
from optax._src.privacy import differentially_private_aggregate
from optax._src.privacy import DifferentiallyPrivateAggregateState
from optax._src.schedule import constant_schedule
from optax._src.schedule import cosine_decay_schedule
from optax._src.schedule import cosine_onecycle_schedule
from optax._src.schedule import exponential_decay
from optax._src.schedule import inject_hyperparams
from optax._src.schedule import InjectHyperparamsState
from optax._src.schedule import join_schedules
from optax._src.schedule import linear_onecycle_schedule
from optax._src.schedule import linear_schedule
from optax._src.schedule import piecewise_constant_schedule
from optax._src.schedule import piecewise_interpolate_schedule
from optax._src.schedule import polynomial_schedule
from optax._src.schedule import sgdr_schedule
from optax._src.schedule import warmup_cosine_decay_schedule
from optax._src.schedule import warmup_exponential_decay_schedule
from optax._src.second_order import fisher_diag
from optax._src.second_order import hessian_diag
from optax._src.second_order import hvp
from optax._src.stochastic_gradient_estimators import measure_valued_jacobians
from optax._src.stochastic_gradient_estimators import pathwise_jacobians
from optax._src.stochastic_gradient_estimators import score_function_jacobians
from optax._src.transform import add_decayed_weights
from optax._src.transform import add_noise
from optax._src.transform import AddDecayedWeightsState
from optax._src.transform import additive_weight_decay
from optax._src.transform import AdditiveWeightDecayState
from optax._src.transform import AddNoiseState
from optax._src.transform import apply_every
from optax._src.transform import ApplyEvery
from optax._src.transform import centralize
from optax._src.transform import ema
from optax._src.transform import EmaState
from optax._src.transform import scale
from optax._src.transform import scale_by_adam
from optax._src.transform import scale_by_belief
from optax._src.transform import scale_by_param_norm
from optax._src.transform import scale_by_radam
from optax._src.transform import scale_by_rms
from optax._src.transform import scale_by_rss
from optax._src.transform import scale_by_schedule
from optax._src.transform import scale_by_sm3
from optax._src.transform import scale_by_stddev
from optax._src.transform import scale_by_trust_ratio
from optax._src.transform import scale_by_yogi
from optax._src.transform import ScaleByAdamState
from optax._src.transform import ScaleByFromageState
from optax._src.transform import ScaleByRmsState
from optax._src.transform import ScaleByRssState
from optax._src.transform import ScaleByRStdDevState
from optax._src.transform import ScaleByScheduleState
from optax._src.transform import ScaleBySM3State
from optax._src.transform import ScaleByTrustRatioState
from optax._src.transform import ScaleState
from optax._src.transform import trace
from optax._src.transform import TraceState
from optax._src.update import apply_updates
from optax._src.update import incremental_update
from optax._src.update import periodic_update
from optax._src.utils import multi_normal
from optax._src.wrappers import apply_if_finite
from optax._src.wrappers import ApplyIfFiniteState
from optax._src.wrappers import flatten
from optax._src.wrappers import masked
from optax._src.wrappers import MaskedState
from optax._src.wrappers import maybe_update
from optax._src.wrappers import MaybeUpdateState
from optax._src.wrappers import MultiSteps
from optax._src.wrappers import MultiStepsState

__version__ = "0.0.7"

__all__ = (
    "adabelief",
    "adagrad",
    "adam",
    "adamw",
    "AdaptiveGradClipState",
    "adaptive_grad_clip",
    "add_decayed_weights",
    "add_noise",
    "AddDecayedWeightsState",
    "additive_weight_decay",
    "AdditiveWeightDecayState",
    "AddNoiseState",
    "apply_if_finite",
    "apply_every",
    "apply_updates",
    "ApplyEvery",
    "ApplyIfFiniteState",
    "centralize",
    "chain",
    "clip",
    "clip_by_global_norm",
    "ClipByGlobalNormState",
    "ClipState",
    "constant_schedule",
    "control_delta_method",
    "control_variates_jacobians",
    "cosine_decay_schedule",
    "cosine_distance",
    "cosine_onecycle_schedule",
    "cosine_similarity",
    "dpsgd",
    "differentially_private_aggregate",
    "DifferentiallyPrivateAggregateState",
    "ema",
    "EmaState",
    "EmptyState",
    "exponential_decay",
    "fisher_diag",
    "flatten",
    "fromage",
    "global_norm",
    "GradientTransformation",
    "hessian_diag",
    "huber_loss",
    "hvp",
    "identity",
    "incremental_update",
    "inject_hyperparams",
    "InjectHyperparamsState",
    "join_schedules",
    "lamb",
    "lookahead",
    "LookaheadParams",
    "LookaheadState",
    "l2_loss",
    "linear_onecycle_schedule",
    "linear_schedule",
    "matrix_inverse_pth_root",
    "masked",
    "MaskedState",
    "measure_valued_jacobians",
    "moving_avg_baseline",
    "multi_normal",
    "noisy_sgd",
    "OptState",
    "Params",
    "pathwise_jacobians",
    "periodic_update",
    "piecewise_constant_schedule",
    "piecewise_interpolate_schedule",
    "polynomial_schedule",
    "power_iteration",
    "radam",
    "rmsprop",
    "scale",
    "scale_by_adam",
    "scale_by_belief",
    "scale_by_param_norm",
    "scale_by_radam",
    "scale_by_rms",
    "scale_by_rss",
    "scale_by_schedule",
    "scale_by_sm3",
    "scale_by_stddev",
    "scale_by_trust_ratio",
    "scale_by_yogi",
    "ScaleByAdamState",
    "ScaleByFromageState",
    "ScaleByRmsState",
    "ScaleByRssState",
    "ScaleByRStdDevState",
    "ScaleByScheduleState",
    "ScaleBySM3State",
    "ScaleByTrustRatioState",
    "ScaleState",
    "Schedule",
    "score_function_jacobians",
    "sgd",
    "sgdr_schedule",
    "sm3",
    "sigmoid_binary_cross_entropy",
    "smooth_labels",
    "softmax_cross_entropy",
    "trace",
    "TraceState",
    "TransformInitFn",
    "TransformUpdateFn",
    "Updates",
    "warmup_cosine_decay_schedule",
    "warmup_exponential_decay_schedule",
    "yogi",
)

#  _________________________________________
# / Please don't use symbols in `_src` they \
# \ are not part of the Optax public API.   /
#  -----------------------------------------
#         \   ^__^
#          \  (oo)\_______
#             (__)\       )\/\
#                 ||----w |
#                 ||     ||
#
