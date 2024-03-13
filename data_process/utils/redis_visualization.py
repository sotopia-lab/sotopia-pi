import matplotlib.pyplot as plt
import numpy as np


def plot_agent_reward_distribution(env_rewards, scorename):
    agent1_rewards = sum([v["agent1"] for v in env_rewards.values()], [])
    agent2_rewards = sum([v["agent2"] for v in env_rewards.values()], [])
    # print(np.mean(agent1_rewards), np.median(agent1_rewards), np.var(agent1_rewards))
    # print(np.mean(agent2_rewards), np.median(agent2_rewards), np.var(agent2_rewards))
    fig, axs = plt.subplots(1, 2, figsize=(25, 12))
    axs[0].hist(agent1_rewards, color="skyblue")
    axs[0].set_title("Agent 1 (All Env) {}".format(scorename), fontsize=16)
    axs[0].legend(
        labels=[
            "Mean {}, Median {}, Var {}".format(
                round(np.mean(agent1_rewards), 2),
                round(np.median(agent1_rewards), 2),
                round(np.var(agent1_rewards), 2),
            )
        ],
        loc="best",
        fontsize=15,
    )
    axs[1].hist(agent2_rewards, color="navy")
    axs[1].set_title("Agent 2 (All Env) {}".format(scorename), fontsize=16)
    axs[1].legend(
        labels=[
            "Mean {}, Median {}, Var {}".format(
                round(np.mean(agent2_rewards), 2),
                round(np.median(agent2_rewards), 2),
                round(np.var(agent2_rewards), 2),
            )
        ],
        loc="best",
        fontsize=15,
    )


def plot_env_reward_distribution(env_rewards, split_agent=True):
    num_env = len(env_rewards)
    if split_agent:
        num_env *= 2
    fig, axs = plt.subplots(
        (num_env // 4) + 1, 4, figsize=(25, 5 * ((num_env // 4) + 1))
    )

    color_options = [
        "#1f77b4",
        "#7bc8f6",
        "#add8e6",
        "#d62728",
        "#9467bd",
        "#90ee90",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
        "#ffc0cb",
        "#c79fef",
        "#ffa500",
        "#dda0dd",
        "#d1b26f",
        "#d2b48c",
    ]
    idx = 0
    for env, dic in env_rewards.items():
        if not split_agent:
            scores = sum(dic.values(), [])
            row = idx // 4
            col = idx % 4
            axs[row, col].hist(
                scores, color=color_options[idx % len(color_options)]
            )
            axs[row, col].set_title(env)
            axs[row, col].title.set_size(12)
            idx += 1
        else:
            color = idx % len(color_options)
            for agent, scores in dic.items():
                row = idx // 4
                col = idx % 4
                axs[row, col].hist(scores, color=color_options[color])
                axs[row, col].set_title(env)
                axs[row, col].title.set_size(12)
                axs[row, col].legend([agent], loc="best", fontsize=8)
                idx += 1

    # Hide x labels and tick labels for top plots and y ticks for right plots.
    plt.subplots_adjust(
        left=0.1, bottom=0.1, right=0.9, top=0.9, wspace=0.4, hspace=0.4
    )


def make_pretty(styler, varmax):
    styler.set_caption("Statistics by Agent and Env")
    styler.format(precision=3)
    styler.background_gradient(
        subset=[("agent1", "var"), ("agent2", "var")],
        vmin=0,
        vmax=varmax,
        cmap="YlGnBu",
    )
    styler.background_gradient(
        subset=[("agent1", "mean"), ("agent2", "mean")],
        vmin=0,
        vmax=10,
        cmap="PuBu",
    )
    return styler
