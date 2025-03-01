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
"""Tests for `transform.py`."""

from absl.testing import absltest
from absl.testing import parameterized

import chex
import jax
import jax.numpy as jnp
import numpy as np

from optax._src import alias
from optax._src import combine
from optax._src import transform
from optax._src import update

STEPS = 50
LR = 1e-2


class TransformTest(parameterized.TestCase):

  def setUp(self):
    super().setUp()
    self.init_params = (jnp.array([1., 2.]), jnp.array([3., 4.]))
    self.per_step_updates = (jnp.array([500., 5.]), jnp.array([300., 3.]))

  @chex.all_variants
  @parameterized.named_parameters([
      ('adam', transform.scale_by_adam),
      ('rmsprop', transform.scale_by_rms),
      ('stddev', transform.scale_by_stddev),
      ('trust_ratio', transform.scale_by_trust_ratio),
      ('param_norm', transform.scale_by_param_norm),
  ])
  def test_scalers(self, scaler_constr):
    params = self.init_params

    scaler = scaler_constr()
    init_fn = self.variant(scaler.init)
    transform_fn = self.variant(scaler.update)

    state = init_fn(params)
    chex.assert_tree_all_finite(state)

    updates, state = transform_fn(self.per_step_updates, state, params)
    chex.assert_tree_all_finite((params, updates, state))
    jax.tree_multimap(lambda *args: chex.assert_equal_shape(args), params,
                      updates)

  @chex.all_variants()
  def test_add_decayed_weights(self):
    # Define a transform that add decayed weights.
    # We can define a mask either as a pytree, or as a function that
    # returns the pytree. Below we define the pytree directly.
    mask = (True, dict(a=True, b=False))
    tx = transform.add_decayed_weights(0.1, mask=mask)
    # Define input updates and weights.
    updates = (
        jnp.zeros((2,), dtype=jnp.float32),
        dict(
            a=jnp.zeros((2,), dtype=jnp.float32),
            b=jnp.zeros((2,), dtype=jnp.float32),))
    weights = (
        jnp.ones((2,), dtype=jnp.float32),
        dict(
            a=jnp.ones((2,), dtype=jnp.float32),
            b=jnp.ones((2,), dtype=jnp.float32),))
    # This mask means that we will add decayed weights to the first two
    # terms in the input updates, but not to the last element.
    expected_tx_updates = (
        0.1*jnp.ones((2,), dtype=jnp.float32),
        dict(
            a=0.1*jnp.ones((2,), dtype=jnp.float32),
            b=jnp.zeros((2,), dtype=jnp.float32),))
    # Apply transform
    state = tx.init(weights)
    transform_fn = self.variant(tx.update)
    new_updates, _ = transform_fn(updates, state, weights)
    # Assert output as expected.
    chex.assert_tree_all_close(new_updates, expected_tx_updates)

  @chex.all_variants()
  def test_ema(self):
    values = jnp.array([5.0, 7.0])
    decay = 0.9
    d = decay

    ema = transform.ema(decay=decay)
    state = ema.init(values[0])

    transform_fn = self.variant(ema.update)
    mean, state = transform_fn(values[0], state)
    np.testing.assert_allclose(mean, values[0], atol=1e-4)

    mean, state = transform_fn(values[1], state)
    np.testing.assert_allclose(
        mean,
        (d * (1 - d) * values[0] + (1 - d) * values[1]) / (1 - d**2), atol=1e-4)

  @chex.all_variants()
  def test_apply_every(self):
    # The frequency of the application of sgd
    k = 4
    zero_update = (jnp.array([0., 0.]), jnp.array([0., 0.]))

    # optax sgd
    optax_sgd_params = self.init_params
    sgd = alias.sgd(LR, 0.0)
    state_sgd = sgd.init(optax_sgd_params)

    # optax sgd plus apply every
    optax_sgd_apply_every_params = self.init_params
    sgd_apply_every = combine.chain(
        transform.apply_every(k=k),
        transform.trace(decay=0, nesterov=False),
        transform.scale(-LR))
    state_sgd_apply_every = sgd_apply_every.init(optax_sgd_apply_every_params)
    transform_fn = self.variant(sgd_apply_every.update)

    for i in range(STEPS):
      # Apply a step of sgd
      updates_sgd, state_sgd = sgd.update(self.per_step_updates, state_sgd)
      optax_sgd_params = update.apply_updates(optax_sgd_params, updates_sgd)

      # Apply a step of sgd_apply_every
      updates_sgd_apply_every, state_sgd_apply_every = transform_fn(
          self.per_step_updates, state_sgd_apply_every)
      optax_sgd_apply_every_params = update.apply_updates(
          optax_sgd_apply_every_params, updates_sgd_apply_every)

      # Every k steps, check equivalence.
      if i % k == k-1:
        chex.assert_tree_all_close(
            optax_sgd_apply_every_params, optax_sgd_params,
            atol=1e-6, rtol=1e-5)
      # Otherwise, check update is zero.
      else:
        chex.assert_tree_all_close(
            updates_sgd_apply_every, zero_update, atol=0.0, rtol=0.0)

  def test_scale(self):
    updates = self.per_step_updates
    for i in range(1, STEPS + 1):
      factor = 0.1 ** i
      rescaler = transform.scale(factor)
      # Apply rescaling.
      scaled_updates, _ = rescaler.update(updates, None)
      # Manually scale updates.
      def rescale(t):
        return t * factor  # pylint:disable=cell-var-from-loop
      manual_updates = jax.tree_map(rescale, updates)
      # Check the rescaled updates match.
      chex.assert_tree_all_close(scaled_updates, manual_updates)

  @parameterized.named_parameters([
      ('1d', [1.0, 2.0], [1.0, 2.0]),
      ('2d', [[1.0, 2.0], [3.0, 4.0]], [[-0.5, 0.5], [-0.5, 0.5]]),
      ('3d', [[[1., 2.], [3., 4.]],
              [[5., 6.], [7., 8.]]], [[[-1.5, -0.5], [0.5, 1.5]],
                                      [[-1.5, -0.5], [0.5, 1.5]]]),
  ])
  def test_centralize(self, inputs, outputs):
    inputs = jnp.asarray(inputs)
    outputs = jnp.asarray(outputs)
    centralizer = transform.centralize()
    centralized_inputs, _ = centralizer.update(inputs, None)
    chex.assert_tree_all_close(centralized_inputs, outputs)


if __name__ == '__main__':
  absltest.main()
