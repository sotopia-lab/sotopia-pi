import os

# this file is used to tranfer data from one redis to another, we do not expect to use it more than once
os.environ["REDIS_OM_URL"] = "redis://:password@server_name:port_num"
# path to migrant: "redis://:auess29aknfl2jro20W@server_name:6377"

import json

from data_process.redis_data_filtering.redis_filtering import (
    get_sotopia_scenarios,
)
from redis_om import Migrator
from sotopia.database.env_agent_combo_storage import (
    EnvAgentComboStorage,
)
from sotopia.database.logs import EpisodeLog
from sotopia.database.persistent_profile import (
    AgentProfile,
    EnvironmentProfile,
    RelationshipProfile,
)

# res_pks = list(RelationshipProfile.all_pks()) # 120
env_agent_combos = list(EnvAgentComboStorage.all_pks())  # 550 > 1000
env_pks = list(EnvironmentProfile.all_pks())  # 62
# agent_pks = list(AgentProfile.all_pks()) # 40
# epi_pks = list(EpisodeLog.all_pks())
# all_combs = list(env_agent_combos)
# print(len(env_agent_combos), len(env_pks))#, len(res_pks), len(agent_pks))


def load_object_to_json(pks, objecttype, path):
    for pk in pks:
        objectp = objecttype.get(pk=pk)
        objectp_json = objectp.json()
        with open(os.path.join(path, f"{pk}.json"), "w") as f:
            f.write(objectp_json)


# load_object_to_json(env_pks, EnvironmentProfile, os.getcwd()+"/redis_env")
# load_object_to_json(env_agent_combos, EnvAgentComboStorage, os.getcwd()+"/redis_combo")


def upload_json_to_db(filepath, objecttype):
    for filename in os.listdir(filepath):
        if filename == ".DS_Store":
            continue
        with open(os.path.join(filepath, filename), "r") as f:
            jsonfile = json.load(f)
            newobject = objecttype(**jsonfile)
            newobject.save()


# Migrator().run()
# upload_json_to_db(os.getcwd()+"/redis_env", EnvironmentProfile)


def remove_bad_env():
    sotopia_pks = get_sotopia_scenarios()
    diff_pks = EnvironmentProfile.find(
        (EnvironmentProfile.pk >> sotopia_pks)
    ).all()
    for pk in diff_pks:
        environ = EnvironmentProfile.get(pk=pk)
        if len(environ.agent_goals) > 2:
            EnvironmentProfile.delete(pk)
