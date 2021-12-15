# MIT License
#
# Copyright (C) 2021. Huawei Technologies Co., Ltd. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


from typing import Any, Dict, Sequence

import gym
import numpy as np


class RGBImage(gym.ObservationWrapper):
    """Filters SMARTS environment observation and returns only top-down RGB
    image as observation.

    If the base env's observation space is frame stacked using the FrameStack
    wrapper, then the returned observation will be a numpy array of stacked
    images with shape (image_width, image_height, 3*num_stack). Here, num_stack
    refers to the number of frames stacked in the base env's observation.
    """

    def __init__(self, env: gym.Env, num_stack: int):
        """
        Args:
            env (gym.Env): SMARTS environment to be wrapped.
            num_stack (int): Use 1 if base env's observation space is not stacked,
                else use the number of stacked frames in base env's observation.
        """
        super().__init__(env)
        agent_specs = env.agent_specs

        for agent_id in agent_specs.keys():
            assert agent_specs[agent_id].interface.rgb, (
                f"To use RGBImage wrapper, enable RGB "
                f"functionality in {agent_id}'s AgentInterface."
            )

        self._num_stack = num_stack
        assert self._num_stack > 0
        self.observation_space = gym.spaces.Dict(
            {
                agent_id: gym.spaces.Box(
                    low=0,
                    high=255,
                    shape=(
                        agent_specs[agent_id].interface.rgb.width,
                        agent_specs[agent_id].interface.rgb.height,
                        3 * self._num_stack,
                    ),
                    dtype=np.uint8,
                )
                for agent_id in agent_specs.keys()
            }
        )

    def observation(self, obs: Dict[str, Any]) -> Dict[str, np.ndarray]:
        wrapped_obs = {}
        for agent_id, agent_obs in obs.items():
            if isinstance(agent_obs, Sequence):
                true_num_stack = len(agent_obs)
            else:
                true_num_stack = 1
                agent_obs = [agent_obs]

            assert self._num_stack == true_num_stack, (
                f"User supplied `num_stack` (={self._num_stack}) argument to "
                f"`RGBImage` wrapper does not match the number of frames "
                f"stacked (={true_num_stack}) in the underlying base env."
            )

            images = []
            for agent_ob in agent_obs:
                image = agent_ob.top_down_rgb.data
                # Replace self color to Lime
                # image[123:132, 126:130, 0] = smarts_colors.Colors.Lime.value[0] * 255
                # image[123:132, 126:130, 1] = smarts_colors.Colors.Lime.value[1] * 255
                # image[123:132, 126:130, 2] = smarts_colors.Colors.Lime.value[2] * 255
                images.append(image.astype(np.uint8))

            stacked_images = np.dstack(images)
            wrapped_obs.update({agent_id: stacked_images})

        # Plot for debugging purposes
        import matplotlib.pyplot as plt
        fig=plt.figure(figsize=(5,5))
        columns = self._num_stack # number of stacked images
        rgb_gray = 3 # 3 for rgb and 1 for grayscale
        rows = len(wrapped_obs.keys())
        for row, (agent_id, state) in enumerate(wrapped_obs.items()):
            for col in range(0, columns):
                img = wrapped_obs[agent_id][:,:,col*rgb_gray:col*rgb_gray+rgb_gray]
                fig.add_subplot(rows, columns, row*columns + col + 1)
                plt.title(f"agent_id {col}")
                plt.imshow(img)
        plt.show()
        print("------------------------------------")
        # plt.pause(3)
        # plt.close()

        # # Plot for debugging purposes
        # import matplotlib.pyplot as plt
        # fig=plt.figure(figsize=(5,5))
        # plt.title(f"Agent obs RESIZED by dreamer")
        # plt.imshow(image)
        # plt.show()

        return wrapped_obs
