from sotopia.database.logs import EpisodeLog
from sotopia.database.persistent_profile import EnvironmentProfile
from sotopia.database.persistent_profile import AgentProfile
import json

# TAG = "ft-llama-2-13b-chat_gpt4_clean_ruiyi_1010_12" 
TAG = "ft-llama-2-13b-chat_baseline_ruiyi_1010_7" 

HARD_ENVS = ["01H7VFHNV13MHN97GAH73E3KM8", "01H7VFHN5WVC5HKKVBHZBA553R", "01H7VFHN9W0WAFZCBT09PKJJNK", "01H7VFHPDZVVCDZR3AARA547CY", "01H7VFHPQQQY6H4DNC6NBQ8XTG", "01H7VFHN7WJK7VWVRZZTQ6DX9T", "01H7VFHPS5WJW2694R1MNC8JFY",
             "01H7VFHNN7XTR99319DS8KZCQM", "01H7VFHQ11NAMZS4A2RDGDB01V", "01H7VFHPSWGDGEYRP63H2DJKV0", "01H7VFHNF4G18PC9JHGRC8A1R6", "01H7VFHNNYH3W0VRWVY178K2TK", "01H7VFHP8AN5643B0NR0NP00VE", "01H7VFHN7A1ZX5KSMT2YN9RXC4"]

envs = {}
eps_by_env = dict()
human_readable_eps_by_env = dict()

for env_profile_id in HARD_ENVS:
    envs[env_profile_id] = EnvironmentProfile.get(pk=env_profile_id).dict()
    eps = list(EpisodeLog.find(EpisodeLog.tag == TAG,
                            EpisodeLog.environment == env_profile_id))
    eps_by_env[env_profile_id] = eps
    human_readable_eps_by_env[env_profile_id] = []
    for ep in eps:
        agent_profiles, messages_and_rewards = ep.render_for_humans()
        while "Agent 1 comments:" not in messages_and_rewards[-1]:
            messages_and_rewards.pop()
        messages_and_rewards.pop()
        human_readable_eps_by_env[env_profile_id].append({"env_pk": env_profile_id, "ep_pk": ep.pk, "env_codename": envs[env_profile_id]['codename'], "agents": ep.agents, "messages": "\n".join(messages_and_rewards)})
        
with open("hard_env_scenarios.json", "w") as f:
    json.dump(envs, f)
    
with open("human_readable_eps_by_env.json", "w") as f:
    json.dump(human_readable_eps_by_env, f)